# Credits and licences

Every font and asset used on the KINETIQ website, with its source and licence.
Nothing is added to the repo without an entry here.

## Fonts
| Font | Source | Licence | Used for |
| --- | --- | --- | --- |
| Archivo (variable, weight and width axes) | Google Fonts, by Omnibus-Type; self-hosted at build time by `next/font` (no font files in the repo) | SIL Open Font License 1.1 | All text; display at width 125 |

## Images and graphics
| File | Source | Licence | Notes |
| --- | --- | --- | --- |
| Racket still (`src/components/RacketSvg.tsx`, inline SVG) | Drawn in code for this repo from `src/lib/racket-shape.ts` | Owned by KINETIQ | Hero image before 3D loads, and with motion off |
| Swiss flag (`src/components/sections/Swiss.tsx`, inline SVG) | Drawn in code (national emblem geometry) | Public symbol; use is governed by the Swiss Coat of Arms Protection Act, see CLAIMS.md #4 | Swiss section |
| Layer stack, hole rings, vibration waves | CSS and inline SVG drawn for this repo | Owned by KINETIQ | Chapters |

## 3D models and textures
| File | Source | Licence | Notes |
| --- | --- | --- | --- |
| Racket model | Generated in code (`src/components/three/RacketModel.tsx`) from `src/lib/racket-shape.ts`; carbon weave texture drawn on a canvas at runtime | Owned by KINETIQ | Hero |
| Studio lighting | drei `Lightformer`s rendered locally; no HDR files downloaded | n/a | Hero |

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
