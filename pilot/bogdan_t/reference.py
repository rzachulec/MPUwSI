import csv
from fractions import Fraction
from pathlib import Path

FEATURES = ("p", "q", "r", "s")
CONDITIONS = FEATURES[1:]


def read_kb(path: Path) -> dict[str, dict[str, int]]:
    history = {}
    with path.open(encoding="utf-8-sig", newline="") as source:
        reader = csv.DictReader(source)
        if reader.fieldnames != ["id", *FEATURES]:
            raise ValueError("Nagłówek bazy musi mieć postać id,p,q,r,s.")

        for row in reader:
            identifier = row["id"]
            if not identifier or identifier in history:
                raise ValueError(f"Wiersz {reader.line_num} ma pusty lub powtórzony identyfikator.")
            if None in row or any(row[feature] not in ("0", "1") for feature in FEATURES):
                raise ValueError(f"Wiersz {reader.line_num} musi zawierać cztery wartości 0 lub 1.")
            history[identifier] = {feature: int(row[feature]) for feature in FEATURES}
    return history


def modality(strength: Fraction) -> str | None:
    if strength >= Fraction(9, 10):
        return "Know"
    if strength >= Fraction(13, 20):
        return "Bel"
    if strength >= Fraction(1, 5):
        return "Pos"
    return None


def evaluate(history: dict[str, dict[str, int]], context: dict[str, int | None]) -> dict:
    known = {feature: context[feature] for feature in CONDITIONS if context[feature] is not None}
    matching = [
        identifier
        for identifier, row in history.items()
        if all(row[feature] == value for feature, value in known.items())
    ]
    positive = sum(history[identifier]["p"] for identifier in matching)
    negative = len(matching) - positive
    strengths = (
        Fraction(positive + 1, len(matching) + 2),
        Fraction(negative + 1, len(matching) + 2),
    )
    messages = []
    for symbol, strength in zip(("p", "¬p"), strengths):
        kind = modality(strength)
        if kind is not None:
            messages.append(f"{kind}({symbol})")

    return {
        "matching_history": matching,
        "reference_counts": {"p": {"true": positive, "false": negative}},
        "reference_holon": {"p": {"true": str(strengths[0]), "false": str(strengths[1])}},
        "reference_messages": messages,
    }
