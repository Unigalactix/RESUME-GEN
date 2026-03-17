import unittest

from ai_helper import parse_json_response, strip_code_fences


class AIHelperTests(unittest.TestCase):
    def test_strip_code_fences_handles_json_block(self):
        raw = "```json\n{\"score\": 91}\n```"
        self.assertEqual(strip_code_fences(raw), '{"score": 91}')

    def test_parse_json_response_handles_wrapped_object(self):
        raw = "Model output:\n{\"strengths\": [\"Python\"]}\nThank you"
        self.assertEqual(parse_json_response(raw), {"strengths": ["Python"]})

    def test_parse_json_response_handles_array(self):
        raw = "```json\n[\"Python\", \"SQL\"]\n```"
        self.assertEqual(parse_json_response(raw), ["Python", "SQL"])


if __name__ == "__main__":
    unittest.main()