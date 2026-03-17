import os
import tempfile
import unittest

from data_loader import build_profile_completeness_report, get_data_inventory, load_all_data


class DataLoaderTests(unittest.TestCase):
    def write_file(self, directory, name, content):
        with open(os.path.join(directory, name), "w", encoding="utf-8") as handle:
            handle.write(content)

    def test_load_all_data_merges_contact_details_and_websites(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            self.write_file(
                temp_dir,
                "Profile.csv",
                "First Name,Last Name,Headline,Summary,Industry,Geo Location,Websites\n"
                'Alex,Chen,Software Engineer,Builds reliable systems,Software,"Seattle, Washington, United States","[Portfolio:alex.dev],[GitHub:github.com/alex]"\n',
            )
            self.write_file(
                temp_dir,
                "Email Addresses.csv",
                "Email Address,Confirmed,Primary,Updated On\n"
                "alex@example.com,Yes,Yes,2026-01-01\n",
            )
            self.write_file(
                temp_dir,
                "PhoneNumbers.csv",
                "Extension,Number,Type\n"
                ",+1 555 0100,Mobile\n",
            )
            self.write_file(
                temp_dir,
                "Positions.csv",
                "Company Name,Title,Description,Location,Started On,Finished On\n"
                'Example Corp,Engineer,"Built APIs and improved latency by 25%",Seattle,Jan 2024,Present\n',
            )
            self.write_file(
                temp_dir,
                "Education.csv",
                "School Name,Start Date,End Date,Notes,Degree Name,Activities\n"
                'State University,Aug 2020,May 2024,,BS Computer Science,\n',
            )
            self.write_file(
                temp_dir,
                "Skills.csv",
                "Name\nPython\nSQL\nStreamlit\n",
            )
            self.write_file(
                temp_dir,
                "Projects.csv",
                "Title,Description,Url,Started On,Finished On\n"
                'Resume Tool,"Built a resume optimizer for students",,Jan 2025,May 2025\n',
            )

            data = load_all_data(temp_dir)

            self.assertEqual(data["profile"]["email"], "alex@example.com")
            self.assertEqual(data["profile"]["phone"], "+1 555 0100")
            self.assertEqual(data["profile"]["website_links"][0]["label"], "Portfolio")
            self.assertEqual(len(data["positions"]), 1)

    def test_inventory_and_completeness_report(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            self.write_file(temp_dir, "Profile.csv", "First Name,Last Name,Headline,Summary,Industry,Geo Location,Websites\nAlex,Chen,Engineer,,Software,Seattle,\n")
            self.write_file(temp_dir, "Positions.csv", "Company Name,Title,Description,Location,Started On,Finished On\n")
            self.write_file(temp_dir, "Education.csv", "School Name,Start Date,End Date,Notes,Degree Name,Activities\n")
            self.write_file(temp_dir, "Skills.csv", "Name\nPython\n")
            self.write_file(temp_dir, "Projects.csv", "Title,Description,Url,Started On,Finished On\n")

            inventory = get_data_inventory(temp_dir)
            report = build_profile_completeness_report(load_all_data(temp_dir))

            self.assertTrue(inventory["exists"])
            self.assertEqual(inventory["missing_required"], [])
            self.assertIn("Summary", report["missing_sections"])
            self.assertIn("Projects", report["missing_sections"])


if __name__ == "__main__":
    unittest.main()