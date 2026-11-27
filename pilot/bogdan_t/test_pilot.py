import json
import unittest
from fractions import Fraction
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from unittest.mock import patch

from reference import evaluate, modality, read_kb
from run import FOLDER, main, prepare_tests, run_api


class ReferenceTest(unittest.TestCase):
    def test_reference_table(self):
        history = read_kb(FOLDER / "kb.csv")
        expected = {
            (None, None, None): (4, 8, "5/14", "9/14", ["Pos(p)", "Pos(¬p)"]),
            (0, 0, 0): (0, 0, "1/2", "1/2", ["Pos(p)", "Pos(¬p)"]),
            (0, 0, 1): (2, 2, "1/2", "1/2", ["Pos(p)", "Pos(¬p)"]),
            (0, 1, 0): (0, 0, "1/2", "1/2", ["Pos(p)", "Pos(¬p)"]),
            (0, 1, 1): (0, 5, "1/7", "6/7", ["Bel(¬p)"]),
            (1, 0, 0): (2, 1, "3/5", "2/5", ["Pos(p)", "Pos(¬p)"]),
            (1, 0, 1): (0, 0, "1/2", "1/2", ["Pos(p)", "Pos(¬p)"]),
            (1, 1, 0): (0, 0, "1/2", "1/2", ["Pos(p)", "Pos(¬p)"]),
            (1, 1, 1): (0, 0, "1/2", "1/2", ["Pos(p)", "Pos(¬p)"]),
        }
        for values, (n1, n0, strength1, strength0, messages) in expected.items():
            with self.subTest(context=values):
                result = evaluate(history, dict(zip(("q", "r", "s"), values)))
                self.assertEqual(result["reference_counts"]["p"], {"true": n1, "false": n0})
                self.assertEqual(
                    result["reference_holon"]["p"], {"true": strength1, "false": strength0}
                )
                self.assertEqual(result["reference_messages"], messages)

    def test_thresholds_include_the_lower_bound(self):
        for decimal, expected in [
            ("0.199", None),
            ("0.2", "Pos"),
            ("0.649", "Pos"),
            ("0.65", "Bel"),
            ("0.899", "Bel"),
            ("0.9", "Know"),
        ]:
            with self.subTest(strength=decimal):
                self.assertEqual(modality(Fraction(decimal)), expected)


class ApiTest(unittest.TestCase):
    def test_cli_saves_exact_replies_and_sends_one_message_per_repeat(self):
        raw = "  Przypuszczam, że p wystąpi.\n\x60\x60\x60\n"
        completion = SimpleNamespace(
            model="model-snapshot",
            choices=[SimpleNamespace(message=SimpleNamespace(content=raw), finish_reason="stop")],
        )
        with TemporaryDirectory(dir=FOLDER) as directory:
            folder = Path(directory)
            for filename in ("kb.csv", "contexts.yaml", "prompt_template.txt"):
                (folder / filename).write_bytes((FOLDER / filename).read_bytes())
            cli = [
                "run.py",
                "--model",
                "openai/example",
                "--test",
                "T2",
                "--repeats",
                "2",
                "--temperature",
                "0.4",
            ]
            with (
                patch("run.FOLDER", folder),
                patch("sys.argv", cli),
                patch("litellm.completion", return_value=completion) as call,
                patch("builtins.print"),
            ):
                main()

            self.assertEqual(call.call_count, 2)
            (file,) = (folder / "results").glob("*/*.jsonl")
            records = [json.loads(line) for line in file.read_text(encoding="utf-8").splitlines()]
            self.assertEqual(len(records), 2)
            for index, (record, request) in enumerate(zip(records, call.call_args_list), 1):
                self.assertEqual(
                    request.kwargs["messages"], [{"role": "user", "content": record["prompt"]}]
                )
                self.assertEqual(request.kwargs["temperature"], 0.4)
                self.assertIn("p=?, q=0, r=1, s=1", record["prompt"])
                self.assertEqual(record["test_id"], "T2")
                self.assertEqual(record["model_version"], "model-snapshot")
                self.assertEqual(record["response"], raw)
                self.assertEqual(record["reference_messages"], ["Bel(¬p)"])
                self.assertEqual(record["repeat"], index)
            (report,) = (folder / "report").glob("*.md")
            self.assertIn(raw, report.read_text(encoding="utf-8"))
            self.assertFalse(list((folder / "results").glob("*/.run.lock")))
            with report.open("a", encoding="utf-8") as output:
                output.write("\nOcena autora.\n")
            with patch("litellm.completion", return_value=completion), patch("builtins.print"):
                run_api(folder, "openai/example", None, 1, prepare_tests(FOLDER, ["T3"]))
            self.assertEqual(len(file.read_text(encoding="utf-8").splitlines()), 3)
            self.assertIn("Ocena autora.", report.read_text(encoding="utf-8"))

    def test_provider_error_preserves_previous_result_and_report(self):
        completion = SimpleNamespace(
            model="model-snapshot",
            choices=[
                SimpleNamespace(
                    message=SimpleNamespace(content="Odpowiedź pierwsza."), finish_reason="stop"
                )
            ],
        )
        with TemporaryDirectory(dir=FOLDER) as directory:
            folder = Path(directory)
            tests = prepare_tests(FOLDER, ["T5"])
            with (
                patch("litellm.completion", side_effect=[completion, TimeoutError]),
                self.assertRaisesRegex(RuntimeError, "T5, powtórzenie 2: TimeoutError"),
            ):
                run_api(folder, "openai/example", None, 2, tests)

            (file,) = (folder / "results").glob("*/*.jsonl")
            record = json.loads(file.read_text(encoding="utf-8"))
            self.assertIsNone(record["temperature"])
            self.assertEqual(record["context"], {"p": None, "q": 1, "r": 1, "s": 1})
            self.assertEqual(record["reference_counts"]["p"], {"true": 0, "false": 0})
            (report,) = (folder / "report").glob("*.md")
            self.assertIn("Odpowiedź pierwsza.", report.read_text(encoding="utf-8"))
            self.assertFalse(list((folder / "results").glob("*/.run.lock")))
