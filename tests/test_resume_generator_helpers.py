import unittest
from unittest.mock import patch

from tools.resume_generator import get_resume_section_choices, save_generated_resume_state


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


if __name__ == "__main__":
    unittest.main()