/* Selecting a line on the page.

   This runs inside the sheet, after the paginator has finished. It does not change
   a single word: it lets you point at a line and says what you pointed at. Every
   button posts an intent outward, and the panel beside the page does the rest,
   so typing never happens inside a paginated sheet and never reflows one.
*/
(function () {
  "use strict";
  function ready(fn) {
    if (document.readyState !== "loading") fn();
    else document.addEventListener("DOMContentLoaded", fn);
  }
  ready(function () {
    if (!window.__MARKUP__) return;
    var sel = null;

    var bar = document.createElement("div");
    bar.className = "cvbar";
    bar.setAttribute("hidden", "");
    var BUTTONS = [
      ["keep", "Read it, happy with it",
       '<path d="M3.4 8.4l3 3 6.2-7" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>'],
      ["flag", "Flag it for later",
       '<path d="M4 2v13M4 3h9l-2 3 2 3H4" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round"/>'],
      ["rewrite", "Needs a rewrite",
       '<path d="M9 2l1.6 4.4L15 8l-4.4 1.6L9 14l-1.6-4.4L3 8l4.4-1.6z" fill="currentColor"/>'],
      ["edit", "Edit it myself",
       '<path d="M3 13l1-3 7-7 2 2-7 7z" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linejoin="round"/>'],
      ["remove", "Take it off this version",
       '<circle cx="8" cy="8" r="5.6" fill="none" stroke="currentColor" stroke-width="1.5"/><path d="M5.4 8h5.2" stroke="currentColor" stroke-width="1.5"/>'],
      ["add", "Write a new line after this one",
       '<path d="M8 3.6v8.8M3.6 8h8.8" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/>'],
      /* The arrows appear only on a line that says it can move, and only the studio
         says so. They shuffle the preview: the printed PDF still follows the order in
         the markdown, which is why the label says so and the studio repeats it. */
      ["up", "Move it up in the preview (the printed PDF still follows your markdown)",
       '<path d="M8 12.6V3.8M4.4 7.2L8 3.6l3.6 3.6" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>'],
      ["down", "Move it down in the preview (the printed PDF still follows your markdown)",
       '<path d="M8 3.4v8.8M4.4 8.8L8 12.4l3.6-3.6" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>']
    ];
    BUTTONS.forEach(function (b) {
      var el = document.createElement("button");
      el.type = "button";
      el.setAttribute("data-act", b[0]);
      el.title = b[1];
      el.setAttribute("aria-label", b[1]);
      el.innerHTML = '<svg viewBox="0 0 16 16" width="14" height="14" aria-hidden="true">'
        + b[2] + "</svg>";
      bar.appendChild(el);
    });
    document.body.appendChild(bar);

    function send(kind, extra) {
      var msg = { cvwb: kind };
      for (var k in extra) msg[k] = extra[k];
      try { window.parent.postMessage(msg, "*"); } catch (e) {}
    }

    function place() {
      if (!sel) { bar.setAttribute("hidden", ""); return; }
      var r = sel.getBoundingClientRect();
      bar.removeAttribute("hidden");
      var w = bar.offsetWidth || 150;
      var x = Math.min(r.right - w, Math.max(4, r.left));
      var y = r.top - bar.offsetHeight - 4;
      if (y < 2) y = r.bottom + 4;
      bar.style.left = (x + window.scrollX) + "px";
      bar.style.top = (y + window.scrollY) + "px";
    }

    function select(el) {
      if (sel) sel.classList.remove("cvsel");
      sel = el;
      if (!sel) { bar.setAttribute("hidden", ""); send("deselect", {}); return; }
      sel.classList.add("cvsel");
      /* Which lines the arrows work on is a question about this person's CV, and the
         page around it is the only thing that knows the answer. It marks them, so
         nothing in here has to guess at heading names. */
      var movable = sel.hasAttribute("data-move");
      Array.prototype.slice.call(bar.querySelectorAll("button")).forEach(function (b) {
        var a = b.getAttribute("data-act");
        if (a === "up" || a === "down") b.hidden = !movable;
      });
      place();
      send("select", { id: sel.getAttribute("data-id"),
                       text: (sel.innerText || "").trim() });
    }

    document.addEventListener("click", function (e) {
      var btn = e.target.closest && e.target.closest(".cvbar button");
      if (btn) {
        e.preventDefault();
        if (sel) send("act", { act: btn.getAttribute("data-act"),
                               id: sel.getAttribute("data-id"),
                               text: (sel.innerText || "").trim() });
        return;
      }
      var hit = e.target.closest && e.target.closest("[data-id]");
      select(hit && hit !== sel ? hit : null);
    });

    window.addEventListener("scroll", place, { passive: true });
    window.addEventListener("resize", place);
    window.addEventListener("message", function (e) {
      var d = e.data || {};
      if (d.cvwb === "clear") { select(null); return; }
      if (d.cvwb === "goto" && d.id) {
        var el = document.querySelector('[data-id="' + d.id.replace(/"/g, '\\"') + '"]');
        if (!el) return;
        el.scrollIntoView({ block: "center", behavior: "smooth" });
        setTimeout(function () { select(el); }, 260);
      }
    });
  });
})();
