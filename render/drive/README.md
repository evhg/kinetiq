# Masters on Google Drive

Render masters (16-bit PNGs and sequence frames) are too large for git. They live in the owner's Google Drive,
folder "KINETIQ masters". Nothing is installed anywhere: a small Google Apps Script web app hands the render
machine a short-lived Drive token that can only see files this script created (`drive.file`), and
`upload.mjs` (plain Node, no packages) uploads with Drive's resumable upload.

## One-time setup (owner, in the browser, ~5 minutes)
1. Open https://script.google.com, signed in to the Google account that should hold the masters. New project,
   name it "KINETIQ masters".
2. Paste `Code.gs` into the editor. Project Settings (gear) → tick "Show appsscript.json manifest file in
   editor", then paste `appsscript.json` over it. Save.
3. Choose the `setup` function in the toolbar and Run. Allow access (Google warns that the app is unverified,
   because it is your own: Advanced → Go to KINETIQ masters). The log shows `UPLOAD_KEY: …`.
4. Deploy → New deployment → type Web app, execute as Me, who has access Anyone → Deploy. Copy the web app URL.
5. In the Claude cloud environment settings (environment menu in the session title bar → Edit), add two
   environment variables: `KQ_DRIVE_URL` (the web app URL) and `KQ_DRIVE_KEY` (the UPLOAD_KEY). Never paste
   them into a chat or commit them.

## Use
`node render/drive/upload.mjs /home/user/kinetiq-render-out/masters` after every final render (skips files
already in Drive with the same size). The key only fetches a one-hour token limited to this folder's files;
to revoke it, delete the deployment or change UPLOAD_KEY (run `setup` again after deleting the property).
