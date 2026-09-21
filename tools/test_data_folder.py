"""Workspace isolation, explicit location overrides and authorised imports.

Every fixture is synthetic. No real user folder is read or changed.
"""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

SKILL = Path(__file__).resolve().parents[1] / "skills/resu-studio"
sys.path.insert(0, str(SKILL / "scripts"))
import paths as P


class WorkspaceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="resu-workspace-")
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.a = self.root / "Workspace A"; self.a.mkdir()
        self.b = self.root / "Workspace B"; self.b.mkdir()
        self.external = self.root / "Earlier work"; self.external.mkdir()
        (self.external / "facts.md").write_text("Old private evidence", encoding="utf-8")
        self.home = self.root / "Home"; self.home.mkdir()
        old_config = self.home / ".resu-studio"; old_config.mkdir()
        (old_config / "locations.json").write_text(json.dumps({"~":{"folder":str(self.external)}}), encoding="utf-8")
        (old_config / "location").write_text(str(self.external), encoding="utf-8")
        self.env = dict(os.environ, RESU_WORKSPACE=str(self.a),
                        HOME=str(self.home), USERPROFILE=str(self.home),
                        RESU_STUDIO_CONFIG=str(old_config), CLAUDE_PLUGIN_DATA=str(self.external),
                        PLUGIN_DATA=str(self.external))
        self.scope = patch.dict(os.environ, self.env, clear=True); self.scope.start()
        self.addCleanup(self.scope.stop)
        self.default = self.a / P.TOP

    def run_cli(self, *args, workspace=None, cwd=None):
        env = dict(self.env)
        if workspace is not None: env["RESU_WORKSPACE"] = str(workspace)
        return subprocess.run([sys.executable, str(SKILL / "scripts/paths.py"), *map(str,args)],
                              cwd=cwd or SKILL, env=env, capture_output=True, text=True, encoding="utf-8")

    def test_status_is_read_only_and_never_discovers_or_uses_legacy_data(self):
        with patch.object(P, "work_in", side_effect=AssertionError("must not scan old work")):
            state = P.status()
        self.assertEqual(Path(state["folder"]), self.default)
        self.assertEqual(state["how"], "workspace")
        self.assertEqual(state["existing_work"], [])
        self.assertEqual(state["suggested"], {"project":str(self.default)})
        self.assertFalse(self.default.exists())
        self.assertEqual((self.external / "facts.md").read_text(), "Old private evidence")

    def test_default_initialises_only_the_standard_folder_and_layout(self):
        result = self.run_cli("--facts")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(Path(result.stdout.strip()), self.default / P.RECORD / "facts.md")
        self.assertEqual({p.name for p in self.a.iterdir()}, {P.TOP})
        for name in (P.ABOUT,P.RECORD,P.JOBS,P.DOCUMENTS,P.SYSTEM):
            self.assertTrue((self.default / name).is_dir())
        self.assertFalse((self.default / P.RECORD / "facts.md").exists())
        self.assertIn("*", (self.default / ".gitignore").read_text())
        subprocess.run(["git","init","-q",str(self.a)],check=True,capture_output=True)
        ignored=subprocess.run(["git","check-ignore",str(self.default / "README.txt")],cwd=self.a,capture_output=True)
        self.assertEqual(ignored.returncode,0)

    def test_global_plugin_is_scoped_to_each_current_workspace_in_one_process(self):
        self.assertEqual(Path(P.data_dir()), self.default)
        os.environ["RESU_WORKSPACE"] = str(self.b)
        self.assertEqual(Path(P.data_dir()), self.b / P.TOP)
        self.assertFalse((self.b / P.TOP / P.RECORD / "facts.md").exists())

    def test_cwd_is_default_and_plugin_directory_is_not_a_workspace(self):
        env = dict(self.env); env.pop("RESU_WORKSPACE")
        for cwd, expected in ((self.b,0),(SKILL,P.NOT_CHOSEN)):
            result=subprocess.run([sys.executable,str(SKILL / "scripts/paths.py"),"--facts"],
                                  cwd=cwd,env=env,capture_output=True,text=True)
            self.assertEqual(result.returncode,expected,result.stderr)
            if not expected:self.assertEqual(Path(result.stdout.strip()),self.b / P.TOP / P.RECORD / "facts.md")
        invalid=self.run_cli("--status","--json",workspace="relative-path")
        self.assertNotIn("Traceback",invalid.stderr)
        self.assertFalse(json.loads(invalid.stdout)["chosen"])

    def test_install_pointer_cannot_override_workspace(self):
        pointer=self.root / "data-location.txt";pointer.write_text(str(self.external))
        with patch.object(P,"_POINTER",str(pointer)):
            self.assertEqual(Path(P.data_dir()),self.default)

    def test_external_location_and_import_need_explicit_instruction(self):
        for args in (("--choose",str(self.external)),("--choose","home"),
                     ("--choose","project","--bring",str(self.external))):
            result=self.run_cli(*args)
            self.assertEqual(result.returncode,5,result.stdout)
            self.assertIn("explicit request",result.stderr)
        self.assertFalse(self.default.exists())

    def test_explicit_override_stays_in_its_workspace_and_can_reset(self):
        result=self.run_cli("--choose",self.external,"--user-instruction","Use the named external folder for this workspace.")
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertEqual(Path(P.data_dir()),self.external)
        other=self.run_cli("--facts",workspace=self.b)
        self.assertEqual(Path(other.stdout.strip()),self.b / P.TOP / P.RECORD / "facts.md")
        record=json.loads(Path(P.locations_file()).read_text())
        self.assertEqual(record["workspace"],str(self.a))
        result=self.run_cli("--choose","project")
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertEqual(Path(P.data_dir()),self.default)
        self.assertTrue((self.external / "facts.md").exists())

    def test_import_only_reads_the_named_folder_and_preserves_existing_files(self):
        self.run_cli("--choose","project")
        facts=self.default / P.RECORD / "facts.md";facts.write_text("Current authorised evidence")
        (self.external / "answers.md").write_text("Earlier answers")
        result=self.run_cli("--choose","project","--bring",self.external,
                            "--user-instruction","Import my records from the named folder.")
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertEqual(facts.read_text(),"Current authorised evidence")
        self.assertEqual((self.default / P.RECORD / "answers.md").read_text(),"Earlier answers")
        self.assertEqual((self.external / "facts.md").read_text(),"Old private evidence")

    def test_invalid_local_record_never_falls_back_to_host_or_another_folder(self):
        self.run_cli("--choose","project")
        record=Path(P.locations_file());record.write_text('{"folder":"elsewhere"}')
        result=self.run_cli("--facts")
        self.assertEqual(result.returncode,P.NOT_CHOSEN)
        self.assertIn("explicit user instruction",result.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)
