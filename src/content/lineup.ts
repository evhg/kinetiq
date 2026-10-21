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
  /** Units made, or null for the open tier. */
  limit: number | null;
  /** Rackets in the box. */
  rackets: number;
  /** False shows "Sold out" and blocks payment. */
  available: boolean;
};

/**
 * The ambassador for the Invite Only extras. The owner has a touring pro in mind who is under
 * contract with another racket brand: a name, autograph or coaching session may only appear once a
 * signed agreement exists. Until then `confirmed` stays false, the name stays out of the public repo,
 * and the site shows the neutral wording. See CLAIMS.md row 21.
 */
export const ambassador = {
  confirmed: false,
  // The athlete the owner named. Fill in together with confirmed: true once a signed agreement exists.
  name: "",
  neutral: "our touring-pro ambassador",
  event: "the next Málaga P1",
};

const amb = ambassador.confirmed ? ambassador.name : ambassador.neutral;
const ambShort = ambassador.confirmed ? ambassador.name.split(" ")[0] : "our ambassador";

export const tiers: Tier[] = [
  {
    id: "reserve",
    name: "ConQuer",
    availability: "Reserve",
    priceEur: 410,
    cardLine: "The full KINETIQ. No lesser version exists. One piece, true to 15 microns, moulded in the feel you choose.",
    includes: ["One KINETIQ racket, Command or Pace", "Its own serial number and measurement card"],
    limit: null,
    rackets: 1,
    available: true,
  },
  {
    id: "limited",
    name: "VanQuish",
    availability: "Limited",
    priceEur: 990,
    cardLine: "Numbered 001 to 500 and laser-marked on the throat. First out of the mould. Never made again.",
    includes: [
      "Your number, 001 to 500, laser-marked on the throat",
      "One of the first 500 out of the mould",
      "Measurement card numbered to match",
      "First to ship, January 2027",
    ],
    limit: 500,
    rackets: 1,
    available: true,
  },
  {
    id: "invite",
    name: "InviQtus",
    availability: "Invite Only",
    priceEur: 2900,
    cardLine: "Fifty sets of three. By invitation.",
    includes: [
      `Three KINETIQ rackets, each signed by ${amb}`,
      `A one-on-one coaching session with ${ambShort} at ${ambassador.event}`,
      "Laser-marked 01 to 50, in a fitted case",
    ],
    limit: 50,
    rackets: 3,
    available: true,
  },
];

/** One icon per line of `includes`, in order (edition cards and the reserve options). */
export const includeIcons: Record<TierId, IconName[]> = {
  reserve: ["mould", "measurementCard"],
  limited: ["numberedTag", "mould", "measurementCard", "deliveryBox"],
  invite: ["penNib", "court", "fittedCase"],
};

/**
 * Whether InviQtus can be paid for: invitation codes exist (INVITE_CODES, server only). Until then it
 * shows, but cannot be reserved. The ambassador stays unnamed until signed (ambassador.confirmed), which
 * changes only the wording, not whether invitations open.
 */
export function invitesOpen(codes: string | undefined): boolean {
  return Boolean(codes?.split(",").some((c) => c.trim()));
}

/** Any tier above this price carries the ambassador extras (owner rule). */
export const EXTRAS_THRESHOLD_EUR = 2000;

export function tierById(id: string | null | undefined): Tier | undefined {
  return tiers.find((t) => t.id === id);
}

export function priceLabel(eur: number): string {
  return `€${eur.toLocaleString("en-IE")}`;
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
