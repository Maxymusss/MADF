# Outlook Verification Instructions

## OST Migration Complete ✓

The OST file has been successfully moved to D: drive with a symbolic link created.

### What Was Done:
1. ✓ Moved OST file from `C:\Users\szmen\AppData\Local\Microsoft\Outlook\`
2. ✓ To new location: `D:\OutlookData\` (7.8 GB)
3. ✓ Created symlink so Outlook sees file in original location

### Next Steps - Manual Verification:

**1. Start Outlook**
   - Open Outlook normally from Start Menu or desktop shortcut
   - Outlook will follow the symlink transparently

**2. Verify Email Access**
   - Check that your emails load normally
   - Try opening a few recent emails
   - Check different folders (Inbox, Sent Items, etc.)

**3. Send Test Email (Optional)**
   - Send yourself a test email
   - Verify it appears in Sent Items
   - Confirm sync is working

**4. Check Status Bar**
   - Look at bottom of Outlook window
   - Should show "Connected to: Microsoft Exchange"
   - Or "All folders are up to date"

### Expected Behavior:
- ✓ Outlook works exactly as before
- ✓ All emails accessible
- ✓ No prompts about missing files
- ✓ OST file now on D: drive (7.8 GB saved on C:)

### If Issues Occur:

**If Outlook prompts about missing file:**
1. Close Outlook
2. Verify symlink exists:
   ```powershell
   Get-Item "C:\Users\szmen\AppData\Local\Microsoft\Outlook\*.ost"
   ```
   Should show LinkType: SymbolicLink

**If emails don't load:**
1. Wait 2-3 minutes for initial sync
2. Check internet connection
3. Verify Exchange server connectivity

**Rollback if needed:**
```powershell
# Delete symlink
Remove-Item "C:\Users\szmen\AppData\Local\Microsoft\Outlook\max.meng@pinpointfund.com - max.ost"

# Move OST back
Move-Item "D:\OutlookData\max.meng@pinpointfund.com - max.ost" "C:\Users\szmen\AppData\Local\Microsoft\Outlook\"
```

### Space Recovery Check:
After verifying Outlook works, run verification script to confirm space recovered.

---

**Ready to test?** Start Outlook and verify it works normally.
