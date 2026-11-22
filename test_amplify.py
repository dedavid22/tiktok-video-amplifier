"""Pruebas deterministas: no usan TikTok real, no publican nada."""
from __future__ import annotations
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock
import amplify

VIDEO=amplify.VIDEO
class AmplifierTests(unittest.TestCase):
 def test_selected_video_canonical(self):
  u,vid=amplify.safe_video(VIDEO+"?utm_source=x")
  self.assertEqual(u,VIDEO)
  self.assertEqual(vid,"7710983123021974816")
 def test_reject_other_creator(self):
  for bad in [
   "https://www.tiktok.com/@someoneelse/video/7710983123021974816",
   "https://www.tiktok.com.evil.test/@dedavid22/video/7710983123021974816",
   "http://www.tiktok.com/@dedavid22/video/7710983123021974816",
   "javascript:alert(1)",
   "https://www.tiktok.com/@dedavid22/video/abc",
   "https://www.tiktok.com/@dedavid22/video/7710983123021974816/evil"
  ]:
   with self.subTest(bad=bad), self.assertRaises(ValueError):amplify.safe_video(bad)
 def test_share_targets_are_real_composers(self):
  d=amplify.share_targets(VIDEO)
  self.assertEqual(set(d),set(amplify.ALLOWED_CHANNELS))
  for key,v in d.items():
   self.assertTrue(v.startswith(("https://","mailto:")))
   self.assertIn("7710983123021974816",v)
 def test_generate_does_not_claim_traffic_or_posts(self):
  with tempfile.TemporaryDirectory() as tmp:
   with mock.patch.multiple(amplify,ROOT=Path(tmp),PAGE=Path(tmp)/"site",DATA=Path(tmp)/"campaign.json",
     MATRIX=Path(tmp)/"distribution.json",REPORT=Path(tmp)/"report.json"):
    report=amplify.generate()
    self.assertEqual(report["status"],"READY_NOT_DISTRIBUTED")
    self.assertEqual(report["social_published_verified"],0)
    self.assertIsNone(report["real_visitors"])
    html=(Path(tmp)/"site"/"index.html").read_text(encoding="utf-8")
    self.assertIn(VIDEO,html)
    self.assertIn("Compartir el vídeo",html)
    channels=json.loads((Path(tmp)/"distribution.json").read_text(encoding="utf-8"))["channels"]
    self.assertTrue(all(v["state"]=="READY_COMPOSER_ONLY" and v["permalink_verified"] is None for v in channels.values()))
 def test_repeat_does_not_invent_publishing(self):
  with tempfile.TemporaryDirectory() as tmp:
   with mock.patch.multiple(amplify,ROOT=Path(tmp),PAGE=Path(tmp)/"site",DATA=Path(tmp)/"campaign.json",
     MATRIX=Path(tmp)/"distribution.json",REPORT=Path(tmp)/"report.json"):
    amplify.generate()
    first=json.loads((Path(tmp)/"campaign.json").read_text())["created_at_utc"]
    amplify.generate()
    second=json.loads((Path(tmp)/"campaign.json").read_text())["created_at_utc"]
    self.assertEqual(first,second)
 def test_html_no_external_embedded_tracker(self):
  with tempfile.TemporaryDirectory() as tmp:
   with mock.patch.multiple(amplify,ROOT=Path(tmp),PAGE=Path(tmp)/"site",DATA=Path(tmp)/"campaign.json",
     MATRIX=Path(tmp)/"distribution.json",REPORT=Path(tmp)/"report.json"):
    amplify.generate()
    text=(Path(tmp)/"site"/"index.html").read_text(encoding="utf-8")
    self.assertNotIn("countapi",text)
    self.assertNotIn("gtag(",text)
    self.assertNotIn("fetch(",text)
 def test_external_status_not_automatically_pass(self):
  with tempfile.TemporaryDirectory() as tmp:
   with mock.patch.multiple(amplify,ROOT=Path(tmp),PAGE=Path(tmp)/"site",DATA=Path(tmp)/"campaign.json",
     MATRIX=Path(tmp)/"distribution.json",REPORT=Path(tmp)/"report.json"):
    amplify.generate()
    report=json.loads((Path(tmp)/"report.json").read_text(encoding="utf-8"))
    self.assertTrue(report["landing_public"].startswith("BLOCKED"))
    self.assertIsNone(report["followers_from_campaign"])

if __name__=="__main__":unittest.main(verbosity=2)
