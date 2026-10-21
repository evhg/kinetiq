// The lineup, modelled on a reservation page with three tiers of rising exclusivity.
// Names, prices, limits and extras are owner decisions tracked in CLAIMS.md.
// Tier ids are stable keys; names and copy can change freely.

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
 * The ambassador for the Invite Only extras. The owner named Paquito Navarro, but he is a
 * Bullpadel athlete with a 2026 signature racket: his name, autograph and a coaching session
 * may only appear once a signed agreement exists. Until then `confirmed` stays false and the
 * site shows the neutral wording. See CLAIMS.md.
 */
export const ambassador = {
  confirmed: false,
  name: "Paquito Navarro",
  neutral: "our Premier Padel ambassador",
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
    cardLine: "Numbered 001 to 500. Includes ConQuer, plus your number laser-marked on the throat. First out of the mould. Never made again.",
    includes: [
      "Your number, 001 to 500, laser-marked on the throat",
      "From the first rackets out of the mould",
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
    cardLine: `Three rackets, each autographed by ${amb}. Then train one-on-one with ${ambShort} at ${ambassador.event}.`,
    includes: [
      `Three KINETIQ rackets, each autographed by ${amb}`,
      `A one-on-one session with ${ambShort} at ${ambassador.event}`,
      "Numbered 01 to 50, in a fitted case",
      "Everything in VanQuish, on all three",
    ],
    limit: 50,
    rackets: 3,
    available: true,
  },
];

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
  ["AT", "Austria"], ["BE", "Belgium"], ["BG", "Bulgaria"], ["HR", "Croatia"], ["CY", "Cyprus"],
  ["CZ", "Czechia"], ["DK", "Denmark"], ["EE", "Estonia"], ["FI", "Finland"], ["FR", "France"],
  ["DE", "Germany"], ["GR", "Greece"], ["HU", "Hungary"], ["IS", "Iceland"], ["IE", "Ireland"],
  ["IT", "Italy"], ["LV", "Latvia"], ["LI", "Liechtenstein"], ["LT", "Lithuania"], ["LU", "Luxembourg"],
  ["MT", "Malta"], ["MC", "Monaco"], ["NL", "Netherlands"], ["NO", "Norway"], ["PL", "Poland"],
  ["PT", "Portugal"], ["RO", "Romania"], ["SM", "San Marino"], ["SK", "Slovakia"], ["SI", "Slovenia"],
  ["ES", "Spain"], ["SE", "Sweden"], ["CH", "Switzerland"], ["GB", "United Kingdom"], ["AD", "Andorra"],
];

export const deliveryCountryCodes = new Set(deliveryCountries.map(([c]) => c));
