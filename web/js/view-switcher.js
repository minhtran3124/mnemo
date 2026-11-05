// Cards and Ledger view switcher. The choice is kept on this device.
(function () {
  var STORAGE_KEY = "mnemo.bookmarks.view";
  var DEFAULT_VIEW = "ledger";
  var CLASSES = { cards: "view-cards", ledger: "view-ledger" };

  function readStored() {
    try {
      var value = window.localStorage.getItem(STORAGE_KEY);
      return CLASSES[value] ? value : DEFAULT_VIEW;
    } catch (e) {
      return DEFAULT_VIEW;
    }
  }

  function store(view) {
    try {
      window.localStorage.setItem(STORAGE_KEY, view);
    } catch (e) {}
  }

  function apply(view) {
    var lists = document.querySelectorAll(".bm-list");
    for (var i = 0; i < lists.length; i++) {
      lists[i].classList.remove(CLASSES.cards, CLASSES.ledger);
      lists[i].classList.add(CLASSES[view]);
    }
    var buttons = document.querySelectorAll(".view-btn");
    for (var j = 0; j < buttons.length; j++) {
      var on = buttons[j].getAttribute("data-view") === view;
      buttons[j].setAttribute("aria-pressed", on ? "true" : "false");
    }
  }

  var buttons = document.querySelectorAll(".view-btn");
  for (var k = 0; k < buttons.length; k++) {
    buttons[k].addEventListener("click", function (event) {
      var view = event.currentTarget.getAttribute("data-view");
      if (!CLASSES[view]) {
        return;
      }
      apply(view);
      store(view);
    });
  }

  apply(readStored());
})();
