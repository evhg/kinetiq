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
  `--path=/reserve` (any page; run it for `/` and `/reserve`), `--gate` (the NDA gate, without the cookie).
  Output goes to `.checks/<label>/` (git-ignored). Uses a free port per run.
- `node scripts/stills.mjs <masters dir> [id ...]`: export Blender masters to `public/stills/` (AVIF + WebP).
- Vercel installs with `PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1 npm ci` (`vercel.json`), so builds never
  download browsers. Locally: `npx playwright install chromium` once.

## Folders
- `src/app/`: routes, `layout.tsx` (motion init script, providers), `globals.css`.
- `src/components/motion/`: `MotionProvider` (reduced-motion state), `SmoothScroll` (Lenis), `PinnedChapter`.
- `src/components/landing/`: one component + CSS module per landing section; `Reveal` and `Scrub` helpers.
- `src/components/graphics/`: data graphics G01–G14 (SVG/canvas), each with a review page at `/lab/<id>` (dev only;
  `KQ_LAB=1` serves them in production).
- `src/components/media/Still.tsx`: product stills with phone art direction. `src/components/reserve/`: /reserve.
- `src/components/chrome/`: `Chrome.tsx` (server: `SiteHeader`, `SiteFooter`) and `HeaderClient.tsx` (scroll state,
  compact Reserve Now after the hero; its label comes in as a prop). No preview banner (owner, 2026-10-22).
- `src/lib/gsap.ts`: the only place GSAP plugins are registered. Import gsap from here.
- `src/content/`: all words; change them there. `copy.ts` (landing), `lineup.ts` (editions, prices, limits, `lifetime`,
  the coach, invitation gate, delivery countries), `reserve.ts`, `site.ts` (CTA labels, ship date, refund, feels).
- Flow (Tesla Roadster reserve page): landing page with one CTA, "Reserve Now" → `/reserve?tier=` (edition,
  feel, trust lines, Due Today, "Pay with Card" expands the form in place) → "Place Reservation" posts to
  `src/app/api/reserve/route.ts` (PaymentIntent via REST, amount from `lineup.ts`) and confirms the card
  with Stripe's Payment Element in place → confirmation in place, or `/reserved` after 3-D Secure.
  InviQtus is invite only: never chosen from a link (`?tier=invite` shows ConQuer) and never interactive until a
  valid code ("Have an invitation?" or `?invite=CODE`, POST /api/invite) unlocks it; /api/reserve checks it again.
- Data minimisation: name, email, delivery address and card only. No phone, accounts or opt-ins.
- `public/`: static assets and `CREDITS.md`. `scripts/`: harness. `docs/`: research notes.
- `.claude/skills/`: saved reference skills (GSAP, Emil Kowalski, our frontend-design notes).

## NDA gate (owner, 2026-10-22: investors declare the NDA, then give an email, once per device)
- `src/proxy.ts` (Next 16 "proxy", formerly middleware; Node runtime) runs on every path except `/_next/static/`,
  the HMR socket and the two icon files (`/icon.svg`, `/apple-icon.png`, from `src/app/`); each exclusion is anchored,
  so `/iconography` or `/_next/imagex` cannot borrow it. Without a valid `kq_nda` cookie: pages are rewritten to
  `/nda` (the URL stays as typed); assets, `/api/*` and other `/_next/*` paths get an empty 403. `POST /api/nda`
  always passes; `/nda` with the cookie redirects to `/`. Dev only: `/__nextjs_*` (the error overlay) passes.
- Cookie (`src/lib/nda.ts`): `kq_nda` = base64url of `{"email","at"}`, HttpOnly, SameSite=Lax, Secure on https,
  Path=/, 365 days; valid when it decodes and the email looks valid. Nothing is stored or logged on the server.
  A declaration, not a login: it is unsigned and its format is public (this repo), so anyone can skip the gate
  without declaring (CLAIMS.md row 25b). Known limit: `/_next/static/` chunks are served without the cookie, and the
  landing and /reserve chunks carry edition copy, so a chunk URL a cleared visitor forwards stays readable.
