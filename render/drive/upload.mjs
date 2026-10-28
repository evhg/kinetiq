// Uploads render masters to the owner's Google Drive ("KINETIQ masters"), mirroring their folder layout in the
// file names. Needs KQ_DRIVE_URL and KQ_DRIVE_KEY (render/drive/README.md). Skips files already uploaded with the
// same size. Usage: node render/drive/upload.mjs <file or folder> [...]
import { readdirSync, statSync, openSync, readSync, closeSync } from "node:fs";
import { join, relative, resolve } from "node:path";

const url = process.env.KQ_DRIVE_URL, key = process.env.KQ_DRIVE_KEY;
if (!url || !key) { console.error("Set KQ_DRIVE_URL and KQ_DRIVE_KEY (render/drive/README.md)."); process.exit(1); }
const root = resolve(process.env.KQ_RENDER_OUT || "/home/user/kinetiq-render-out");
const CHUNK = 32 * 1024 * 1024; // a multiple of 256 KiB, as Drive's resumable upload requires

async function session() {
  const r = await fetch(url, { method: "POST", body: JSON.stringify({ key }), redirect: "follow" });
  const j = await r.json();
  if (!j.ok) throw new Error("Drive web app refused: " + j.error);
  return j;
}

function files(p) {
  const s = statSync(p);
  if (s.isFile()) return [p];
  return readdirSync(p).flatMap((n) => files(join(p, n)));
}

async function existing(token, folderId, name) {
  const q = encodeURIComponent(`name='${name.replace(/'/g, "\\'")}' and '${folderId}' in parents and trashed=false`);
  const r = await fetch(`https://www.googleapis.com/drive/v3/files?q=${q}&fields=files(id,size)`, { headers: { Authorization: `Bearer ${token}` } });
  return (await r.json()).files?.[0];
}

async function upload(token, folderId, path, name) {
  const size = statSync(path).size;
  const start = await fetch("https://www.googleapis.com/upload/drive/v3/files?uploadType=resumable&fields=id,size", {
    method: "POST",
    headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json", "X-Upload-Content-Length": String(size) },
    body: JSON.stringify({ name, parents: [folderId] }),
  });
  if (!start.ok) throw new Error(`start ${start.status} ${await start.text()}`);
  const loc = start.headers.get("location");
  const fd = openSync(path, "r");
  try {
    for (let off = 0; off < size; off += CHUNK) {
      const len = Math.min(CHUNK, size - off), buf = Buffer.alloc(len);
      readSync(fd, buf, 0, len, off);
      const r = await fetch(loc, { method: "PUT", headers: { "Content-Range": `bytes ${off}-${off + len - 1}/${size}` }, body: buf });
      if (![200, 201, 308].includes(r.status)) throw new Error(`chunk ${r.status} ${await r.text()}`);
    }
  } finally { closeSync(fd); }
}

const { token, folderId } = await session();
for (const arg of process.argv.slice(2)) {
  for (const f of files(resolve(arg))) {
    const name = (f.startsWith(root) ? relative(root, f) : f.split("/").pop()).replaceAll("/", "__");
    const have = await existing(token, folderId, name);
    if (have && Number(have.size) === statSync(f).size) { console.log("skip", name); continue; }
    await upload(token, folderId, f, name);
    console.log("uploaded", name, statSync(f).size);
  }
}
