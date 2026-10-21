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
Lenis · three.js via `@react-three/fiber` and `@react-three/drei` · Playwright (dev only).

## Scripts
- `npm run dev`: local dev server.
- `npm run build` / `npm start`: production build and server.
- `npm run lint`, `npm run typecheck`.
- `npm run check`: the check harness (see Definition of done). `--skip-build`, `--url=<url>`,
  `--study` (reference mode), `--only=phone|desktop`, `--mode=motion|reduced`, `--verbose`,
  `--path=/reserve` (any page; run it for `/` and `/reserve`).
  Output goes to `.checks/<label>/` (git-ignored). Uses a free port per run.
- Vercel installs with `PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1 npm ci` (`vercel.json`), so builds never
  download browsers. Locally: `npx playwright install chromium` once.

## Folders
- `src/app/`: routes, `layout.tsx` (motion init script, providers), `globals.css`.
- `src/components/motion/`: `MotionProvider` (motion state), `MotionToggle`, `SmoothScroll` (Lenis).
- `src/components/three/`: lazy R3F scenes. `LazyHeroScene` owns the fallback and loading rules.
- `src/lib/gsap.ts`: the only place GSAP plugins are registered. Import gsap from here.
- `src/content/`: all copy that carries a claim (`claims.ts`) or a commercial fact (`site.ts`: editions,
  prices, limits, ship date, refund, models, CTA labels). Change words there, not in components.
- Flow (modelled on a car-maker reservation page): landing page with one CTA, "Reserve Now", at three
  peaks and nothing after the last one → `/reserve` (edition, then racket, trust lines, "Due today",
  "Pay by Card") → `src/app/api/checkout/route.ts` (Stripe Checkout via REST, inline `price_data`,
  preview mode without a key) → `/reserved`. `/checkout` redirects to `/reserve`.
- Data minimisation: we collect nothing ourselves; Stripe collects email, name, delivery address and
  card only. Don't add phone, accounts or opt-ins without a fulfilment reason.
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
- `html[data-motion="on|off"]` is set before first paint by the inline script in `layout.tsx`:
  saved choice first, otherwise `prefers-reduced-motion`.
- The Motion on/off switch is always visible and saved in `localStorage` (`kinetiq-motion`).
- Motion off means: no pins, no scrub, no Lenis, no 3D (static image), CSS durations forced to 0.
  Every section must still read correctly, in order, with all its content visible.
- Read the state with `useMotion()`; pass `motionOn` as a `useGSAP` dependency with
  `revertOnUpdate: true`.

## 3D
- three.js only through React Three Fiber, loaded with `next/dynamic` + `ssr: false` from a client
  component (`LazyScene`), after the page is idle.
- Device pixel ratio capped: 2 on desktop, 1.5 on phones (`dpr={[1, max]}`).
- `frameloop="never"` when off-screen (IntersectionObserver) or the tab is hidden.
- Dispose: keep geometries/materials declarative so R3F disposes them; dispose anything created
  imperatively (textures, render targets) in effect cleanup.
- Static fallback image always rendered underneath; shown alone when WebGL is missing or motion is off.
- No drei helpers that fetch from CDNs at runtime (e.g. `Environment` presets). Self-host HDRs and models.

## Performance budget (phone profile: 4× CPU, 150 ms RTT, 1.6 Mbps)
- LCP ≤ 2.5 s, CLS ≤ 0.1, INP ≤ 200 ms, no dropped frames while scrolling.
- The LCP element is text or a static image, never the canvas. Keep hero JavaScript small; 3D after.
- Fonts with `next/font` (self-hosted at build), `display: swap`, subsets for every brief language.

## Accessibility
- Semantic HTML, one `h1`, landmarks, real buttons and links.
- Visible focus (`:focus-visible` outline), full keyboard use, logical tab order.
- WCAG AA contrast (4.5:1 body, 3:1 large text and UI). Check new colour tokens.
- No scroll traps: pins always end, Skip links work, no hijacked keys.
- Decorative canvases get `aria-hidden`; fallbacks get real `alt` text.

## Content and claims
- No placeholder text in a finished build. The preview banner is deliberate, not a placeholder.
- Every claim is listed in `CLAIMS.md`. A new claim gets a row there in the same commit.
- Launch gate: `NEXT_PUBLIC_LAUNCHED=true` (removes banner and noindex) only when CLAIMS.md is cleared.
- Stripe: `STRIPE_SECRET_KEY`, `NEXT_PUBLIC_SITE_URL` (see `.env.example`). One landing CTA label
  everywhere: "Reserve Now" (`site.ctaLabel`); the only other action is "Pay by Card" (`site.payLabel`).
- An edition that sells out: set `available: false` in `site.ts` (shows "Sold out", blocks payment).
- Fonts must cover every language listed in `DESIGN.md`.

## Definition of done
1. `npm run lint`, `npm run typecheck` and `npm run build` pass.
2. `npm run check` passes: phone + desktop, motion + reduced motion, 0 console errors, no blank frames
   (including the 3D region), no horizontal overflow, budgets met, Skip link and Motion switch work.
3. You have opened and reviewed the screenshots yourself: fix anything blank, overlapping, cropped or
   unreadable, then rerun.
4. After pushing, run `npm run check -- --url=<production url>` (and `--path=/reserve`) on the live site.

## Notes
- Headless WebGL needs swiftshader flags (the harness sets them). Long-frame counts from headless runs
  are a smoke signal, not a device measurement.
- The harness launches Chromium with `--disable-gpu-compositing`: with GPU compositing, swiftshader
  stalls screenshots after a WebGL frame (captures hang for minutes). Don't remove it.
- The harness scrolls natively (`window.scrollTo`); Lenis follows native scroll events.
- drei `<Environment>` is the expensive part of the hero in software rendering; keep its
  `resolution` at 64 unless reflections need to be sharper.
- Stale servers: never `pkill -f "next start"` (it matches your own shell and kills it). Kill by
  process name: `for d in /proc/[0-9]*; do [ "$(cat $d/comm)" = "next-server (v1" ] && kill ${d#/proc/}; done`.
- Production URL: https://kinetiq-seven-neon.vercel.app (Vercel team EVHG, project `kinetiq`).
- `docs/reference-notes.md`: study of lighthouse.storage/token (techniques only, nothing copied).
