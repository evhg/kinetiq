import { countWord, tierById, type TierId } from "@/content/lineup";
import { site, type FeelId } from "@/content/site";

// Words on /reserve and /reserved. The structure follows a car-maker reservation page.
// The editions are KINETIQ, First 500 and One of Ten (names in lineup.ts, with their no-break spaces): every
// edition holds the same racket, so nothing here describes one edition's racket as different from another's.

const name = (id: TierId) => tierById(id)?.name ?? site.name;

/** Under each feel on the picker (16 px minimum): what we made, then what it does for the player (CLAIMS.md row 16). */
const feelLines: Record<FeelId, string> = {
  command: "It gives a little as it meets the ball, and helps you place it.",
  pace: "It is stiffer and quicker, and gives you more power through the ball.",
};

export const reserveCopy = {
  pageTitle: "Reserve",
  /**
   * The options column's h1. It names the racket, never the edition: the edition cards below name each one, and the
   * KINETIQ edition carries the brand's name, so the chrome around it varies instead of repeating it.
   */
  columnTitle: `Reserve your ${site.name}`,
  /** The sticky bar's first line, by the number of rackets: "One racket", "Two rackets", "Three rackets". */
  barCount: (rackets: number) => {
    const w = countWord(rackets);
    return `${w.charAt(0).toUpperCase()}${w.slice(1)} racket${rackets > 1 ? "s" : ""}`;
  },
  /** Over each card's includes. The card already names its edition, so the head never repeats it. */
  included: "Included",
  galleryLabel: "Edition gallery",
  previousImage: "Previous image",
  nextImage: "Next image",
  chooseLegend: "Choose your edition",
  soldOut: "Sold out",
  /** Under One of Ten's includes while no invitations exist (its status still reads "Invite Only"). */
  invitesClosedNote: "Invitations open soon.",
  /** One of Ten is shown to everyone but chosen only with an invitation code. */
  invite: {
    ask: "Have an invitation?",
    label: "Invitation code",
    unlock: "Unlock",
    checking: "Checking",
    accepted: `Invitation accepted. You can now reserve ${name("invite")}.`,
    acceptedStatus: "Invited",
    invalid: "That invitation code is not valid.",
    offline: "The code could not be checked. Please try again.",
  },
  feelLegend: (rackets: number) =>
    rackets === 1 ? "Your feel" : rackets === 2 ? "Your feel, for both rackets" : `Your feel, for all ${countWord(rackets)} rackets`,
  /** One line per feel, under its name, sub and spec (site.ts `feels`). */
  feelLines,
  /** Under the two feels: guidance, not a result (CLAIMS.md row 16). */
  feelHelper: "Command suits a game built on placement, and Pace suits a game built on pressure.",
  /** Under the helper, by the number of rackets. No-break spaces keep "in the feel you choose." on one line. */
  feelHint: (rackets: number) =>
    rackets === 1
      ? "Your racket is moulded in\u00a0the\u00a0feel\u00a0you\u00a0choose."
      : rackets === 2
        ? "Both rackets are moulded in\u00a0the\u00a0feel\u00a0you\u00a0choose."
        : `All ${countWord(rackets)} rackets are moulded in\u00a0the\u00a0feel\u00a0you\u00a0choose.`,
  dueTodayLabel: "Due Today",
  trustLines: [
    site.refundLabel,
    "Free delivery in Europe, duties included",
    "Serial number and measurement card with every racket",
  ],
  formHeading: "Your details",
  fields: {
    name: "Full name",
    email: "Email",
    line1: "Address",
    line2: "Apartment, suite (optional)",
    postalCode: "Postal code",
    city: "City",
    country: "Country",
    countryPlaceholder: "Select",
    card: "Card",
  },
  feelRequired: "Choose Command or Pace.",
  processing: "Placing reservation…",
  cardPreview: "Card payments open at launch. Nothing can be charged yet.",
  /**
   * The order and its total, stated directly above Place Reservation: "KINETIQ, one Command racket. Due today €410.",
   * "First 500, two Command rackets. Due today €990.", "One of Ten, three Pace rackets. Due today €2,900.". No-break
   * spaces keep "Due today" and the price on one line.
   */
  placeDue: (order: string, price: string) => `${order}. Due\u00a0today\u00a0${price}.`,
  errors: {
    checkCard: "Please check your card details.",
    generic: "Something went wrong. Nothing was charged.",
    cardUnavailable: "The card field could not load. Please reload the page. Nothing was charged.",
    notCharged: "Your card was not charged. Please try again.",
  },
  stickyPay: site.payLabel,
  /** After payment, by the number of rackets in the order; unknown when /reserved cannot tell the edition. */
  confirmationHeadline: (rackets?: number) =>
    rackets === undefined
      ? "Thank you. Your reservation is complete."
      : rackets > 1
        ? "Thank you. Your rackets are reserved."
        : "Thank you. Your racket is reserved.",
  /**
   * After payment, by edition: what ships, when, and what comes with it; unknown when /reserved cannot tell the
   * edition. "Until then" is the shipping date it follows (CLAIMS.md row 23). The receipt is said once, here: with the
   * address when the page has it (the in-place confirmation), "your inbox" when it does not (/reserved).
   */
  confirmationBody: (tierId?: TierId, email?: string) => {
    const receipt = email ? `Your receipt is on its way to ${email}.` : "Your receipt is on its way to your inbox.";
    const tier = tierById(tierId);
    switch (tier?.id) {
      case "reserve":
        return `${receipt} Your ${site.name} ships in ${site.shipMonth}, after the ${name("limited")} sets, with its serial number and measurement card. It is fully refundable until then.`;
      case "limited":
        return `${receipt} Your set is one of the ${tier.name}, and it ships first, in ${site.shipMonth}, with its number on both throats and two measurement cards to match. It is fully refundable until then.`;
      case "invite":
        return `${receipt} Your ${countWord(tier.rackets)} rackets ship in ${site.shipMonth} with ${countWord(tier.rackets)} measurement cards, in a fitted case marked with your set number, and we will write to you about your coaching session. They are fully refundable until then.`;
      default:
        return `${receipt} We ship in ${site.shipMonth}, and your reservation is fully refundable until then.`;
    }
  },
  /**
   * @deprecated Retired (round 2): `confirmationBody` now names the address, so the receipt is said once. Delete it
   * with its last use, ReservePanel.tsx's `styles.sent` line.
   */
  receiptSent: (email: string) => `Receipt sent to ${email}.`,
  /**
   * The reference the buyer can quote, "Reservation KQ-1A2B3C4D". /api/reserve makes it (KQ- and 8 hex characters)
   * and stores it in the payment's description and `metadata[reference]`, so it prints on Stripe's receipt and the
   * owner can look it up. Pass that reference, never the payment's id.
   */
  reference: (ref: string) => `Reservation ${ref}`,
  reserved: {
    pageTitle: "Reserved",
    checking: "Checking your reservation.",
    failedHeadline: "Your card was not charged.",
    failedBody: "The bank did not confirm the payment, so nothing was reserved and nothing was charged.",
    retry: "Try again",
    noneHeadline: "No reservation found.",
    noneBody: "Nothing was reserved or charged from this link.",
    back: `Back to ${site.name}`,
  },
};
