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
- No extra animation or UI libraries (Motion/Framer Motion, shadcn, 21st.dev, other kits) unless the brief asks. Our
  stack covers it. Where a skill suggests Motion's `useSpring`, use `gsap.quickTo`.

## Scripts
- `npm run dev` (local), `npm run build` / `npm start` (production), `npm run lint`, `npm run typecheck`.
- `npm run check`: the harness (Definition of done). `--skip-build`, `--url=<url>`, `--study` (reference mode),
  `--only=phone|phone-short|tablet|laptop|desktop|wide` (or a list), `--mode=motion|reduced`, `--verbose`,
  `--path=/reserve` (any page), `--gate` (the NDA gate, no cookie). Output in `.checks/<label>/`.
- `node scripts/stills.mjs <masters dir> [id ...]`: export Blender masters to `public/stills/` (AVIF + WebP).
- `node scripts/sequence.mjs <seq dir> [name ...]`: hero swivel frames (`f000.png`…) to `public/stills/seq/`.
- Vercel runs `PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1 npm ci` (no browsers); locally `npx playwright install chromium`.

## Folders
- `src/app/`: routes, `layout.tsx` (motion init script, providers), `globals.css`. `src/lib/gsap.ts` is the only place
  GSAP plugins are registered: import gsap from there. `src/lib/racket-shape.ts`: the racket (Stills and graphics).
- `src/components/`: `motion/` (`MotionProvider`, `SmoothScroll` for Lenis, `PinnedChapter`), `landing/` (a component
  and CSS module per section; `Reveal`, `Scrub`), `graphics/` (G01–G16, each with a review page at `/lab/<id>`, dev
  only; `KQ_LAB=1` serves them in production), `media/Still.tsx`, `reserve/`, `chrome/` (`SiteHeader`, `SiteFooter`;
  `HeaderClient.tsx`: the compact Reserve Now, label passed in, hidden over hero and `data-cta`). No preview banner.
