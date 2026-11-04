---
paths:
  - "**/*.{html,css,scss,tsx,jsx,vue,svelte}"
  - "**/templates/**"
  - "PRODUCT.md"
  - "DESIGN.md"
---

# Design rules (UI and UX)

## Source of truth
- Read `PRODUCT.md` and `DESIGN.md` (when present) before UI work. Follow the established visual direction; do not introduce a new palette, font or component style without updating the design record.
- Every colour, font, size, radius, shadow and spacing value comes from a token. Add a token before using a new value.

## Accessibility (WCAG 2.2 AA)
- Text contrast at least 4.5:1 (3:1 for large text and for control borders and focus indicators), in every theme.
- Touch targets at least 44 by 44 CSS pixels.
- Focus is always visible and never removed without a replacement.
- Colour is never the only signal of state. Pair it with text or an icon.
- Respect `prefers-reduced-motion` and `prefers-color-scheme`.

## Layout and type
- Use a fixed spacing scale and a type scale; no one-off values.
- Limit line length for reading text to about 60 to 75 characters.
- Long titles, names and URLs wrap or truncate with a way to see the full value. Test with real, messy content, not placeholder text.

## States
- Design every state, not just the filled one: empty, loading, success, error, partial, and overflow.
- Empty states say what to do next. Error states say what happened and what the user can do, in plain words.
- Show uncertainty honestly. Content the system generated or guessed is labelled so the user can tell it from their own input.

## Interaction
- One primary action per view. Secondary actions are visually quieter.
- Feedback within 100ms for any action; show progress for anything slower than a second.
- Reversible actions get Undo; irreversible ones get a confirmation that names what will be lost.

## Copy
- Short, plain, specific words. Labels name the action ("Save link"), not the mechanism ("Submit").
- Use the same term for the same thing everywhere.

## Avoid
- Decorative gradients, glows, glassmorphism and stock "AI" styling that lower contrast or add noise.
- Placeholder-as-label inputs, hover-only controls, and icon-only buttons without a text label or tooltip.
