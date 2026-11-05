// Theme control. Loaded in <head> without defer so the saved choice is applied before first paint.
// System means no data-theme attribute. Light and Dark set it. The choice is kept in localStorage.
(function () {
  var KEY = "mnemo-theme";
  var root = document.documentElement;

  function read() {
    try {
      var value = window.localStorage.getItem(KEY);
      return value === "light" || value === "dark" ? value : "system";
    } catch (e) {
      return "system";
    }
  }

  function apply(choice) {
    if (choice === "light" || choice === "dark") {
      root.setAttribute("data-theme", choice);
    } else {
      root.removeAttribute("data-theme");
    }
  }

  function save(choice) {
    try {
      if (choice === "system") {
        window.localStorage.removeItem(KEY);
      } else {
        window.localStorage.setItem(KEY, choice);
      }
    } catch (e) {
      // Storage is unreadable. The choice still applies for this page view.
    }
  }

  function show(choice) {
    var items = document.querySelectorAll("[data-theme-choice]");
    for (var i = 0; i < items.length; i++) {
      var on = items[i].getAttribute("data-theme-choice") === choice;
      if (items[i].type === "radio") {
        items[i].checked = on;
      } else {
        items[i].setAttribute("aria-pressed", on ? "true" : "false");
      }
    }
  }

  apply(read());

  document.addEventListener("DOMContentLoaded", function () {
    show(read());
    document.addEventListener("click", function (event) {
      var item = event.target.closest ? event.target.closest("[data-theme-choice]") : null;
      if (!item) {
        return;
      }
      var choice = item.getAttribute("data-theme-choice");
      apply(choice);
      save(choice);
      show(choice);
    });
  });
})();
