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
// Does not delete old snapshots -- managed mmanually
//   // ── CLEANUP ─────────────────────────────────────────────────
// This script does not automatically delete old snapshots.
// Without cleanup, Google Drive Snapshots will grow by 1 dated
// folder per week — 52 folders per year. With 87GB free on
// Google Drive this is not an immediate concern but worth
// reviewing manually once or twice a year to delete snapshots
// you no longer need. A deleteOldSnapshots() function can be
// added to automate this if needed in the future.
// ───────────────────────────────────────────────────────────
// Does not send email notificaionts -- can be added later if needed

function exportGoogleFilesAsSnapshots() {
  // ── CONFIGURATION ──────────────────────────────────────────
  const BACKUP_FOLDER_NAME = "Google Drive Snapshots";

  const FILE_TYPES = [
    { mimeType: MimeType.GOOGLE_DOCS,   exportMime: MimeType.MICROSOFT_WORD,       ext: ".docx" },
    { mimeType: MimeType.GOOGLE_SHEETS, exportMime: MimeType.MICROSOFT_EXCEL,      ext: ".xlsx" },
    { mimeType: MimeType.GOOGLE_SLIDES, exportMime: MimeType.MICROSOFT_POWERPOINT, ext: ".pptx" },
  ];

  // Create today's dated folder
  const today = Utilities.formatDate(new Date(), Session.getScriptTimeZone(), "yyyy-MM-dd");
  const rootBackupFolder = getOrCreateFolder(DriveApp.getRootFolder(), BACKUP_FOLDER_NAME);
  const todayFolder = getOrCreateFolder(rootBackupFolder, today);
  
  // Initalize counter that tracks how many files were successfully exported
  // and how many were skipped due to errors. Used in the final log message
  const stats = { exported: 0, skipped: 0 };

  // Kick off saving exports into today's dated folder starting from the root of your Google Drive
  processFolder(DriveApp.getRootFolder(), todayFolder);


  function processFolder(sourceFolder, destFolder) {
    // Export Docs, Sheets and Slides by building a Google Drive API export URL for the file
    for (const type of FILE_TYPES) {
      const files = sourceFolder.getFilesByType(type.mimeType);
      while (files.hasNext()) {
        const file = files.next();
        try {
          const url = "https://www.googleapis.com/drive/v3/files/"
            + file.getId()
            + "/export?mimeType="
            + encodeURIComponent(type.exportMime);

          const response = UrlFetchApp.fetch(url, {
            headers: { Authorization: "Bearer " + ScriptApp.getOAuthToken() },
            muteHttpExceptions: true
          });

         // TOOD: Simplify the  exception handling
          if (response.getResponseCode() === 200) {
            destFolder.createFile(response.getBlob().setName(file.getName() + type.ext));
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

    // TODO: Simplify recurse into subfolders
    const subfolders = sourceFolder.getFolders();
    while (subfolders.hasNext()) {
      const sub = subfolders.next();
      if (sub.getName() === BACKUP_FOLDER_NAME) continue;
      processFolder(sub, getOrCreateFolder(destFolder, sub.getName()));
    }
  }

  function getOrCreateFolder(parent, name) {
    const existing = parent.getFoldersByName(name);
    return existing.hasNext() ? existing.next() : parent.createFolder(name);
  }

  Logger.log("Snapshot complete: " + stats.exported + " exported, " + stats.skipped + " skipped.");
}