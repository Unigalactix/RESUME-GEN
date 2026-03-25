import unittest
from unittest.mock import patch

from tools.resume_generator import generate_and_store_resume, get_resume_section_choices, save_generated_resume_state


class ResumeGeneratorHelperTests(unittest.TestCase):
    def test_get_resume_section_choices_excludes_header(self):
        sections = get_resume_section_choices()

        self.assertNotIn("Header", sections)
        self.assertIn("Summary", sections)
        self.assertIn("Experience", sections)

    def test_save_generated_resume_state_populates_prefixed_keys(self):
        fake_state = {}
        package = {
            "resume_md": "# Resume\n",
            "ai_suggestions": ["Add Python APIs"],
            "selected_experience_count": 2,
            "selected_projects_count": 1,
            "selected_certifications_count": 1,
            "selection_details": {"experience": [], "projects": []},
        }

        with patch("tools.resume_generator.st.session_state", fake_state):
            save_generated_resume_state(
                prefix="scorer_followup",
                package=package,
                variant_name="Software Engineer (ATS-Hybrid)",
                target_brief="Gap brief",
                company_name="Example Corp",
                role_name="Backend Engineer",
            )

        self.assertEqual(fake_state["scorer_followup_resume_md"], "# Resume\n")
        self.assertEqual(fake_state["scorer_followup_resume_editor"], "# Resume\n")
        self.assertEqual(fake_state["scorer_followup_resume_target_role"], "Backend Engineer")
        self.assertEqual(fake_state["scorer_followup_resume_selection_summary"], (2, 1, 1))

    def test_generate_and_store_resume_adds_score_report(self):
        fake_state = {}
        fake_package = {
            "resume_md": "# Resume\n",
            "ai_suggestions": [],
            "selected_experience_count": 1,
            "selected_projects_count": 1,
            "selected_certifications_count": 0,
            "selection_details": {},
        }

        with patch("tools.resume_generator.st.session_state", fake_state), \
            patch("tools.resume_generator.build_tailored_resume_from_jd", return_value=fake_package), \
            patch("tools.resume_generator.get_resume_score", return_value={"score": 91, "category_scores": [], "keyword_hits": {}}):
            generate_and_store_resume(
                prefix="resume",
                jd_text="Backend engineer JD",
                data={},
                variant_name="Software Engineer (ATS-Hybrid)",
                selected_sections=["Summary", "Experience"],
            )

        self.assertEqual(fake_state["resume_resume_score_report"]["score"], 91)


if __name__ == "__main__":
    unittest.main()