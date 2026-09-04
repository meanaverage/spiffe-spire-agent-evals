from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from runner.core import build_user_prompt, prepare_request, select_prompt_visible
from scoring.aggregate import aggregate
from scoring.validate import CORPUS_ROOT, RESULT_ROOT, ROOT, validate


class PublicationTests(unittest.TestCase):
    def test_full_publication_validation(self) -> None:
        result = validate()
        self.assertEqual(result["status"], "passed", result["errors"])
        self.assertEqual(result["case_count"], 23)
        self.assertEqual(result["matched_pair_count"], 6)
        self.assertEqual(result["provenance_case_count"], 23)

    def test_sanitized_grades_reconstruct_scores(self) -> None:
        actual = aggregate(RESULT_ROOT / "grades.numeric.json", CORPUS_ROOT)
        expected = json.loads((RESULT_ROOT / "scores.json").read_text(encoding="utf-8"))
        sort_key = lambda item: (item["corpus"], item["provider"], item["condition"])
        self.assertEqual(
            sorted(actual["condition_aggregates"], key=sort_key),
            sorted(expected["condition_aggregates"], key=sort_key),
        )
        self.assertEqual(actual["inter_rater"], expected["inter_rater"])

    def test_runner_selects_prompt_visible_only(self) -> None:
        corpus = CORPUS_ROOT / "contrastive.json"
        selected = select_prompt_visible(corpus, "holdout-toctou-serialized-reread")
        self.assertEqual(set(selected), {"case_id", "fixture_sha256", "prompt"})
        self.assertNotIn("expected", selected)
        self.assertNotIn("must_not", selected)
        self.assertNotIn("finding_threshold", selected)

    def test_prepared_request_does_not_contain_ground_truth(self) -> None:
        corpus = CORPUS_ROOT / "contrastive.json"
        prompts = json.loads((ROOT / "prompts" / "prompts.json").read_text(encoding="utf-8"))
        request = prepare_request(
            corpus_path=corpus,
            case_id="holdout-toctou-serialized-reread",
            condition_id="NO_SKILL",
            packet_path=None,
            model_config={"model_identifier": "test"},
            system_prompt=prompts["target_system_prompt"]["text"],
            sample_id="test-sample",
        )
        corpus_data = json.loads(corpus.read_text(encoding="utf-8"))
        truth = corpus_data["scenarios"][0]["ground_truth"]
        self.assertNotIn(truth["expected"][0], request.user_prompt)
        self.assertIn("(No additional security-review reference packet supplied.)", request.user_prompt)

    def test_packet_is_intentional_input(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            packet = Path(directory) / "packet.md"
            packet.write_text("PUBLIC PACKET", encoding="utf-8")
            text = build_user_prompt("SCENARIO", packet.read_text(encoding="utf-8"))
        self.assertIn("SCENARIO", text)
        self.assertIn("PUBLIC PACKET", text)
        self.assertNotIn("ground_truth", text)


if __name__ == "__main__":
    unittest.main()
