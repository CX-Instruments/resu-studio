"""Exercise the writing lifecycle with synthetic evidence and the actual local UI.

Standard-library checks run everywhere; browser checks run when Playwright and a
Chromium browser are available. All material is fictional and stays in a temp folder.
"""
import copy
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest

REPO = Path(__file__).resolve().parents[1]
SKILL = REPO / "skills/resu-studio"
SCR = Path(tempfile.mkdtemp(prefix="resu-writing-"))
os.environ["RESU_STUDIO_CONFIG"] = str(SCR / "config")
os.environ["CLAUDE_PLUGIN_DATA"] = str(SCR / "data")
sys.path.insert(0, str(SKILL / "scripts"))
import paths
import jobs
import writing as W
import proposal_records as P
import render_cv as R
import build_studio as B
import assemble as A

CV = """# Sample Person
sample@example.test

## PROFILE
Coordinates venue teams and improves procedures.

## EXPERIENCE
### Coordinator, Sample Venue | 2021 to 2025
- Wrote an incident procedure and trained 35 staff.
- Rebuilt the roster after recurring gaps.

## PROJECTS
### Procedure library | 2023
- Documented the incident response process.

## LANGUAGES
English
"""


def write(path, text):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return str(path)


def run(*args):
    p = subprocess.run([sys.executable, *map(str,args)], cwd=SKILL, capture_output=True,
                       text=True, encoding="utf-8")
    if p.returncode:
        raise AssertionError(p.stdout + p.stderr)
    return p.stdout


