# KINETIQ website: working rules

Award-level, animation-heavy marketing site for KINETIQ padel rackets. Solo, public repo. **Before any interface or
animation work, read this file and `DESIGN.md`.** Next.js 16 differs from older versions: read `AGENTS.md` and the
guide in `node_modules/next/dist/docs/` before using an API. Stack: Next.js 16 (App Router, TypeScript, Turbopack) ·
React 19 · GSAP 3 + ScrollTrigger + `@gsap/react` · Lenis · Playwright (dev only). No real-time 3D: Blender stills.

## Repo rules
- Public repo. Never commit secrets, `.env*` files, paid fonts, or any asset without an open licence.
  Every font and asset goes in `public/CREDITS.md` with its source and licence, in the same commit.
- Assets on kinetiq-review.vercel.app (made by Erik) are not cleared for reuse until their licence is in `CREDITS.md`.
- Commit straight to `main`; pushing to `main` deploys production on Vercel. Pin exact versions (`save-exact`).
- No extra animation or UI libraries (Motion/Framer Motion, shadcn, 21st.dev, other kits) unless the
  brief asks. Our stack covers it. Where a skill suggests Motion's `useSpring`, use `gsap.quickTo`.

## Scripts
- `npm run dev` (local), `npm run build` / `npm start` (production), `npm run lint`, `npm run typecheck`.
- `npm run check`: the check harness (see Definition of done). `--skip-build`, `--url=<url>`, `--study` (reference
  mode), `--only=phone|desktop|wide`, `--mode=motion|reduced`, `--verbose`, `--path=/reserve` (any page; run it for
  `/` and `/reserve`), `--gate` (the NDA gate, without the cookie). Output in `.checks/<label>/`; a free port per run.
- `node scripts/stills.mjs <masters dir> [id ...]`: export Blender masters to `public/stills/` (AVIF + WebP).
- Vercel runs `PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1 npm ci` (no browsers); locally `npx playwright install chromium`.

## Folders
- `src/app/`: routes, `layout.tsx` (motion init script, providers), `globals.css`. `src/lib/gsap.ts` is the only place
  GSAP plugins are registered: import gsap from there. `src/lib/racket-shape.ts`: the racket (Stills and graphics).
- `src/components/`: `motion/` (`MotionProvider`, `SmoothScroll` for Lenis, `PinnedChapter`), `landing/` (a component
  and CSS module per section; `Reveal`, `Scrub`), `graphics/` (G01–G15, each with a review page at `/lab/<id>`, dev
  only; `KQ_LAB=1` serves them in production), `media/Still.tsx`, `reserve/`, `chrome/` (`SiteHeader`, `SiteFooter`;
  `HeaderClient.tsx`: scroll state and the compact Reserve Now after the hero, its label passed in). No preview banner.
- `src/content/`: all words; change them there. `copy.ts` (landing), `lineup.ts` (editions, prices, limits, `lifetime`,
  `identicalFine`, `sampleSet`, the coach, invitation gate, delivery countries), `reserve.ts`, `site.ts` (CTA labels,
  price note, ship date, refund, feels), `stills.json` (crops).
- Flow (Tesla Roadster reserve page): "Reserve Now" → `/reserve?tier=` (edition, feel, trust lines, Due Today, "Pay
  with Card" expands the form in place) → "Place Reservation" posts to `src/app/api/reserve/route.ts` (PaymentIntent
  via REST, amount from `lineup.ts`) and confirms the card with Stripe's Payment Element in place → confirmation in
  place, or `/reserved` after 3-D Secure. One of Ten: never chosen from a link (`?tier=invite` shows KINETIQ), never
  interactive until a valid code (POST /api/invite, or `?invite=CODE`) unlocks it; /api/reserve checks it again.
- Data minimisation: name, email, delivery address and card only. No phone, accounts or opt-ins.
- `public/`: assets and `CREDITS.md`. `scripts/`: harness. `docs/`: research. `.claude/skills/`: reference skills.

## NDA gate (owner, 2026-10-22: investors declare the NDA, then give an email, once per device)
- `src/proxy.ts` (Next 16 "proxy", formerly middleware) rewrites every page to `/nda` without a valid `kq_nda` cookie
  (`src/lib/nda.ts`) and answers assets, `/api/*` and other `/_next/*` paths with an empty 403; only `/_next/static/`,
  the HMR socket, the two icon files and `POST /api/nda` pass. Exclusions, cookie and arrival: DESIGN.md "NDA gate".
- A declaration, not a login (unsigned cookie, public format; CLAIMS.md row 25b). Nothing is stored or logged.
- The root layout's metadata is neutral (title "KINETIQ", noindex): the product's title, description and og:image live
  in `src/lib/product-metadata.ts`, used by `/` and `/reserve` only. Never put product metadata back in `layout.tsx`.
- Stills are `Cache-Control: private` with `Vary: Cookie` (`next.config.ts`). After each deploy, check production
  headers for `/` and a still with and without the cookie (`curl -D -`): never `public` or cacheable.
