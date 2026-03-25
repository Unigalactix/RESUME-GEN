import unittest

from markdown_generator import create_markdown_resume


class MarkdownGeneratorTests(unittest.TestCase):
    def test_adds_biodata_divider_after_header_block(self):
        markdown = create_markdown_resume(
            profile={"first_name": "Alex", "last_name": "Chen", "headline": "Software Engineer"},
            top_skills=[],
            experience=[],
            education=[],
            projects=[],
            options={"section_order": []},
        )

        lines = markdown.splitlines()
        self.assertEqual(lines[0], "# Alex Chen")
        self.assertEqual(lines[1], "Software Engineer")
        self.assertEqual(lines[2], "---")

    def test_formats_dates_consistently_in_sections(self):
        markdown = create_markdown_resume(
            profile={"first_name": "Alex", "last_name": "Chen"},
            top_skills=[],
            experience=[
                {
                    "title": "Backend Engineer",
                    "company": "Example Corp",
                    "start": "January 2024",
                    "end": "current",
                    "location": "Seattle, WA",
                    "bullets": ["Built APIs"],
                }
            ],
            education=[
                {
                    "school": "State University",
                    "degree": "B.Tech",
                    "start": "2020",
                    "end": "May 2024",
                }
            ],
            projects=[
                {
                    "title": "Resume App",
                    "start": "2025-03-01",
                    "end": "2025-11-21",
                    "bullets": ["Shipped MVP"],
                }
            ],
            options={"section_order": ["Experience", "Projects", "Education"]},
        )

        self.assertIn("*Seattle, WA | Jan 2024 - Present*", markdown)
        self.assertIn("*Mar 2025 - Nov 2025*", markdown)
        self.assertIn("B.Tech | 2020 - May 2024", markdown)


if __name__ == "__main__":
    unittest.main()
