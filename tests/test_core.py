import os, sys, tempfile, unittest
from pathlib import Path
from unittest.mock import patch
from dev_environment_checker.core import _satisfies, audit, load_policy

class Tests(unittest.TestCase):
    def test_constraints(self):
        self.assertTrue(_satisfies("3.12.2", ">=3.10,<4"))
        self.assertFalse(_satisfies("2.7", ">=3.10"))

    def test_policy_validation(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"p.json"; p.write_text('{"tools":[{"name":"Python","command":"python"}]}')
            self.assertEqual(load_policy(p)["tools"][0]["name"], "Python")

    def test_audit_real_python_and_secret_not_exposed(self):
        policy={"tools":[{"name":"Python","command":sys.executable,"version_args":["--version"],"version":">=3.10"}],"environment":["DEV_ENV_CHECK_TEST_SECRET"]}
        with patch.dict(os.environ,{"DEV_ENV_CHECK_TEST_SECRET":"super-secret"}):
            report=audit(policy)
        self.assertTrue(report["healthy"])
        self.assertNotIn("super-secret", str(report))
        self.assertFalse(report["environment"][0]["value_exposed"])

    def test_missing_tool(self):
        report=audit({"tools":[{"name":"Nope","command":"certainly-not-a-real-tool-xyz"}]})
        self.assertFalse(report["healthy"]); self.assertEqual(report["tools"][0]["status"],"missing")

if __name__ == "__main__": unittest.main()
