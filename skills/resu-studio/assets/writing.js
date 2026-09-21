/* One source passage, several evidence-grounded directions. The local page
   collects requests; generation continues in the host chat. */
(function () {
  "use strict";
  const root = document.getElementById("writing-content");
  if (!root) return;
  function el(tag, text, cls) {
    const e = document.createElement(tag);
    if (text !== undefined) e.textContent = text;
    if (cls) e.className = cls;
    return e;
  }
  function button(label, fn, cls = "cta") {
    const b = el("button", label, cls); b.type = "button";
    b.addEventListener("click", fn); return b;
  }
  const samples = WRITING.samples || [], phase = WRITING.phase;
  const pending = ["rewrite_requested", "revision_requested", "preview_requested"].includes(phase);
  const locked = pending || phase === "stale" || !samples.length;
  const w = S.writing = S.writing || {};
  // Retain drafts through reloads and host rebuilds, without applying them to
  // a built-in or silently turning them into a saved preference.
  w.draft = w.draft || {note:w.adjustments || "", name:w.saveAs || "", reuse:!!w.saveAs};
  if (w.revision !== WRITING.revision) {
    w.revision = WRITING.revision;
    w.mode = (WRITING.selected || {}).id || WRITING.preview_mode ||
      (samples.find(s => s.mode === w.mode) || samples.find(s => s.mode === "credible-conviction") || samples[0] || {}).mode || "";
    w.sent = null;
    w.viewMode = w.mode;
    if (WRITING.preview_mode) w.passage = "profile";
  }
  w.passage = w.passage || "profile";
  w.viewMode = samples.some(s => s.mode === w.viewMode) ? w.viewMode : w.mode;
  const draft = w.draft;
  draft.base = samples.some(s => s.mode === draft.base) ? draft.base : w.mode;
  save();
  const choice = () => samples.find(s => s.mode === w.mode);
  const notice = el("p", "", "writing-notice"); notice.setAttribute("role", "status");
  const handBox = el("section", undefined, "writing-handoff"); handBox.hidden = true;
  handBox.append(el("h3", "Continue in your AI chat"), el("p", "Copy this request into the same conversation. Your choices and current review decisions travel together.", "hint"));
  const handText = el("textarea"); handText.readOnly = true; handText.rows = 7;
  handText.setAttribute("aria-label", "Writing request to send to AI");
  handBox.append(handText, button("Copy request", async () => {
    try { await navigator.clipboard.writeText(handText.value); notice.textContent = "Copied. Paste into your AI chat to continue."; }
    catch (e) { handText.focus(); handText.select(); notice.textContent = "Select and copy the request, then paste it into your AI chat."; }
  }), button("Save request", () => {
    const match = handText.value.match(/```json\n([\s\S]*)\n```/);
    const url = URL.createObjectURL(new Blob([match[1]], {type:"application/json"}));
    const a = el("a"); a.href = url; a.download = "writing-request.json"; a.click();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  }, "cta ghost"));
  function directions() {
    return [draft.emphasis && "Emphasise: " + draft.emphasis + ".",
      draft.voice && "Voice: " + draft.voice + ".", draft.rhythm && "Rhythm: " + draft.rhythm + ".",
      (draft.note || "").trim(), draft.avoid && "Avoid: " + draft.avoid.trim()].filter(Boolean).join("\n");
  }
  function handoff(action, adjustments = "", mode = w.mode, saveAs = "") {
    if (locked || !samples.some(s => s.mode === mode)) return;
    const intent = {schema:1, job:WRITING.job, revision:WRITING.revision, source_hash:SOURCE_HASH,
      mode, action, adjustments, save_as:saveAs,
      scope:action === "revise" ? "lines" : action === "preview" && saveAs ? "preference" : "application"};
    const signature = JSON.stringify(intent);
    if (!w.sent || w.sent.signature !== signature) w.sent = {signature, id:Date.now().toString(36) + "-" + Math.random().toString(36).slice(2)};
    intent.id = w.sent.id;
    const payload = JSON.parse(decisionsFile()); payload.writing_request = intent;
    const prompt = action === "rewrite"
      ? "Use this selected mode and rewrite my CV. This is my request to begin; do not ask again whether to proceed."
      : action === "revise" ? "Revise the requested lines using the current guiding brief. Preserve my other decisions."
      : "Show adjusted writing samples for this application. Keep my CV and prior decisions intact.";
    handText.value = prompt + "\nSave this handoff in the application's folder and run writing.py request --job " + WRITING.job
      + " --input <saved handoff>. Read references/writing-engine.md and the saved writing context before continuing.\n\n```json\n"
      + JSON.stringify(payload, null, 2) + "\n```";
    handBox.hidden = false;
    notice.textContent = "Request ready. Send it to your AI chat to " + (action === "preview" ? "generate the samples." : "continue the rewrite.");
    save(); handBox.scrollIntoView({block:"nearest"}); handText.focus();
  }
  root.textContent = "";
  const hero = el("header", undefined, "writing-hero"), heading = el("div");
  heading.append(el("p", "YOUR CV, YOUR VOICE", "writing-eyebrow"), el("h2", "Find the way you want to sound"),
    el("p", "Open a passage. Compare the directions. Choose what feels like you.", "writing-intro"));
  hero.append(heading); root.append(hero);
  if (WRITING.brief) {
    const brief = el("details", undefined, "writing-brief");
    brief.append(el("summary", "The guiding brief · " + WRITING.brief.target), el("p", WRITING.brief.central_case));
    const pillars = el("div", undefined, "writing-pillars");
    const labels = {passion:"Working habits", strengths:"Supported strengths", impact:"Proof of impact", value:"Distinctive contribution"};
    Object.entries(WRITING.brief.pillars || {}).forEach(([key, p]) => {
      const item = el("div"); item.append(el("h4", labels[key] || key), el("p", (p.status === "supported" ? "" : "Not used: ") + p.statement)); pillars.append(item);
    });
    brief.append(pillars, el("p", "Voice: " + WRITING.brief.voice), el("p", "Boundaries: " + [].concat(WRITING.brief.boundaries).join(" ")));
    root.append(brief);
  }
  if (locked) root.append(el("p", phase === "stale"
    ? "The source material has changed. Ask the AI to refresh these samples. Earlier work is retained."
    : pending ? "Your request is with the AI. Send the saved handoff if you have not already; refreshed samples or suggestions will appear after the Studio is rebuilt."
    : "Ask the AI to prepare examples from your CV and this advertisement.", "writing-status"));
  const nav = el("div", undefined, "writing-workspace-nav");
  const compare = el("section"); compare.id = "writing-compare";
  const builder = el("section", undefined, "writing-builder"); builder.id = "writing-builder"; builder.hidden = true;
  const compareTab = button("Compare writing modes", () => setWorkspace(false), "writing-nav-button");
  const createTab = button("Create my own mode", () => setWorkspace(true), "writing-nav-button");
  compareTab.setAttribute("aria-controls", compare.id); createTab.setAttribute("aria-controls", builder.id);
  function setWorkspace(custom) {
    compare.hidden = custom; builder.hidden = !custom; actionBar.hidden = custom || locked;
    compareTab.setAttribute("aria-pressed", String(!custom)); createTab.setAttribute("aria-pressed", String(custom));
    handBox.hidden = true; notice.textContent = "";
  }
  nav.append(compareTab, createTab);
  if (samples.length) root.append(nav);
  root.append(compare, builder);
  compare.append(el("p", "One original, different directions. These two passages preview the approach to the full CV.", "hint"));
  const cards = [], sourcePanels = [], mobileButtons = [];
  const sourceTitles = {profile:"Profile summary", bullet:"Experience bullet"};
  function syncSelection() {
    cards.forEach(({sample, box, radio}) => {
      radio.checked = sample.mode === w.mode;
      box.classList.toggle("is-selected", radio.checked);
      box.classList.toggle("is-mobile-visible", sample.mode === w.viewMode);
    });
    mobileButtons.forEach(({b, mode}) => b.setAttribute("aria-pressed", String(mode === w.viewMode)));
    selectedText.textContent = "Selected: " + ((choice() || {}).definition || {}).name;
  }
  ["profile", "bullet"].forEach(key => {
    if (!samples.length) return;
    const panel = el("section", undefined, "writing-source");
    const toggle = button("", () => {
      w.passage = w.passage === key ? "closed" : key; save(); syncPassages();
    }, "writing-source-toggle");
    toggle.append(el("span", "ORIGINAL · " + sourceTitles[key], "writing-eyebrow"),
      el("span", samples[0][key].current || "No profile on the source CV.", "writing-original"),
      el("span", "Compare " + samples.length + " directions", "writing-expand"));
    const body = el("div", undefined, "writing-comparison"); body.id = "writing-compare-" + key;
    toggle.setAttribute("aria-controls", body.id);
    const mobile = el("div", undefined, "writing-mobile-switch");
    mobile.setAttribute("aria-label", "View a " + sourceTitles[key].toLowerCase() + " mode");
    samples.forEach(sample => {
      const b = button(sample.definition.name, () => {w.viewMode = sample.mode; save(); syncSelection();}, "writing-chip");
      mobileButtons.push({b, mode:sample.mode}); mobile.append(b);
    }); body.append(mobile);
    const grid = el("div", undefined, "writing-samples");
    grid.style.setProperty("--mode-count", Math.min(samples.length, 4));
    const ordered = samples.slice().sort((a, b) => {
      const rank = s => s.mode === WRITING.preview_mode ? 0 : s.mode === WRITING.preview_base ? 1 : 2;
      return rank(a) - rank(b);
    });
    ordered.forEach(sample => {
      const box = el("article", undefined, "writing-card"); box.dataset.mode = sample.mode;
      box.style.setProperty("--mode-color", ["#337b88", "#ae682b", "#687844", "#8a67ad"][samples.indexOf(sample) % 4]);
      const label = el("label", undefined, "writing-mode-label"), radio = el("input");
      radio.type = "radio"; radio.name = "writing-mode-" + key; radio.value = sample.mode; radio.disabled = locked;
      radio.addEventListener("change", () => {w.mode = sample.mode; w.viewMode = sample.mode; save(); syncSelection();});
      label.append(radio, el("span", sample.definition.name));
      box.append(el("p", sample.definition.signature || sample.definition.voice, "writing-mode-signature"), label,
        el("p", sample[key].suggested, "writing-suggestion"));
      const explanation = el("details", undefined, "writing-explanation");
      explanation.append(el("summary", "What changes & why"), el("p", sample[key].difference || sample.why));
      const same = samples.filter(other => other !== sample && other[key].suggested.trim().toLowerCase() === sample[key].suggested.trim().toLowerCase());
      if (same.length) explanation.append(el("p", "Same wording as " + same.map(s => s.definition.name).join(", ") + ". This passage does not demonstrate a different voice."));
      const proof = el("details"); proof.append(el("summary", "Check the evidence"));
      sample[key].claims.forEach(c => {
        proof.append(el("p", c.text));
        c.facts.forEach(id => {
          const source = (WRITING.evidence || {})[id];
          if (source) {
            source.text.forEach(t => proof.append(el("blockquote", t)));
            if (source.context.length) proof.append(el("p", source.context.join(" · "), "hint"));
          }
          proof.append(el("p", "Source: " + id, "hint"));
        });
      });
      box.append(explanation, proof); grid.append(box); cards.push({sample, box, radio});
    });
    body.append(grid); panel.append(toggle, body); compare.append(panel); sourcePanels.push({key, toggle, body});
  });
  function syncPassages() {
    sourcePanels.forEach(({key, toggle, body}) => {
      body.hidden = w.passage !== key; toggle.setAttribute("aria-expanded", String(!body.hidden));
      toggle.querySelector(".writing-expand").textContent = body.hidden ? "Compare " + samples.length + " directions +" : "Close comparison −";
    });
  }
  if (!locked) compare.append(button("These sound too similar", () => handoff("preview",
    "Rework the offered mode samples so their evidence emphasis, sentence construction and rhythm demonstrate meaningful differences. Keep the same source passages and factual boundaries. Compare them side by side before returning; explain any unavoidable overlap. Preserve the existing modes as choices."), "writing-text-button"));
  const builderTitle = el("div"); builderTitle.append(el("p", "MAKE IT YOURS", "writing-eyebrow"), el("h3", "Build a direction, then hear it in your words"),
    el("p", "Start with a mode you like. Choose as much or as little as helps—your own description is enough.", "hint"));
  builder.append(builderTitle);
  const form = el("fieldset", undefined, "writing-builder-fields"); form.disabled = locked;
  const fields = el("div", undefined, "writing-builder-controls"), preview = el("aside", undefined, "writing-direction-preview");
  form.append(fields, preview); builder.append(form);
  const baseLabel = el("label", "Start from"); baseLabel.htmlFor = "writing-base";
  const base = el("select"); base.id = "writing-base";
  samples.forEach(s => {const opt = el("option", s.definition.name); opt.value = s.mode; base.append(opt);});
  base.value = draft.base; base.addEventListener("change", () => {draft.base = base.value; updateDraft();}); fields.append(baseLabel, base);
  function chips(title, field, values) {
    const group = el("fieldset", undefined, "writing-choice-group"); group.append(el("legend", title));
    const row = el("div", undefined, "writing-chips");
    values.forEach(value => {
      const b = button(value, () => {
        draft[field] = draft[field] === value ? "" : value;
        Array.from(row.children).forEach(x => x.setAttribute("aria-pressed", String(x.textContent === draft[field]))); updateDraft();
      }, "writing-chip");
      b.setAttribute("aria-pressed", String(draft[field] === value)); row.append(b);
    }); group.append(row); fields.append(group);
  }
  chips("Bring forward", "emphasis", ["Results & scale", "People & collaboration", "Problem-solving & process", "Distinctive combinations"]);
  chips("How it should feel", "voice", ["Measured", "Warm", "Persuasive", "Playful"]);
  chips("Pace & rhythm", "rhythm", ["Short & direct", "Balanced", "More flowing"]);
  function textField(label, field, placeholder, multiline) {
    const lab = el("label", label), input = el(multiline ? "textarea" : "input");
    input.id = "writing-draft-" + field; lab.htmlFor = input.id;
    if (multiline) input.rows = 3; else input.type = "text";
    input.placeholder = placeholder; input.value = draft[field] || "";
    input.addEventListener("input", () => {draft[field] = input.value; updateDraft();});
    fields.append(lab, input); return input;
  }
  textField("Describe it your way", "note", "For example: practical and warm, with a little flair. Let the work speak for itself.", true);
  textField("Anything to avoid?", "avoid", "For example: sales language or long sentences", false);
  const reuseLabel = el("label", undefined, "writing-reuse"), reuse = el("input");
  reuse.type = "checkbox"; reuse.checked = !!draft.reuse;
  reuseLabel.append(reuse, document.createTextNode(" Save this as a reusable personal mode")); fields.append(reuseLabel);
  const name = textField("Name your mode", "name", "For example: Practical with warmth", false), nameLabel = name.previousElementSibling;
  reuse.addEventListener("change", () => {draft.reuse = reuse.checked; updateDraft();});
  preview.append(el("p", "YOUR DIRECTION", "writing-eyebrow"));
  const previewBase = el("h4"), previewText = el("p", "", "writing-direction-text");
  preview.append(previewBase, previewText, el("p", "Always: true to your evidence, tailored to this job, clear for ATS and engaging for people.", "writing-guardrail"),
    el("p", "This is your brief. The AI will write a profile and bullet sample for you to compare before you commit.", "hint"));
  const builderError = el("p", "", "writing-notice"); builderError.setAttribute("role", "status"); preview.append(builderError);
  preview.append(button("Preview my mode", () => {
    if (draft.reuse && !(draft.name || "").trim()) {builderError.textContent = "Give your reusable mode a name, or untick saving to try it for this application."; name.focus(); return;}
    if (!directions()) {builderError.textContent = "Choose a feel, an emphasis, or describe what you want to change."; return;}
    builderError.textContent = "";
    handoff("preview", directions(), draft.base, draft.reuse ? draft.name.trim() : "");
  }));
  function updateDraft() {
    const source = samples.find(s => s.mode === draft.base);
    previewBase.textContent = source ? "Starting with " + source.definition.name : "Your own direction";
    previewText.textContent = directions() || "Your choices will appear here. Keep what you like about the starting mode and tell us what to change.";
    name.hidden = nameLabel.hidden = !draft.reuse;
    save();
  }
  updateDraft();
  const actionBar = el("div", undefined, "writing-action-bar");
  const selectedText = el("strong"); const actionSummary = el("div");
  actionSummary.append(selectedText, el("p", "The full rewrite follows this direction. You review every proposed change.", "hint"));
  actionBar.append(actionSummary);
  if (phase === "review" || phase === "review_required") actionBar.append(button("Review suggested changes", () => {
    document.getElementById("t-skin").click(); S.turnView = "need"; openDrawer("turn");
  }));
  if (WRITING.display_is_source !== false) actionBar.append(button("Use this mode and rewrite my CV", () => handoff("rewrite")));
  if (WRITING.selected) actionBar.append(button("Send my revision requests", () => handoff("revise", "", WRITING.selected.id), "cta ghost"));
  root.append(actionBar, notice, handBox);
  if (WRITING.final_review) Object.values(WRITING.final_review).forEach(item => {if (item.status !== "pass") root.append(el("p", item.notes));});
  if (LEGACY_STORE && LEGACY_STORE !== STORE && !RAW_STATE) {
    let legacy = null; try {legacy = localStorage.getItem(LEGACY_STORE);} catch (e) {}
    if (legacy) root.append(button("Restore earlier local review", () => {localStorage.setItem(STORE, legacy); location.reload();}, "cta ghost"));
  }
  syncPassages(); syncSelection(); setWorkspace(false);
  document.getElementById("t-writing").click();
})();
