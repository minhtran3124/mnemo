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

  // Ask the server. Resolves with the JSON body; rejects with a readable message.
  function post(message, pastedText) {
    var payload = { message: message };
    if (pastedText) {
      payload.pasted_text = pastedText;
    }
    return fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    }).then(
      function (response) {
        return response.json().then(
          function (body) {
            if (!response.ok) {
              var text = body && body.error && body.error.message;
              throw new Error(text || "The server could not do that. Try again.");
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
    margin.appendChild(el("span", null, "Filed in"));
    margin.appendChild(el("span", "entry-folder", record.folder || "Unsorted"));
    margin.appendChild(el("span", "entry-number", "No. " + record.id));
    return margin;
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
    entry.appendChild(main);
    return entry;
  }

  // A link that was saved without a summary, or not saved at all. The link
  // stays, nothing is invented about the page, and the user can paste the text.
  function pageNotReadCard(url, record, title) {
    var entry = el("article", "entry");
    if (record) {
      entry.appendChild(marginColumn(record));
    }
    var main = el("div", "entry-main");
    main.appendChild(warnLabel());
    main.appendChild(
      el("h2", "entry-title", title || "I could not read this page. I saved the link only.")
    );
    main.appendChild(el("p", "entry-url", url));
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
      // The pasted text goes to the first link of a message, so resend this
      // link alone.
      post(url, text).then(
        function (body) {
          var first = body.kind === "cards" && body.cards && body.cards[0];
          if (!first || (first.page_status && first.page_status !== "ok")) {
            // Still not readable (the text was too short): keep this card and
            // its box, say why, and let the user paste more.
            send.disabled = false;
            send.textContent = "Save";
            note.textContent =
              "That text was too short to make an entry. Paste more of the page and try again.";
            note.hidden = false;
            area.focus();
            return;
          }
          entry.replaceWith.apply(entry, replyNodes(body));
        },
        function (err) {
          send.disabled = false;
          send.textContent = "Save";
          note.textContent = err.message;
          note.hidden = false;
        }
      );
    });

    entry.appendChild(main);
    return entry;
  }

  function deletedEntry(record) {
    return el("p", "app-line", "Bookmark " + record.id + " was deleted.");
  }

  function recordNode(record) {
    if (record.deleted) {
      return deletedEntry(record);
    }
    if (record.page_status && record.page_status !== "ok") {
      return pageNotReadCard(record.url, record);
    }
    return savedCard(record);
  }

  // Nodes for one /api/chat answer.
  function replyNodes(body) {
    var nodes = [];
    if (body.kind === "cards") {
      (body.cards || []).forEach(function (record) {
        nodes.push(recordNode(record));
      });
      (body.failed || []).forEach(function (url) {
        nodes.push(pageNotReadCard(url, null, "I could not save this link."));
      });
    } else {
      nodes.push(el("p", "app-line", body.text || ""));
    }
    return nodes;
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
    if (busy || !message) {
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
      if (!cards.length) {
        log.appendChild(el("p", "app-line", message.text || ""));
        return;
      }
      cards.forEach(function (record) {
        log.appendChild(recordNode(record));
      });
    });
  }

  function loadHistory() {
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
      });
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