- `src/content/`: all words. `copy.ts` (landing), `lineup.ts` (editions, prices, limits, `lifetime`, `sampleSet`, coach,
  invitations, countries), `reserve.ts`, `site.ts` (CTAs, price note, ship date, refund, feels; `DEFAULT_FEEL` Command,
  `FEEL_PREFERENCE_KEY` "kq-feel", `storedFeel()`; the toggle's store is `lib/feel-store.ts`), `stills.json` (crops).
- Flow (Tesla Roadster reserve page): "Reserve Now" → `/reserve?tier=` (feel, edition, trust lines, Due Today, "Pay
  with Card" expands the form in place; the gallery opens on K08, both feels, until a feel is chosen) → "Place
  Reservation" posts to `src/app/api/reserve/route.ts` (PaymentIntent via REST, amount from `lineup.ts`; enforces
  `Tier.perCustomer` and fails closed) and confirms the card with Stripe's Payment Element in place → confirmation in
  place, or `/reserved` after 3-D Secure. One of Ten: never chosen from a link (`?tier=invite` shows KINETIQ), never
  interactive until a valid code (POST /api/invite, or `?invite=CODE`) unlocks it; /api/reserve checks it again.
- Data minimisation: name, email, delivery address and card only; no phone, accounts or opt-ins (NDA emails: below).
  `public/`: assets and `CREDITS.md`. `scripts/`: harness. `docs/`: research. `.claude/skills/`: reference skills.

## NDA gate (owner, 2026-10-22: investors declare the NDA, then give an email, once per device)
- `src/proxy.ts` (Next 16 "proxy", formerly middleware) rewrites every page to `/nda` without a valid `kq_nda` cookie
  (`src/lib/nda.ts`) and answers assets, `/api/*` and other `/_next/*` paths with an empty 403; only `/_next/static/`,
  the HMR socket, the two icon files and `POST /api/nda` pass. Exclusions, cookie and arrival: DESIGN.md "NDA gate".
- A declaration, not a login (unsigned cookie, public format; CLAIMS.md row 25b). With RESEND_API_KEY, NDA_NOTIFY_TO and
  NDA_NOTIFY_FROM on Vercel only (never the repo), a same-origin sign-in emails the owner its address, time and page
  (path, edition) via Resend (`nda-notify.ts`): once per address a day, 20 an hour, 40 a day per instance, the rest in
  the next email; never for a reserved test domain (`.invalid`: the harness). Nothing else is stored or logged.
- The root layout's metadata is neutral (title "KINETIQ", noindex): the product's title, description and og:image live
  in `src/lib/product-metadata.ts`, used by `/` and `/reserve` only. Never put product metadata back in `layout.tsx`.
- Cleared pages are `private, no-cache` (`src/proxy.ts`), stills `private` with `Vary: Cookie` (`next.config.ts`). After
  each deploy, check production headers for `/` and a still with and without the cookie (`curl -D -`): never `public`.
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
- Graphics are SVG or canvas, drawn from `racket-shape.ts`. Text in them stays ≥ 15 px at 390 px wide. Canvas loops
  cap at 30 fps, pause off-screen and when hidden, DPR ≤ 2. No "Illustrative" captions (owner, 2026-10-23).
- Feel toggle: DESIGN.md "Feel toggle" (`html[data-feel]` before first paint; Pace still = id + "-pace", same crops).
- One canonical racket in every still and graphic (`racket-shape.ts`, render audit 2026-10-22): 455.0 × 260.0 × 38.0 mm
  (the FIP limits); 42 moulded holes, a crown of 8 of Ø14.0 mm along the top and 34 of Ø12.4 mm below; 1.5 mm edge
  radius, the flat face ending 4 mm from the edge (`FACE_INSET`); one handle: a round overgrip with a helical wrap, a
  satin black cap engraved Q (the company logo, owner 2026-10-22), the head flowing into it with no collar or joint; no
  wrist cord. Only the face follows the feel: Command is white 3K twill (the default in any image that names no feel),
  Pace black 12K (owner, 2026-10-22). Throats: a single racket's serial (KQ-000427), a First 500 set's number (027/500)
  on both. Change it and G01, G15, K12 and the sweet-spot numbers change with it. Ship the canon graphics and the
  white-Command copy to `main` only with the canon re-exports of K01 to K12, so no screen shows two different rackets.

## Performance and accessibility
- Phone profile (4× CPU, 150 ms RTT, 1.6 Mbps; the `phone` and `phone-short` cases): LCP ≤ 2.5 s, CLS ≤ 0.1, INP ≤ 200
  ms, no dropped frames while scrolling. LCP element: the hero still or the h1. Keep hero JavaScript small; graphics
  load with their sections. Fonts: `next/font` (self-hosted), `display: swap`, every language in `DESIGN.md`.
- Semantic HTML, one `h1`, landmarks, real buttons and links; visible `:focus-visible` outline, full keyboard use,
  logical tab order; no scroll traps (pins end, Skip links work, no hijacked keys). WCAG AA contrast (4.5:1 body, 3:1
  large text and UI; check new colour tokens). Decorative canvases get `aria-hidden`; fallbacks real `alt` text.

## Content and claims
- No placeholder text in a finished build. Every claim has a row in `CLAIMS.md`, added in the same commit; unverified
  claims stay off the live domain, and `NEXT_PUBLIC_LAUNCHED=true` (removes noindex) waits until CLAIMS.md is cleared.
  Voice (owner, 2026-10-22): whole, plain sentences that say what we made and what it does for the player.
- Stripe: `STRIPE_SECRET_KEY`, `NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY`, `INVITE_CODES` (`.env.example`); both sides on API
  `2026-09-30.endive` (`allowed_payment_method_types`). No keys: /reserve runs in preview. One of Ten fails closed
  (`invitationsOpen()`): `INVITE_CODES` (12+ characters each) stays empty until rows 20, 21, 29 are ready; no payment
  until the atomic one-use check exists (`INVITE_ONE_USE_ENFORCED`).
- The hero lead is the owner's sentence (2026-10-22), verbatim though "one piece" is retired elsewhere: "One single
  piece of space-grade carbon. No tube, no joints. Ultra-precision moulded to 15 microns and 1 gram. Every racket plays
  exactly the same." Nothing follows it. Elsewhere "unibody", "Zero seams"; never "zero weak points".
- Sweet spot (row 6b): "Edge to edge.", "Nearly 94% of the face is sweet spot", "4 mm from the sweet spot to the edge",
  line 1 saying the flat face is sweet spot by design: a ceiling from `racket-shape.ts`, rounded down (or up only with
  "Nearly"). `SWEET_CLAIM` builds every number; none is typed in `copy.ts` (/lab/g15 checks). Never "bezel", "all sweet
  spot", "zero", "100%", "no dead zones", "largest", or a tube or brand comparison.
- Sealed core (CLAIMS.md rows 30 to 34; DESIGN.md): "Three times longer" only against the same core left open ("an
  exposed EVA core"), as a design ("made to last") until tested; never heat, "airtight", "waterproof" or "first"; it
  follows Holes. The process is "patent pending", never "patented". Tolerances: ±1.0 g, balance ±0.1 mm (2026-10-23).
- Lineup (owner): KINETIQ, one racket, €410; First 500, two identical rackets in one feel, sets 001 to 500, first to
  ship, one set per customer (row 40), €990; One of Ten, ten sets of three with an exclusive coaching session, €2,900.
  Edition bullets: 4 at most. "First 500" and "One of Ten" in full (no-break spaces), never shortened or with ™ (row
  35). Every edition holds the same racket, and the copy says so; never compare the pair's price with KINETIQ's.
- Five years only in Durability (owner, 2026-10-22): its h2 (`lifetime.line`), lead, G14 and point 4; never the hero,
  finale, meta or confirmation; the one include naming it is One of Ten's "A five-year KINETIQ guarantee on all three
  rackets" (never "lifetime guarantee"). "First" only in the Durability lead and the owner's lines (rows 36 and 38).
- No small print (owner, 2026-10-22, risk accepted in CLAIMS.md): no footnote markers (*, †, ‡, §) and no fine-print
  lines, on the landing page, the edition cards or /reserve. A qualifier that keeps a claim honest goes in a plain
  sentence of the body copy ("as designed", "made to last"), or is dropped. /reserve keeps what the law needs at the
  payment: Due Today, the refund line, the order line.
- One landing CTA, "Reserve Now"; then "Pay with Card" and "Place Reservation". Sold out: `available: false`.
- Space-grade (rows 41 to 44): only against "the standard carbon most padel rackets use"; no defence, military, maker.
- The coach is named "Paquito Navarro" (`COACH_FULL_NAME`, `lineup.ts`), approved in writing (owner, 2026-10-22), in
  the One of Ten coaching include and G12. Exactly that name; never his family, no descriptor until a true one is
  confirmed, signed rackets only with `signs`. His racket sponsor's contract must allow it (CLAIMS.md row 21).

## Definition of done
1. `npm run lint`, `npm run typecheck` and `npm run build` pass.
2. `npm run check` passes for `/`, `--path=/reserve` and `--gate`: phone (390x844), phone-short (390x664, Safari on an
   iPhone), tablet (768x1024), laptop (1536x730, a browser window), desktop (1440x900) and wide (2560), motion and
   reduced motion, 0 console errors, no blank frames, the fill rule, no horizontal overflow, budgets met, Skip links
   reached by Tab work, no footnote markers, the gate opens by keyboard, and assets and APIs answer 403 without it.
3. Review the screenshots yourself, plus a 375x667 spot check: fix anything blank, overlapping, cropped or unreadable.
4. After pushing, run `npm run check -- --url=https://kinetiq-seven-neon.vercel.app` (and `--path=/reserve`, `--gate`)
   on the live site (Vercel team EVHG, project `kinetiq`).

## Notes
- Headless long-frame counts are a smoke signal (`--disable-gpu-compositing`). Stale servers: never `pkill -f`; kill
  by name: `for d in /proc/[0-9]*; do [ "$(cat $d/comm)" = "next-server (v1" ] && kill ${d#/proc/}; done`.
- Never call a contextSafe function synchronously inside a gsap.matchMedia().add() callback (Back-button crash, 10-23).
- `docs/reference-notes.md`: lighthouse.storage/token. `docs/research/non-tubular.md`: construction terms ("no frame
  tube", not "tubeless"), factory questions. `docs/agent-learnings.md`: detach long jobs (`setsid nohup`, progress in
  a file), kill by PID, no foreground `sleep`, one Blender render at a time (`flock`), one writer per file set.
- Never name the factory, its town, its patents or its other customers in the public repo or on the site.
