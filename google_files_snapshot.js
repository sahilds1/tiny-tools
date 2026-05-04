// Set up Apps Script: 
//
// Go to script.google.com and create a new project
// Paste the exportGoogleFilesAsSnapshots script and save
// Run exportGoogleFilesAsSnapshots manually to test
// Authorize permissions when prompted
// Confirm folder appears in Google Drive with today's date
// Confirm .docx, .xlsx, and .pptx files are inside the dated folder
// Set weekly trigger for exportGoogleFilesAsSnapshots — Sunday 11pm

// Alternatives: https://rclone.org/ 
// The extra complexity of rclone is hard to justify unless you want finer 
// control over scheduling or want to eliminate the Apps Script dependency entirely.

// Does not export Google Forms, Drawings or Maps
// Does not include files shared with you that live on other people's Drives.
// Does not include Shared Drives
// Does not delete old snapshots -- managed manually
// Does not send email notifications on completion -- check Apps Script logs to confirm runs
// Files over ~10MB may be silently skipped -- Drive export API limit; logged with reason
// Uses only one parent folder name in filename -- files with multiple parents may be mislabeled
// Running twice on the same day reuses the dated folder -- files from the second run overwrite the first

// This script does not automatically delete old snapshots.
// Without cleanup, Google Drive Snapshots will grow by 1 dated
// folder per week — 52 folders per year. With 87GB free on
// Google Drive this is not an immediate concern but worth
// reviewing manually once or twice a year to delete snapshots
// you no longer need. A deleteOldSnapshots() function can be
// added to automate this if needed in the future.

// Apps Scripts is free but has daily usage limits
// Script runtime 6 minutes per execution
// URL fetch calls 20000 per day 

function exportGoogleFilesAsSnapshots() {
  // ── CONFIGURATION ──────────────────────────────────────────
  const BACKUP_FOLDER_NAME = "Google Files Snapshots";

  // Consider exporting alternative or additional file type
  const FILE_TYPES = [
    { mimeType: MimeType.GOOGLE_DOCS,   exportMime: MimeType.MICROSOFT_WORD,       ext: ".docx" },
    { mimeType: MimeType.GOOGLE_SHEETS, exportMime: MimeType.MICROSOFT_EXCEL,      ext: ".xlsx" },
    { mimeType: MimeType.GOOGLE_SLIDES, exportMime: MimeType.MICROSOFT_POWERPOINT, ext: ".pptx" },
  ];

  // Create today's dated folder
  const today = Utilities.formatDate(new Date(), Session.getScriptTimeZone(), "yyyy-MM-dd");
  const rootBackupFolder = getOrCreateFolder(DriveApp.getRootFolder(), BACKUP_FOLDER_NAME);
  const todayFolder = getOrCreateFolder(rootBackupFolder, today);
  
  // Initialize counter that tracks how many files were successfully exported
  // and how many were skipped due to errors. Used in the final log message
  const stats = { exported: 0, skipped: 0 };
  
  // Export by building a Google Drive API export URL for the file

  for (const type of FILE_TYPES) {
    const files = DriveApp.getFilesByType(type.mimeType);
    while (files.hasNext()) {
      const file = files.next();
      try {
        // Only uses the first parent -- files with multiple Drive parents may get a misleading folder name
        const folderName = file.getParents().hasNext()
          ? file.getParents().next().getName()
          : "Root";
        const fileName = folderName + " - " + file.getName() + " - " + file.getId().slice(0, 8) + type.ext;

        const url = "https://www.googleapis.com/drive/v3/files/"
          + file.getId()
          + "/export?mimeType="
          + encodeURIComponent(type.exportMime);

        const response = UrlFetchApp.fetch(url, {
          headers: { Authorization: "Bearer " + ScriptApp.getOAuthToken() },
          muteHttpExceptions: true
        });

        // if/else handles HTTP errors (non-200 status); try/catch handles JS exceptions
        // (network failures, quota errors, bad calls). muteHttpExceptions: true is what
        // requires the if/else — without it, HTTP errors would throw and catch would suffice,
        // but we'd lose response.getContentText() which explains why a file was skipped.
        if (response.getResponseCode() === 200) {
          todayFolder.createFile(response.getBlob().setName(fileName));
          stats.exported++;
        } else {
          Logger.log("Skipped: " + file.getName() + " — " + response.getContentText());
          stats.skipped++;
        }
      } catch (e) {
        Logger.log("Error exporting " + file.getName() + ": " + e.message);
        stats.skipped++;
      }
    }
  }
  
  function getOrCreateFolder(parent, name) {
    const existing = parent.getFoldersByName(name);
    return existing.hasNext() ? existing.next() : parent.createFolder(name);
  }

  Logger.log("Snapshot complete: " + stats.exported + " exported, " + stats.skipped + " skipped.");
}