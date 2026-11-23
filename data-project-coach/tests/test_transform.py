import json
from pathlib import Path
import unittest
from school_pipeline.transform import numeric, statistics, surveys, school

ROOT = Path(__file__).resolve().parents[1]


class TransformTests(unittest.TestCase):
    def test_numeric_symbols(self):
        self.assertEqual(numeric("272,3"), 272.3)
        self.assertEqual(numeric("84%"), 84)
        for raw in [None, "~100", "cirka 50", "*", "..", "-"]:
            self.assertIsNone(numeric(raw))

    def test_statistics_preserve_flags(self):
        payload = {"status": "OK", "body": {"schoolUnit": "12345678", "docLinks": None, "m": [
            {"value": "~100", "valueType": "ROUNDED", "timePeriod": "2025/26"},
            {"value": "10,4", "valueType": "EXISTS", "timePeriod": "2024/25"}], "empty": []}}
        rows = statistics(payload, "12345678", {})
        self.assertIsNone(rows[0]["numeric_value"])
        self.assertEqual(rows[0]["raw_value"], "~100")
        self.assertEqual(rows[1]["numeric_value"], 10.4)
        self.assertEqual(rows[2]["value_type"], "EMPTY_SOURCE_ARRAY")
        with self.assertRaises(ValueError):
            statistics(payload, "00000000", {})

    def test_live_saved_survey_shapes(self):
        for kind, fixture in [("parents", "probe_parent_survey.json"), ("pupils", "probe_pupil_survey.json")]:
            data = json.loads((ROOT / "outputs" / fixture).read_text())
            rows = surveys(data, "98760751", kind, {})
            self.assertTrue(rows)
            self.assertTrue(all(r["semester"] == "VT26" for r in rows))
            self.assertTrue(any(r["value_status"] == "SOURCE_SYMBOL_UNRESOLVED" for r in rows))
            if kind == "pupils":
                self.assertEqual({r["year_group"] for r in rows}, {"ak5", "ak8"})
                self.assertTrue(all(r["answers_raw"] and r["response_rate_raw"] for r in rows))

    def test_register_minimization(self):
        data = json.loads((ROOT / "outputs/pilot_register_kristofferskolan.json").read_text())
        row = school(data, "98760751", {})
        self.assertEqual(row["municipality_code"], "0180")
        self.assertNotIn("headMaster", row)


if __name__ == "__main__":
    unittest.main()
