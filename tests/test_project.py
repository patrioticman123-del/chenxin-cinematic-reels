import unittest
import json
from pathlib import Path
from importlib.util import spec_from_file_location, module_from_spec

ROOT = Path(__file__).resolve().parents[1]
spec = spec_from_file_location("reels", ROOT / "tools" / "reels.py")
m = module_from_spec(spec)
spec.loader.exec_module(m)

class ProjectTests(unittest.TestCase):
    def setUp(self):
        self.data=json.loads((ROOT/"templates"/"project.blank.json").read_text(encoding="utf-8"))
    def test_runtime(self):
        self.assertEqual(sum(x["duration"] for x in self.data["scenes"]),30)
    def test_flow_clip_lengths(self):
        self.assertEqual([s["flow_generation_seconds"] for s in self.data["scenes"]],[8,8,8,8])
        self.assertEqual([s["duration"] for s in self.data["scenes"]],[8,8,8,6])
    def test_brand(self):
        self.assertEqual(self.data["brand"],"宸新復健科")
    def test_validation_warns_missing_media(self):
        errors,_=m.validate(self.data,ROOT)
        self.assertTrue(any("media" in x for x in errors))
if __name__=="__main__":
    unittest.main()