- The root layout's metadata is neutral (title "KINETIQ", noindex): the product's title, description and og:image
  live in `src/lib/product-metadata.ts`, used by `/` and `/reserve` only, so a 404 or any path the proxy lets through
  inherits no claim. Never put product metadata back in `layout.tsx`.
- Stills are `Cache-Control: private` with `Vary: Cookie` (`next.config.ts`), so no shared cache can hand one to a
  visitor without the cookie. After each deploy, check production headers for `/` and a still with and without the
  cookie (`curl -D -`): the gate must never come back `public` or cacheable.
- `/nda` (`src/components/nda/NdaGate.tsx`, words in `src/content/nda.ts`) must ship no product copy, prices, claims
  or stills, and no og:image. The root not-found's tree (and its client chunks) ships with every page, the gate
  included: keep words out of `HeaderClient` and anything not-found renders (its footer drops "100% Swiss Made.").
- Arrival: the gate sets `kq_nda_tried` in sessionStorage and reloads; the head script (`lib/motion-preference.ts`)
  then marks `html[data-arrive]` and the page lifts out of a void veil (globals.css; /reserve holds it until its
  neutral shell is replaced by the linked edition). `components/nda/Arrival.tsx` clears the flag and the attribute.
- Scripts pass the gate with `scripts/nda-cookie.mjs`: `await context.addCookies([ndaCookie(baseUrl)])` before the
  first navigation; `curl -H "Cookie: $(node scripts/nda-cookie.mjs)" <url>`. `check.mjs` adds it to every case.

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
  Without keys, /reserve runs in preview (Place Reservation disabled). Invite Only fails closed without codes;
  keep `INVITE_CODES` empty until CLAIMS.md rows 20, 21 and 29 (terms, coach, guarantee statement) are ready.
- Hero lead is the owner's own sentence (2026-10-22); keep it verbatim, even while "one piece" is retired as a
  marketing phrase elsewhere: "One single piece of space-grade carbon. No tube, no joints. Ultra-precision
  moulded to 15 microns and 1 gram. Every racket plays exactly the same." "Built to last five years." follows it
  as its own sentence (`hero.life`). Elsewhere say "unibody" and "Zero seams.", never "zero weak points".
- Sealed core (CLAIMS.md rows 30 to 34): the shell closes around the whole EVA core and lines all 42 holes ("The core
  never touches the air."); "Swiss-made EVA" at country level only; "Injected straight into the mould". "Three times
  longer" only against an open core and always with its † fine print (`durability.coreFine`). Never heat, "airtight",
  "waterproof" or "first".
- Lineup (owner, 2026-10-22): ConQuer, one racket, €410; VanQuish, a matched pair (both Command or both Pace: one
  feel per set), 500 sets, €990; InviQtus, ten sets of three, €2,900, each with one of ten coaching sessions.
- Durability lives in `lifetime` (`lineup.ts`): "Built to last five years" always travels with `lifetime.fine`; only
  InviQtus has a guarantee ("five-year guarantee", never "lifetime guarantee"); "first" only in the Durability lead.
- One landing CTA label: "Reserve Now" (`site.ctaLabel`); then "Pay with Card" and "Place Reservation".
- An edition that sells out: set `available: false` in `lineup.ts` (shows "Sold out", blocks payment).
- The coach has agreed (`ambassador.confirmed: true`); name him only once `COACH_FULL_NAME` (`lineup.ts`) holds his
  first name and surname as approved in writing. Never a nickname or his family; signed rackets only with `signs`.
- Fonts must cover every language listed in `DESIGN.md`.

## Definition of done
1. `npm run lint`, `npm run typecheck` and `npm run build` pass.
2. `npm run check` passes for `/`, `--path=/reserve` and `--gate`: phone, desktop and wide (2560), motion and reduced
   motion, 0 console errors, no blank frames, the fill rule, no horizontal overflow, budgets met, Skip link works,
   the gate's keyboard flow opens the page and assets and APIs answer 403 without the cookie.
3. You have opened and reviewed the screenshots yourself: fix anything blank, overlapping, cropped or
   unreadable, then rerun.
4. After pushing, run `npm run check -- --url=<production url>` (and `--path=/reserve`, `--gate`) on the live site.

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
