# Agent learnings

What went wrong while agents built this site (October 2026), and the rule that prevents each problem.
Agents read `CLAUDE.md` automatically; the most important rules from this page are repeated there.

## What "Failed" means in the background-task panel

The panel marks any command that exits non-zero as Failed. Across the build, agents ran 3,237 shell
commands and 51 exited non-zero. None of them broke the site. They fall into four groups:

| Group | Count | What happened |
| --- | --- | --- |
| Normal test iterations | ~30 | A check script exited 1 on a failed assertion, a Playwright locator matched two elements, a Blender script raised after an edit. The next command fixed it. |
| Watches that ran out | several | A Monitor or wait loop reached its time window (30 minutes at most) while a render still had an hour to go. The render itself finished fine (one took 78 minutes). |
| Processes stopped on purpose | 5 | An agent stopped a render or server it no longer wanted; the kill also hit the agent's own shell (exit code 144). |
| Blocked by the harness | 8 | Foreground `sleep` (7 times) and one `rm` whose path depended on an unset variable. |

## Long jobs (renders, builds, harness runs)

- **A subagent's background tasks die when the subagent returns.** A two-hour render chain started with
  `run_in_background` is killed the moment its agent finishes. For anything that must outlive the agent,
  detach it (`setsid nohup script.sh > log 2>&1 < /dev/null &`), write progress to a file, and have
  whoever needs the result watch the output file.
- **Wait for the output file, not the process.** A watcher that gives up when the render process is gone
  raised a false alarm between two test renders. Wait until the final file exists and its size stops
  changing; a PNG that is still being written fails to decode (`vipspng: libpng read error`).
- **No foreground `sleep`.** The harness blocks `sleep N; cat log`. Use a background `until` loop that
  exits when the condition is true, or a Monitor.
- **Monitors last at most 30 minutes.** A Cycles final at 3200 x 1800 took 25 to 78 minutes on this
  4-core machine, so expect to re-arm. End watch loops with an explicit status line (and `|| true`), so a
  window that expires doesn't read as a failure.
- **A pipeline that ends in `grep` exits 1 when nothing matches**, even when "no match" means success
  (`render ... | grep Error`). Add `|| true`, or use `grep -c`.

## Stopping processes

- **Never kill by matching command-line text.** A loop like `case "$cmdline" in *K01-hero-frame.py*) kill`
  also matches the shell running the loop, which then kills itself (exit 144). This happened five
  times. Record the PID when you start something (`echo $! > job.pid`) and kill that PID, or match the
  process name in `/proc/<pid>/comm` (see Notes in `CLAUDE.md` for the Next.js server).
- **Check the port before trusting a server.** An old `next start` still held port 3300; the new one
  failed with `EADDRINUSE` in its log, and smoke tests quietly hit the stale build. Read the start log,
  stop the old server by PID, and confirm with a route that only the new build has.

## Several agents, one working tree

- **One writer at a time per file set.** A review fixer and an integration step edited `stills.json` and
  `Precision.tsx` at the same time. Hold your own edits until the other agent finishes, or give each
  agent its own git worktree.
- **Never `git stash` or `git checkout` a shared tree** while other agents are editing it. One fixer
  stashed for a few seconds to compare against HEAD; it came back intact, but it could have lost
  another agent's edits.
- **Commit only verified states.** The commit hook asks for a commit when a turn ends. If an agent is
  still mid-edit, wait for it to finish rather than committing half-applied changes.

## Shared machine (4 cores)

- **One Blender render at a time.** Two parallel renders each run at roughly half speed and both miss
  their windows. Run every render through a lock: `flock render.lock python shots/<shot>.py ...`.
- **Keep previews small** (960 x 540, 24 to 48 samples) and render finals only after a critic pass.
- **Chromium can crash (`Target crashed`) under memory pressure** while renders run. Use one browser at
  a time, and close contexts between viewports.

## Playwright on this site

- **The site has duplicate controls by design:** the compact header Reserve Now, the hero CTA, and on
  /reserve the phone sticky bar repeats Pay with Card. Scope locators (`main a[href^="/reserve"]`,
  `main button[aria-controls$=-form]`) or use `getByRole` with an exact name; otherwise strict mode
  fails or the click waits on a hidden, `aria-hidden` copy until it times out.
- **Browser revision mismatch:** if Playwright asks for a Chromium build that isn't installed under
  `/opt/pw-browsers`, launch with `executablePath` pointing at the installed one. Never download browsers.

## Shell safety

- **Chain with `&&`, or use `set -e`.** `rsync` isn't installed. A copy chain failed, the `cd` after it
  failed too, and the following commands wrote stub files into the repo root.
- **Guard variables in destructive paths:** `rm -rf "${OUT:?}/tmp"`. The harness blocks an `rm` whose
  target it can't resolve.

## Renders and stills

- **The render kit and the 16-bit masters live only in the session scratchpad**, which is deleted with
  the container. `public/stills/` holds the exported AVIF and WebP files, but re-exporting a crop or
  re-rendering a shot needs the masters and the scripts.
- **Check the fill rule before a final**, not after: early renders (K01, K05) were 61 to 82% flat black and
  had to be redone. Run `fillcheck.py` on previews, on the page crops (phone, card) as well as the full
  frame.
- **Brief every shot with its page constraints:** the crop boxes it must survive (phone, card), where the
  words sit, and which shots must register pixel for pixel (base and full variants, K03b and K03).
- **One critic pass per shot pays off.** Every shot a critic reviewed came back clearly better (K05
  went from a dim racket on a starfield to a lit, woven face with a fine laser line).
