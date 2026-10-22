// The lineup, modelled on a reservation page with three tiers of rising exclusivity.
// Names, prices, limits and extras are owner decisions tracked in CLAIMS.md.
// Tier ids are stable keys; names and copy can change freely.
//
// One racket, three editions (owner, 2026-10-22). Every edition holds the same KINETIQ, in the feel the buyer
// chooses: the editions differ only in how many rackets come, when they ship and what comes with them. So the names
// never describe the racket; each is a number you can read (its serial; its set number, 001 to 500, on both throats;
// its set number, 01 to 10, on the case). Command and Pace stay the only words about play. Write "First 500" and
// "One of Ten" in full, with no-break spaces, never shortened ("500", "The Ten") and never with ™ (CLAIMS.md row 35).
// ConQuer, VanQuish and InviQtus are retired.

import type { IconName } from "@/components/graphics/Icons";

export type TierId = "reserve" | "limited" | "invite";

export type Tier = {
  id: TierId;
  name: string;
  /** A state, never a verb: "Reserve" read as a second button beside Reserve Now. */
  availability: "Available" | "Limited" | "Invite Only";
  priceEur: number;
  /** One line on the option card. */
  cardLine: string;
  includes: string[];
  /** Units made (sets, for the editions sold as sets), or null for the open tier. */
  limit: number | null;
  /**
   * Sets promised or given away off the site (no checkout): they count against `limit` like a paid
   * reservation. Raise it the day a set is promised; never reissue a number.
   */
  offSite: number;
  /** Rackets in the edition. A set is one feel: every racket in it is Command, or every racket is Pace. */
  rackets: number;
  /** False shows "Sold out" and blocks payment. */
  available: boolean;
};

/**
 * Durability (owner, 2026-10-22). Every KINETIQ is built to last five years; only One of Ten carries a guarantee.
 * The five-year line is said in one place only, the Durability section (owner, 2026-10-22: "it's too much" in the
 * hero, the finale and the edition includes), with no footnote marker and no small print: its usage profile and
 * the promised fatigue tests are told in the section's own sentences (copy.ts `durability`). CLAIMS.md rows 26 and
 * 29: the design life needs an independent fatigue report (promised before shipping, never claimed as done), and
 * the guarantee needs its written statement and the EU harmonised guarantee label before One of Ten can be paid
 * for (INVITE_TERMS_READY). Never "lifetime guarantee", never "sustainable", and never a guarantee for the KINETIQ
 * or First 500 editions.
 */
export const lifetime = {
  line: "Built to last five years",
  /** Its scope is the written statement's (CLAIMS.md row 29): KINETIQ guarantees all three rackets of the set. */
  guarantee: "A five-year KINETIQ guarantee on all three rackets",
};

/**
 * The sample set number shown for First 500: on both throats in K10 and K11 ("027/500") and on the two sample
 * measurement cards ("Set No. 027 / 500 A" and "B"). Never reissued; a single racket shows its serial instead
 * (KQ-000427, `identical.card.serial` in copy.ts). The set's two cards carry serials of their own, KQ-000053 and
 * KQ-000054 (`identical.card.setSerials`), never the single racket's.
 */
export const sampleSet = {
  /** As laser-marked on the throats. */
  mark: "027/500",
  /** As spoken in alt text. */
  words: "set 027 of 500",
  /** The line on each of the set's two measurement cards. */
  card: (racket: "A" | "B") => `Set No. 027 / 500 ${racket}`,
};

/**
 * The coach behind the One of Ten sessions (owner, 2026-10-22: he has agreed to ten sessions, one per set). The
 * site names him exactly as his name was approved in writing (owner, 2026-10-22): "Paquito Navarro". Never another
 * form of his name, and never his family. Left empty, `name` falls back to the neutral wording. Signed rackets are
 * offered only once he has agreed in writing to sign them (`signs`). CLAIMS.md row 21: his racket sponsor's
 * contract must allow it.
 */
