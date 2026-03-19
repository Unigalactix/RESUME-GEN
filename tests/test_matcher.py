import unittest

from matcher import build_target_role_brief, infer_role_target_profile, render_target_role_brief


class MatcherTests(unittest.TestCase):
    def test_infer_role_target_profile_matches_data_engineer(self):
        profile = infer_role_target_profile("Senior Data Engineer")

        self.assertIn("SQL", profile["skills"])
        self.assertIn("Airflow", profile["tools"])

    def test_render_target_role_brief_contains_sections(self):
        brief = render_target_role_brief(
            "Databricks",
            "Machine Learning Engineer",
            {
                "summary": "Compact hiring brief.",
                "responsibilities": ["build production ML systems"],
                "skills": ["Python", "MLOps"],
                "tools": ["PyTorch"],
                "domain_terms": ["model performance"],
            },
        )

        self.assertIn("Target Company: Databricks", brief)
        self.assertIn("Target Role: Machine Learning Engineer", brief)
        self.assertIn("Priority Skills: Python, MLOps", brief)

    def test_build_target_role_brief_fallback_mode(self):
        brief = build_target_role_brief("Microsoft", "Backend Engineer", prefer_ai=False)

        self.assertIn("Target Company: Microsoft", brief)
        self.assertIn("Target Role: Backend Engineer", brief)
        self.assertIn("Priority Skills:", brief)


if __name__ == "__main__":
    unittest.main()