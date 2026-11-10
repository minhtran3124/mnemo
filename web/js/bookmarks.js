// Bookmark page clicks. Rows are drawn by the server; this file handles
// opening, moving, undoing and deleting. Text is set with textContent only.
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

  function messageFrom(body, fallback) {
    return (body && body.error && body.error.message) || fallback;
  }

  function readError(response, fallback) {
    return response.json().then(
      function (body) {
        return messageFrom(body, fallback);
      },
      function () {
        return fallback;
      }
    );
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
    var empty = document.getElementById("bm-empty");
    if (empty) {
      empty.hidden = false;
    }
  }

  function onMove(button) {
    var row = button.closest(".bm-row");
    var select = row ? row.querySelector(".bm-move-select") : null;
    if (!select) {
      return;
    }
    clearError();
    button.disabled = true;
    button.textContent = "Moving...";
    function onFailed(message) {
      button.disabled = false;
      button.textContent = "Move";
      showError(message);
    }

    fetch(button.getAttribute("data-move-url"), {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ folder: select.value })
    }).then(function (response) {
      if (!response.ok) {
        return readError(
          response,
          "Could not move this bookmark. Nothing was changed. Try again."
        ).then(onFailed);
      }
      // Reload so the row shows the new folder and its Undo control.
      window.location.reload();
    }, function () {
      onFailed("Could not reach the server. Nothing was changed. Try again.");
    });
  }

  function onUndo(button) {
    clearError();
    button.disabled = true;
    button.textContent = "Undoing...";
    function onFailed(message) {
      button.disabled = false;
      button.textContent = "Undo";
      showError(message);
    }

    fetch(button.getAttribute("data-undo-url"), { method: "POST" }).then(
      function (response) {
        if (!response.ok) {
          return readError(
            response,
            "Could not undo. Nothing was changed. Try again."
          ).then(onFailed);
        }
        window.location.reload();
      },
      function () {
        onFailed("Could not reach the server. Nothing was changed. Try again.");
      }
    );
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
    var move = event.target.closest("button[data-move-url]");
    if (move) {
      onMove(move);
      return;
    }
    var undo = event.target.closest("button[data-undo-url]");
    if (undo) {
      onUndo(undo);
      return;
    }
    var button = event.target.closest("button[data-delete-url]");
    if (button) {
      onDelete(button);
    }
  });
})();
