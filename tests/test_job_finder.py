import csv
import os
import tempfile
import unittest
from unittest.mock import patch

from tools.job_finder import collect_linkedin_jobs, collect_live_jobs


class JobFinderTests(unittest.TestCase):
    def test_collect_live_jobs_aggregates_and_enriches_results(self):
        suggestions = [
            {
                "company": "Databricks",
                "reason": "Strong fit for backend and AI infrastructure roles.",
                "sponsorship_signal": "Known sponsor",
                "visa_fit": "Often practical for OPT and H-1B candidates.",
            },
            {
                "company": "NVIDIA",
                "reason": "Good fit for systems and AI engineering.",
                "sponsorship_signal": "Known sponsor",
                "visa_fit": "Historically active in sponsorship.",
            },
        ]
        filters = {
            "role": "Backend Engineer",
            "location": "Remote",
            "strict_location": True,
            "experience_level": "Entry Level",
            "job_modes": ["Remote"],
            "industries": [],
            "company_stages": [],
            "work_auth_focus": "General search",
            "sponsor_only": False,
        }

        fake_jobs = {
            "Databricks": [
                {
                    "title": "Backend Engineer",
                    "location": "Remote",
                    "url": "https://example.com/db-backend",
                    "description": "Build backend systems.",
                    "source": "Greenhouse",
                }
            ],
            "NVIDIA": [
                {
                    "title": "Platform Engineer",
                    "location": "Remote",
                    "url": "https://example.com/nv-platform",
                    "description": "Build platform services.",
                    "source": "Lever",
                }
            ],
        }

        with patch("tools.job_finder.fetch_live_jobs_for_company", side_effect=lambda company, role, location: fake_jobs.get(company, [])):
            jobs = collect_live_jobs(suggestions, filters, max_jobs_per_company=2, max_total_jobs=10)

        self.assertEqual(len(jobs), 2)
        self.assertEqual(jobs[0]["company"], "Databricks")
        self.assertEqual(jobs[0]["title"], "Backend Engineer")
        self.assertIn("search_link", jobs[0])
        self.assertIn("ats_links", jobs[0])
        self.assertEqual(jobs[1]["source"], "Lever")

    def test_collect_live_jobs_deduplicates_and_respects_total_limit(self):
        suggestions = [
            {"company": "Databricks"},
            {"company": "Databricks"},
            {"company": "NVIDIA"},
        ]
        filters = {
            "role": "Software Engineer",
            "location": "Remote",
            "strict_location": True,
            "experience_level": "Any",
            "job_modes": [],
            "industries": [],
            "company_stages": [],
            "work_auth_focus": "General search",
            "sponsor_only": False,
        }

        def fake_fetch(company, role, location):
            return [
                {
                    "title": "Software Engineer",
                    "location": "Remote",
                    "url": f"https://example.com/{company.lower()}-role",
                    "description": "Role description",
                    "source": "Greenhouse",
                }
            ]

        with patch("tools.job_finder.fetch_live_jobs_for_company", side_effect=fake_fetch):
            jobs = collect_live_jobs(suggestions, filters, max_jobs_per_company=2, max_total_jobs=1)

        self.assertEqual(len(jobs), 1)
        self.assertEqual(jobs[0]["company"], "Databricks")

    def test_collect_linkedin_jobs_reads_saved_and_applied_jobs(self):
        filters = {
            "role": "Software Engineer",
            "location": "Remote",
            "strict_location": True,
            "experience_level": "Any",
            "job_modes": [],
            "industries": [],
            "company_stages": [],
            "work_auth_focus": "General search",
            "sponsor_only": False,
        }
        suggestions = [{"company": "Meta", "reason": "Strong fit.", "sponsorship_signal": "Known sponsor", "visa_fit": "Practical."}]

        with tempfile.TemporaryDirectory() as temp_dir:
            saved_path = os.path.join(temp_dir, "Saved Jobs.csv")
            with open(saved_path, "w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(handle, fieldnames=["Saved Date", "Job Url", "Job Title", "Company Name"])
                writer.writeheader()
                writer.writerow({"Saved Date": "1/1/26, 10:00 AM", "Job Url": "https://linkedin.com/jobs/view/1", "Job Title": "Software Engineer", "Company Name": "Meta"})

            applied_path = os.path.join(temp_dir, "Job Applications.csv")
            with open(applied_path, "w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(handle, fieldnames=["Application Date", "Company Name", "Job Title", "Job Url"])
                writer.writeheader()
                writer.writerow({"Application Date": "1/2/26, 10:00 AM", "Company Name": "Snowflake", "Job Title": "Software Engineer", "Job Url": "https://linkedin.com/jobs/view/2"})

            jobs = collect_linkedin_jobs(filters, suggestions, data_dir=temp_dir, max_total_jobs=10)

        self.assertEqual(len(jobs), 2)
        self.assertEqual(jobs[0]["source"], "LinkedIn Saved")
        self.assertEqual(jobs[1]["source"], "LinkedIn Applied")
        self.assertIn("search_link", jobs[0])


if __name__ == "__main__":
    unittest.main()