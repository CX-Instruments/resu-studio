"""Verify actual PDF text order for the default renderer and Studio print surface.

Uses only fictional repository fixtures in an isolated temporary data folder.
Playwright and pypdf are test dependencies, not plugin runtime dependencies.
"""
from pathlib import Path
import os
import re
import subprocess
import sys
import tempfile
import unicodedata
import unittest

from pypdf import PdfReader
from playwright.sync_api import sync_playwright

REPO = Path(__file__).resolve().parents[1]
SKILL = REPO / "skills/resu-studio"
sys.path.insert(0, str(SKILL / "scripts"))
import to_pdf


def words(text):
    return re.findall(r"\w+", unicodedata.normalize("NFKC", text).casefold())


class PdfReadingOrderTests(unittest.TestCase):
    def setUp(self):
        self.folder = Path(tempfile.mkdtemp(prefix="resu-pdf-order-"))
        self.env = dict(os.environ, CLAUDE_PLUGIN_DATA=str(self.folder / "data"),
                        RESU_STUDIO_CONFIG=str(self.folder / "config"))
        self.source = (REPO / "docs/review/sample-cv.md").read_text(encoding="utf-8")
        self.cv = self.folder / "sample.md"
        self.cv.write_text(self.source, encoding="utf-8")

    def run_script(self, script, *args):
        result = subprocess.run([sys.executable, str(SKILL / "scripts" / script),
                                 *map(str, args)], cwd=SKILL, env=self.env,
                                capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def assert_pdf_text(self, pdf):
        reader = PdfReader(pdf)
        self.assertGreater(len(reader.pages), 0)
        actual = "\n".join(page.extract_text() for page in reader.pages)
        # Whole-document comparison catches missing text, duplicated text and
        # section headings detached from their content in the PDF paint order.
        self.assertEqual(words(actual), words(self.source))

    def test_default_renderer_preserves_text_order_across_pages(self):
        # Add fictional sections to exercise pagination as well as role/date order.
        for i in range(1, 7):
            self.source += "\n## SAMPLE PROJECT %d\n\n" % i
            self.source += ("Documented the booking process for sample venue %d, "
                            "including schedules, supplier contacts and incident records.\n\n" % i) * 7
        self.cv.write_text(self.source, encoding="utf-8")
        self.run_script("render_cv.py", self.cv, "--out", self.folder / "cv.html",
                        "--pdf", "--pdf-dir", self.folder, "--role", "Sample role")
        pdf = next(self.folder.glob("*.pdf"))
        self.assertGreater(len(PdfReader(pdf).pages), 1)
        self.assert_pdf_text(pdf)

    def test_studio_default_print_preserves_text_order(self):
        html = self.folder / "studio.html"
        self.run_script("build_studio.py", "--cv", self.cv, "--role", "Sample role",
                        "--employer", "Sample employer", "--out", html)
        with sync_playwright() as pw:
            browser = pw.chromium.launch(**({"executable_path": os.environ["CV_BROWSER"]}
                                            if os.environ.get("CV_BROWSER") else {}))
            page = browser.new_page()
            page.goto(html.as_uri())
            page.get_by_role("tab", name="Design", exact=True).click()
            page.get_by_role("button", name="Final", exact=True).click()
            page.frame_locator("#paper").locator(".sheet").first.wait_for()
            printable = page.locator("#paper").get_attribute("srcdoc")
            self.assertTrue(printable)
            printed_html = self.folder / "studio-print.html"
            printed_html.write_text(printable, encoding="utf-8")
            # Print the same document the Studio sends to its paper iframe.
            printed_pdf = self.folder / "studio-print.pdf"
            to_pdf.html_to_pdf(str(printed_html), str(printed_pdf))
            self.assert_pdf_text(printed_pdf)
            browser.close()


if __name__ == "__main__":
    unittest.main(verbosity=2)
