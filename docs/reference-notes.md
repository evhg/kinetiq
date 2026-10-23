# Reference study: lighthouse.storage/token

Studied 2026-10-21 with `npm run check -- --url=https://www.lighthouse.storage/token --study`
(phone 390×844 and desktop 1440×900, motion on and reduced motion, screenshots every 10%).
Techniques only. No text, images or exact layouts are copied.

## What it loads
- **Lenis** for smooth scrolling. The `lenis` class is on `<html>` with motion on, and gone under
  reduced motion, so Lenis is switched off when the OS asks for less motion.
- **three.js** (three chunks) for one WebGL canvas: a 3D lighthouse model.
- **No GSAP and no ScrollTrigger.** No `.pin-spacer` elements at any step. Its "pins" are CSS
  `position: sticky`, with scroll progress read by its own code (it looks like Lenis's scroll event)
  and written to the 3D camera and to a progress bar.
- Next.js app. One console error on every run: a WebSocket closing (`onClose` in a lazy chunk). Ours
  must have zero.
- Numbers: phone LCP 1.5–2.1 s on our throttled phone profile, desktop 0.7–1.1 s, CLS ≤ 0.04.

## What pins, what scrubs, what triggers
| Chapter | Pin | Scrub / trigger |
| --- | --- | --- |
| Hero, "flight" | The hero section is `position: sticky` for about two screens. | Scroll scrubs the camera: it flies from a full view of the model up into its lamp room (the frames at 0%, 10% and 20% differ only in camera position). A thin progress bar at the bottom fills with it. |
| Chapters (Utility, Credits, Tokenomics) | A sticky side rail on desktop ("Explore the token") with numbered chapter links and a moving track marker; it collapses into a toggle on phones. | Chapter headings carry a `data-tp-reveal` attribute: a one-shot reveal when they enter the viewport, not scrubbed. The rail's active link follows scroll position (`aria-current="location"`). |
| Allocation chart | Not pinned. | A labelled chart (`aria-label` on the figure) that reveals on entry. |

## Skip link and motion switch
- **Skip link:** "Skip to details" sits inside the sticky hero, bottom right, visible for the whole
  flight (a plain anchor to the first chapter). On phones it's centred under the progress bar.
  Small and quiet, but always there: the right idea.
- **Motion switch:** a "Motion on" button in the chapter rail, with `aria-pressed` and an
  `aria-label` ("Pause token page animations") and a small animated wave icon. It's only reachable
  from the rail (below the hero), not from the hero itself.

## What we reuse (as techniques)
1. **Scroll-scrubbed camera move on one hero model** as the opening act. We do the same with the racket:
   the reveal plays on load, then scroll turns the racket edge-on (one piece, 38 mm).
2. **A skip link inside the pinned stage**, for the whole length of the pin. Ours is in every pinned
   chapter and moves keyboard focus, but it appears only on keyboard focus (owner's question, 2026-10-22):
   visually hidden otherwise, shown at once at the top of the stage. Mouse and touch visitors never need it.
3. **A thin progress cue during a long pinned sequence**, so people know how long it lasts.
   (Our precision chapter uses comparison bars that fill as you scroll.)
4. **Lenis off under reduced motion**: ours goes further, with no Lenis on touch devices either.
5. **One sticky "where am I" rail on desktop** is worth considering if the page grows past ~6 chapters.
   Not used now: a single-CTA landing page shouldn't offer competing navigation.

## What we do differently
- GSAP ScrollTrigger pins with real spacers (the scroll length is explicit and refresh-safe) instead of
  sticky plus custom maths.
- The motion switch is in the header on every screen, not only in a mid-page rail, and it is saved
  between visits.
- Zero console errors, LCP from server-rendered text and an inline SVG still, and 3D loaded after idle.
- No duplicate CTAs in the header: they show a primary button in the nav plus two hero buttons. We
  use one action, one label, placed at the emotional peaks.
