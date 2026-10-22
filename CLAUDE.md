# KINETIQ website: working rules

Award-level, animation-heavy marketing site for KINETIQ padel rackets. Solo, public repo.
**Before any interface or animation work, read this file and `DESIGN.md`.** Next.js 16 differs from
older versions: read `AGENTS.md` and the guide in `node_modules/next/dist/docs/` before using an API.

## Repo rules
- Public repo. Never commit secrets, `.env*` files, paid fonts, or any asset without an open licence.
  Every font and asset goes in `public/CREDITS.md` with its source and licence, in the same commit.
- Assets on kinetiq-review.vercel.app (made by Erik) are not cleared for reuse. Import one only after
  its licence is recorded in `public/CREDITS.md`.
- Commit straight to `main`. Pushing to `main` deploys production on Vercel.
- No extra animation or UI libraries (Motion/Framer Motion, shadcn, 21st.dev, other kits) unless the
  brief asks. Our stack covers it. Where a skill suggests Motion's `useSpring`, use `gsap.quickTo`.
- Pin exact versions (`.npmrc` has `save-exact=true`).

## Stack
Next.js 16 (App Router, TypeScript, Turbopack) · React 19 · GSAP 3 + ScrollTrigger + `@gsap/react` ·
Lenis · Playwright (dev only). No real-time 3D: product imagery is Blender stills (see Stills and graphics).

## Scripts
- `npm run dev`: local dev server.
- `npm run build` / `npm start`: production build and server.
- `npm run lint`, `npm run typecheck`.
- `npm run check`: the check harness (see Definition of done). `--skip-build`, `--url=<url>`,
  `--study` (reference mode), `--only=phone|desktop|wide`, `--mode=motion|reduced`, `--verbose`,
  `--path=/reserve` (any page; run it for `/` and `/reserve`).
  Output goes to `.checks/<label>/` (git-ignored). Uses a free port per run.
- `node scripts/stills.mjs <masters dir> [id ...]`: export Blender masters to `public/stills/` (AVIF + WebP).
- Vercel installs with `PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1 npm ci` (`vercel.json`), so builds never
  download browsers. Locally: `npx playwright install chromium` once.

## Folders
- `src/app/`: routes, `layout.tsx` (motion init script, providers), `globals.css`.
- `src/components/motion/`: `MotionProvider` (reduced-motion state), `SmoothScroll` (Lenis), `PinnedChapter`.
- `src/components/landing/`: one component + CSS module per landing section; `Reveal` and `Scrub` helpers.
- `src/components/graphics/`: data graphics G01–G13 (SVG/canvas), each with a review page at `/lab/<id>` (dev only;
  `KQ_LAB=1` serves them in production).
- `src/components/media/Still.tsx`: product stills with phone art direction. `src/components/reserve/`: /reserve.
- `src/components/chrome/`: header (compact Reserve Now after the hero), footer. No preview banner (owner, 2026-10-22).
- `src/lib/gsap.ts`: the only place GSAP plugins are registered. Import gsap from here.
- `src/content/`: all words. `copy.ts` (landing), `lineup.ts` (editions, prices, limits, ambassador gate,
  delivery countries), `reserve.ts`, `site.ts` (CTA labels, ship date, refund, feels). Change words there.
- Flow (Tesla Roadster reserve page): landing page with one CTA, "Reserve Now" → `/reserve?tier=` (edition,
  feel, trust lines, Due Today, "Pay with Card" expands the form in place) → "Place Reservation" posts to
  `src/app/api/reserve/route.ts` (PaymentIntent via REST, amount from `lineup.ts`) and confirms the card
  with Stripe's Payment Element in place → confirmation in place, or `/reserved` after 3-D Secure.
- Data minimisation: name, email, delivery address and card only. No phone, accounts or opt-ins.
- `public/`: static assets and `CREDITS.md`. `scripts/`: harness. `docs/`: research notes.
- `.claude/skills/`: saved reference skills (GSAP, Emil Kowalski, our frontend-design notes).

## Interface micro-animations (Emil Kowalski's rules)
- Animate `transform` and `opacity` only. Never `transition: all`.
- 150–300 ms. Ease-out by default with custom curves (`--ease-out`, `--ease-in-out` in globals.css).
  Never ease-in for UI.
- No animation on keyboard-triggered actions (skip links, shortcuts, focus moves): jump instantly.
- Nothing scales from 0: start at `scale(0.95)` or more, with opacity.
- Pressables get `scale(0.97)` on `:active`. Hover effects only behind
  `@media (hover: hover) and (pointer: fine)`.
- Exit faster than enter. Stagger 30–80 ms. Use transitions, not keyframes, for interruptible UI.
- `will-change` only after you see a 1px shift or measured dropped frames, on the animating element.

## Scroll storytelling
- GSAP ScrollTrigger (`pin`, `scrub`) inside `useGSAP` with a `scope` ref. Cleanup is automatic;
  anything made later in handlers goes through `contextSafe`.
- Wrap setups in `gsap.matchMedia()`; return `mm.revert()`. Put ScrollTrigger on the timeline, never on
  a child tween. Create triggers top to bottom, or set `refreshPriority`.
- Call `ScrollTrigger.refresh()` after fonts, images or late content change layout.
- Lenis smooth scrolling on desktop only (fine pointer, ≥1024 px), driven by `gsap.ticker` and wired to
  `ScrollTrigger.update` (`SmoothScroll.tsx`). Never add ScrollSmoother as well.
- Every pinned sequence has a visible Skip link inside the pinned stage. It jumps instantly to the next
  section and moves focus there (target has `tabIndex={-1}`). See `motion/PinnedChapter.tsx`.
