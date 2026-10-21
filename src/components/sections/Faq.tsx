import { site } from "@/content/site";

const faqs = [
  {
    q: "What do I pay today?",
    a: `The full price, ${site.priceLabel}. Your racket is reserved from the first production run.`,
  },
  { q: "When does it ship?", a: "January 2027, in the order reservations were made." },
  { q: "Can I change my mind?", a: `Yes. ${site.refundLabel}, no questions asked.` },
  { q: "What does shipping cost?", a: "Shipping is free in Europe. Duties and import VAT are included in the price." },
  {
    q: "Command or Pace?",
    a: "If you win by placement and want a soft, easy feel, choose Command. If you build pressure and want more power when the moment is right, choose Pace.",
  },
  {
    q: "Is it really one piece?",
    a: "Yes. Face, frame, throat and core come out of the mould as a single part. The only thing added afterwards is the grip.",
  },
];

export function Faq() {
  return (
    <section className="section faq" aria-labelledby="faq-title">
      <h2 id="faq-title" className="display-2">
        Questions
      </h2>
      <div className="faq-list">
        {faqs.map((f) => (
          <details key={f.q}>
            <summary>{f.q}</summary>
            <p>{f.a}</p>
          </details>
        ))}
      </div>
    </section>
  );
}