const COACH_FULL_NAME = "Paquito\u00a0Navarro";
export const ambassador = {
  /** He has agreed to the ten coaching sessions, so the One of Ten extras can be offered. */
  confirmed: true,
  /** How the site names him: his approved full name, or the neutral wording until then. */
  name: COACH_FULL_NAME || "our coach",
  named: Boolean(COACH_FULL_NAME),
  neutral: "our coach",
  /** A true descriptor only (e.g. "padel coach"), shown once he is named. */
  descriptor: "",
  /** Whether he signs the three rackets of each set (only once agreed in writing). */
  signs: false,
  sessions: 10,
  /**
   * The second line of the G12 court plan. No event is promised (the Málaga P1 line is retired: no
   * 2027 dates are published and the coach is not tied to it), so it says what exists: ten sessions.
   */
  event: "ten sessions, one per set",
};

const COUNT_WORDS: Record<number, string> = { 1: "one", 2: "two", 3: "three", 4: "four", 5: "five", 10: "ten" };
export const countWord = (n: number) => COUNT_WORDS[n] ?? String(n);

// "Exclusive" is the owner's word; the format (one-on-one or a small group) waits for the written terms (row 20).
// "One of ten sessions" is retired: it clashed with the edition's name.
const coaching = ambassador.named
  ? `An exclusive coaching session with ${ambassador.name}, one per\u00a0set`
  : "An exclusive coaching session, one per\u00a0set";

/** The editions section on the landing page: one racket, three editions. */
export const editionsIntro = {
  headline: "We make one racket, in three editions.",
  // The h2 says one racket; the KINETIQ card line says it is the same in every edition (the one line /reserve shows),
  // and Two feels has just said "the feel you choose", so the lead says neither again.
  lead: "They differ only in how many rackets you receive, when they ship and what comes with them.",
  /** The invitation edition's card says so where the other two cards carry their arrow. */
  byInvitation: "By invitation",
};

export const tiers: Tier[] = [
  {
    id: "reserve",
    name: "KINETIQ",
    availability: "Available",
    priceEur: 410,
    cardLine: "It is the same racket you will find in every edition.",
    // Four includes, in the First 500 card's order (racket, number, card, shipping), so this card has no empty band
    // above its price. The serial on the throat is the canon mark (CLAIMS.md row 15); the ship month is the same as
    // `site.shipMonth` (typed here: site.ts imports this file). It ships after the First 500 sets, which keeps their
    // "first to ship" true in the same month (CLAIMS.md rows 19 and 22). Never the five years (Durability only).
    includes: [
      "One KINETIQ racket, Command\u00a0or\u00a0Pace",
      "Its own serial number, laser-marked on the\u00a0throat",
      "A measurement card, numbered to\u00a0match",
      "Ships in January\u00a02027, after the First\u00a0500\u00a0sets",
    ],
    limit: null,
    offSite: 0,
    rackets: 1,
    available: true,
  },
  {
    id: "limited",
    name: "First\u00a0500",
    availability: "Limited",
    priceEur: 990,
    // "First" is a production promise (CLAIMS.md row 19): sets 001 to 500 leave the mould before any other
    // edition and ship first. Every line says "sets": 500 sets are 1,000 rackets. "First to ship" is said once, by
    // the includes; the card line says what the set is.
    cardLine: "The first 500 sets we make are numbered 001\u00a0to\u00a0500. Each set is two identical rackets in one\u00a0feel.",
    includes: [
      "Two identical KINETIQ rackets, both Command or both\u00a0Pace",
      "Your set number, 001\u00a0to\u00a0500, laser-marked on both throats",
      "Two measurement cards, numbered to\u00a0match",
      "First out of the mould and first to ship, in\u00a0January\u00a02027",
    ],
    limit: 500,
    offSite: 0,
    rackets: 2,
    available: true,
  },
  {
    id: "invite",
    name: "One\u00a0of\u00a0Ten",
    availability: "Invite Only",
    priceEur: 2900,
    // The tag, and "Invitations open soon." or (once they open) the foot, already say "invitation": the card line
    // does not. The set number is on the case plate (K09, "No. 01 / 10"); each racket has its own serial (row 15).
    cardLine: "We make ten sets of three identical rackets, numbered 01\u00a0to\u00a010.",
    includes: [
      "Three identical KINETIQ rackets in a fitted case marked with your set number, 01\u00a0to\u00a010",
      "Three measurement cards, numbered to\u00a0match",
      ...(ambassador.signs ? [`Each racket signed by ${ambassador.name}`] : []),
      coaching,
      lifetime.guarantee,
    ],
    limit: 10,
    offSite: 0,
    rackets: 3,
    available: true,
  },
];

