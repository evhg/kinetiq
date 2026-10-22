import { Fragment } from "react";

/**
 * Text whose hyphenated words never break at the hyphen ("laser-marked", "Ultra-precision", "space-grade").
 * Archivo and Saira have no non-breaking hyphen (U+2011), so each such word is kept whole with a nowrap span
 * instead of a glyph from a fallback font.
 */
export function Hyphens({ text }: { text: string }) {
  return text.split(/(\S+-\S+)/).map((part, i) =>
    i % 2 ? (
      <span key={i} style={{ whiteSpace: "nowrap" }}>
        {part}
      </span>
    ) : (
      <Fragment key={i}>{part}</Fragment>
    ),
  );
}
