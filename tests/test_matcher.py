import unittest

from matcher import (
    build_target_role_brief,
    build_targeting_context,
    get_matched_keywords,
    infer_role_target_profile,
    is_locally_relevant,
    render_target_role_brief,
    select_top_relevant_items,
)


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

    def test_select_top_relevant_items_prefers_keyword_overlap(self):
        targeting_context = build_targeting_context(
            "Need a backend engineer with Python, APIs, cloud infrastructure, and distributed systems experience",
            company_name="Amazon",
            role_name="Backend Engineer",
        )
        items = [
            {"title": "Campus Ambassador", "description": "Ran marketing events and campus outreach"},
            {"title": "Platform Engineer", "description": "Built Python APIs and improved cloud infrastructure reliability"},
            {"title": "Backend Developer", "description": "Developed distributed systems and production services with Python"},
            {"title": "Tutor", "description": "Mentored students in calculus and physics"},
        ]

        selected = select_top_relevant_items(
            items,
            targeting_context,
            text_builder=lambda item: f"{item['title']} {item['description']}",
            max_items=3,
            min_score=1,
        )

        selected_titles = [item["title"] for item in selected]

        self.assertIn("Backend Developer", selected_titles)
        self.assertIn("Platform Engineer", selected_titles)
        self.assertNotIn("Campus Ambassador", selected_titles)
        self.assertEqual(len(selected), 2)

    def test_get_matched_keywords_returns_overlap(self):
        context = build_targeting_context(
            "Python APIs distributed systems cloud infrastructure",
            role_name="Backend Engineer",
        )
        kws = get_matched_keywords("Developed Python APIs and distributed services", context)

        self.assertIn("python", kws)
        self.assertIn("apis", kws)
        # irrelevant word absent from context keywords is not returned
        self.assertNotIn("developed", kws)

    def test_get_matched_keywords_empty_text(self):
        context = build_targeting_context("Python ML inference deployment")
        self.assertEqual(get_matched_keywords("", context), [])

    def test_is_locally_relevant_above_threshold(self):
        context = build_targeting_context("Python APIs cloud infrastructure distributed systems")
        self.assertTrue(
            is_locally_relevant("Built Python APIs and improved cloud infrastructure", context, min_score=3)
        )

    def test_is_locally_relevant_below_threshold(self):
        context = build_targeting_context("Python APIs cloud infrastructure distributed systems")
        self.assertFalse(
            is_locally_relevant("Mentored students in calculus", context, min_score=3)
        )


if __name__ == "__main__":
    unittest.main()