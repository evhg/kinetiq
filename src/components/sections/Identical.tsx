import { claims } from "@/content/claims";
import { HOLE_RADIUS } from "@/lib/racket-shape";

const card = [
  ["Model", "Command"],
  ["Serial", "KQ-C-000142"],
  ["Weight", "355.2 g"],
  ["Balance", "250.4 mm"],
  ["Thickness", "38.00 mm"],
  ["Surface deviation", "0.011 mm"],
] as const;

export function Identical() {
  const r = HOLE_RADIUS * 400;
  return (
    <section className="section identical" aria-labelledby="identical-title">
      <div className="holes">
        <svg className="holes-art" viewBox="0 0 400 260" aria-hidden="true">
          {[0, 1, 2].map((i) => {
            const cx = 80 + i * 120;
            const cy = 130;
            return (
              <g key={i}>
                {[1.25, 1.55, 1.85, 2.15].map((k) => (
                  <circle key={k} cx={cx} cy={cy} r={r * k} className="fibre-ring" />
                ))}
                <circle cx={cx} cy={cy} r={r} className="hole" />
              </g>
            );
          })}
        </svg>
        <div>
          <h3 className="display-3">{claims.worldFirstMouldedHoles}</h3>
          <p>{claims.mouldedHolesDetail}</p>
        </div>
      </div>

      <div className="identical-main">
        <div>
          <h2 id="identical-title" className="display-2">
            {claims.identical.headline}
          </h2>
          <p className="lead">{claims.identical.detail}</p>
          <p>
            {claims.balanceMoulded} {claims.measurementCard}
          </p>
        </div>
        <figure className="card" aria-label="Example measurement card">
          <div className="card-inner">
            <p className="card-brand">KINETIQ</p>
            <dl className="card-rows">
              {card.map(([k, v]) => (
                <div key={k}>
                  <dt>{k}</dt>
                  <dd>{v}</dd>
                </div>
              ))}
            </dl>
            <p className="card-foot">Measured in St. Gallen, Switzerland</p>
          </div>
          <figcaption>Every racket ships with a card like this, with its own numbers.</figcaption>
        </figure>
      </div>
    </section>
  );
}
