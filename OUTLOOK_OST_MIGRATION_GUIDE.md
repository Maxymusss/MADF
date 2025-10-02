# Outlook OST File Migration Guide

## Current Status
- **File**: `max.meng@pinpointfund.com - max.ost`
- **Location**: `C:\Users\szmen\AppData\Local\Microsoft\Outlook\`
- **Size**: 7.8 GB
- **Type**: OST (Offline Storage Table) - Email cache file

## Important Context

**What is an OST file?**
- Cached copy of mailbox data from Exchange/Microsoft 365
- Allows offline access to emails
- Automatically syncs when online
- **Can be regenerated** if deleted (will re-download from server)

**Why move it?**
- Free up 7.8 GB on C: drive
- Improve system performance
- Separate user data from system drive

---

## ⚠️ CRITICAL WARNINGS

1. **OST files differ from PST files**:
   - PST = Personal archive (contains unique data)
   - OST = Server cache (can be regenerated)

2. **Risk Assessment**:
   - **LOW RISK**: OST regenerates from server if lost
   - **TIME COST**: Initial sync may take hours depending on mailbox size
   - **DATA SAFE**: All data remains on Exchange server

3. **Before proceeding**:
   - Ensure stable internet connection
   - Close Outlook completely
   - Verify Exchange account credentials

---

## Method 1: ForceOSTPath Registry Key (RECOMMENDED)

**Best for**: Permanent relocation for current and future OST files

### Steps:

1. **Close Outlook completely** (check Task Manager for OUTLOOK.EXE)

2. **Create target directory**:
   ```powershell
   New-Item -ItemType Directory -Path "D:\OutlookData" -Force
   ```

3. **Open Registry Editor**:
   - Press `Win + R`
   - Type `regedit`
   - Click OK

4. **Navigate to Outlook registry key**:
   ```
   HKEY_CURRENT_USER\Software\Microsoft\Office\16.0\Outlook
   ```
   *Note: "16.0" is for Office 2016/2019/365. Use "15.0" for Office 2013*

5. **Create new registry value**:
   - Right-click on "Outlook" key
   - Select `New > Expandable String Value`
   - Name it: `ForceOSTPath`
   - Double-click to edit
   - Set value: `D:\OutlookData`
   - Click OK

6. **Move existing OST file**:
   ```powershell
   Move-Item "C:\Users\szmen\AppData\Local\Microsoft\Outlook\*.ost" "D:\OutlookData\"
   ```

7. **Restart Outlook**:
   - Outlook will find the OST at new location
   - Or create new OST at `D:\OutlookData` if not found

8. **Verify**:
   - Check `D:\OutlookData\` contains OST file
   - Emails load normally

---

## Method 2: Symbolic Link (ALTERNATIVE)

**Best for**: Quick solution without registry changes

### Steps:

1. **Close Outlook completely**

2. **Move OST file**:
   ```powershell
   # Create target directory
   New-Item -ItemType Directory -Path "D:\OutlookData" -Force

   # Move OST file
   Move-Item "C:\Users\szmen\AppData\Local\Microsoft\Outlook\*.ost" "D:\OutlookData\"
   ```

3. **Create symbolic link** (requires Administrator):
   ```powershell
   # Run PowerShell as Administrator
   New-Item -ItemType SymbolicLink -Path "C:\Users\szmen\AppData\Local\Microsoft\Outlook\max.meng@pinpointfund.com - max.ost" -Target "D:\OutlookData\max.meng@pinpointfund.com - max.ost"
   ```

4. **Restart Outlook**:
   - Outlook follows symlink transparently
   - OST physically on D:, Outlook sees it on C:

---

## Method 3: Delete and Regenerate (SIMPLEST)

**Best for**: When you want a fresh start and have good internet

### Steps:

1. **Close Outlook completely**

2. **Delete OST file**:
   ```powershell
   Remove-Item "C:\Users\szmen\AppData\Local\Microsoft\Outlook\*.ost"
   ```

3. **Apply ForceOSTPath registry setting** (see Method 1, steps 3-5)

4. **Restart Outlook**:
   - Outlook creates new OST at `D:\OutlookData`
   - Automatically re-downloads all emails from server
   - **Time required**: 30 minutes to several hours (7.8 GB mailbox)

5. **Wait for sync to complete**:
   - Status shown at bottom of Outlook window
   - "All folders up to date" when finished

---

## Recommended Approach for Your Situation

### Option A: ForceOSTPath + Move Existing (FASTEST)
- **Time**: 5-10 minutes
- **Downtime**: Minimal
- **Steps**: Method 1 (all steps)
- **Pros**: Keeps existing data, quick
- **Cons**: Requires registry edit

### Option B: ForceOSTPath + Regenerate (CLEANEST)
- **Time**: 2-4 hours (initial sync)
- **Downtime**: Works while syncing
- **Steps**: Method 3
- **Pros**: Fresh OST, no corruption risk
- **Cons**: Long initial sync

### Option C: Symbolic Link (NO REGISTRY)
- **Time**: 5 minutes
- **Downtime**: Minimal
- **Steps**: Method 2
- **Pros**: No registry changes, reversible
- **Cons**: Requires admin rights for symlink

---

## Verification After Migration

Run this verification script:

```powershell
# Check OST location
Write-Host "Checking OST file location..."

if (Test-Path "D:\OutlookData\*.ost") {
    $ostFiles = Get-ChildItem "D:\OutlookData\*.ost"
    foreach ($file in $ostFiles) {
        $sizeGB = [math]::Round($file.Length/1GB, 2)
        Write-Host "[OK] OST file on D: drive: $sizeGB GB - $($file.Name)"
    }
}

if (Test-Path "C:\Users\szmen\AppData\Local\Microsoft\Outlook\*.ost") {
    Write-Host "[INFO] OST still on C: drive (check if symlink)"
    $item = Get-Item "C:\Users\szmen\AppData\Local\Microsoft\Outlook\*.ost"
    if ($item.LinkType -eq "SymbolicLink") {
        Write-Host "[OK] Symlink detected - pointing to: $($item.Target)"
    }
}

# Check registry
$regPath = "HKCU:\Software\Microsoft\Office\16.0\Outlook"
if (Test-Path $regPath) {
    $forceOST = Get-ItemProperty -Path $regPath -Name "ForceOSTPath" -ErrorAction SilentlyContinue
    if ($forceOST) {
        Write-Host "[OK] ForceOSTPath registry key: $($forceOST.ForceOSTPath)"
    }
}
```

---

## Rollback Procedure

If something goes wrong:

### If using ForceOSTPath:
1. Delete registry key: `ForceOSTPath`
2. Move OST back to original location
3. Restart Outlook

### If using Symlink:
1. Delete symlink (doesn't delete target file)
2. Move OST back from D: to C:
3. Restart Outlook

### If regenerating:
- Just wait for sync to complete
- Data is always safe on server

---

## Expected Results

**Space Recovery**: 7.8 GB on C: drive
**Total C: Drive Free Space After**: ~21 GB (13.18 GB current + 7.8 GB)
**Performance Impact**: None (D: drive has 1.6 TB free)

---

## Next Steps

Choose your preferred method:
1. **Quick & Safe**: Method 2 (Symlink) - 5 minutes
2. **Permanent**: Method 1 (ForceOSTPath + Move) - 10 minutes
3. **Clean Start**: Method 3 (Regenerate) - 2-4 hours

Would you like me to execute any of these methods?
