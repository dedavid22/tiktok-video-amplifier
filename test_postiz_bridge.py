"""Postiz bridge tests: no live posts or credentials required."""
from __future__ import annotations
import tempfile
import unittest
from pathlib import Path
from unittest import mock
import postiz_bridge as p
import amplify

class PostizTests(unittest.TestCase):
 def test_no_api_key_is_blocked(self):
  with mock.patch.dict("os.environ",{"POSTIZ_API_KEY":""}):
   with self.assertRaisesRegex(RuntimeError,"BLOCKED_NO_POSTIZ_API_KEY"):
    p.auth()
 def test_unapproved_destination_cannot_publish(self):
  with mock.patch.object(p,"ALLOW",set()):
   with mock.patch.object(p,"call") as call:
    report=p.publish("random-personal-channel",execute=True)
    self.assertEqual(report["state"],"BLOCKED_UNAPPROVED_PERSONAL_CHANNEL")
    call.assert_not_called()
 def test_dry_run_does_not_post(self):
  with mock.patch.object(p,"ALLOW",{"verified-id"}):
   with mock.patch.object(p,"channels",return_value=[{
     "id":"verified-id","network":"bluesky","disabled":False
   }]):
    with mock.patch.object(p,"call") as call:
     report=p.publish("verified-id",execute=False)
     self.assertEqual(report["state"],"PASS_DRY_RUN_ONLY")
     self.assertIs(report["published"],False)
     call.assert_not_called()
 def test_submit_receipt_never_claims_publication(self):
  with tempfile.TemporaryDirectory() as tmp:
   with mock.patch.object(p,"RECEIPTS",Path(tmp)/"receipts.json"):
    with mock.patch.object(p,"ALLOW",{"verified-id"}):
     with mock.patch.object(p,"channels",return_value=[{
       "id":"verified-id","network":"bluesky","disabled":False
     }]):
      with mock.patch.object(p,"call",return_value={"id":"provider-accepted"}):
       result=p.publish("verified-id",execute=True)
       self.assertEqual(result["state"],"SUBMITTED_UNVERIFIED")
       self.assertIs(result["published_verified"],False)
       self.assertIsNone(result["permalink"])
       duplicate=p.publish("verified-id",execute=True)
       self.assertEqual(duplicate["state"],"BLOCKED_DUPLICATE_UNRESOLVED_SUBMISSION")

if __name__=="__main__":unittest.main(verbosity=2)