class WritingTests(unittest.TestCase):
    def setUp(self):
        self.job = jobs.create("Coordinator", "Sample", again=True)["id"]
        self.folder = Path(paths.job_dir(self.job))
        self.cv = write(self.folder / "source.md", CV)
        write(paths.facts_file(), "```\nid: f1\ntext: Wrote an incident procedure and trained 35 staff.\n```\n")
        write(self.folder / "asks.md", "```\nid: a1\ntext: Improve procedures and train the team.\nnecessity: must\n```\n")
        write(self.folder / "ad/ad.md", "Improve procedures and train the team.")
        self.review = {k:{"status":"pass","notes":"Reviewed synthetic evidence and the finished meaning."} for k in W.OBJECTIVES}
        self.data = {"brief": {"target":"Coordinator at Sample", "central_case":"Improves procedures and equips the team.",
          "priorities":["a1"], "voice":"Concrete and warm", "boundaries":"No invented outcomes or motivations.",
          "section_plan":[{"section":"Experience","purpose":"Prove training and procedure work."}],
          "constraints":{"page_limit":2,"bullet_budgets":{"experience/0":2}},
          "pillars":{k:{"status":"absent","statement":"Not enough evidence."} for k in W.PILLARS}},"samples":[]}
        examples = [
          ("Documents procedures and trains venue teams.", "Wrote an incident procedure, then trained 35 staff in its use."),
          ("Incident procedure writing. Staff training for a team of 35.", "Trained 35 staff in the incident procedure written for the venue."),
          ("Trains venue staff in incident procedures, drawing on procedure-writing experience.", "Trained a team of 35 staff in the venue's incident procedure after writing it."),
          ("From writing the incident procedure to training staff in its use: practical venue experience.", "An incident procedure, put into practice through training: wrote the procedure and trained 35 staff.")]
        for mode, (profile, bullet) in zip(W.modes(), examples):
            self.data["samples"].append({"mode":mode["id"],"why":"Shows supported procedure and team work.",
              "profile":{"line":"profile/0","current":"Coordinates venue teams and improves procedures.",
                "suggested":profile,
                "claims":[{"text":profile,"facts":["f1"]}]},
              "bullet":{"line":"experience/0/b0","current":"Wrote an incident procedure and trained 35 staff.",
                "suggested":bullet,
                "claims":[{"text":bullet,"facts":["f1"]}]}})
        self.state = W.prepare(self.job, self.cv, self.data)

    def request(self, action="rewrite", **extra):
        req = {"schema":1,"id":os.urandom(8).hex(),"job":self.job,"revision":W.load(self.job)["revision"],
               "source_hash":W.file_hash(self.cv),"mode":"credible-conviction","action":action,**extra}
        return W.request(self.job, req)

    def publish(self, text="Trained 35 staff in the incident procedure written for the venue."):
        proposal = f'''## P1. Experience, first bullet
**Line:** experience/0/b0
**Currently:** Wrote an incident procedure and trained 35 staff.
**Suggested:** {text}
**Why:** Brings team training forward without changing the claim.
**Purpose:** voice
**Draws on:** f1
**Claims:** {json.dumps([{"text":text,"facts":["f1"]}])}
**Decision:**
'''
        self.proposals = write(self.folder / "proposals.md", proposal)
        return W.publish(self.job, self.proposals, self.review)

    def decisions(self, state):
        rec = W.batch_for(state)["records"][0]
        return {"writing":{"job":self.job,"batch":state["batch"],"source_hash":W.file_hash(self.cv)},
                "marks":{rec["line"]:{"a":"edit","text":rec["sug"]}},
                "proposals":[{"uid":rec["uid"],"suggested":rec["sug"],"was":"used"}],"undecided":[]}

    def build(self):
        self.html = self.folder / "studio.html"
        run("scripts/build_studio.py", "--job", self.job, "--cv", self.cv,"--out",self.html)
        return self.html

    def test_authorisation_versions_and_finish(self):
        with self.assertRaisesRegex(ValueError,"authorised"):
            W.publish(self.job, "missing.md", self.review)
        requested=self.request()
        self.assertEqual(W.request(self.job, requested["request"])["revision"],requested["revision"])
        published=self.publish(); decisions=self.decisions(published)
        self.assertEqual(W.decision_faults(decisions,published,self.cv),[])
        altered=copy.deepcopy(decisions);altered["marks"]["experience/0/b0"]["text"]="Invented improvement."
        self.assertTrue(W.decision_faults(altered,published,self.cv))
        with self.assertRaisesRegex(ValueError,"assembled"):
            W.finish(self.job,self.cv,self.review,decisions)
        dfile=write(self.folder/"decisions.json",json.dumps(decisions))
        output=self.folder/"cv-ready.md"
        run("scripts/assemble.py",self.cv,"--decisions",dfile,"--out",output)
        self.assertIn("## LANGUAGES",output.read_text(encoding="utf-8"))
        ready=W.finish(self.job,str(output),self.review,decisions)
        self.assertEqual(ready["phase"],"ready")
        self.assertEqual(W.page_data(self.job,str(output))["phase"],"ready")
        self.assertGreater(len(list((self.folder/".writing").glob("*.json"))),3)
        self.assertTrue(Path(ready["sources"]["cv"]["snapshot"]).exists())

    def test_stale_ad_claim_map_and_custom_modes(self):
        facts=Path(paths.facts_file())
        facts.write_text(facts.read_text(encoding="utf-8")+"\n```\nid: unrelated\ntext: Another fact.\n```\n",encoding="utf-8")
        self.assertEqual(W.stale(W.load(self.job)),[])
        original=facts.read_text(encoding="utf-8")
        facts.write_text(original.replace("trained 35","trained 3"),encoding="utf-8")
        self.assertIn("facts",W.stale(W.load(self.job)))
        facts.write_text(original,encoding="utf-8")
        bad=copy.deepcopy(self.data);bad["samples"][0]["profile"]["claims"][0]["text"]="Incomplete."
        with self.assertRaisesRegex(ValueError,"full suggested"):
            W.prepare(self.job,self.cv,bad)
        bad=copy.deepcopy(self.data);bad["samples"][1]["bullet"]["line"]="experience/0/b1"
        with self.assertRaises(ValueError): W.prepare(self.job,self.cv,bad)
        write(self.folder/"ad/ad.md","A materially different job.")
        with self.assertRaisesRegex(ValueError,"changed"):
            self.request()
        self.assertIn("ad:ad.md",W.stale(W.load(self.job)))
        mode=dict(W.modes()[0],id="personal-test",version=1,name="My voice")
        target=W.save_mode(mode)
        self.assertTrue(Path(target).is_relative_to(Path(paths.record_dir())))
        with self.assertRaisesRegex(ValueError,"already exists"):
            W.save_mode(dict(mode,voice="Changed"))

    def test_exact_suggestion_identity_and_order(self):
        self.request(); first=self.publish()
        self.request("revise"); second=self.publish("Wrote the incident procedure used to train 35 staff.")
        self.assertNotEqual(W.batch_for(first)["records"][0]["uid"],W.batch_for(second)["records"][0]["uid"])
        self.assertTrue(W.decision_faults(self.decisions(first),second,self.cv))
        records=P.parse('''## P2. Role order
**Line:** experience/0
**Currently:** Current bullet order.
**Suggested:** Put the roster before training.
**Why:** Surface the relevant responsibility.
**Purpose:** structure
**Order:** [1, 0]
''')
        self.assertEqual(P.validate(records,self.cv,paths.facts_file(),str(self.folder/"asks.md"),True),[])

    def test_distinct_samples_and_preview_selection(self):
        same=copy.deepcopy(self.data)
        same["samples"][1]["profile"]=copy.deepcopy(same["samples"][0]["profile"])
        same["samples"][1]["bullet"]=copy.deepcopy(same["samples"][0]["bullet"])
        with self.assertRaisesRegex(ValueError,"identical samples"):
            W.prepare(self.job,self.cv,same)
        bad=copy.deepcopy(self.data);bad["preview_mode"]="not-offered"
        with self.assertRaisesRegex(ValueError,"must have samples"):
            W.prepare(self.job,self.cv,bad)
        self.request("preview",adjustments="More flowing, with concrete detail.")
        adjusted=copy.deepcopy(self.data);adjusted["preview_mode"]="expressive"
        state=W.prepare(self.job,self.cv,adjusted)
        self.assertEqual(state["preview_mode"],"expressive")
        self.assertEqual(state["phase"],"choose")
        self.assertIsNone(state["selected"])

    def test_generic_sections_and_new_profile(self):
        cv=B.cv_block(R.parse(CV))
        self.assertEqual(cv["order"],["profile","experience","source-projects","source-languages"])
        self.assertIn("projects/0/b0",B.cv_ids(cv))
        self.assertNotEqual(B.fingerprint(cv),B.fingerprint(B.cv_block(R.parse(CV.replace("English","French")))))
        two_skills=B.cv_block(R.parse(CV+"\n## KEY SKILLS\n**Tools:** Excel\n\n## OTHER SKILLS\n**Languages:** French\n"))
        self.assertIn("key-skills/languages",B.cv_ids(two_skills))
        spec={"title":"Profile","slug":"profile","after":"^","format":"paragraphs",
              "lines":[{"key":"profile/own0","text":"Documents procedures and trains venue teams."}]}
        source=CV.replace("## PROFILE\nCoordinates venue teams and improves procedures.\n\n","")
        assembled, record=A.assemble(source,{"sections":[spec]})
        self.assertLess(assembled.index("## PROFILE"),assembled.index("## EXPERIENCE"))
        self.assertNotIn("- Documents",assembled)
        self.assertIsNone(A.verify(source,{"sections":[spec]},assembled))
        order={"section_order":["languages","projects","experience","profile"]}
        assembled,_=A.assemble(CV,order)
        self.assertIsNone(A.verify(CV,order,assembled))
        self.assertLess(assembled.index("## LANGUAGES"),assembled.index("## PROFILE"))

    def test_consistent_partial_counts_and_section_proposals(self):
        text="""---
depth: all
counts:
  asks_total: 3
  you_have: 99
  a_reader_would_find: 99
---
| Ask | Necessity | State | Evidence | Note |
|---|---|---|---|---|
| a1 Procedure | must | page | f1 | |
| a2 Related | must | near | f1 | Partial |
| a3 Untouched | nice | unscored | | |
"""
        counts=jobs.scorecard_counts(write(self.folder/"scorecard.md",text))
        self.assertEqual((counts["you_have"],counts["a_reader_would_find"],counts["unscored"]),(1,1,1))
        spec={"title":"Achievements","slug":"achievements","after":"profile","format":"bullets",
              "lines":[{"text":"Wrote an incident procedure and trained 35 staff."}]}
        proposal='''## P1. New achievements section
**Line:** new-section/achievements
**Currently:** Not on the CV.
**Suggested:** Wrote an incident procedure and trained 35 staff.
**Why:** Give useful evidence a visible place.
**Purpose:** evidence visibility
**Costs:** One line; remove a duplicate after review.
**Draws on:** f1
**Claims:** [{"text":"Wrote an incident procedure and trained 35 staff.","facts":["f1"]}]
**Section:** '''+json.dumps(spec)
        self.assertEqual(P.validate(P.parse(proposal),self.cv,paths.facts_file(),str(self.folder/"asks.md"),True),[])
        self.request()
        state=W.publish(self.job,write(self.folder/"proposals.md",proposal),self.review)
        self.assertEqual(W.batch_for(state)["records"][0]["kind"],"section")
        self.build()
        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            return
        with sync_playwright() as pw:
            browser=pw.chromium.launch(**({"executable_path":os.environ["CV_BROWSER"]} if os.environ.get("CV_BROWSER") else {}))
            page=browser.new_page(); errors=[];page.on("pageerror",lambda e:errors.append(str(e)))
            page.goto(self.html.as_uri())
            page.get_by_role("button",name="Review suggested changes",exact=True).click()
            page.get_by_role("button",name="Use this",exact=True).click()
            decisions=json.loads(page.evaluate("decisionsFile()"))
            self.assertEqual(W.decision_faults(decisions,state,self.cv),[])
            dfile=write(self.folder/"decisions.json",json.dumps(decisions))
            output=self.folder/"cv-section.md"
            run("scripts/assemble.py",self.cv,"--decisions",dfile,"--out",output)
            W.finish(self.job,str(output),self.review,decisions)
            self.cv=str(output);self.build();page.reload()
            page.wait_for_selector('#writing-content')
            self.assertEqual(page.evaluate('S.order.filter(x=>secDef(x.id).slug==="achievements").length'),1)
            self.assertIn("Wrote an incident procedure",page.evaluate('sectionHTML("source-achievements")'))
            self.assertEqual(errors,[])
            browser.close()

    def test_browser_choice_handoff_review_and_isolation(self):
        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            self.skipTest("Playwright is needed for the browser check")
        self.build()
        with sync_playwright() as pw:
            browser=pw.chromium.launch(**({"executable_path":os.environ["CV_BROWSER"]} if os.environ.get("CV_BROWSER") else {}))
            page=browser.new_page(viewport={"width":1400,"height":950})
            errors=[]; page.on("pageerror",lambda e:errors.append(str(e)))
            page.goto(self.html.as_uri()); page.wait_for_selector('#writing-content input[type="radio"]')
            self.assertEqual(page.locator('#writing-content input[type="radio"]:visible').count(),len(self.data["samples"]))
            boxes=page.locator('#writing-compare-profile .writing-card').all()
            self.assertEqual(len({round(b.bounding_box()["y"]) for b in boxes}),1)
            self.assertEqual(page.locator('.writing-original').count(),2)
            page.get_by_role("button",name=re.compile("ORIGINAL.*Experience bullet")).click()
            self.assertFalse(page.locator('#writing-compare-profile').is_visible())
            page.locator('#writing-compare-bullet input[value="warm-collaborative"]').check()
            self.assertEqual(page.evaluate("S.writing.mode"),"warm-collaborative")
            page.get_by_role("button",name=re.compile("ORIGINAL.*Profile summary")).click()
            self.assertTrue(page.locator('#writing-compare-profile input[value="warm-collaborative"]').is_checked())
            page.locator('#writing-compare-profile input[value="credible-conviction"]').check()
            page.screenshot(path=str(SCR/"writing-comparison.png"),full_page=True)
            page.get_by_role("button",name="Use this mode and rewrite my CV",exact=True).click()
            handoff=page.get_by_label("Writing request to send to AI").input_value()
            req=json.loads(re.search(r'```json\n(.*)\n```',handoff,re.S)[1])
            self.assertEqual(req["writing_request"]["mode"],"credible-conviction")
            W.request(self.job,req); published=self.publish(); self.build()
            page.reload();page.wait_for_selector('#writing-content input[type="radio"]')
            page.get_by_role("button",name="Review suggested changes",exact=True).click()
            page.get_by_role("button",name="Use this",exact=True).click()
            decisions=json.loads(page.evaluate("decisionsFile()"))
            self.assertEqual(W.decision_faults(decisions,published,self.cv),[])
            self.assertIn("LANGUAGES",page.evaluate("buildDoc()"))
            store=page.evaluate("STORE")
            page.reload();page.wait_for_selector('#writing-content')
            self.assertEqual(json.loads(page.evaluate("decisionsFile()"))["proposals"][0]["was"],"used")
            page.screenshot(path=str(SCR/"writing-studio.png"),full_page=True)
            other=jobs.create("Coordinator","Sample",again=True)["id"]
            other_html=self.folder/"other.html"
            run("scripts/build_studio.py","--job",other,"--cv",self.cv,"--out",other_html)
            page.goto(other_html.as_uri());page.wait_for_selector('#writing-content')
            self.assertNotEqual(store,page.evaluate("STORE"))
            self.assertEqual(page.evaluate("Object.keys(S.marks).length"),0)
            self.assertEqual(errors,[])
            browser.close()

    def test_browser_personal_mode_preview_and_responsive_comparison(self):
        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            self.skipTest("Playwright is needed for the browser check")
        self.build()
        with sync_playwright() as pw:
            browser=pw.chromium.launch(**({"executable_path":os.environ["CV_BROWSER"]} if os.environ.get("CV_BROWSER") else {}))
            page=browser.new_page(viewport={"width":1440,"height":1100})
            errors=[];page.on("pageerror",lambda e:errors.append(str(e)))
            page.goto(self.html.as_uri())
            page.get_by_role("button",name="Create my own mode",exact=True).click()
            page.get_by_label("Start from",exact=True).select_option("warm-collaborative")
            page.get_by_role("button",name="People & collaboration",exact=True).click()
            page.get_by_role("button",name="Playful",exact=True).click()
            page.get_by_role("button",name="More flowing",exact=True).click()
            page.get_by_label("Describe it your way",exact=True).fill("Keep the practical details. A little flair.")
            page.get_by_label("Anything to avoid?",exact=True).fill("Slogans")
            self.assertIn("Voice: Playful",page.locator('.writing-direction-text').inner_text())
            page.get_by_role("button",name="Preview my mode",exact=True).click()
            def handoff():
                return json.loads(re.search(r'```json\n(.*)\n```',page.get_by_label("Writing request to send to AI").input_value(),re.S)[1])
            local=handoff()["writing_request"]
            self.assertEqual((local["action"],local["scope"],local["save_as"]),("preview","application",""))
            self.assertEqual(local["mode"],"warm-collaborative")
            for text in ("People & collaboration","Playful","More flowing","A little flair.","Avoid: Slogans"):
                self.assertIn(text,local["adjustments"])
            page.get_by_label("Save this as a reusable personal mode",exact=True).check()
            page.get_by_role("button",name="Preview my mode",exact=True).click()
            self.assertIn("Give your reusable mode a name",page.locator('.writing-direction-preview').inner_text())
            page.get_by_label("Name your mode",exact=True).fill("Practical with flair")
            page.reload()
            page.get_by_role("button",name="Create my own mode",exact=True).click()
            self.assertEqual(page.get_by_label("Name your mode",exact=True).input_value(),"Practical with flair")
            self.assertEqual(page.get_by_label("Start from",exact=True).input_value(),"warm-collaborative")
            page.locator('.panes').evaluate('(e)=>{e.scrollTop=0}')
            page.screenshot(path=str(SCR/"writing-builder.png"),full_page=True)
            page.get_by_role("button",name="Preview my mode",exact=True).click()
            reusable=handoff()
            self.assertEqual(reusable["writing_request"]["scope"],"preference")
            self.assertEqual(reusable["writing_request"]["save_as"],"Practical with flair")
            page.get_by_role("button",name="Preview my mode",exact=True).click()
            self.assertEqual(handoff()["writing_request"]["id"],reusable["writing_request"]["id"])
            W.request(self.job,reusable);self.build();page.reload()
            self.assertEqual(page.locator('#writing-content input[type="radio"]:enabled').count(),0)
            page.get_by_role("button",name="Create my own mode",exact=True).click()
            self.assertTrue(page.get_by_role("button",name="Preview my mode",exact=True).is_disabled())
            # Host returns a new application-only mode, highlighted but not authorised.
            refreshed=copy.deepcopy(self.data)
            mode=dict(W.modes()[0],id="personal-flair",name="Practical with flair",version=1)
            sample=copy.deepcopy(refreshed["samples"][0]);sample["mode"]=mode["id"]
            sample["profile"]["suggested"]="Writes venue incident procedures and trains staff in their use."
            sample["profile"]["claims"]=[{"text":sample["profile"]["suggested"],"facts":["f1"]}]
            refreshed["samples"].append(sample);refreshed["custom_modes"]=[mode];refreshed["preview_mode"]=mode["id"]
            state=W.prepare(self.job,self.cv,refreshed);self.build();page.reload()
            self.assertEqual(page.evaluate('S.writing.mode'),mode["id"])
            self.assertEqual(page.evaluate('S.writing.viewMode'),mode["id"])
            self.assertEqual(page.locator('#writing-compare-profile .writing-card').first.get_attribute('data-mode'),mode["id"])
            self.assertEqual(page.locator('#writing-compare-profile .writing-card').nth(1).get_attribute('data-mode'),"warm-collaborative")
            self.assertIsNone(state["selected"])
            page.set_viewport_size({"width":390,"height":844})
            page.locator('.panes').evaluate('(e)=>{e.scrollTop=0}')
            page.locator('#writing-compare-profile .writing-mobile-switch').get_by_role("button",name="Direct and focused",exact=True).click()
            self.assertEqual(page.locator('#writing-compare-profile .writing-card:visible').count(),1)
            self.assertEqual(page.locator('#writing-compare-profile .writing-card:visible').get_attribute('data-mode'),"direct-impact")
            self.assertEqual(page.evaluate('S.writing.mode'),mode["id"])
            page.locator('#writing-compare-profile input[value="direct-impact"]').check()
            page.get_by_role("button",name=re.compile("ORIGINAL.*Experience bullet")).click()
            self.assertEqual(page.locator('#writing-compare-bullet .writing-card:visible').get_attribute('data-mode'),"direct-impact")
            self.assertTrue(page.evaluate('document.documentElement.scrollWidth <= window.innerWidth'))
            self.assertTrue(page.locator('.panes').evaluate('(e)=>e.scrollWidth <= e.clientWidth'))
            page.screenshot(path=str(SCR/"writing-mobile.png"),full_page=True)
            page.get_by_role("button",name="Use this mode and rewrite my CV",exact=True).click()
            req=handoff()["writing_request"]
            self.assertEqual((req["mode"],req["adjustments"],req["save_as"]),("direct-impact","",""))
            W.request(self.job,req);self.build();page.reload()
            self.assertEqual(page.evaluate('S.writing.mode'),"direct-impact")
            # Editing the ad makes comparison read-only, without losing the draft.
            write(self.folder/"ad/ad.md","A changed advertisement.");self.build();page.reload()
            self.assertEqual(page.locator('#writing-content input[type="radio"]:enabled').count(),0)
            self.assertEqual(page.get_by_role("button",name="Use this mode and rewrite my CV",exact=True).count(),0)
            page.get_by_role("button",name="Create my own mode",exact=True).click()
            self.assertEqual(page.get_by_label("Name your mode",exact=True).input_value(),"Practical with flair")
            self.assertTrue(page.get_by_label("Name your mode",exact=True).is_disabled())
            self.assertEqual(errors,[])
            browser.close()


if __name__ == "__main__":
    print("Synthetic writing artifacts:",SCR,flush=True)
    unittest.main(verbosity=2)