- `/nda` ships no product copy, prices, claims, stills or og:image. The root not-found's tree and client chunks ship
  with every page, the gate included: keep words out of `HeaderClient` and anything not-found renders.
- Scripts pass the gate with `scripts/nda-cookie.mjs`: `await context.addCookies([ndaCookie(baseUrl)])` before the
  first navigation; `curl -H "Cookie: $(node scripts/nda-cookie.mjs)" <url>`. `check.mjs` adds it to every case.

## Interface micro-animations (Emil Kowalski's rules)
- Animate `transform` and `opacity` only, never `transition: all`; 150–300 ms, ease-out by default (`--ease-out`,
  `--ease-in-out` in globals.css), never ease-in for UI; exit faster than enter; stagger 30–80 ms; transitions, not
  keyframes, for interruptible UI. Nothing scales from 0: start at `scale(0.95)` or more, with opacity.
- No animation on keyboard-triggered actions (skip links, shortcuts, focus moves): jump instantly.
- Pressables get `scale(0.97)` on `:active`; hover only behind `@media (hover: hover) and (pointer: fine)`.
  `will-change` only after you see a 1px shift or measured dropped frames, on the animating element.

## Scroll storytelling
- GSAP ScrollTrigger (`pin`, `scrub`) inside `useGSAP` with a `scope` ref; anything made later in handlers goes
  through `contextSafe`. Wrap setups in `gsap.matchMedia()`; return `mm.revert()`. ScrollTrigger on the timeline,
  never on a child tween. Triggers top to bottom, or set `refreshPriority`. `ScrollTrigger.refresh()` after fonts,
  images or late content change layout.
- Lenis smooth scrolling on desktop only (fine pointer, ≥1024 px), driven by `gsap.ticker` and wired to
  `ScrollTrigger.update` (`SmoothScroll.tsx`). Never add ScrollSmoother as well.
- Every pinned sequence has a Skip link inside the pinned stage that appears on keyboard focus (visually hidden
  otherwise, shown instantly at the top of the stage). It jumps instantly to the next section and moves focus there
  (target has `tabIndex={-1}`). See `motion/PinnedChapter.tsx`; `check.mjs` reaches every one by Tab.
- Cross-fades in scrubbed sequences must not overlap: two half-faded headings are unreadable.

## Motion safety
- No motion toggle (owner, 2026-10-21): `html[data-motion="on|off"]` follows `prefers-reduced-motion` only, set before
  first paint in `layout.tsx`. Read it with `useMotion()`; pass `motionOn` to `useGSAP` with `revertOnUpdate: true`.
- Reduced motion means: no pins, no scrub, no Lenis, CSS durations forced to 0. Every section must still read
  correctly, in order, with all its content visible. Server render shows the final state.
- Pinned chapters pin only at ≥ 900 px (`PIN_MEDIA`), beats layered via `.pin-layered`: CSS `position: sticky` in a
  section `(1 + --pin-len) × 100svh` tall; ScrollTrigger only scrubs. Never `pin: true` (`position: fixed`, CLS ≈ 1).

## Stills and graphics
- Product imagery = own Blender Cycles stills (no people, no other brands, no autographs). Masters are 16-bit PNG,
  not committed; `scripts/stills.mjs` dithers and exports AVIF + WebP crops listed in `stills.json`. `<Still>`
  renders nothing for a still that has not been exported, so a section must still read without it.
- Graphics are SVG or canvas, drawn from `racket-shape.ts`. Text in them stays ≥ 15 px at 390 px wide.
  Canvas loops cap at 30 fps, pause off-screen and when hidden, DPR ≤ 2. Unmeasured data says "Illustrative".
- One canonical racket in every still and graphic (`racket-shape.ts`, render audit 2026-10-22): 455.0 × 260.0 × 38.0
  mm (the FIP limits); 42 moulded holes, a crown of 8 of Ø14.0 mm along the top and 34 of Ø12.4 mm below; 1.5 mm edge
  radius, the flat face ending 4 mm from the edge (`FACE_INSET`); one handle: a round overgrip with a helical wrap, a
  satin black cap engraved Q (the company logo, owner 2026-10-22), the head flowing into it with no collar or joint; no
  wrist cord. Only the face follows the feel: Command is white 3K twill (the default in any image that names no feel),
  Pace black 12K (owner, 2026-10-22). Throats: a single racket's serial (KQ-000427), a First 500 set's number (027/500)
  on both. Change it and G01, G15, K12 and the sweet-spot numbers change with it. Ship the graphics and the stills
  together: the canon graphics and the white-Command copy go to `main` only with the canon re-exports of every still
  the page shows (K01, K02, K05 to K11; K12 when ready), so no screen shows two different rackets.

## Performance and accessibility
- Phone profile (4× CPU, 150 ms RTT, 1.6 Mbps): LCP ≤ 2.5 s, CLS ≤ 0.1, INP ≤ 200 ms, no dropped frames while
  scrolling. The LCP element is the hero still or the h1. Keep hero JavaScript small; graphics load with their
  sections. Fonts with `next/font` (self-hosted at build), `display: swap`, covering every language in `DESIGN.md`.
