/* Lay the CV out on real A4 sheets.

   Nothing here rewrites a word. It moves finished blocks between sheets so that
   a bullet, a role heading or a skills group is never cut in half by a page
   edge. If anything goes wrong it puts the document back the way it was, on one
   long sheet, rather than showing a page with something missing.

   Expects, in the document:
     <div id="src" hidden>
       <div data-region="aside">...</div>   (only on layouts with a sidebar)
       <div data-region="main">...</div>
     </div>
     <div id="doc"></div>
     window.__PAGE__ = {kind, side, ruled, head, headtag, headcls}
*/
(function () {
  "use strict";

  /* Wait for the document AND for the typefaces.

     Everything below measures text to decide where a sheet ends. Measured in a
     fallback face and repainted in the real one, every measurement is wrong by a
     little, and a bullet that fitted moves to the next page. Worse, it is wrong
     differently in the preview and in the print, so the PDF stops matching what
     was on screen. document.fonts.ready settles that before a single height is
     read. The timeout is there so a font server that never answers costs three
     seconds rather than the whole document. */
  function ready(fn) {
    function go() {
      if (!document.fonts || document.fonts.status === "loaded") return fn();
      var done = false;
      var once = function () { if (!done) { done = true; fn(); } };
      try { document.fonts.ready.then(once); } catch (e) { return once(); }
      setTimeout(once, 3000);
    }
    if (document.readyState !== "loading") go();
    else document.addEventListener("DOMContentLoaded", go);
  }

  ready(function () {
    var CFG = window.__PAGE__ || {};
    var SRC = document.getElementById("src");
    var DOC = document.getElementById("doc");
    if (!SRC || !DOC) return;

    var kind = CFG.kind || "plain";
    var side = CFG.side || "left";
    var ruled = CFG.ruled ? " ruled" : "";
    var headHTML = CFG.head || "";
    var headTag = CFG.headtag || "div";
    var headCls = CFG.headcls || "headwrap";
    var gid = 0;

    /* ---------------------------------------------------------- atomising */

    function el(tag, cls) {
      var e = document.createElement(tag);
      if (cls) e.className = cls;
      return e;
    }

    /* A role becomes its head plus one atom per remaining bullet, all sharing a
       group id so the pieces that land on one sheet are stitched back together. */
    function splitRole(role, g) {
      var out = [], ul = null, before = [];
      Array.prototype.slice.call(role.childNodes).forEach(function (n) {
        if (n.nodeType === 1 && n.tagName === "UL" && !ul) ul = n;
        else before.push(n);
      });
      var head = role.cloneNode(false);
      head.setAttribute("data-grp", g);
      before.forEach(function (n) { head.appendChild(n); });
      var lis = ul ? Array.prototype.slice.call(ul.children) : [];
      if (ul) {
        var u = ul.cloneNode(false);
        if (lis.length) u.appendChild(lis.shift());
        head.appendChild(u);
      }
      out.push(head);
      lis.forEach(function (li) {
        var w = role.cloneNode(false);
        w.setAttribute("data-grp", g);
        var u2 = ul.cloneNode(false);
        u2.appendChild(li);
        w.appendChild(u2);
        out.push(w);
      });
      return out;
    }

    /* A loose bullet list becomes one atom per bullet. */
    function splitList(ul, g) {
      var out = [];
      Array.prototype.slice.call(ul.children).forEach(function (li) {
        var u = ul.cloneNode(false);
        u.setAttribute("data-grp", g);
        u.appendChild(li);
        out.push(u);
      });
      return out;
    }

    function atomise(container) {
      var out = [];
      Array.prototype.slice.call(container.children).forEach(function (k) {
        var g = "g" + (gid++);
        if (k.classList.contains("role")) {
          splitRole(k, g).forEach(function (a) { out.push(a); });
          return;
        }
        if (k.tagName === "UL") {
          splitList(k, g).forEach(function (a) { out.push(a); });
          return;
        }
        if (k.classList.contains("cols2")) {
          /* a section set in two columns: one atom per item, rebuilt into one box
             on whichever sheet the items land */
          Array.prototype.slice.call(k.children).forEach(function (c) {
            var w = k.cloneNode(false);
            w.setAttribute("data-grp", g);
            w.appendChild(c);
            out.push(w);
          });
          return;
        }
        if (k.classList.contains("secwrap")) {
          /* slab: the heading floats into the gutter beside its own section, so
             every piece of the section needs its own wrapper */
          atomise(k).forEach(function (a) {
            var w = k.cloneNode(false);
            w.setAttribute("data-grp", g);
            w.appendChild(a);
            out.push(w);
          });
          return;
        }
        out.push(k);
      });
      return out;
    }

    /* A heading on its own at the foot of a sheet is worse than a shorter
       sheet, so it travels with whatever follows it. */
    function markKeeps(atoms) {
      atoms.forEach(function (a, i) {
        var isHead = (a.tagName === "H2" && a.classList.contains("sec")) ||
                     a.classList.contains("legend") ||
                     (a.querySelector && a.querySelector(":scope > h2.sec") &&
                      a.children.length === 1);
        if (isHead && i < atoms.length - 1) a.setAttribute("data-keep", "1");
        a.setAttribute("data-atom", "1");
      });
      return atoms;
    }

    /* Move one atom's contents into the block above it, and remember enough to put
       them back. Merging has to happen while the sheet is being filled, not after:
       a role card carries its own padding and margin, so six bullet atoms measured
       separately are three hundred pixels taller than the one card they become. Fill
       on the pre-merge measurement and the page stops half empty. */
    function mergeInto(dst, src) {
      var moved = [], keep = dst.getAttribute("data-keep");
      Array.prototype.slice.call(src.children).forEach(function (c) {
        var last = dst.lastElementChild;
        if (last && c.tagName === "UL" && last.tagName === "UL" &&
            last.className === c.className) {
          var lis = Array.prototype.slice.call(c.children);
          lis.forEach(function (li) { last.appendChild(li); });
          moved.push({ back: c, nodes: lis });
        } else {
          dst.appendChild(c);
          moved.push({ back: src, nodes: [c] });
        }
      });
      /* it is no longer a heading on its own, so it must not be pulled back as one */
      if (keep) dst.removeAttribute("data-keep");
      return { moved: moved, dst: dst, keep: keep };
    }

    function unmerge(m) {
      m.moved.slice().reverse().forEach(function (x) {
        x.nodes.forEach(function (n) { x.back.appendChild(n); });
      });
      if (m.keep) m.dst.setAttribute("data-keep", m.keep);
    }

    function sameGroup(a, b) {
      var ga = a && a.getAttribute && a.getAttribute("data-grp");
      var gb = b && b.getAttribute && b.getAttribute("data-grp");
      return !!(ga && ga === gb);
    }

    /* Two atoms of the same group that land on one sheet become one block. */
    function stitch(region) {
      var i = 0;
      while (i < region.children.length - 1) {
        var a = region.children[i], b = region.children[i + 1];
        var ga = a.getAttribute("data-grp"), gb = b.getAttribute("data-grp");
        if (ga && ga === gb) {
          Array.prototype.slice.call(b.children).forEach(function (c) {
            var last = a.lastElementChild;
            if (last && c.tagName === "UL" && last.tagName === "UL" &&
                last.className === c.className) {
              Array.prototype.slice.call(c.children).forEach(function (li) {
                last.appendChild(li);
              });
            } else {
              a.appendChild(c);
            }
          });
          b.parentNode.removeChild(b);
          stitch(a);
        } else {
          i++;
        }
      }
    }

    /* ------------------------------------------------------------- sheets */

    function newSheet(index) {
      var sheet = el("div", "sheet" + ruled);
      var regions = {};
      var hasAside = (kind === "sidebar" || kind === "sidebartop");

      function head() {
        var h = el(headTag, headCls);
        h.innerHTML = headHTML;
        return h;
      }

      if (kind === "sidebar") {
        var grid = el("div", "grid " + side);
        var aside = el("div", "aside"), main = el("div", "main");
        if (side === "left") { grid.appendChild(aside); grid.appendChild(main); }
        else { grid.appendChild(main); grid.appendChild(aside); }
        sheet.appendChild(grid);
        regions.aside = aside; regions.main = main;
      } else if (kind === "sidebartop") {
        if (index === 0) {
          /* page one has a sidebar, floor to ceiling. Page two onwards does not.
             That is the whole of this layout. */
          var g2 = el("div", "grid " + side);
          var a2 = el("div", "aside"), m2 = el("div", "main");
          if (side === "right") { g2.appendChild(m2); g2.appendChild(a2); }
          else { g2.appendChild(a2); g2.appendChild(m2); }
          sheet.appendChild(g2);
          regions.aside = a2; regions.main = m2;
        } else {
          var rest = el("div", "rest");
          sheet.appendChild(rest);
          regions.main = rest;
        }
      } else if (kind === "band" || kind === "slab") {
        if (index === 0) {
          var band = el("div", kind === "band" ? "hdr" : "slab");
          band.innerHTML = headHTML;
          sheet.appendChild(band);
        }
        var pad = el("div", "pad");
        sheet.appendChild(pad);
        regions.main = pad;
      } else {
        var pad2 = el("div", "pad");
        if (index === 0 && headHTML) pad2.appendChild(head());
        sheet.appendChild(pad2);
        regions.main = pad2;
      }
      sheet.setAttribute("data-page", index + 1);
      DOC.appendChild(sheet);
      return { sheet: sheet, regions: regions };
    }

    function overflowing(r) {
      return r.scrollHeight > r.clientHeight + 1;
    }

    /* --------------------------------------------------------------- fill */

    var asideSrc = SRC.querySelector('[data-region="aside"]');
    var mainSrc = SRC.querySelector('[data-region="main"]');

    /* Take the register before anything is split: every line that has an id in the
       source has to have one on a sheet at the end. Counting atoms would not do it,
       because atoms merge back together as the sheet fills. */
    var wanted = {}, wantedN = 0;
    Array.prototype.slice.call(SRC.querySelectorAll("[data-id]")).forEach(function (n) {
      var k = n.getAttribute("data-id");
      if (!wanted[k]) { wanted[k] = 1; wantedN++; }
    });

    var asideAtoms = asideSrc ? markKeeps(atomise(asideSrc)) : [];
    var mainAtoms = mainSrc ? markKeeps(atomise(mainSrc)) : [];

    /* If the sidebar cannot hold everything on page one, the remainder joins the main
       flow at the marker its section left behind, so the order the person set is the
       order that prints. The heading travels with it. */
    var original = DOC.innerHTML;
    var cursors = { aside: 0, main: 0 };

    function fill(region, atoms, cursor, gauge) {
      if (!region) return cursor;
      var box = gauge || region;
      var placed = 0;
      while (cursor < atoms.length) {
        var a = atoms[cursor];
        var prev = region.lastElementChild;
        var merged = sameGroup(prev, a) ? mergeInto(prev, a) : null;
        if (!merged) region.appendChild(a);
        if (overflowing(box)) {
          if (merged) unmerge(merged); else region.removeChild(a);
          /* pull back any heading that would be stranded */
          while (region.lastElementChild &&
                 region.lastElementChild.getAttribute("data-keep") === "1") {
            region.removeChild(region.lastElementChild);
            cursor--; placed--;
          }
          if (placed <= 0) {
            /* one block taller than a whole sheet. Let the sheet grow rather
               than clip it: a long page is a problem you can see, a clipped
               one is not. */
            region.appendChild(a);
            var sh = region.closest ? region.closest(".sheet") : null;
            if (sh) sh.classList.add("grow");
            cursor++;
          }
          return cursor;
        }
        cursor++; placed++;
      }
      return cursor;
    }

    var page = 0, guard = 0;
    while ((cursors.aside < asideAtoms.length || cursors.main < mainAtoms.length)
           && guard++ < 60) {
      var p = newSheet(page);
      var before = cursors.aside + cursors.main;
      if (p.regions.aside)
        cursors.aside = fill(p.regions.aside, asideAtoms, cursors.aside);
      if (p.regions.main) cursors.main = fill(p.regions.main, mainAtoms, cursors.main);

      /* sidebar-top has no aside after page one, so anything left over there joins the
         main flow rather than disappearing. Its heading stayed behind in the panel, so
         the continuation carries a copy of it: a run of groups with no heading over
         them reads as a section that was cut off. */
      if (kind === "sidebartop" && page === 0 && cursors.aside < asideAtoms.length) {
        var spill = asideAtoms.slice(cursors.aside);
        var firstIsHead = spill[0] && spill[0].tagName === "H2" &&
                          spill[0].classList.contains("sec");
        if (!firstIsHead && p.regions.aside) {
          var heads = p.regions.aside.querySelectorAll("h2.sec");
          if (heads.length) {
            var again = heads[heads.length - 1].cloneNode(true);
            again.removeAttribute("data-id");
            again.setAttribute("data-atom", "1");
            again.setAttribute("data-keep", "1");
            spill = [again].concat(spill);
          }
        }
        mainAtoms = mainAtoms.slice(0, cursors.main)
          .concat(spill)
          .concat(mainAtoms.slice(cursors.main));
        cursors.aside = asideAtoms.length;
      }
      if (cursors.aside + cursors.main === before) break;   /* no progress */
      page++;
    }

    var landed = {}, missing = 0;
    Array.prototype.slice.call(DOC.querySelectorAll("[data-id]")).forEach(function (n) {
      landed[n.getAttribute("data-id")] = 1;
    });
    for (var want in wanted) { if (!landed[want]) missing++; }
    if (missing || page === 0) {
      /* something did not add up, so show everything on one sheet instead of
         showing a tidy page with a line missing */
      DOC.innerHTML = original;
      var one = el("div", "sheet" + ruled + " unpaged");
      one.innerHTML = SRC.innerHTML;
      DOC.appendChild(one);
      DOC.setAttribute("data-paginated", "no");
    } else {
      Array.prototype.slice.call(DOC.querySelectorAll(".aside,.main,.pad,.rest"))
        .forEach(stitch);
      DOC.setAttribute("data-paginated", String(page));
    }
    SRC.parentNode.removeChild(SRC);
    document.documentElement.setAttribute("data-pages", DOC.children.length);
    if (window.parent && window.parent !== window) {
      try {
        window.parent.postMessage({ cvPages: DOC.children.length,
                                    height: document.body.scrollHeight }, "*");
      } catch (e) {}
    }
  });
})();
