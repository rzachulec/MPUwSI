# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml"]
# ///
"""Pilot: renderuje prompty, wysyła każdy jako pojedynczą wiadomość w nowej rozmowie
(OpenAI-compatible /chat/completions, bez system promptu) i zapisuje wyniki do JSONL.

Klucz API tylko ze zmiennych środowiskowych (LLM_API_KEY / LLM_BASE_URL / LLM_MODEL,
z fallbackiem na LLM_REMOTE_*) albo z pliku wskazanego przez --env-file.

Przykład:
    uv run run.py --env-file ../../../hacknation/cyfryzacja-formularzy/.env \
        --model arklabsai/Bielik-11B-v3.1-Instruct --repeats 3
"""

import argparse
import itertools
import json
import os
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

import yaml

from reference import load_kb, reference

HERE = Path(__file__).parent
TEMPLATES = {"symbolic": "prompt_template.txt", "domain": "prompt_template_domain.txt"}


def load_env_file(path: Path) -> None:
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        os.environ[k.strip()] = v.strip().strip('"').strip("'")  # późniejsze nadpisują wcześniejsze


def kb_table(kb: list[dict]) -> str:
    return "\n".join(f"{u['id']:<3} {u['p']} {u['q']} {u['r']} {u['s']}" for u in kb)


def render(template: str, kb: list[dict], ctx: dict) -> str:
    return (
        template.replace("{KB_TABLE}", kb_table(kb))
        .replace("{Q}", str(ctx["q"]))
        .replace("{R}", str(ctx["r"]))
        .replace("{S}", str(ctx["s"]))
    )


def all_contexts() -> list[dict]:
    out = []
    for q, r, s in itertools.product(["?", 0, 1], repeat=3):
        out.append({"id": f"C_q{q}_r{r}_s{s}".replace("?", "x"),
                    "q": q, "r": r, "s": s, "goal": "kontekst z pełnej siatki 27"})
    return out


def chat(base_url: str, api_key: str, model: str, prompt: str, temperature: float, max_tokens: int,
         timeout: float) -> dict:
    body = {"model": model, "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature, "max_tokens": max_tokens}
    req = urllib.request.Request(
        base_url.rstrip("/") + "/chat/completions",
        data=json.dumps(body).encode(),
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
    )
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return json.loads(resp.read())
        except (urllib.error.URLError, TimeoutError) as e:
            if attempt == 3:
                raise
            print(f"  retry ({e})")
            time.sleep(5 * (attempt + 1))
    raise RuntimeError("unreachable")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--env-file", type=Path)
    ap.add_argument("--model")
    ap.add_argument("--base-url")
    ap.add_argument("--temperature", type=float, default=0.7)
    ap.add_argument("--max-tokens", type=int, default=2048)
    ap.add_argument("--repeats", type=int, default=1)
    ap.add_argument("--variant", choices=list(TEMPLATES), default="symbolic")
    ap.add_argument("--all-contexts", action="store_true", help="27 kontekstów zamiast T1–T5")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--timeout", type=float, default=300)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    if args.env_file:
        load_env_file(args.env_file)
    env = os.environ.get
    base_url = args.base_url or env("LLM_BASE_URL_PILOT") or env("LLM_REMOTE_BASE_URL") or env("LLM_BASE_URL")
    api_key = env("LLM_REMOTE_API_KEY") or env("LLM_API_KEY") or ""
    model = args.model or env("LLM_REMOTE_MODEL") or env("LLM_MODEL")

    kb = load_kb()
    template = (HERE / TEMPLATES[args.variant]).read_text()
    tests = all_contexts() if args.all_contexts else yaml.safe_load((HERE / "contexts.yaml").read_text())["tests"]
    if args.variant == "domain":
        tests = [{**t, "id": t["id"].replace("T", "D", 1) if t["id"].startswith("T") else "D" + t["id"]} for t in tests]

    jobs = [(t, rep) for t in tests for rep in range(1, args.repeats + 1)]
    if args.dry_run:
        print(render(template, kb, jobs[0][0]))
        print(f"\n{len(jobs)} zapytań → {model} @ {base_url}")
        return

    out_dir = HERE / "results" / model.replace("/", "__")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{datetime.now().date().isoformat()}.jsonl"

    def run_one(job):
        t, rep = job
        ctx = {k: t[k] for k in ("q", "r", "s")}
        prompt = render(template, kb, ctx)
        ts = datetime.now(timezone.utc).isoformat()
        t0 = time.time()
        raw = chat(base_url, api_key, model, prompt, args.temperature, args.max_tokens, args.timeout)
        msg = raw["choices"][0]["message"]
        ref = reference(ctx, kb)
        rec = {
            "test_id": t["id"], "variant": args.variant, "repeat": rep, "goal": t.get("goal"),
            "context": ctx, "model": model, "model_version": raw.get("model"),
            "temperature": args.temperature, "max_tokens": args.max_tokens, "timestamp": ts,
            "latency_s": round(time.time() - t0, 1), "prompt": prompt,
            "response": msg.get("content"),
            "reasoning": msg.get("reasoning_content") or msg.get("reasoning"),
            "finish_reason": raw["choices"][0].get("finish_reason"), "usage": raw.get("usage"),
            "reference_class": ref["class"], "reference_counts": [ref["n_pos"], ref["n_neg"]],
            "reference_holon": ref["holon"], "reference_messages": ref["messages"],
        }
        print(f"  {t['id']} #{rep}: {rec['latency_s']}s, {rec['finish_reason']}")
        return rec

    print(f"{len(jobs)} zapytań → {model} ({args.variant}) → {out_path}")
    with ThreadPoolExecutor(args.workers) as pool:
        records = list(pool.map(run_one, jobs))
    with open(out_path, "a") as f:
        for rec in records:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    print("zapisano", len(records), "rekordów")


if __name__ == "__main__":
    main()
