// Chat page. Sends a message to /api/chat, draws the reply as entries, and
// redraws the saved chat from /api/chat/history. All text is set with
// textContent; nothing from the server or the user is parsed as HTML.
(function () {
  var log = document.getElementById("chat-log");
  var emptyEl = document.getElementById("chat-empty");
  var form = document.getElementById("chat-form");
  var input = document.getElementById("chat-message");
  var saveBtn = document.getElementById("chat-save");
  var statusEl = document.getElementById("chat-status");
  var busy = false;

  var TYPE_LABELS = {
    github_repo: "Code repository",
    article: "Article",
    docs: "Documentation",
    pdf: "PDF book",
    video_page: "Video",
    tool: "Tool",
    image: "Image",
    note: "Note",
    other: "Page"
  };

  // Keep this list in step with STARTER_FOLDERS in config.py. The bookmark
  // page draws its select from config; this page has no server template.
  var STARTER_FOLDERS = ["Work", "Learning", "Reference", "Personal", "Ideas"];
  var UNSORTED = "Unsorted";

  function el(tag, className, text) {
    var node = document.createElement(tag);
    if (className) {
      node.className = className;
    }
    if (text !== undefined && text !== null) {
      node.textContent = text;
    }
    return node;
  }

  function showStatus(message) {
    statusEl.textContent = message;
    statusEl.hidden = !message;
  }

  function hideEmpty() {
    emptyEl.hidden = true;
  }

  function scrollToEnd() {
    window.scrollTo(0, document.body.scrollHeight);
  }

  // Call the API. Resolves with the JSON body; rejects with an Error whose
  // message is readable and whose code is the server's error code, if any.
  function requestJson(path, method, payload) {
    var options = { method: method };
    if (payload !== undefined) {
      options.headers = { "Content-Type": "application/json" };
      options.body = JSON.stringify(payload);
    }
    return fetch(path, options).then(
      function (response) {
        return response.json().then(
          function (body) {
            if (!response.ok) {
              var info = (body && body.error) || {};
              var err = new Error(info.message || "The server could not do that. Try again.");
              err.code = info.code;
              throw err;
            }
            return body;
          },
          function () {
            throw new Error("The server sent an answer I could not read. Try again.");
          }
        );
      },
      function () {
        throw new Error("Could not reach the server. Nothing was saved. Try again.");
      }
    );
  }

  function postJson(path, payload) {
    return requestJson(path, "POST", payload);
  }

  function patchJson(path, payload) {
    return requestJson(path, "PATCH", payload);
  }

  function postNoBody(path) {
    return requestJson(path, "POST");
  }

  function post(message) {
    return postJson("/api/chat", { message: message });
  }

  // Short honest lines for the paste route's error codes (ticket #62). Any
  // other failure gets the generic line; no cause is guessed.
  var PASTE_ERRORS = {
    text_too_short: "That text is too short to read. Paste more of the page.",
    summary_failed: "I could not make a summary from that text. The bookmark is unchanged.",
    already_read: "That bookmark was already read."
  };
  var PASTE_GENERIC = "Something went wrong. Try again.";

  function hostOf(url) {
    try {
      return new URL(url).hostname.replace(/^www\./, "");
    } catch (err) {
      return "";
    }
  }

  var ICON_WARN = [
    "m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3",
    "M12 9v4",
    "M12 17h.01"
  ];

  function warnLabel() {
    var label = el("div", "warn-label");
    var svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    svg.setAttribute("viewBox", "0 0 24 24");
    svg.setAttribute("aria-hidden", "true");
    ICON_WARN.forEach(function (d) {
      var path = document.createElementNS("http://www.w3.org/2000/svg", "path");
      path.setAttribute("d", d);
      svg.appendChild(path);
    });
    label.appendChild(svg);
    label.appendChild(el("span", null, "Page not read"));
    return label;
  }

  function marginColumn(record) {
    var margin = el("div", "entry-margin");
    margin.appendChild(el("span", "entry-filed", "Filed in: " + (record.folder || UNSORTED)));
    margin.appendChild(el("span", "entry-number", "No. " + record.id));
    return margin;
  }

  // Move and Undo stay visible on every card (FO-05). The select lists only
  // existing folders; Undo is enabled after a filing or a Move.
  function cardActions(record, entry) {
    var controls = el("div", "card-actions");
    var id = "move-" + record.id + "-" + Math.random().toString(36).slice(2);
    var label = el("label", "visually-hidden", "Move to folder");
    label.setAttribute("for", id);
    var select = document.createElement("select");
    select.id = id;
    select.className = "card-move-select";
    STARTER_FOLDERS.concat([UNSORTED]).forEach(function (name) {
      var option = document.createElement("option");
      option.value = name;
      option.textContent = name;
      option.selected = name === (record.folder || UNSORTED);
      select.appendChild(option);
    });
    var move = el("button", "btn", "Move");
    move.type = "button";
    var undo = el("button", "btn", "Undo");
    undo.type = "button";
    undo.disabled = !record.prev_folder;
    var note = el("p", "card-note");
    note.hidden = true;

    function setBusy(on) {
      move.disabled = on;
      undo.disabled = on || !record.prev_folder;
      move.textContent = on ? "Moving..." : "Move";
      undo.textContent = on ? "Undoing..." : "Undo";
    }

    function failed(err) {
      setBusy(false);
      note.textContent = err.message;
      note.hidden = false;
    }

    move.addEventListener("click", function () {
      note.hidden = true;
      setBusy(true);
      patchJson("/api/bookmarks/" + record.id, { folder: select.value }).then(
        function (updated) {
          entry.replaceWith(cardFor(updated));
        },
        failed
      );
    });
    undo.addEventListener("click", function () {
      note.hidden = true;
      setBusy(true);
      postNoBody("/api/bookmarks/" + record.id + "/undo").then(
        function (updated) {
          entry.replaceWith(cardFor(updated));
        },
        failed
      );
    });

    controls.appendChild(label);
    controls.appendChild(select);
    controls.appendChild(move);
    controls.appendChild(undo);
    controls.appendChild(note);
    return controls;
  }

  // A saved bookmark with a summary.
  function savedCard(record) {
    var entry = el("article", "entry");
    entry.appendChild(marginColumn(record));
    var main = el("div", "entry-main");
    var host = hostOf(record.url);
    var kind = TYPE_LABELS[record.type] || "Page";
    main.appendChild(el("p", "entry-type", host ? kind + " on " + host : kind));
    main.appendChild(el("h2", "entry-title", record.title || record.url));
    if (record.summary) {
      main.appendChild(el("p", "entry-summary", record.summary));
    }
    if (Array.isArray(record.tags) && record.tags.length) {
      main.appendChild(el("p", "entry-tags", record.tags.slice(0, 3).join(", ")));
    }
    if (record.reason) {
      var why = el("p", "entry-reason");
      why.appendChild(el("strong", null, "Why you saved it:"));
      why.appendChild(document.createTextNode(" " + record.reason + " "));
      if (record.reason_source === "guess") {
        why.appendChild(el("span", "flag", "guess"));
      }
      main.appendChild(why);
    }
    main.appendChild(cardActions(record, entry));
    entry.appendChild(main);
    return entry;
  }

  // A link that was not saved at all: no bookmark id, so nothing to paste into.
  function failedCard(url) {
    var entry = el("article", "entry");
    var main = el("div", "entry-main");
    main.appendChild(el("h2", "entry-title", "I could not save this link."));
    main.appendChild(el("p", "entry-url", url));
    entry.appendChild(main);
    return entry;
  }

  // A saved link without a summary. The link stays, nothing is invented about
  // the page, and the user can paste the text into this same bookmark.
  function pageNotReadCard(record) {
    var entry = el("article", "entry");
    entry.appendChild(marginColumn(record));
    var main = el("div", "entry-main");
    main.appendChild(warnLabel());
    main.appendChild(el("h2", "entry-title", "I could not read this page. I saved the link only."));
    main.appendChild(el("p", "entry-url", record.url));
    main.appendChild(
      el(
        "p",
        "entry-summary",
        "I have no summary and I will not guess what is on it. Paste the text of the page and I will make the entry."
      )
    );

    var buttons = el("div", "btn-row");
    var open = el("button", "btn btn-primary", "Paste the text");
    open.type = "button";
    open.setAttribute("aria-expanded", "false");
    buttons.appendChild(open);
    main.appendChild(buttons);

    var box = el("div", "paste-box");
    box.hidden = true;
    var id = "paste-" + Math.random().toString(36).slice(2);
    var label = el("label", null, "Text of the page");
    label.setAttribute("for", id);
    var area = document.createElement("textarea");
    area.id = id;
    area.rows = 6;
    var send = el("button", "btn btn-primary", "Save");
    send.type = "button";
    var row = el("div", "btn-row");
    row.appendChild(send);
    box.appendChild(label);
    box.appendChild(area);
    box.appendChild(row);
    main.appendChild(box);
    var note = el("p", "entry-reason");
    note.hidden = true;
    main.appendChild(note);

    open.addEventListener("click", function () {
      box.hidden = !box.hidden;
      open.setAttribute("aria-expanded", String(!box.hidden));
      if (!box.hidden) {
        area.focus();
      }
    });
    send.addEventListener("click", function () {
      var text = area.value.trim();
      if (!text) {
        note.textContent = "Paste the text first.";
        note.hidden = false;
        area.focus();
        return;
      }
      note.hidden = true;
      send.disabled = true;
      send.textContent = "Saving...";
      postJson("/api/bookmarks/" + record.id + "/paste", { text: text }).then(
        function (updated) {
          entry.replaceWith(cardFor(updated));
        },
        function (err) {
          send.disabled = false;
          send.textContent = "Save";
          note.textContent = PASTE_ERRORS[err.code] || PASTE_GENERIC;
          note.hidden = false;
        }
      );
    });

    main.appendChild(cardActions(record, entry));
    entry.appendChild(main);
    return entry;
  }

  function deletedEntry(record) {
    return el("p", "app-line", "Bookmark " + record.id + " was deleted.");
  }

  // The one card builder for a stored or returned record.
  function cardFor(record) {
    if (record.deleted) {
      return deletedEntry(record);
    }
    if (record.page_status && record.page_status !== "ok") {
      return pageNotReadCard(record);
    }
    return savedCard(record);
  }

  // Nodes for a list of records plus links that were not saved. The live reply
  // and the redrawn history both use this.
  function cardNodes(cards, failed) {
    var nodes = (cards || []).map(cardFor);
    (failed || []).forEach(function (url) {
      nodes.push(failedCard(url));
    });
    return nodes;
  }

  // Nodes for one /api/chat answer.
  function replyNodes(body) {
    if (body.kind === "cards") {
      return cardNodes(body.cards, body.failed);
    }
    return [el("p", "app-line", body.text || "")];
  }

  function appendUser(text) {
    log.appendChild(el("div", "user-msg", text));
  }

  function setBusy(on) {
    busy = on;
    saveBtn.disabled = on;
    saveBtn.textContent = on ? "Saving..." : "Save";
  }

  function onSubmit(event) {
    event.preventDefault();
    var message = input.value.trim();
    if (busy || historyPending || !message) {
      return;
    }
    showStatus("");
    setBusy(true);
    post(message).then(
      function (body) {
        hideEmpty();
        appendUser(message);
        replyNodes(body).forEach(function (node) {
          log.appendChild(node);
        });
        input.value = "";
        setBusy(false);
        scrollToEnd();
      },
      function (err) {
        showStatus(err.message);
        setBusy(false);
      }
    );
  }

  // Redraw the saved chat. A message with cards draws them; a bookmark that was
  // deleted since is {id, deleted: true}.
  function drawHistory(messages) {
    messages.forEach(function (message) {
      if (message.role === "user") {
        appendUser(message.text || "");
        return;
      }
      var cards = message.cards || [];
      if (!cards.length && !(message.failed || []).length) {
        log.appendChild(el("p", "app-line", message.text || ""));
        return;
      }
      cardNodes(cards, message.failed).forEach(function (node) {
        log.appendChild(node);
      });
      // The summary line keeps a partial failure visible after a reload.
      if (message.text) {
        log.appendChild(el("p", "app-line", message.text));
      }
    });
  }

  // Sending waits until the saved chat is drawn, so the log never shows a new
  // exchange out of order or twice.
  var historyPending = false;

  function endHistory() {
    historyPending = false;
    saveBtn.disabled = busy;
  }

  function loadHistory() {
    historyPending = true;
    saveBtn.disabled = true;
    fetch("/api/chat/history")
      .then(function (response) {
        if (!response.ok) {
          throw new Error("history");
        }
        return response.json();
      })
      .then(function (body) {
        var messages = (body && body.messages) || [];
        if (!messages.length) {
          emptyEl.hidden = false;
          return;
        }
        drawHistory(messages);
        scrollToEnd();
      })
      .catch(function () {
        emptyEl.hidden = false;
        showStatus("Could not load your earlier chat. You can still paste a link.");
      })
      .then(endHistory);
  }

  form.addEventListener("submit", onSubmit);
  input.addEventListener("keydown", function (event) {
    if (event.key === "Enter" && !event.shiftKey && !event.isComposing) {
      event.preventDefault();
      form.requestSubmit();
    }
  });
  loadHistory();
})();
