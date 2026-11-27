import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote
from uuid import uuid4

import yaml

from reference import CONDITIONS, FEATURES, evaluate, read_kb

FOLDER = Path(__file__).resolve().parent


def read_contexts(path: Path) -> dict[str, dict[str, int | None]]:
    contexts = yaml.safe_load(path.read_text(encoding="utf-8-sig"))
    if not isinstance(contexts, dict) or not contexts:
        raise ValueError("contexts.yaml musi zawierać co najmniej jeden test.")

    for test_id, context in contexts.items():
        if not isinstance(test_id, str) or not test_id.strip():
            raise ValueError("Każdy test musi mieć tekstowy identyfikator.")
        if not isinstance(context, dict) or set(context) != set(CONDITIONS):
            raise ValueError(f"{test_id}: podaj wartości q, r i s.")
        if any(v is not None and (type(v) is not int or v not in (0, 1)) for v in context.values()):
            raise ValueError(f"{test_id}: wartości muszą być równe 0, 1 lub null.")
    return contexts


def prepare_tests(folder: Path, selected: list[str]) -> list[dict]:
    history = read_kb(folder / "kb.csv")
    contexts = read_contexts(folder / "contexts.yaml")
    unknown = set(selected) - contexts.keys()
    if unknown:
        raise ValueError(f"Nieznane testy: {', '.join(sorted(unknown))}.")

    template = (folder / "prompt_template.txt").read_text(encoding="utf-8-sig").strip()
    table = "\n".join(
        [
            "id p q r s",
            *(
                identifier + " " + " ".join(str(row[k]) for k in FEATURES)
                for identifier, row in history.items()
            ),
        ]
    )
    return [
        {
            "test_id": test_id,
            "context": {"p": None, **context},
            "prompt": template.format(
                history=table, **{k: "?" if v is None else v for k, v in context.items()}
            ),
            **evaluate(history, context),
        }
        for test_id, context in contexts.items()
        if not selected or test_id in selected
    ]


def literal_block(value: str) -> str:
    longest = max((len(match[0]) for match in re.finditer(r"\x60+", value)), default=0)
    fence = "\x60" * max(3, longest + 1)
    return f"{fence}text\n{value}\n{fence}"


def write_report(path: Path, trials: list[dict]) -> None:
    previous = path.read_text(encoding="utf-8").rstrip("\n") if path.exists() else "# Pilotaż API"
    lines = [previous, ""]
    for trial in trials:
        counts = trial["reference_counts"]["p"]
        strengths = trial["reference_holon"]["p"]
        messages = ", ".join(trial["reference_messages"])
        matching = ", ".join(trial["matching_history"]) or "pusta klasa"
        response = trial["response"]
        lines.extend(
            [
                f"## {trial['test_id']} – powtórzenie {trial['repeat']}",
                "",
                (
                    f"Model i wersja: {trial['model']} ({trial['model_version']}). "
                    f"Temperatura: {trial['temperature']}. Czas UTC: {trial['timestamp']}."
                ),
                "",
                f"Kontekst: {literal_context(trial['context'])}.",
                "",
                "**Prompt**",
                "",
                literal_block(trial["prompt"]),
                "",
                "**Odpowiedź**",
                "",
                literal_block(response)
                if response is not None
                else "Interfejs zwrócił pustą treść.",
                "",
                f"Zakończenie odpowiedzi: {trial['finish_reason']}.",
                "",
                "**Punkt odniesienia**",
                "",
                (
                    f"Obserwacje: {matching}. Liczebności n₁/n₀: {counts['true']}/{counts['false']}. "
                    f"Holon: [{strengths['true']}, {strengths['false']}]. Komunikaty: {messages}."
                ),
                "",
                "**Frazy i ich klasy, w tym niejednoznaczne**",
                "",
                "**Wykorzystanie kontekstu i uzasadnienie**",
                "",
                "**Spostrzeżenia i wstępna ocena logiczno-pragmatyczna**",
                "",
            ]
        )
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".md.tmp")
    temporary.write_text("\n".join(lines), encoding="utf-8")
    temporary.replace(path)


def literal_context(context: dict[str, int | None]) -> str:
    return ", ".join(f"{k}={'?' if context[k] is None else context[k]}" for k in FEATURES)


def run_api(
    folder: Path, model: str, temperature: float | None, repeats: int, tests: list[dict]
) -> None:
    from dotenv import load_dotenv

    load_dotenv(folder / ".env", override=False)

    from litellm import completion
    from litellm.exceptions import LITELLM_EXCEPTION_TYPES

    started = datetime.now(timezone.utc)
    series = uuid4().hex
    model_dir = quote(model, safe="")
    result_folder = folder / "results" / model_dir
    result_folder.mkdir(parents=True, exist_ok=True)
    result_file = result_folder / f"{started.date()}.jsonl"
    report_file = folder / "report" / f"{model_dir}.md"
    lock = result_folder / ".run.lock"
    params = {} if temperature is None else {"temperature": temperature}
    provider_errors = (*LITELLM_EXCEPTION_TYPES, TimeoutError, IndexError)
    saved = []

    try:
        with lock.open("x"):
            pass
    except FileExistsError:
        raise RuntimeError(f"Zajęta blokada serii dla modelu {model}: {lock}.") from None
    try:
        with result_file.open("a", encoding="utf-8", newline="\n") as output:
            for test in tests:
                for repeat in range(1, repeats + 1):
                    try:
                        result = completion(
                            model=model,
                            messages=[{"role": "user", "content": test["prompt"]}],
                            timeout=120,
                            **params,
                        )
                        choice = result.choices[0]
                    except provider_errors as exc:
                        raise RuntimeError(
                            f"{test['test_id']}, powtórzenie {repeat}: {type(exc).__name__}."
                        ) from None
                    record = {
                        **test,
                        "model": model,
                        "model_version": result.model,
                        "temperature": temperature,
                        "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                        "response": choice.message.content,
                        "finish_reason": choice.finish_reason,
                        "repeat": repeat,
                        "run_id": series,
                    }
                    output.write(json.dumps(record, ensure_ascii=False) + "\n")
                    output.flush()
                    saved.append(record)
    finally:
        try:
            if saved:
                write_report(report_file, saved)
        finally:
            lock.unlink()
    print(result_file)
    print(report_file)


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(description="Pilotaż T1–T5 z niezależnymi rozmowami.")
    parser.add_argument("--model", help="Identyfikator LiteLLM w postaci dostawca/model.")
    parser.add_argument("--temperature", type=float)
    parser.add_argument("--repeats", type=int, default=1)
    parser.add_argument(
        "--test", action="append", default=[], help="Uruchom wybrany test. Opcję można powtórzyć."
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Pokaż dane wejściowe i referencje przed próbą."
    )
    args = parser.parse_args()

    if args.repeats < 1:
        parser.error("--repeats wymaga dodatniej liczby całkowitej.")
    if args.temperature is not None and not 0 <= args.temperature <= 2:
        parser.error("--temperature musi być w przedziale od 0 do 2.")
    if not args.dry_run and (
        not args.model or not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_./:@-]+", args.model)
    ):
        parser.error("Podaj --model w postaci dostawca/model.")

    try:
        tests = prepare_tests(FOLDER, args.test)
        if args.dry_run:
            print(json.dumps(tests, ensure_ascii=False, indent=2))
        else:
            run_api(FOLDER, args.model, args.temperature, args.repeats, tests)
    except (ValueError, KeyError, OSError, RuntimeError, yaml.YAMLError, ImportError) as exc:
        parser.error(str(exc))


if __name__ == "__main__":
    main()
