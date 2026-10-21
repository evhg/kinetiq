import { readFileSync } from "node:fs";
import { join } from "node:path";
import type { Metadata } from "next";
import type { ReactNode } from "react";
import { SiteFooter, SiteHeader } from "@/components/chrome/Chrome";
import styles from "./credits.module.css";

export const metadata: Metadata = { title: "Credits" };

/** The sections of public/CREDITS.md that describe what the site shows (the rest is repo housekeeping). */
const PUBLIC_SECTIONS = ["Fonts", "Images and graphics"];

type Block =
  | { kind: "h1"; text: string }
  | { kind: "h2"; text: string }
  | { kind: "p"; text: string }
  | { kind: "table"; head: string[]; rows: string[][] }
  | { kind: "list"; items: string[] };

/** The small Markdown subset CREDITS.md uses: headings, paragraphs, pipe tables and bullet lists. */
function parse(md: string): Block[] {
  const lines = md.split("\n");
  const blocks: Block[] = [];
  const cells = (l: string) => l.trim().replace(/^\||\|$/g, "").split("|").map((c) => c.trim());
  for (let i = 0; i < lines.length; ) {
    const line = lines[i];
    if (!line.trim()) {
      i++;
    } else if (line.startsWith("# ") || line.startsWith("## ")) {
      const text = line.replace(/^#+ /, "");
      blocks.push(line.startsWith("# ") ? { kind: "h1", text } : { kind: "h2", text });
      i++;
    } else if (line.startsWith("|")) {
      const rows: string[][] = [];
      while (i < lines.length && lines[i].startsWith("|")) rows.push(cells(lines[i++]));
      blocks.push({ kind: "table", head: rows[0], rows: rows.slice(2) });
    } else if (line.startsWith("- ")) {
      const items: string[] = [];
      while (i < lines.length && (lines[i].startsWith("- ") || lines[i].startsWith("  "))) {
        if (lines[i].startsWith("- ")) items.push(lines[i].slice(2));
        else items[items.length - 1] += ` ${lines[i].trim()}`;
        i++;
      }
      blocks.push({ kind: "list", items });
    } else {
      const text: string[] = [];
      while (i < lines.length && lines[i].trim() && !/^(#|\||- )/.test(lines[i])) text.push(lines[i++].trim());
      blocks.push({ kind: "p", text: text.join(" ") });
    }
  }
  return blocks;
}

/** Inline code spans become <code>; everything else is plain text. */
function inline(text: string): ReactNode[] {
  return text.split(/(`[^`]+`)/).map((part, i) => (part.startsWith("`") ? <code key={i}>{part.slice(1, -1)}</code> : part));
}

/** Credits and licences, read from public/CREDITS.md when the page is built. */
export default function CreditsPage() {
  const blocks = parse(readFileSync(join(process.cwd(), "public/CREDITS.md"), "utf8"));
  // Keep the title and intro, then only the public sections.
  const shown: Block[] = [];
  let keep = true;
  for (const b of blocks) {
    if (b.kind === "h2") keep = PUBLIC_SECTIONS.includes(b.text);
    if (keep) shown.push(b);
  }
  return (
    <>
      <SiteHeader />
      <main id="main" className={`lift ${styles.page}`}>
        <div className={styles.inner}>
          {shown.map((b, i) =>
            b.kind === "h1" ? (
              <h1 key={i} className="t-h2">
                {b.text}
              </h1>
            ) : b.kind === "h2" ? (
              <h2 key={i} className={`t-h3 ${styles.h2}`}>
                {b.text}
              </h2>
            ) : b.kind === "p" ? (
              <p key={i} className="t-body">
                {inline(b.text)}
              </p>
            ) : b.kind === "list" ? (
              <ul key={i} className={styles.list}>
                {b.items.map((it) => (
                  <li key={it}>{inline(it)}</li>
                ))}
              </ul>
            ) : (
              <div key={i} className={styles.tableWrap}>
                <table className={styles.table}>
                  <thead>
                    <tr>
                      {b.head.map((h) => (
                        <th key={h} scope="col">
                          {h}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {b.rows.map((r) => (
                      <tr key={r[0]}>
                        {r.map((c, n) => (
                          <td key={n}>{inline(c)}</td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ),
          )}
        </div>
      </main>
      <SiteFooter />
    </>
  );
}
