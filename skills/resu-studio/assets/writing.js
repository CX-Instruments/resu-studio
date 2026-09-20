/* The writing journey uses the same application and handoff as CV review.
   The page collects an intent; it does not pretend to run an AI in the browser. */
(function () {
  "use strict";
  const root = document.getElementById("writing-content");
  if (!root) return;
  function element(tag, text, cls) {
    const e = document.createElement(tag);
    if (text !== undefined) e.textContent = text;
    if (cls) e.className = cls;
    return e;
  }
  function button(label, fn, cls) {
    const b = element("button", label, cls || "cta");
    b.type = "button"; b.addEventListener("click", fn); return b;
  }
  const phase = WRITING.phase;
  const samples = WRITING.samples || [];
  S.writing = S.writing || {};
  if (S.writing.revision !== WRITING.revision) {
    // Retain unsent wording in an explicit draft instead of treating it as sent.
    S.writing.previous = S.writing.adjustments || S.writing.previous || "";
    S.writing.revision = WRITING.revision;
    S.writing.mode = (WRITING.selected || {}).id || (samples.find(s=>s.mode==="credible-conviction") || samples[0] || {}).mode || "";
    S.writing.adjustments = "";
    S.writing.saveAs = "";
    S.writing.sent = null;
    save();
  }
  function showHandoff(action) {
    const choice = samples.find(s => s.mode === S.writing.mode);
    if (!choice) return;
    const adjustments = (S.writing.adjustments || "").trim();
    if (action === "rewrite" && adjustments) {
      notice.textContent = "Preview your adjustments first, then choose the version you want rewritten.";
      return;
    }
    const intent = {schema:1, job:WRITING.job, revision:WRITING.revision, source_hash:SOURCE_HASH,
      mode:choice.mode, action:action, adjustments:adjustments,
      save_as:(S.writing.saveAs || "").trim()};
    intent.scope=action==="revise"?"lines":action==="preview"&&intent.save_as?"preference":"application";
    const signature=JSON.stringify(intent);
    if (!S.writing.sent || S.writing.sent.signature !== signature) {
      S.writing.sent = {signature:signature, id:Date.now().toString(36)+"-"+Math.random().toString(36).slice(2)};
    }
    intent.id=S.writing.sent.id;
    const handoff=JSON.parse(decisionsFile());
    handoff.writing_request=intent;
    const prompt = action === "rewrite"
      ? "Use this selected mode and rewrite my CV. This is my request to begin; do not ask again whether to proceed."
      : action === "revise"
      ? "Revise the requested lines using the current guiding brief. Preserve my other decisions."
      : "Show adjusted writing samples for this application. Keep my CV and prior decisions intact.";
    const text=prompt+"\nSave this handoff in the application's folder and run writing.py request --job "
      +WRITING.job+" --input <saved handoff>. Read references/writing-engine.md and the saved writing context before continuing.\n\n```json\n"
      +JSON.stringify(handoff,null,2)+"\n```";
    handBox.hidden=false; handText.value=text;
    notice.textContent="Your request is ready. Copy it into your AI chat to continue this application.";
    save();
  }
  root.textContent="";
  root.appendChild(element("h2", "Your writing direction"));
  root.appendChild(element("p", "Every mode keeps your evidence, this job's priorities and clear, readable writing at its centre.", "hint"));
  root.appendChild(element("p", WRITING.label || "Your CV and job are being prepared.", "hint"));
  if (WRITING.brief) {
    root.appendChild(element("h3", "The case your CV can make"));
    root.appendChild(element("p", WRITING.brief.central_case));
    const detail=element("details"); detail.appendChild(element("summary", "Your guiding brief"));
    detail.appendChild(element("p", WRITING.brief.target));
    const labels={passion:"Working habits",strengths:"Supported strengths",impact:"Proof of impact",value:"Distinctive contribution"};
    Object.entries(WRITING.brief.pillars || {}).forEach(([key,p])=>{
      detail.appendChild(element("h4",labels[key] || key));
      detail.appendChild(element("p",p.status==="supported" ? p.statement : "Not used: "+p.statement));
    });
    detail.appendChild(element("p","Voice: "+WRITING.brief.voice));
    detail.appendChild(element("p","Boundaries: "+[].concat(WRITING.brief.boundaries).join(" ")));
    root.appendChild(detail);
  }
  const pending=["rewrite_requested","revision_requested","preview_requested"].includes(phase);
  if (phase === "unprepared" || phase === "stale") {
    root.appendChild(element("p",phase==="stale"
      ? "The source material has changed. Ask the AI to refresh these samples before starting another rewrite. Earlier work is retained."
      : "Ask the AI to prepare examples from your CV and this advertisement. A saved style is adapted to each job."));
  }
  const sampleGrid=element("div",undefined,"writing-samples");
  root.appendChild(sampleGrid);
  samples.forEach(sample=>{
    const box=element("div",undefined,"writing-card");
    const label=element("label"); const radio=document.createElement("input");
    radio.type="radio"; radio.name="writing-mode"; radio.value=sample.mode;
    radio.checked=S.writing.mode===sample.mode;
    radio.disabled=pending || phase==="stale";
    radio.addEventListener("change",()=>{ S.writing.mode=sample.mode; save(); });
    label.appendChild(radio); label.appendChild(document.createTextNode(" "+sample.definition.name));
    box.appendChild(label); box.appendChild(element("p",sample.why,"hint"));
    ["profile","bullet"].forEach(key=>{
      box.appendChild(element("h4",key==="profile"?"Profile summary":"Experience bullet"));
      const old=element("details"); old.open=true; old.appendChild(element("summary","Original"));
      old.appendChild(element("p",sample[key].current || "No profile on the source CV.")); box.appendChild(old);
      box.appendChild(element("p","In this mode","hint"));
      box.appendChild(element("p",sample[key].suggested));
      const proof=element("details"); proof.appendChild(element("summary","Supporting evidence"));
      sample[key].claims.forEach(c=>{
        proof.appendChild(element("p",c.text));
        c.facts.forEach(id=>{
          const source=(WRITING.evidence||{})[id];
          if(source){
            source.text.forEach(t=>proof.appendChild(element("blockquote",t)));
            if(source.context.length) proof.appendChild(element("p",source.context.join(" · "),"hint"));
          }
          proof.appendChild(element("p","Source: "+id,"hint"));
        });
      }); box.appendChild(proof);
    });
    sampleGrid.appendChild(box);
  });
  const notice=element("p","","hint"); notice.setAttribute("role","status");
  const handBox=element("div",undefined,"grp"); handBox.hidden=true;
  handBox.appendChild(element("h3","Continue in your AI chat"));
  handBox.appendChild(element("p","This local page keeps your choices here until you send them back.","hint"));
  const handText=document.createElement("textarea"); handText.readOnly=true;
  handText.rows=8; handText.style.width="100%"; handText.setAttribute("aria-label","Writing request to send to AI");
  handBox.appendChild(handText);
  handBox.appendChild(button("Copy request",async()=>{
    try { await navigator.clipboard.writeText(handText.value); notice.textContent="Copied. Paste into your AI chat to continue."; }
    catch(e) { handText.focus(); handText.select(); notice.textContent="Select and copy the request, then paste it into your AI chat."; }
  }));
  handBox.appendChild(button("Save request",()=>{
    const match=handText.value.match(/```json\n([\s\S]*)\n```/);
    const url=URL.createObjectURL(new Blob([match[1]],{type:"application/json"}));
    const a=document.createElement("a"); a.href=url; a.download="writing-request.json"; a.click();
    setTimeout(()=>URL.revokeObjectURL(url),1000);
  },"cta ghost"));
  if (samples.length && !pending && phase!=="stale") {
    const actions=element("div",undefined,"writing-actions");
    root.insertBefore(actions,sampleGrid);
    const explore=element("details");explore.appendChild(element("summary","Explore or save your own mode"));
    actions.appendChild(explore);
    const lab=element("label","What would you like to change about the direction?");
    lab.htmlFor="writing-adjustments"; explore.appendChild(lab);
    const input=document.createElement("textarea"); input.id="writing-adjustments"; input.rows=3;
    input.style.width="100%"; input.value=S.writing.adjustments || "";
    input.placeholder="For example: keep the practical emphasis, with a warmer voice.";
    input.addEventListener("input",()=>{S.writing.adjustments=input.value;save();});explore.appendChild(input);
    const name=document.createElement("input"); name.type="text";name.placeholder="Name a personal mode to save (optional)";
    name.setAttribute("aria-label","Name for a reusable personal writing mode");name.style.width="100%";
    name.value=S.writing.saveAs || "";name.addEventListener("input",()=>{S.writing.saveAs=name.value;save();});explore.appendChild(name);
    if(S.writing.previous) explore.appendChild(button("Restore my unsent note",()=>{input.value=S.writing.previous;S.writing.adjustments=input.value;save();},"cta ghost"));
    explore.appendChild(button("Preview my adjustments",()=>showHandoff("preview"),"cta ghost"));
    if(WRITING.display_is_source !== false) actions.appendChild(button("Use this mode and rewrite my CV",()=>showHandoff("rewrite")));
    if(WRITING.selected) actions.appendChild(button("Send my revision requests",()=>showHandoff("revise"),"cta ghost"));
    actions.appendChild(element("p","Choosing a direction requests suggestions. You still decide which wording goes into your CV.","hint"));
  }
  if(phase==="review" || phase==="review_required") {
    root.insertBefore(button("Review suggested changes",()=>{document.getElementById("t-skin").click();S.turnView="need";openDrawer("turn");}),sampleGrid);
    root.appendChild(element("p","Keep what works, request another version where needed, and return your decisions through hand to AI.","hint"));
  }
  if(WRITING.final_review) Object.entries(WRITING.final_review).forEach(([key,item])=>{
    if(item.status!=="pass") root.appendChild(element("p",item.notes));
  });
  root.insertBefore(notice,sampleGrid);root.insertBefore(handBox,sampleGrid);
  if (LEGACY_STORE && LEGACY_STORE!==STORE && !RAW_STATE) {
    let legacy=null;try{legacy=localStorage.getItem(LEGACY_STORE);}catch(e){}
    if(legacy) root.appendChild(button("Restore earlier local review",()=>{
      // User-triggered, with the old store left intact. Normal fingerprint
      // migration on reload still checks line decisions against their wording.
      localStorage.setItem(STORE,legacy);location.reload();
    },"cta ghost"));
  }
  document.getElementById("t-writing").click();
})();
