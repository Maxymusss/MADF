# Windows Disk Cleanup - User Instructions

## Disk Cleanup Wizard Launched

The Disk Cleanup wizard is now running in a separate window.

---

## Step-by-Step Instructions:

### **Step 1: Wait for Calculation**
- Disk Cleanup will calculate how much space can be freed
- This may take 1-2 minutes
- Progress bar will show "Calculating..."

### **Step 2: Review Cleanup Options**
When the dialog appears, you'll see a list of file categories with checkboxes.

### **RECOMMENDED SELECTIONS** (Safe to delete):

✓ **Windows Update Cleanup**
  - Old Windows Update files (1-3 GB typical)
  - Safe to delete after updates installed

✓ **Temporary files**
  - System temp files (already mostly cleared)
  - Safe to delete

✓ **Temporary Windows installation files**
  - Leftover from Windows updates
  - Safe to delete

✓ **Downloaded Program Files**
  - ActiveX controls, Java applets (rarely used)
  - Safe to delete

✓ **Delivery Optimization Files**
  - Windows Update P2P cache
  - Safe to delete

✓ **Thumbnails**
  - Image thumbnails (will regenerate if needed)
  - Safe to delete

✓ **Previous Windows installation(s)** (if shown)
  - Old Windows.old folder
  - **Large recovery potential** (10+ GB)
  - Safe to delete if Windows working fine

### **OPTIONAL SELECTIONS** (Your choice):

⚠️ **Recycle Bin**
  - Only if you want to permanently delete items
  - Review Recycle Bin first if unsure

⚠️ **Downloads folder**
  - **DO NOT SELECT** unless you want to delete downloads
  - Check your Downloads folder first

### **DO NOT SELECT**:

❌ **System error memory dump files**
  - Needed for troubleshooting crashes
  - Keep unless specifically advised to delete

❌ **Per user archived Windows Error Reporting**
  - Diagnostic data for Windows support
  - Keep for now

---

## Step 3: Execute Cleanup

1. After selecting checkboxes, click **"OK"**
2. Confirm dialog: "Are you sure you want to permanently delete these files?"
3. Click **"Delete Files"**
4. Cleanup will run (may take 5-10 minutes for large cleanups)
5. Progress dialog will show status

---

## Step 4: Verify Results

After cleanup completes, let me know and I'll verify the space recovered.

---

## Expected Recovery:

- **Minimum**: 0.5-1 GB (if no major updates pending)
- **Typical**: 1-3 GB (Windows Update Cleanup)
- **Best case**: 5-15 GB (if "Previous Windows installation" available)

---

## Alternative: Clean up system files

If you want even more options, in the Disk Cleanup window:

1. Click **"Clean up system files"** button
2. This rescans with administrator privileges
3. Shows additional options like:
   - System restore points (can be large)
   - Windows Upgrade log files
   - Device driver packages

---

## Current Status:

**C: Drive**: 125.64 GB used / 23.60 GB free
**Already recovered**: 22.19 GB (from 1.41 GB initial)

---

**Let me know when cleanup is complete and I'll verify the final results!**