/** One icon per line of `includes`, in order (edition cards and the reserve options). */
export const includeIcons: Record<TierId, IconName[]> = {
  reserve: ["racket", "numberedTag", "measurementCard", "deliveryBox"],
  limited: ["rackets2", "numberedTag", "measurementCard", "deliveryBox"],
  invite: ["fittedCase", "measurementCard", ...(ambassador.signs ? (["penNib"] as IconName[]) : []), "court", "shieldCheck"],
};

/**
 * The One of Ten paperwork exists: the written coaching terms (CLAIMS.md row 20), the coach's signed agreement
 * (row 21), and the guarantee statement with the EU guarantee label and legal-guarantee notice on /reserve
 * (row 29). Until it is set to true, invitations stay closed even if INVITE_CODES is filled in early.
 */
export const INVITE_TERMS_READY = false;

/**
 * Whether One of Ten can be paid for: the paperwork is ready (INVITE_TERMS_READY) and invitation codes
 * exist (INVITE_CODES, server only). Until then it shows, but cannot be reserved. Even then only an
 * invitee can choose it: /reserve unlocks it with a valid code (/api/invite), and /api/reserve checks the
 * code again, and that it has not been used, before any charge.
 */
export function invitesOpen(codes: string | undefined): boolean {
  return INVITE_TERMS_READY && Boolean(codes?.split(",").some((c) => c.trim()));
}

/** Any tier above this price carries the ambassador extras (owner rule). */
export const EXTRAS_THRESHOLD_EUR = 2000;

export function tierById(id: string | null | undefined): Tier | undefined {
  return tiers.find((t) => t.id === id);
}

export function priceLabel(eur: number): string {
  return `€${eur.toLocaleString("en-IE")}`;
}

/**
 * The order in words, one pattern for every edition: "KINETIQ, one Command racket", "First 500, two Command
 * rackets", "One of Ten, three Pace rackets" (a set is one feel: it covers every racket in it).
 */
export function orderLine(tier: Tier, feelName: string): string {
  const rackets = `${countWord(tier.rackets)} ${feelName ? `${feelName} ` : ""}racket${tier.rackets > 1 ? "s" : ""}`;
  return `${tier.name}, ${rackets}`;
}

/** A name for places that take plain text only (Stripe's description and metadata): no-break spaces as spaces. */
export const plainText = (s: string) => s.replace(/\u00a0/g, " ");

/** Delivery countries offered in the address form (EU, EEA, Switzerland, UK and micro-states). */
export const deliveryCountries: [code: string, name: string][] = [
  ["AD", "Andorra"], ["AT", "Austria"], ["BE", "Belgium"], ["BG", "Bulgaria"], ["HR", "Croatia"], ["CY", "Cyprus"],
  ["CZ", "Czechia"], ["DK", "Denmark"], ["EE", "Estonia"], ["FI", "Finland"], ["FR", "France"],
  ["DE", "Germany"], ["GR", "Greece"], ["HU", "Hungary"], ["IS", "Iceland"], ["IE", "Ireland"],
  ["IT", "Italy"], ["LV", "Latvia"], ["LI", "Liechtenstein"], ["LT", "Lithuania"], ["LU", "Luxembourg"],
  ["MT", "Malta"], ["MC", "Monaco"], ["NL", "Netherlands"], ["NO", "Norway"], ["PL", "Poland"],
  ["PT", "Portugal"], ["RO", "Romania"], ["SM", "San Marino"], ["SK", "Slovakia"], ["SI", "Slovenia"],
  ["ES", "Spain"], ["SE", "Sweden"], ["CH", "Switzerland"], ["GB", "United Kingdom"],
];

export const deliveryCountryCodes = new Set(deliveryCountries.map(([c]) => c));
