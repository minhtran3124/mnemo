# Phase 9: MCP Server
Status: Draft v0.1 · Owner: KhoiTran · Phase: 9

Let Claude Code search your bookmarks. MCP (Model Context Protocol) is a standard way for a tool to offer functions to an AI app.

## Goal
F-17.

## You can now
Search your bookmarks from Claude Code.

## Sessions and lessons
3 sessions. Lessons 47-56, 60. Read lesson 57 here (2 minutes).

## Inputs
Phase 4 done (tools and `mnemo/core/store.py`).

## Tasks
1. Write `mcp_server.py` with the Python SDK. It must use `mnemo/core/store.py` only.
2. Add tools `search_bookmarks`, `add_bookmark`, `get_bookmark`.
3. Add a direct resource that lists bookmarks and a templated resource for one bookmark.
4. Add a prompt named `find_related_to_task`.
5. Test each part with the MCP Inspector.
6. Write `mcp_client.py` and use it in the app.
7. Add the server to Claude Code.
8. Private bookmarks (F-19): the server must not return their content to a model without a clear rule. Open question: what rule?

## Done when
- [ ] Inspector tests pass for tools, both resources and the prompt.
- [ ] Claude Code finds a known bookmark by a plain question.
- [ ] The API key is not exposed through the server (NF-01).
- [ ] Wrong inputs give clear errors.

## Risks
Exposing data to another tool; see [privacy and security](../feature-specs/privacy-and-security.md).

## If time runs short
Cut the whole phase (second in cut order); read the lessons only.

## Links to specs
[MCP server](../feature-specs/mcp-server.md) · [storage](../feature-specs/storage.md) · [server API](../feature-specs/server-api.md)
