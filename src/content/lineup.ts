// The lineup, modelled on a reservation page with three tiers of rising exclusivity.
// Names, prices, limits and extras are owner decisions tracked in CLAIMS.md.
// Tier ids are stable keys; names and copy can change freely.

import type { IconName } from "@/components/graphics/Icons";

export type TierId = "reserve" | "limited" | "invite";

export type Tier = {
  id: TierId;
  name: string;
  availability: "Reserve" | "Limited" | "Invite Only";
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
  /** Rackets in the box. A set is one feel: every racket in it is Command, or every racket is Pace. */
  rackets: number;
  /** False shows "Sold out" and blocks payment. */
  available: boolean;
};

/**
 * Durability (owner, 2026-10-22). Every KINETIQ is built to last five years; only InviQtus carries a
 * guarantee. The fine print travels with each line wherever it is shown: beside it on /reserve, and
 * through the footnote marker (`mark`) on the landing page. CLAIMS.md rows 26 and 29: the design life
 * needs an independent fatigue report (promised before shipping, never claimed as done), and the
 * guarantee needs its written statement and the EU harmonised guarantee label before InviQtus can be
 * paid for (INVITE_TERMS_READY). Never "lifetime guarantee", never "sustainable", and never a guarantee
 * for ConQuer or VanQuish.
 */
export const lifetime = {
  line: "Built to last five years",
  /** The design life as an edition property (ConQuer and VanQuish includes), never as a perk or cover. */
  include: "A five-year design life",
  /** Footnote marker from a five-year line to `fine`. */
  mark: "*",
  fine: "Five years at two 90-minute sessions a week (about 780 hours), ball strikes only, to be verified in independent fatigue tests before we ship. A design life, not a guarantee; your legal guarantee rights are unaffected.",
  /** Its scope is the written statement's (CLAIMS.md row 29): KINETIQ guarantees all three rackets of the set. */
  guarantee: "A five-year KINETIQ guarantee on all three rackets",
  /**
   * Footnote marker from the guarantee to its own fine-print line (guaranteeTerms, then legal), kept apart from the
   * design life's `fine`, which says "not a guarantee" (* is the design life, \u2020 the sealed core's comparison).
   */
  guaranteeMark: "\u2021",
  guaranteeTerms: "InviQtus guarantee terms come in writing with every invitation.",
  legal: "Your legal guarantee rights are unaffected.",
};

/**
 * The coach behind the InviQtus sessions (owner, 2026-10-22: he has agreed to ten sessions, one per
 * set). The site names him only by his first name and surname exactly as he approves them in writing:
 * never a nickname, and never his family. Until `fullName` is filled in, `name` is the neutral wording.
 * Signed rackets are offered only once he has agreed in writing to sign them (`signs`). CLAIMS.md row 21.
 */
const COACH_FULL_NAME = "";
export const ambassador = {
  /** He has agreed to the ten coaching sessions, so the InviQtus extras can be offered. */
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
  event: "one of ten sessions, one per set",
};

const COUNT_WORDS: Record<number, string> = { 1: "one", 2: "two", 3: "three", 4: "four", 5: "five", 10: "ten" };
export const countWord = (n: number) => COUNT_WORDS[n] ?? String(n);

// "Exclusive" is the owner's word; the format (one-on-one or a small group) waits for the written terms (row 20).
const coaching = ambassador.named
  ? `One of ten exclusive coaching sessions with ${ambassador.name}`
  : "One of ten exclusive coaching sessions";

export const tiers: Tier[] = [
  {
    id: "reserve",
    name: "ConQuer",
    availability: "Reserve",
    priceEur: 410,
    cardLine: "The full KINETIQ. No lesser version exists. Unibody, true to 15 microns, moulded in the feel you choose.",
    includes: ["One KINETIQ racket, Command\u00a0or\u00a0Pace", "Its own serial number and measurement card", lifetime.include],
    limit: null,
    offSite: 0,
    rackets: 1,
    available: true,
  },
  {
    id: "limited",
    name: "VanQuish",
    availability: "Limited",
    priceEur: 990,
    cardLine: "A matched pair. Two Command or two Pace, numbered 001\u00a0to\u00a0500 on both throats. Never made again.",
    includes: [
      "Two KINETIQ rackets, both Command or both\u00a0Pace",
      "Your set number, 001\u00a0to\u00a0500, laser-marked on both throats",
      "Two measurement cards, numbered to\u00a0match",
      "First out of the mould. First to ship, January\u00a02027",
      lifetime.include,
    ],
    limit: 500,
    offSite: 0,
    rackets: 2,
    available: true,
  },
  {
    id: "invite",
    name: "InviQtus",
    availability: "Invite Only",
    priceEur: 2900,
    cardLine: "Ten sets of three. By invitation.",
    includes: [
      "Three KINETIQ rackets, laser-marked 01\u00a0to\u00a010, in a fitted case",
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
  reserve: ["mould", "measurementCard", "fiveYears"],
  limited: ["rackets2", "numberedTag", "measurementCard", "deliveryBox", "fiveYears"],
  invite: ["fittedCase", ...(ambassador.signs ? (["penNib"] as IconName[]) : []), "court", "shieldCheck"],
};

/** The fine print that belongs to an edition's includes: the design life, or InviQtus's guarantee. */
export function includesFine(id: TierId): string {
  return id === "invite" ? `${lifetime.guaranteeTerms} ${lifetime.legal}` : lifetime.fine;
}

/**
 * The InviQtus paperwork exists: the written coaching terms (CLAIMS.md row 20), the coach's signed agreement
 * (row 21), and the guarantee statement with the EU guarantee label and legal-guarantee notice on /reserve
 * (row 29). Until it is set to true, invitations stay closed even if INVITE_CODES is filled in early.
 */
export const INVITE_TERMS_READY = false;

/**
 * Whether InviQtus can be paid for: the paperwork is ready (INVITE_TERMS_READY) and invitation codes
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
 * The order in words: "ConQuer, Command" for one racket, "VanQuish, two Command rackets" for a set
 * (the feel covers every racket in it).
 */
export function orderLine(tier: Tier, feelName: string): string {
  return tier.rackets > 1 ? `${tier.name}, ${countWord(tier.rackets)} ${feelName} rackets` : `${tier.name}, ${feelName}`;
}

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
