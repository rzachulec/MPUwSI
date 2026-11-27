# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml"]
# ///
"""Generuje report/<model>.md w formacie z pilot_README §6.

Pola faktograficzne (prompt, odpowiedź, odpowiedź referencyjna) pochodzą z results/<model>/*.jsonl.
Pola analityczne pochodzą z analysis/<model>.yaml (propozycja – do weryfikacji przez autora).

    uv run report.py arklabsai__Bielik-11B-v3.1-Instruct
"""

import json
import sys
from pathlib import Path

import yaml

HERE = Path(__file__).parent
SYM = {0: "−", 1: "+", "?": "±"}
CLASS_NAMES = {(q, r, s): f"B{q * 4 + r * 2 + s}" for q in (0, 1) for r in (0, 1) for s in (0, 1)}


def ctx_str(c: dict) -> str:
    return "{p±, " + ", ".join(f"{a}{SYM[c[a] if c[a] == '?' else int(c[a])]}" for a in "qrs") + "}"


def class_name(c: dict) -> str:
    if any(str(c[a]) == "?" for a in "qrs"):
        return "B0∅" if all(str(c[a]) == "?" for a in "qrs") else "klasa częściowa"
    return CLASS_NAMES[(int(c["q"]), int(c["r"]), int(c["s"]))]


def quote(text: str) -> str:
    return "\n".join("> " + line if line.strip() else ">" for line in (text or "").strip().splitlines())


def ref_line(r: dict) -> str:
    cls = ", ".join(r["reference_class"]) or "∅ (brak obserwacji)"
    n_pos, n_neg = r["reference_counts"]
    lp, ln = r["reference_holon"]
    return (f"klasa {class_name(r['context'])} = {{{cls}}}, n+/n− = {n_pos}/{n_neg}, "
            f"holon [{lp}, {ln}] → **{', '.join(r['reference_messages'])}**")


def main(model_slug: str) -> None:
    records = []
    for f in sorted((HERE / "results" / model_slug).glob("*.jsonl")):
        records += [json.loads(line) for line in f.open()]
    ann_path = HERE / "analysis" / f"{model_slug}.yaml"
    ann = yaml.safe_load(ann_path.read_text()) if ann_path.exists() else {}
    grid_ann = ann.get("grid", {})

    main_tests = [r for r in records if not r["test_id"].startswith("C_")]
    grid = [r for r in records if r["test_id"].startswith("C_")]
    first = records[0]
    model_line = (f"{first['model_version']} / API OpenAI-compatible (`/chat/completions`, ark-labs.cloud) / "
                  f"{first['timestamp'][:10]} / temperature={first['temperature']}, max_tokens={first['max_tokens']}, "
                  f"bez własnego system promptu; {ann.get('meta', {}).get('uwagi', '')}")

    out = [f"# Raport pilotażu – {first['model_version']}", "",
           "> Pola faktograficzne (prompt, odpowiedź, odpowiedź referencyjna) wygenerowane automatycznie z "
           f"`results/{model_slug}/`. Pola analityczne (frazy, klasyfikacja, ocena) to **propozycja LLM "
           "(Claude Opus 5.5) do weryfikacji przez autora** – źródło: "
           f"`analysis/{model_slug}.yaml`.", "",
           f"- System / wersja / interfejs / data / parametry: {model_line}", ""]

    shown_prompt = set()
    for variant, title in (("symbolic", "Testy właściwe T1–T5 (symbole p, q, r, s)"),
                           ("domain", "Wariant z interpretacją dziedzinową D1–D5 (CI/build)")):
        recs = [r for r in main_tests if r["variant"] == variant]
        if not recs:
            continue
        out += [f"## {title}", ""]
        for r in sorted(recs, key=lambda r: (r["test_id"], r["repeat"])):
            key = f"{r['test_id']}#{r['repeat']}"
            a = ann.get(key, {})
            out += [f"### {key} — {r.get('goal') or ''}",
                    f"- Kontekst bieżący: {ctx_str(r['context'])}"]
            if (variant, r["test_id"]) not in shown_prompt:
                out += ["- Prompt (dosłownie):", "", quote(r["prompt"]), ""]
                shown_prompt.add((variant, r["test_id"]))
            else:
                out += [f"- Prompt: identyczny jak w {r['test_id']}#1 (nowa, czysta sesja)"]
            out += ["- Odpowiedź systemu (dosłownie, bez skracania):", "", quote(r["response"]), "",
                    f"- Odpowiedź referencyjna: {ref_line(r)}"]
            if a:
                out += ["- Środki lingwistyczne i klasyfikacja:", "",
                        "  | fraza | dotyczy | klasa |", "  |---|---|---|"]
                out += [f"  | „{f}” | {d} | {k} |" for f, d, k in a.get("frazy", [])] or ["  | — | — | — |"]
                out += ["", f"- Środki nieklasyfikowalne: {'; '.join(a.get('nieklas', [])) or '—'}",
                        f"- Uzasadnienie systemu: {a.get('uzasadnienie', '…')}; "
                        f"odwołuje się do klasy warunkowej: {a.get('klasa_warunkowa', '…')}",
                        f"- Wykorzystanie kontekstu: {a.get('kontekst', '…')}",
                        f"- Najważniejsze spostrzeżenia: {a.get('spostrzezenia', '…')}",
                        f"- Wstępna ocena poprawności: {a.get('ocena', '…')}"]
            else:
                out += ["- Środki lingwistyczne i klasyfikacja: …", "- Wstępna ocena poprawności: …"]
            out.append("")

    if grid:
        out += ["## Siatka 27 kontekstów (1 przebieg każdy)", "",
                "Pełne odpowiedzi w JSONL. Tu: ostatnie zdanie odpowiedzi + referencja + skrócona ocena.", "",
                "| kontekst | n+/n− | referencja | ostatnie zdanie odpowiedzi | ocena (propozycja) |",
                "|---|---|---|---|---|"]
        for r in sorted(grid, key=lambda r: r["test_id"]):
            last = [x for x in r["response"].strip().splitlines() if x.strip()][-1].replace("|", "\\|")
            n_pos, n_neg = r["reference_counts"]
            out.append(f"| {ctx_str(r['context'])} | {n_pos}/{n_neg} | {', '.join(r['reference_messages'])} "
                       f"| {last} | {grid_ann.get(r['test_id'], '…')} |")
        out.append("")

    path = HERE / "report" / f"{model_slug}.md"
    path.parent.mkdir(exist_ok=True)
    path.write_text("\n".join(out))
    print("zapisano", path)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "arklabsai__Bielik-11B-v3.1-Instruct")
