# Credits and licences

Every font and asset used on the KINETIQ website, with its source and licence.
Nothing is added to the repo without an entry here.

## Fonts
| Font | Source | Licence | Used for |
| --- | --- | --- | --- |
| Archivo (variable, weight and width axes) | Google Fonts, by Omnibus-Type; self-hosted at build time by `next/font` (no font files in the repo) | SIL Open Font License 1.1 | Headlines, body, wordmark |
| Saira (variable weight) | Google Fonts, by Omnibus-Type; self-hosted at build time by `next/font` | SIL Open Font License 1.1 | Data labels, numerals, captions |

## Images and graphics
| File | Source | Licence | Notes |
| --- | --- | --- | --- |
| Product stills (`public/stills/K01` to `K15`, with `K03b` and the `og.jpg` crop, AVIF and WebP; K15's planet, atmosphere and stars are composited in code by `render/shots/K15-space.py`) | Rendered for this repo in Blender 4.2 Cycles from a procedural model of `src/lib/racket-shape.ts`; procedural carbon weave textures generated in code | Owned by KINETIQ | 16-bit masters are kept outside the repo and exported with `scripts/stills.mjs` |
| Data graphics G01 to G15 (`src/components/graphics/`) | Drawn in code (SVG and canvas) for this repo | Owned by KINETIQ | Values marked "Illustrative" are not yet measured. |
| Swiss cross (Born whole lockup, badges, measurement card) | Drawn in code (national emblem geometry) | Public symbol; commercial use is governed by the Swiss Coat of Arms Protection Act | |
| Weave swatches on /reserve | Drawn in code (SVG patterns) | Owned by KINETIQ | |
| Site icon (`src/app/icon.svg`, `src/app/apple-icon.png`) | Drawn for this repo as SVG paths (the Q, the company mark, over an amber light line; no font); the PNG is rendered from it with sharp | Owned by KINETIQ | Shown on the NDA gate too: it carries no product image or claim |
| Sealed-core trace over K03 (`src/components/graphics/SealedCoreTrace.tsx`) | Drawn in code (SVG) for this repo, over the K03 still | Owned by KINETIQ | |

## Not cleared
- Assets from https://kinetiq-review.vercel.app (made by Erik): not imported. They need written
  permission or a licence before they can be added here.

## Code and reference material
| Item | Source | Licence |
| --- | --- | --- |
| GSAP skills (`.claude/skills/gsap-*`) | github.com/greensock/gsap-skills | MIT (copy in each folder) |
| Emil Kowalski skills (`.claude/skills/emil-design-eng`, `animation-performance`) | github.com/emilkowalski/skill | MIT (copy in each folder) |
| Frontend design notes (`.claude/skills/frontend-design-notes`) | Our own summary of anthropics/claude-code's frontend-design skill | Original not redistributed (all rights reserved) |
| npm dependencies | See `package.json` | Each package's own licence |
