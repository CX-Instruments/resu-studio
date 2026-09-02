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
     was on screen.

     Waiting on document.fonts.ready alone does not do it, and the way it fails is
     silent. A browser fetches a face only when something it is about to draw calls
     for it, and this document arrives with every word inside a hidden #src and an
     empty #doc, so at DOMContentLoaded not one face has been asked for. The set is
     idle, status reads "loaded", and ready is already resolved. The paginator then
     measured the whole CV in the fallback face, which sets wider: it counted lines
     that were not there, and every sheet stopped four or five lines short of the
     foot, with the overflow pushed onto a page of its own.

     So ask for the faces first. Calling load() on each declared face is what turns
     the wait into a real one, and it costs nothing here because the faces are
     carried in the file. Then fonts.ready, for anything the styles pull in later.
     The timeout is there so a font server that never answers costs three seconds
     rather than the whole document. */
  function ready(fn) {
    function go() {
      var fonts = document.fonts;
      if (!fonts) return fn();
      var done = false;
      var once = function () { if (!done) { done = true; fn(); } };
      var waiting = [];
      try {
        fonts.forEach(function (face) {
          if (face.status === "unloaded") {
            waiting.push(face.load().then(null, function () {}));
          }
        });
      } catch (e) { /* an older FontFaceSet: fall through to ready alone */ }
      try {
        Promise.all(waiting)
          .then(function () { return fonts.ready; })
          .then(once, once);
      } catch (e) { return once(); }
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

    /* Is there anything left over the edge of this region.

       scrollHeight counts the bottom margin of the last block in the region, and on
       the last block of a sheet that margin is measuring a gap to a block that is on
       the next page. A role card carries eighteen pixels of it. So a card that ended
       two pixels past the line was thrown onto a sheet of its own to protect white
       space nobody would ever have seen, and the page before it finished an inch
       short. That margin is given back here.

       Nothing else is. The padding at the foot of the region is the design's own
       page margin and still has to fit, so what this allows is exactly: the ink of
       the last block ends on or above the line where the bottom margin starts. The
       region clips what hangs past it, and after this it has nothing to clip. */
    function overflowing(r) {
      var over = r.scrollHeight - r.clientHeight;
      if (over <= 1) return false;
      var last = r.lastElementChild;
      if (last) {
        var gap = parseFloat(getComputedStyle(last).marginBottom) || 0;
        if (gap > 0 && over - gap <= 1) return false;
      }
      return true;
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
      /* One entry per atom put on this sheet, newest last: null when the atom was
         appended whole, and the merge record when it was folded into the block above
         it. Taking an atom off again is not simply removing the last child, because
         a merged atom is not a child any more, and the sheet has to be able to give
         one back once it knows what the next sheet would have started with. */
      var trail = [];
      function back() {
        if (!trail.length) return false;
        var m = trail.pop();
        if (m) unmerge(m);
        else if (region.lastElementChild) region.removeChild(region.lastElementChild);
        cursor--; placed--;
        return true;
      }
      while (cursor < atoms.length) {
        var a = atoms[cursor];
        var prev = region.lastElementChild;
        var merged = sameGroup(prev, a) ? mergeInto(prev, a) : null;
        if (!merged) region.appendChild(a);
        if (overflowing(box)) {
          if (merged) unmerge(merged); else region.removeChild(a);
          /* A single bullet at the top of the next sheet, with the whole of its role
             left behind on this one, reads as something that went wrong rather than
             as a role that ran on. So send the bullet above it along for company.
             Only when this sheet has two blocks to spare: a sheet that gives back
             everything it has made no progress, and the loop outside would stop. */
          if (placed >= 2 && cursor > 0 &&
              sameGroup(atoms[cursor - 1], atoms[cursor]) &&
              !sameGroup(atoms[cursor], atoms[cursor + 1])) {
            back();
          }
          /* pull back any heading that would be stranded */
          while (region.lastElementChild &&
                 region.lastElementChild.getAttribute("data-keep") === "1") {
            if (!back()) break;
          }
          if (placed <= 0) {
            /* Nothing at all would stay on this sheet. Put back whatever the cursor
               now points at rather than the block that overflowed: after a pull back
               they are not the same atom, and appending the wrong one dropped a
               heading off the document altogether.

               If it still does not fit, it is one block taller than a whole sheet.
               Let the sheet grow rather than clip it: a long page is a problem you
               can see, a clipped one is not. */
            region.appendChild(atoms[cursor]);
            if (overflowing(box)) {
              var sh = region.closest ? region.closest(".sheet") : null;
              if (sh) sh.classList.add("grow");
            }
            cursor++;
          }
          return cursor;
        }
        trail.push(merged);
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

    /* How much of the last sheet is actually written on.

       A CV can still spill a few lines onto a sheet of its own, and nobody wants to
       post that without being told. The paginator is the only thing that knows, so
       it says so here and leaves the document alone.

       Measured as ink against the writable column, not against the paper: the foot
       and head margins are not empty page, they are the design. So for each region
       on the last sheet, take the bottom of the lowest thing that draws anything and
       compare it with the height between the padding. Children with no height are
       skipped, because a layout leaves display:none markers behind and the last one
       of those is not where the writing stops. Regions are taken at their best, not
       averaged: on a sidebar layout the panel is empty after page one, and averaging
       it in would report every second page as half empty when it is full.

       The line count is that ink divided by one line of body text: it is what would
       have to come off the CV to lose the sheet, in the unit a person edits in. */
    function fillOfLastSheet() {
      var sheet = DOC.lastElementChild;
      if (!sheet || DOC.getAttribute("data-paginated") === "no" ||
          sheet.classList.contains("grow") || sheet.classList.contains("unpaged")) {
        return null;
      }
      var regions = Array.prototype.slice.call(
        sheet.querySelectorAll(".aside,.main,.pad,.rest"));
      if (!regions.length) regions = [sheet];
      var best = null;
      regions.forEach(function (r) {
        var cs = getComputedStyle(r);
        var top = parseFloat(cs.paddingTop) || 0;
        var bot = parseFloat(cs.paddingBottom) || 0;
        var usable = r.clientHeight - top - bot;
        if (usable <= 0) return;
        var rt = r.getBoundingClientRect().top, ink = 0, any = false;
        Array.prototype.slice.call(r.children).forEach(function (c) {
          var box = c.getBoundingClientRect();
          if (box.height <= 0) return;
          any = true;
          if (box.bottom - rt > ink) ink = box.bottom - rt;
        });
        if (!any) return;
        var used = ink - top;
        if (used < 0) used = 0;
        var frac = used / usable;
        if (frac > 1) frac = 1;
        if (!best || frac > best.fill) best = { fill: frac, used: used, box: r };
      });
      if (!best) return { fill: 0, lines: 0 };
      var lh = parseFloat(getComputedStyle(best.box).lineHeight);
      if (!lh || lh <= 0) lh = parseFloat(getComputedStyle(document.body).lineHeight);
      if (!lh || lh <= 0) lh = 16;
      return { fill: best.fill, lines: Math.max(1, Math.round(best.used / lh)) };
    }

    var lastFill = null;
    try { lastFill = fillOfLastSheet(); } catch (e) {}
    if (lastFill) {
      document.documentElement.setAttribute("data-lastfill", lastFill.fill.toFixed(3));
      document.documentElement.setAttribute("data-lastlines", String(lastFill.lines));
    }

    if (window.parent && window.parent !== window) {
      try {
        window.parent.postMessage({ cvPages: DOC.children.length,
                                    lastFill: lastFill ? lastFill.fill : null,
                                    lastLines: lastFill ? lastFill.lines : null,
                                    height: document.body.scrollHeight }, "*");
      } catch (e) {}
    }
  });
})();
