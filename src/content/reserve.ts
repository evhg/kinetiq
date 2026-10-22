import { countWord } from "@/content/lineup";
import { site } from "@/content/site";

// Words on /reserve and /reserved. The structure follows a car-maker reservation page.
export const reserveCopy = {
  pageTitle: "Reserve",
  includedWith: (edition: string) => `Included with ${edition}`,
  galleryLabel: "Edition gallery",
  previousImage: "Previous image",
  nextImage: "Next image",
  chooseLegend: "Choose your edition",
  soldOut: "Sold out",
  /** Under InviQtus's includes while no invitations exist (its status still reads "Invite Only"). */
  invitesClosedNote: "Invitations open soon.",
  /** InviQtus is shown to everyone but chosen only with an invitation code. */
  invite: {
    ask: "Have an invitation?",
    label: "Invitation code",
    unlock: "Unlock",
    checking: "Checking",
    accepted: "Invitation accepted. InviQtus is yours to reserve.",
    acceptedStatus: "Invited",
    invalid: "That invitation code is not valid.",
    offline: "The code could not be checked. Please try again.",
  },
  feelLegend: (rackets: number) =>
    rackets === 1 ? "Your feel" : rackets === 2 ? "Your feel, for both rackets" : `Your feel, for all ${countWord(rackets)} rackets`,
  feelHint: (rackets: number) =>
    rackets === 1
      ? "Chosen before your racket is moulded."
      : rackets === 2
        ? "Both rackets are moulded in the feel you choose."
        : `All ${countWord(rackets)} rackets are moulded in the feel you choose.`,
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
  /** The order and its total, stated directly above Place Reservation ("VanQuish, two Command rackets."). */
  placeDue: (order: string, price: string) => `${order}. Due today ${price}.`,
  fineprint: "Charged in full today. Payments by Stripe.",
  /** Shown instead of the fine print while card payments are off (no Stripe key: the preview). */
  previewLine: "Reservations open at launch. Nothing is charged in this preview.",
  errors: {
    checkCard: "Please check your card details.",
    generic: "Something went wrong. Nothing was charged.",
    cardUnavailable: "The card field could not load. Please reload the page. Nothing was charged.",
    notCharged: "Your card was not charged. Please try again.",
  },
  stickyPay: site.payLabel,
  confirmationHeadline: "Reserved. Now we make it.",
  /** After payment; `rackets` is unknown when /reserved cannot tell the edition. */
  confirmationBody: (rackets?: number) =>
    rackets && rackets > 1
      ? `Your receipt is on its way to your inbox. Your ${countWord(rackets)} rackets ship in ${site.shipMonth}, each with its serial number and measurement card. Fully refundable until then.`
      : `Your receipt is on its way to your inbox. Your KINETIQ ships in ${site.shipMonth} with its serial number and measurement card. Fully refundable until then.`,
  receiptSent: (email: string) => `Receipt sent to ${email}.`,
  /** A short reference the buyer can quote: KQ- and the last 8 characters of the payment's id. */
  reference: (paymentId: string) => `Reservation KQ-${paymentId.slice(-8).toUpperCase()}`,
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
