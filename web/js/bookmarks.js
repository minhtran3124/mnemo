// Bookmark page clicks. Rows are drawn by the server; this file only handles
// opening a link and deleting. Text is set with textContent only.
(function () {
  var statusEl = document.getElementById("bm-status");

  function showError(message) {
    statusEl.textContent = message;
    statusEl.hidden = false;
  }

  function clearError() {
    statusEl.textContent = "";
    statusEl.hidden = true;
  }

  function onOpen(link) {
    // Log the open without blocking the new tab. Failure must not stop the link.
    fetch(link.getAttribute("data-open-url"), { method: "POST", keepalive: true }).catch(
      function () {}
    );
  }

  function refreshAfterDelete() {
    var banner = document.getElementById("bm-banner");
    if (banner && !document.querySelector(".bm-row[data-unreadable]")) {
      banner.remove();
    }
    if (document.querySelector(".bm-row")) {
      return;
    }
    // No rows left: drop the folder line and show the empty message.
    var folder = document.getElementById("bm-folder");
    if (folder) {
      folder.remove();
    }
    var empty = document.getElementById("bm-empty");
    if (empty) {
      empty.hidden = false;
    }
  }

  function onDelete(button) {
    var row = button.closest(".bm-row");
    if (!window.confirm(button.getAttribute("data-confirm"))) {
      return;
    }
    clearError();
    button.disabled = true;
    button.textContent = "Deleting...";
    function onFailed() {
      button.disabled = false;
      button.textContent = "Delete";
      showError("Could not delete this bookmark. Nothing was changed. Try again.");
    }

    // Two-argument then: only the request itself can reach onFailed. A fault in
    // the page cleanup after a delete that worked must not report a failure.
    fetch(button.getAttribute("data-delete-url"), { method: "DELETE" }).then(function (response) {
      if (!response.ok) {
        onFailed();
        return;
      }
      var group = row.closest(".bm-group");
      row.remove();
      if (group && !group.querySelector(".bm-row")) {
        group.remove();
      }
      refreshAfterDelete();
    }, onFailed);
  }

  document.addEventListener("click", function (event) {
    var link = event.target.closest("a[data-open-url]");
    if (link) {
      onOpen(link);
      return;
    }
    var button = event.target.closest("button[data-delete-url]");
    if (button) {
      onDelete(button);
    }
  });
})();
