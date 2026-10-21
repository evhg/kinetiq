import { site } from "@/content/site";

const COUNT_WORDS: Record<number, string> = { 2: "two", 3: "three", 4: "four", 5: "five" };

// Words on /reserve and /reserved. The structure follows a car-maker reservation page.
export const reserveCopy = {
  pageTitle: "Reserve",
  includedWith: (edition: string) => `Included with ${edition}`,
  galleryLabel: "Edition gallery",
  previousImage: "Previous image",
  nextImage: "Next image",
  chooseLegend: "Choose your edition",
  soldOut: "Sold out",
  /** InviQtus while invitations are closed (no codes yet, or the ambassador is not signed). */
  invitesClosedStatus: "Opens soon",
  invitesClosedNote: "Invitations open soon. Nothing can be reserved yet.",
  feelLegend: "Your feel",
  feelHint: "Chosen before your racket is moulded.",
  feelAll: (rackets: number) => `Applies to all ${COUNT_WORDS[rackets] ?? rackets} rackets.`,
  dueTodayLabel: "Due Today",
  trustLines: [
    site.refundLabel,
    "Free delivery in Europe, duties included",
    "Serial number and measurement card with every racket",
  ],
  inviteNote: "By invitation. Enter your code with your details.",
  formHeading: "Your details",
  fields: {
    invite: "Invitation code",
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
  /** The order and its total, stated directly above Place Reservation. */
  placeDue: (edition: string, feel: string, price: string) => `${edition}, ${feel}. Due today ${price}.`,
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
  confirmationBody: `Your receipt is on its way to your inbox. Your KINETIQ ships in ${site.shipMonth} with its serial number and measurement card. Fully refundable until then.`,
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
