"""Odpowiedź referencyjna: klasa warunkowa + holon + progi modalności (pilot_README §4)."""

import csv
from pathlib import Path

HERE = Path(__file__).parent
POS_MIN, BEL_MIN, KNOW_MIN = 0.2, 0.65, 0.9
ASPECTS = ("q", "r", "s")


def load_kb(path: Path = HERE / "kb.csv") -> list[dict]:
    with open(path, newline="") as f:
        return [{k: (v if k == "id" else int(v)) for k, v in row.items()} for row in csv.DictReader(f)]


def _known(v) -> int | None:
    return None if str(v) == "?" else int(v)


def modality(lam: float) -> str | None:
    if lam >= KNOW_MIN:
        return "Know"
    if lam >= BEL_MIN:
        return "Bel"
    if lam >= POS_MIN:
        return "Pos"
    return None


def reference(context: dict, kb: list[dict] | None = None) -> dict:
    """context: {'q': 0|1|'?', 'r': ..., 's': ...}. Nieznane cechy nie zawężają klasy."""
    kb = kb or load_kb()
    known = {a: _known(context[a]) for a in ASPECTS if _known(context[a]) is not None}
    cls = [u for u in kb if all(u[a] == v for a, v in known.items())]
    n_pos = sum(u["p"] == 1 for u in cls)
    n_neg = len(cls) - n_pos
    lam_pos = (1 + n_pos) / (2 + n_pos + n_neg)
    lam_neg = (1 + n_neg) / (2 + n_pos + n_neg)
    messages = []
    if (m := modality(lam_pos)) is not None:
        messages.append(f"{m}(p)")
    if (m := modality(lam_neg)) is not None:
        messages.append(f"{m}(¬p)")
    return {
        "class": [u["id"] for u in cls],
        "n_pos": n_pos,
        "n_neg": n_neg,
        "holon": [round(lam_pos, 3), round(lam_neg, 3)],
        "messages": messages,
    }


def _selftest() -> None:
    expected = {  # tabela z pilot_README §4
        ("?", "?", "?"): ([0.357, 0.643], ["Pos(p)", "Pos(¬p)"]),
        (0, 0, 0): ([0.5, 0.5], ["Pos(p)", "Pos(¬p)"]),
        (0, 0, 1): ([0.5, 0.5], ["Pos(p)", "Pos(¬p)"]),
        (0, 1, 0): ([0.5, 0.5], ["Pos(p)", "Pos(¬p)"]),
        (0, 1, 1): ([0.143, 0.857], ["Bel(¬p)"]),
        (1, 0, 0): ([0.6, 0.4], ["Pos(p)", "Pos(¬p)"]),
        (1, 0, 1): ([0.5, 0.5], ["Pos(p)", "Pos(¬p)"]),
        (1, 1, 0): ([0.5, 0.5], ["Pos(p)", "Pos(¬p)"]),
        (1, 1, 1): ([0.5, 0.5], ["Pos(p)", "Pos(¬p)"]),
    }
    for (q, r, s), (holon, msgs) in expected.items():
        ref = reference({"q": q, "r": r, "s": s})
        assert ref["holon"] == holon and ref["messages"] == msgs, ((q, r, s), ref)
    print("reference.py: OK – zgodne z tabelą w pilot_README §4")


if __name__ == "__main__":
    _selftest()
