import unittest

from ai.analyzer import analyze


class FallbackAnalyzerTests(unittest.TestCase):
    def test_fallback_analyzer_extracts_basic_metadata(self) -> None:
        article = "Police in Austin, Texas are searching for a missing person after a suspicious death."

        result = analyze(article)

        self.assertEqual(result["incident_type"], "Missing Person")
        self.assertEqual(result["location"]["city"], "Austin")
        self.assertEqual(result["location"]["state"], "Texas")
        self.assertEqual(result["agency"], "Police")
        self.assertGreaterEqual(result["confidence"], 0.3)


if __name__ == "__main__":
    unittest.main()
