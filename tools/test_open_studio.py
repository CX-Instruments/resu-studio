"""Browser dispatch regression tests; never launch a real browser."""
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "skills/resu-studio/scripts"))
import open_studio as O


class OpenStudioTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.page = Path(self.tmp.name) / "Résumé & operations #1 (draft)-Studio.html"
        self.page.write_text('<html><script>const CV = {name:"Test"};</script></html>', encoding="utf-8")

    @patch.object(O.subprocess, "Popen")
    @patch.object(O.to_pdf, "find_browser", return_value="C:/Program Files/Browser/browser.exe")
    def test_single_exact_url_no_shell_and_no_relaunch_after_rebuild(self, browser, launch):
        O.open_studio(self.page)
        launch.assert_called_once_with([browser.return_value, self.page.as_uri()],
            stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        self.assertIn("%23", launch.call_args.args[0][1])
        self.assertNotIn(" ", launch.call_args.args[0][1])
        self.page.write_text(self.page.read_text(encoding="utf-8") + "\n<!-- rebuilt -->", encoding="utf-8")
        for _ in range(12):
            self.assertIn("Already attempted", O.open_studio(self.page))
        self.assertEqual(launch.call_count, 1)
        O.open_studio(self.page, again=True)
        self.assertEqual(launch.call_count, 2)

    @patch.object(O.subprocess, "Popen", side_effect=OSError("launch failed"))
    @patch.object(O.to_pdf, "find_browser", return_value="browser")
    def test_failed_launch_does_not_retry(self, browser, launch):
        with self.assertRaises(OSError):
            O.open_studio(self.page)
        self.assertIn("Already attempted", O.open_studio(self.page))
        launch.assert_called_once()

    @patch.object(O.subprocess, "Popen")
    @patch.object(O.to_pdf, "find_browser", return_value="C:/Program Files/Browser/browser.exe")
    def test_multiword_data_folder_and_job_filename_are_one_browser_argument(self, browser, launch):
        page = (Path(self.tmp.name) / "Resume" / "Resu - CV Builder" / "4 Finished documents"
                / "Senior Business Analyst - Example Organisation"
                / "Senior Business Analyst - Example Organisation - Studio.html")
        page.parent.mkdir(parents=True)
        page.write_bytes(self.page.read_bytes())
        O.open_studio(page)
        command = launch.call_args.args[0]
        self.assertEqual(len(command), 2)
        self.assertEqual(command[1], page.as_uri())
        self.assertIn("Resu%20-%20CV%20Builder/4%20Finished%20documents/", command[1])
        self.assertTrue(command[1].endswith("%20-%20Studio.html"))
        self.assertNotIn("shell", launch.call_args.kwargs)

    @patch.object(O.subprocess, "Popen")
    @patch.object(O.to_pdf, "find_browser", return_value=None)
    def test_missing_browser_template_and_missing_file_never_launch(self, browser, launch):
        self.assertIn("No browser found", O.open_studio(self.page))
        with self.assertRaises(FileNotFoundError):
            O.open_studio(self.page.with_name("missing.html"))
        self.page.write_text("const CV = {}; BUILD_STAMP", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "not a built Studio"):
            O.open_studio(self.page)
        launch.assert_not_called()


if __name__ == "__main__":
    unittest.main(verbosity=2)
