import { claims } from "@/content/claims";

export function Swiss() {
  return (
    <section className="section swiss" aria-labelledby="swiss-title">
      <svg className="swiss-cross" viewBox="0 0 32 32" role="img" aria-label="Swiss flag">
        <rect width="32" height="32" rx="2" fill="#DA291C" />
        <path d="M13 6h6v7h7v6h-7v7h-6v-7H6v-6h7z" fill="#fff" />
      </svg>
      <h2 id="swiss-title" className="display">
        {claims.swissMade}
      </h2>
      <p className="lead">{claims.swissDetail}</p>
      <ul className="swiss-facts">
        <li>{claims.worldFirstSwiss}</li>
        <li>{claims.patented}</li>
        <li>Foam made on site. Carbon moulded on site. Every racket measured on site.</li>
      </ul>
    </section>
  );
}
