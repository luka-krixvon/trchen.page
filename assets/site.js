(function () {
  "use strict";
  var root = document.documentElement;
  var DEMO = root.dataset.demo === "1"; 

  /* ---- theme toggle ---- */
  try {
    var saved = localStorage.getItem("theme");
    if (saved === "dark" || saved === "light") root.setAttribute("data-theme", saved);
  } catch (e) {}
  var tbtn = document.querySelector("[data-theme-toggle]");
  if (tbtn) {
    tbtn.addEventListener("click", function () {
      var dark = root.getAttribute("data-theme") === "dark" ||
        (!root.hasAttribute("data-theme") && window.matchMedia("(prefers-color-scheme: dark)").matches);
      var next = dark ? "light" : "dark";
      root.setAttribute("data-theme", next);
      try { localStorage.setItem("theme", next); } catch (e) {}
    });
  }

  /* ---- publication filters ---- */
  var filters = document.querySelectorAll("[data-filter]");
  var pubs = document.querySelectorAll("[data-topics]");
  var note = document.querySelector("[data-filter-note]");
  function applyFilter(key) {
    var shown = 0;
    pubs.forEach(function (li) {
      var ok = key === "all"
        ? true
        : key === "video"
          ? li.dataset.video === "1"
          : (" " + li.dataset.topics + " ").indexOf(" " + key + " ") > -1;
      li.hidden = !ok;
      if (ok) shown++;
    });
    if (note) note.textContent = note.dataset.tpl.replace("{n}", String(shown));
  }
  filters.forEach(function (b) {
    b.addEventListener("click", function () {
      filters.forEach(function (x) { x.setAttribute("aria-pressed", String(x === b)); });
      applyFilter(b.dataset.filter);
    });
  });
  if (note && note.dataset.tpl) applyFilter("all");

  /* ---- inline talk panel ---- */
  document.querySelectorAll("[data-watch]").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var panel = document.getElementById(btn.getAttribute("aria-controls"));
      var open = btn.getAttribute("aria-expanded") === "true";
      btn.setAttribute("aria-expanded", String(!open));
      panel.hidden = open;
      if (open) resetPlayer(panel.querySelector(".yt"));
    });
  });

  /* ---- YouTube facade ---- */
  function resetPlayer(box) {
    if (!box) return;
    var fr = box.querySelector("iframe");
    if (fr) fr.remove();
    var face = box.querySelector(".yt-face");
    if (face) face.hidden = false;
  }
  function play(box, start) {
    if (!box) return;
    var id = box.dataset.yt;
    if (DEMO || !id || id === "VIDEO_ID") {
      box.classList.add("is-demo");
      var tag = box.querySelector(".yt-demo");
      if (tag) tag.textContent = tag.dataset.demoOn || tag.textContent;
      return;
    }
    resetPlayer(box);
    var fr = document.createElement("iframe");
    fr.src = "https://www.youtube-nocookie.com/embed/" + encodeURIComponent(id) +
      "?autoplay=1&rel=0&modestbranding=1" + (start ? "&start=" + encodeURIComponent(start) : "");
    fr.title = box.dataset.title || "Recorded talk";
    fr.allow = "accelerometer; autoplay; encrypted-media; picture-in-picture; web-share";
    fr.referrerPolicy = "strict-origin-when-cross-origin";
    fr.allowFullscreen = true;
    box.appendChild(fr);
    var face = box.querySelector(".yt-face");
    if (face) face.hidden = true;
  }
  document.querySelectorAll(".yt-face").forEach(function (face) {
    face.addEventListener("click", function () { play(face.closest(".yt"), 0); });
  });
  document.querySelectorAll("[data-seek]").forEach(function (ch) {
    ch.addEventListener("click", function () {
      play(ch.closest(".vpanel").querySelector(".yt"), parseInt(ch.dataset.seek, 10) || 0);
    });
  });

  /* ---- poster frames ---- */
  document.querySelectorAll(".yt[data-yt]").forEach(function (box) {
    var id = box.dataset.yt;
    if (!id || id === "VIDEO_ID" || DEMO) return;
    var img = new Image();
    img.onload = function () {
      box.style.backgroundImage = "linear-gradient(180deg,rgba(4,6,10,.12),rgba(4,6,10,.5)), url(" + img.src + ")";
    };
    img.src = "https://i.ytimg.com/vi/" + encodeURIComponent(id) + "/maxresdefault.jpg";
  });

  /* ---- nav highlight ---- */
  var secs = Array.prototype.slice.call(document.querySelectorAll("main section[id]"));
  var navs = {};
  document.querySelectorAll(".rail-nav a").forEach(function (a) {
    var h = a.getAttribute("href") || "";
    if (h.charAt(0) === "#") navs[h.slice(1)] = a;
  });
  if (secs.length && "IntersectionObserver" in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (!en.isIntersecting) return;
        Object.keys(navs).forEach(function (k) { navs[k].classList.toggle("on", k === en.target.id); });
      });
    }, { rootMargin: "-15% 0px -75% 0px" });
    secs.forEach(function (s) { io.observe(s); });
  }
})();


document.querySelectorAll("[data-pubtoggle]").forEach(function (btn) {
  btn.addEventListener("click", function () {
    var body = document.getElementById(btn.getAttribute("aria-controls"));
    var open = btn.getAttribute("aria-expanded") === "true";
    btn.setAttribute("aria-expanded", String(!open));
    body.hidden = open;
  });
});
