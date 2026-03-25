import unittest

from tools.resume_scorer import _build_ats_report, _classify_keyword_hits, get_resume_score


class ResumeScorerTests(unittest.TestCase):
    def test_classify_keyword_hits_separates_found_partial_and_missing(self):
        jd_text = "Python SQL distributed systems Kubernetes"
        resume_text = "Built Python APIs, strong SQL pipelines, and distributed platform services."

        hits = _classify_keyword_hits(jd_text, resume_text, max_terms=8)

        self.assertIn("Python", hits["found"])
        self.assertIn("SQL", hits["found"])
        self.assertIn("Distributed Systems", hits["partial"])
        self.assertIn("Kubernetes", hits["missing"])

    def test_build_ats_report_returns_category_scores_and_recommendations(self):
        jd_text = (
            "Senior C# .NET backend engineer with Azure OpenAI, search mode, answer cards, "
            "and 3+ years experience. Bachelor's degree required."
        )
        resume_text = (
            "Software Engineer\n"
            "Experience\n"
            "- Built Python backend services and distributed systems for internal tools.\n"
            "Education\n"
            "B.Tech in Computer Science\n"
        )

        report = _build_ats_report(resume_text, jd_text)

        self.assertIn("score", report)
        self.assertEqual(len(report["category_scores"]), 7)
        self.assertGreater(len(report["improvement_recommendations"]), 0)
        self.assertTrue(any("C#" in item or ".NET" in item for item in report["improvement_recommendations"]))
        self.assertIn("missing", report["keyword_hits"])

    def test_get_resume_score_returns_local_report_without_ai(self):
        jd_text = "Backend engineer with Python, APIs, and AWS experience."
        resume_text = "Experience\n- Built Python APIs for cloud services on AWS."

        report = get_resume_score(resume_text, jd_text)

        self.assertIsInstance(report, dict)
        self.assertIn("score", report)
        self.assertIn("keyword_hits", report)
        self.assertIn("actionable_suggestions", report)
        self.assertNotIn("error", report)


if __name__ == "__main__":
    unittest.main()