/**
 * KINETIQ masters uploader: a Google Apps Script web app the owner deploys once, in the browser (no install).
 * The render machine calls it with the shared key and gets a short-lived Drive token (drive.file scope: this
 * script can see only files it created), then uploads the large masters straight to Google Drive with Drive's
 * resumable upload. Setup: render/drive/README.md.
 */
const FOLDER_NAME = "KINETIQ masters";

function doPost(e) {
  const body = JSON.parse(e.postData.contents || "{}");
  const key = PropertiesService.getScriptProperties().getProperty("UPLOAD_KEY");
  if (!key || body.key !== key) return json({ ok: false, error: "forbidden" });
  return json({ ok: true, token: ScriptApp.getOAuthToken(), folderId: folderId() });
}

function folderId() {
  const props = PropertiesService.getScriptProperties();
  const id = props.getProperty("FOLDER_ID");
  if (id) return id;
  const res = UrlFetchApp.fetch("https://www.googleapis.com/drive/v3/files?fields=id", {
    method: "post",
    contentType: "application/json",
    headers: { Authorization: "Bearer " + ScriptApp.getOAuthToken() },
    payload: JSON.stringify({ name: FOLDER_NAME, mimeType: "application/vnd.google-apps.folder" }),
  });
  const created = JSON.parse(res.getContentText()).id;
  props.setProperty("FOLDER_ID", created);
  return created;
}

// Run once from the editor: makes the random key the render machine needs, and the Drive folder.
function setup() {
  const props = PropertiesService.getScriptProperties();
  if (!props.getProperty("UPLOAD_KEY")) props.setProperty("UPLOAD_KEY", Utilities.getUuid() + Utilities.getUuid());
  folderId();
  Logger.log("UPLOAD_KEY: " + props.getProperty("UPLOAD_KEY"));
}

function json(o) {
  return ContentService.createTextOutput(JSON.stringify(o)).setMimeType(ContentService.MimeType.JSON);
}
