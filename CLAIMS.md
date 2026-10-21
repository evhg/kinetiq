# Claims register

Every marketing and commercial claim on the site, where it appears, and what is needed before launch.
Owner decision (2026-10-21): claim boldly now, verify before launch.
**Launch gate:** keep `NEXT_PUBLIC_LAUNCHED` unset (preview banner on, noindex) until every row is ✅.
Text lives in `src/content/claims.ts` and `src/content/site.ts`.

| # | Claim | Where | Status | Needed before launch |
| --- | --- | --- | --- | --- |
| 1 | "The world's first one-piece padel racket." | Hero h1, page title, FAQ | ⚠️ Unverified | Prior-art search (patents, other brands' monocoque rackets). Comparative/superlative claims must be provable (EU Directive 2005/29/EC, Swiss UWG Art. 3). |
| 2 | "The most precise padel racket ever made", 15 µm on every surface | Hero, Precision chapter | ⚠️ Unverified | Define what is measured (surface profile vs mould), measurement method, sample size; independent report. "Ever made" needs comparison data. |
| 3 | "The world's first padel racket with moulded holes", zero drilled, zero cut fibres | Identical section, hero stats | ⚠️ Unverified | Factory confirms holes are moulded; prior-art search. |
| 4 | "100% Swiss Made" / "world's first 100% Swiss Made padel racket" | Hero, Swiss section | ⚠️ High risk | Swissness rules (MSchG Art. 48c): ≥60% of manufacturing cost in CH plus key steps. "100%" is a stronger claim; imported fibre/resin may make it misleading. Legal review required. |
| 5 | "Patented one-mould process" | Swiss section | ⚠️ High risk | Only true once a patent is granted. Until then use "patent pending" (false patent marking is unlawful in several markets). |
| 6 | "Every racket within ±1 g and ±1 mm of the reference" | Identical section | ⚠️ Unverified | Factory tolerance data from a production run. |
| 7 | "Balance is set inside the mould" | Identical section | ⚠️ Unverified | Factory confirms moulded-in weights. |
| 8 | Measurement card with serial number and own measurements | Identical section | ⚠️ Commitment | Operational process to measure and print per racket. |
| 9 | Feel/vibration: no glue lines, settles faster, easier on the arm, same response edge to centre | Feel section | ⚠️ Unverified (reasoned, not measured) | Lab vibration test (decay time) vs a glued reference racket; "easier on your arm" is a health-adjacent claim, keep it modest or back it. |
| 10 | Workshop "already builds full-carbon golf clubs" in St. Gallen | Swiss section | ⚠️ Permission | Factory's permission to reference its golf work. |
| 11 | Foam and carbon made/moulded on site | Swiss section, specs | ⚠️ Unverified | Factory confirmation. |
| 12 | Paid in full today; ships January 2027 | Reserve page, finale | ⚠️ Commitment | Production schedule confirmed by factory. Taking full payment for later delivery: EU rules on delivery dates (Directive 2011/83/EU Art. 18). |
| 13 | "Fully refundable until your racket ships … every euro comes back. No questions." and "reply to the receipt email and we refund every euro" | Landing CTA notes, finale, reserve page, confirmation | ⚠️ Commitment | Business decision + terms page; a monitored inbox for receipt replies (Stripe's receipt reply-to = your support email). Separate from the 14-day statutory withdrawal right, which still applies after delivery. |
| 14 | "Free delivery in Europe, duties included" | Reserve page | ⚠️ Commitment | Requires DDP shipping from CH to EU (EU VAT registration or fiscal representative). Accountant sign-off. |
| 15 | Comparison values: paper 100 µm, human hair 70 µm | Precision chapter | ℹ️ General knowledge | Typical values; fine as approximations ("about"). |
| 16 | Example measurement card numbers (355.2 g, 250.4 mm, 0.011 mm) | Identical section | ℹ️ Illustrative | Replace with a real measured racket before launch. |

| 17 | Edition prices: KINETIQ €410, Founders Series €990, Atelier Edition €2,900 | `site.ts`, reserve page | ⚠️ Owner to confirm | Set by Claude as a starting point (2026-10-21), not by the owner. |
| 18 | "Founders Series: Numbered 001 to 500. Never made again." | Reserve page | ⚠️ Scarcity claim | Must be true: cap at 500 (set `available: false` when sold; Stripe can't count for us), and never reissue. Laser-marked number, first out of the mould, signed card: production commitments. |
| 19 | "Atelier Edition: Fifty rackets. One for each name." Name on card, film of your racket leaving the mould, hand-finished, fitted case | Reserve page | ⚠️ Scarcity + commitments | Cap at 50; the film and case need a supplier and a process. |
| 20 | "We only ask for what we need to deliver it: your email, name and address." | Reserve page | ✅ True by design | Keep Stripe Checkout settings as in `route.ts` (no phone, billing address auto). Privacy policy still needed. |

Also needed before launch, not claims: terms of sale, withdrawal/refund policy, privacy policy, imprint/contact (required for EU/CH e-commerce), and real Stripe keys.