- Semantic HTML, one `h1`, landmarks, real buttons and links; visible `:focus-visible` outline, full keyboard use,
  logical tab order; no scroll traps (pins end, Skip links work, no hijacked keys). WCAG AA contrast (4.5:1 body, 3:1
  large text and UI; check new colour tokens). Decorative canvases get `aria-hidden`; fallbacks real `alt` text.

## Content and claims
- No placeholder text in a finished build. Every claim has a row in `CLAIMS.md`, added in the same commit; unverified
  claims stay off the live domain, and `NEXT_PUBLIC_LAUNCHED=true` (removes noindex) waits until CLAIMS.md is cleared.
  Voice (owner, 2026-10-22): whole, plain sentences that say what we made and what it does for the player.
- Stripe: `STRIPE_SECRET_KEY`, `NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY`, `INVITE_CODES` (`.env.example`); server and
  Stripe.js pinned to API version `2026-09-30.endive` (`allowed_payment_method_types`). No keys: /reserve runs in
  preview. One of Ten fails closed without codes: keep `INVITE_CODES` empty until CLAIMS.md rows 20, 21, 29 are ready.
- The hero lead is the owner's sentence (2026-10-22), verbatim though "one piece" is retired elsewhere: "One single
  piece of space-grade carbon. No tube, no joints. Ultra-precision moulded to 15 microns and 1 gram. Every racket
  plays exactly the same." Then "Built to last five years." Elsewhere "unibody", "Zero seams"; never "zero weak points".
- Sweet spot (CLAIMS.md row 6b): "Edge to edge.", "Nearly 94% of the face is sweet spot" and "4 mm from the sweet spot
  to the edge", always with the ‡ fine print: a design ceiling from `racket-shape.ts`, rounded as Apple rounds (down,
  or up only with "Nearly"). `SWEET_CLAIM` (`graphics-sweetspot.ts`) builds every number the section prints; none is
  typed in `copy.ts` (/lab/g15 checks). Never "bezel", "all sweet spot", "zero", "100%", "no dead zones", "largest",
  or a tube or brand comparison.
- Sealed core (CLAIMS.md rows 30 to 34; wording in DESIGN.md): "Three times longer" only against an open core and
  always with its † fine print (`durability.coreFine`). Never heat, "airtight", "waterproof" or "first".
- Lineup (owner, 2026-10-22): KINETIQ, one racket, €410; First 500, two identical rackets (one feel per set), the
  first 500 sets, numbered 001 to 500, first to ship, €990; One of Ten, ten sets of three, €2,900, each with an
  exclusive coaching session. "First 500" and "One of Ten" in full (no-break spaces in code), never shortened or with
  ™ (row 35). Every edition holds the same racket, and the copy says so; never compare the pair's price with KINETIQ's.
- Durability lives in `lifetime` (`lineup.ts`): "Built to last five years" always travels with `lifetime.fine`; only One
  of Ten has a guarantee ("five-year guarantee", never "lifetime guarantee"); "first" only in the Durability lead.
  Footnote markers: * design life, † sealed core, ‡ sweet spot, § the One of Ten guarantee.
- One landing CTA, "Reserve Now"; then "Pay with Card" and "Place Reservation". Sold out: `available: false`.
- The coach has agreed (`ambassador.confirmed: true`); name him only once `COACH_FULL_NAME` (`lineup.ts`) holds his
  first name and surname as approved in writing. Never a nickname or his family; signed rackets only with `signs`.

## Definition of done
1. `npm run lint`, `npm run typecheck` and `npm run build` pass.
2. `npm run check` passes for `/`, `--path=/reserve` and `--gate`: phone, desktop and wide (2560), motion and reduced
   motion, 0 console errors, no blank frames, the fill rule, no horizontal overflow, budgets met, Skip links reached
   by Tab work, the gate's keyboard flow opens the page and assets and APIs answer 403 without the cookie.
3. You have opened and reviewed the screenshots yourself: fix anything blank, overlapping, cropped or unreadable.
4. After pushing, run `npm run check -- --url=<production url>` (and `--path=/reserve`, `--gate`) on the live site.

## Notes
- Headless long-frame counts are a smoke signal only; the harness uses `--disable-gpu-compositing` and native scroll.
- Stale servers: never `pkill -f "next start"` (it matches your own shell and kills it). Kill by
  process name: `for d in /proc/[0-9]*; do [ "$(cat $d/comm)" = "next-server (v1" ] && kill ${d#/proc/}; done`.
- Production URL: https://kinetiq-seven-neon.vercel.app (Vercel team EVHG, project `kinetiq`).
- `docs/reference-notes.md`: lighthouse.storage/token (techniques only). `docs/research/non-tubular.md`: construction
  terms ("no frame tube", not "tubeless") and factory questions.
- `docs/agent-learnings.md`: what failed while agents built the site. In short: detach long jobs (`setsid nohup`,
  progress in a file), kill by PID never by command-line text, no foreground `sleep`, one Blender render at a time
  (`flock`), one writer per file set in a shared tree.
- Never name the factory, its town, its patents or its other customers in the public repo or on the site.