- Cross-fades in scrubbed sequences must not overlap: two half-faded headings are unreadable.

## Motion safety
- No motion toggle (owner, 2026-10-21). `html[data-motion="on|off"]` follows `prefers-reduced-motion` only,
  set before first paint by the inline script in `layout.tsx`.
- Reduced motion means: no pins, no scrub, no Lenis, CSS durations forced to 0. Every section must still
  read correctly, in order, with all its content visible. Server render shows the final state.
- Read the state with `useMotion()`; pass `motionOn` as a `useGSAP` dependency with `revertOnUpdate: true`.
- Pinned chapters pin only at ≥ 900 px (`PIN_MEDIA`); their beats layer via `.pin-layered` in globals.css.
  The pin is CSS `position: sticky` in a section sized `(1 + --pin-len) × 100svh`; ScrollTrigger only scrubs.
  Never use ScrollTrigger `pin: true`: its switch to `position: fixed` measured as CLS ≈ 1.0.

## Stills and graphics
- Product imagery = own Blender Cycles stills (no people, no other brands, no autographs). Masters are 16-bit
  PNG, not committed; `scripts/stills.mjs` dithers and exports AVIF + WebP crops listed in `stills.json`.
- `<Still>` renders nothing for a still that has not been exported, so a section must still read without it.
- Graphics are SVG or canvas, drawn from `racket-shape.ts`. Text in them stays ≥ 15 px at 390 px wide.
  Canvas loops cap at 30 fps, pause off-screen and when hidden, DPR ≤ 2. Unmeasured data says "Illustrative".

## Performance budget (phone profile: 4× CPU, 150 ms RTT, 1.6 Mbps)
- LCP ≤ 2.5 s, CLS ≤ 0.1, INP ≤ 200 ms, no dropped frames while scrolling.
- The LCP element is the hero still or the h1. Keep hero JavaScript small; graphics load with their sections.
- Fonts with `next/font` (self-hosted at build), `display: swap`, subsets for every brief language.

## Accessibility
- Semantic HTML, one `h1`, landmarks, real buttons and links.
- Visible focus (`:focus-visible` outline), full keyboard use, logical tab order.
- WCAG AA contrast (4.5:1 body, 3:1 large text and UI). Check new colour tokens.
- No scroll traps: pins always end, Skip links work, no hijacked keys.
- Decorative canvases get `aria-hidden`; fallbacks get real `alt` text.

## Content and claims
- No placeholder text in a finished build.
- Every claim is listed in `CLAIMS.md`. A new claim gets a row there in the same commit.
- Launch gate: `NEXT_PUBLIC_LAUNCHED=true` (removes noindex) only when CLAIMS.md is cleared. Unverified claims
  stay off the live domain until then; the site shows no preview banner (owner: not appropriate).
- Stripe: `STRIPE_SECRET_KEY`, `NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY`, `INVITE_CODES` (see `.env.example`).
  Server and Stripe.js are pinned to API version `2026-09-30.endive` (`allowed_payment_method_types`).
  Without keys, /reserve runs in preview (Place Reservation disabled). Invite Only fails closed without codes.
- Hero lead is the owner's own sentence (2026-10-22); keep it verbatim, even while "one piece" is retired as a
  marketing phrase elsewhere: "One single piece of space-grade carbon. No tube, no joints. Ultra-precision
  moulded to 15 microns and 1 gram. Every racket plays exactly the same."
- One landing CTA label: "Reserve Now" (`site.ctaLabel`); then "Pay with Card" and "Place Reservation".
- An edition that sells out: set `available: false` in `lineup.ts` (shows "Sold out", blocks payment).
- The ambassador (Invite Only extras) stays neutral until `ambassador.confirmed` is true (`lineup.ts`).
- Fonts must cover every language listed in `DESIGN.md`.

## Definition of done
1. `npm run lint`, `npm run typecheck` and `npm run build` pass.
2. `npm run check` passes for `/` and `--path=/reserve`: phone, desktop and wide (2560), motion and reduced
   motion, 0 console errors, no blank frames, the fill rule, no horizontal overflow, budgets met, Skip link works.
3. You have opened and reviewed the screenshots yourself: fix anything blank, overlapping, cropped or
   unreadable, then rerun.
4. After pushing, run `npm run check -- --url=<production url>` (and `--path=/reserve`) on the live site.

## Notes
- Long-frame counts from headless runs are a smoke signal, not a device measurement.
- The harness launches Chromium with `--disable-gpu-compositing` (it stalled captures after WebGL frames).
- The harness scrolls natively (`window.scrollTo`); Lenis follows native scroll events.
- Stale servers: never `pkill -f "next start"` (it matches your own shell and kills it). Kill by
  process name: `for d in /proc/[0-9]*; do [ "$(cat $d/comm)" = "next-server (v1" ] && kill ${d#/proc/}; done`.
- Production URL: https://kinetiq-seven-neon.vercel.app (Vercel team EVHG, project `kinetiq`).
- `docs/reference-notes.md`: study of lighthouse.storage/token (techniques only, nothing copied).
- `docs/agent-learnings.md`: what failed while agents built the site, and why. In short: detach long jobs that
  must outlive a subagent (`setsid nohup`, progress in a file), kill by PID and never by command-line text,
  no foreground `sleep`, one Blender render at a time (`flock`), one writer per file set in a shared tree.
- `docs/research/non-tubular.md`: construction terms ("no frame tube", not "tubeless") and factory questions.
- Never name the factory, its town, its patents or its other customers in the public repo or on the site.
