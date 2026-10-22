/**
 * Words on the NDA gate (/nda; src/proxy.ts shows it in place of every page until the visitor has declared the NDA).
 * The gate is seen before the NDA, so nothing here may describe the product: no claims, prices, editions or
 * materials. Its HTML is also what a link preview reads, hence the plain title and description.
 */
export const ndaCopy = {
  meta: {
    title: "KINETIQ",
    description: "Confidential. Shared under NDA.",
  },
  eyebrow: "Confidential",
  title: "Shared under NDA.",
  ask: {
    lead: "Have you signed the KINETIQ non-disclosure agreement?",
    yes: "Yes, I have signed it",
    no: "Not yet",
  },
  email: {
    lead: "Enter your email to open the presentation.",
    label: "Email",
    submit: "Open the presentation",
    busy: "Opening",
    note: "Your email is kept in a cookie on this device, so you only do this once.",
    invalid: "Enter a valid email address.",
    failed: "The presentation did not open. Please try again.",
    blocked: "This browser did not keep the cookie. Allow cookies for this site, then try again.",
    back: "Back",
  },
  notYet: {
    lead: "The presentation opens once the NDA is signed. Ask your KINETIQ contact for the agreement.",
    back: "Back",
  },
};
