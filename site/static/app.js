// Small progressive enhancements. The site works without JavaScript.
(function () {
  "use strict";

  // 1. Show dates in the reader's local time zone.
  var fmt;
  try {
    fmt = new Intl.DateTimeFormat("en-GB", { day: "numeric", month: "short", year: "numeric", hour: "2-digit", minute: "2-digit" });
  } catch (e) { fmt = null; }
  document.querySelectorAll("time[data-local]").forEach(function (el) {
    var d = new Date(el.getAttribute("datetime"));
    if (fmt && !isNaN(d)) { el.textContent = fmt.format(d); el.title = d.toUTCString(); }
  });

  // 2. Theme filter on the news page. The choice is remembered in the URL (#theme)
  //    and in localStorage, so it survives a reload.
  var buttons = document.querySelectorAll(".filter[data-filter]");
  if (buttons.length) {
    var stories = document.querySelectorAll(".story-list .story");
    var count = document.querySelector(".filter-count");
    var empty = document.querySelector(".empty-filter");
    var apply = function (theme) {
      var shown = 0;
      stories.forEach(function (s) {
        var ok = theme === "all" || (" " + s.dataset.themes + " ").indexOf(" " + theme + " ") !== -1;
        s.hidden = !ok;
        if (ok) shown++;
      });
      buttons.forEach(function (b) { b.setAttribute("aria-pressed", String(b.dataset.filter === theme)); });
      if (count) count.textContent = shown + (shown === 1 ? " story" : " stories");
      if (empty) empty.hidden = shown !== 0;
      try { localStorage.setItem("theme-filter", theme); } catch (e) {}
    };
    buttons.forEach(function (b) {
      b.addEventListener("click", function () {
        apply(b.dataset.filter);
        history.replaceState(null, "", b.dataset.filter === "all" ? location.pathname : "#" + b.dataset.filter);
      });
    });
    var initial = location.hash.slice(1);
    if (!initial) { try { initial = localStorage.getItem("theme-filter") || ""; } catch (e) {} }
    var valid = Array.prototype.some.call(buttons, function (b) { return b.dataset.filter === initial; });
    apply(valid ? initial : "all");
  }

  // 3. Instant filter on the glossary page.
  var search = document.getElementById("glossary-search");
  if (search) {
    var items = document.querySelectorAll(".glossary-list li");
    var none = document.querySelector(".empty-filter");
    search.addEventListener("input", function () {
      var q = search.value.trim().toLowerCase();
      var shown = 0;
      items.forEach(function (li) {
        var ok = !q || li.dataset.search.indexOf(q) !== -1;
        li.hidden = !ok;
        if (ok) shown++;
      });
      if (none) none.hidden = shown !== 0;
    });
  }

  // 4. Let Escape close a glossary tooltip opened with the keyboard.
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape" && document.activeElement && document.activeElement.classList.contains("term")) {
      document.activeElement.blur();
    }
  });
})();
