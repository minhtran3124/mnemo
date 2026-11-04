---
paths:
  - "**/*.{html,css,js,mjs,ts,tsx,jsx,vue,svelte}"
  - "**/templates/**"
  - "**/static/**"
---

# Frontend rules

## Markup
- Semantic HTML first: `button` for actions, `a` for navigation, `form` with real `label`s for inputs, landmarks (`header`, `nav`, `main`). No clickable `div`s.
- Every image has `alt` (empty for decorative). Every icon-only control has an accessible name.
- Use ARIA only when native HTML cannot express the role or state.

## Behavior
- The page holds no secrets. Every privileged action goes through the server.
- Treat all server and user content as untrusted: insert it as text (`textContent`, framework escaping), never with `innerHTML` or unescaped template output.
- Every async action shows a pending state, disables double submit, and handles failure with a visible message. A failed request never leaves a blank or frozen screen.
- Destructive actions ask for confirmation or offer undo.
- Keep state in one place per screen. The URL reflects what a user would want to bookmark or share (filters, view, selected item).

## Styling
- Styles reference design tokens (CSS custom properties). No raw colour values in component rules.
- Mobile first. Layout uses flex/grid; no fixed widths that cause horizontal scroll on a 390px viewport.
- Theme switching uses an attribute on the root element and sets `color-scheme`. Apply the saved theme before first paint to avoid a flash.

## Performance
- Ship as little JavaScript as the page needs. No framework for a page that works as HTML plus a little JS.
- Self-host or preload fonts with `font-display: swap` and a fallback stack.
- Lazy-load below-the-fold images; give every image width and height to avoid layout shift.

## Quality checks
- Keyboard only: every control reachable with Tab, focus visible, Escape closes overlays, focus returns where it came from.
- Check each screen at 390px and at laptop width, in light and dark themes, before calling it done.
- Test empty, loading, error and long-content states, not only the happy path.
