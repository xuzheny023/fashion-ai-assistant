"""Offline tests for prompt formatting, response parsing and DashScope key handling.

These tests do not call external APIs or require real credentials.
"""
import json
import os
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from PIL import Image

from src import fabric_api_infer as infer


class InferenceHelpersTest(unittest.TestCase):
    def test_parse_direct_json(self):
        self.assertEqual(infer.try_parse_json('{"task": "fabric"}'), {"task": "fabric"})

    def test_parse_fenced_json(self):
        self.assertEqual(
            infer.try_parse_json('```json\n{"task":"print"}\n```'),
            {"task": "print"},
        )

    def test_parse_embedded_json(self):
        self.assertEqual(
            infer.try_parse_json('Result: {"task":"construction"} done'),
            {"task": "construction"},
        )

    def test_parse_invalid_response(self):
        self.assertEqual(infer.try_parse_json("not valid JSON"), {})

    def test_prompts_include_context_and_language(self):
        en = infer.make_prompt("print", "en", "low", "activewear", "wash")
        zh = infer.make_prompt("fabric", "zh", "high", "casual", "eco")
        self.assertIn("activewear", en)
        self.assertIn("wash", en)
        self.assertIn("print", en)
        self.assertIn("casual", zh)
        self.assertIn("eco", zh)
        self.assertIn("面料", zh)

    def test_upscale_small_image(self):
        image = Image.new("RGB", (320, 480), color="white")
        resized = infer.ensure_min_size(image, 640)
        self.assertEqual(resized.size, (640, 960))

    def test_explicit_key_and_structured_response_without_network(self):
        received = {}
        sdk = SimpleNamespace(api_key=None)
        response = {
            "task": "fabric",
            "summary": "Illustrative offline result",
            "details": {"fabric": {"material": "cotton"}},
            "recommendations": {},
            "dfm_risks": [],
            "next_actions": [],
        }

        class FakeConversation:
            @staticmethod
            def call(**kwargs):
                received.update(kwargs)
                return SimpleNamespace(output={
                    "choices": [{"message": {"content": json.dumps(response)}}]
                })

        with patch.dict(os.environ, {"DASHSCOPE_API_KEY": ""}), \
             patch.object(infer, "dashscope", sdk), \
             patch.object(infer, "MultiModalConversation", FakeConversation):
            result = infer.cloud_infer(
                pil_image=Image.new("RGB", (640, 640), color="white"),
                engine="qwen-vl",
                task_type="fabric",
                lang="en",
                api_key="test-key-not-a-real-credential",
            )

        self.assertIsNone(sdk.api_key)
        self.assertEqual(received["api_key"], "test-key-not-a-real-credential")
        self.assertEqual(received["model"], "qwen-vl-max")
        self.assertEqual(result["task"], "fabric")
        self.assertEqual(result["details"]["fabric"]["material"], "cotton")
        self.assertEqual(result["_meta"]["engine"], "cloud")


if __name__ == "__main__":
    unittest.main()
