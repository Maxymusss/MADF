# Additional C: Drive Space Recovery Opportunities

## Current Status
- **C: Drive**: 128.39 GB used / 20.84 GB free (14% free) - HEALTHY
- **Total Recovered So Far**: ~19 GB (from 1.4 GB free initially)

---

## Available Recovery Opportunities (39+ GB)

### **TIER 1: HIGH IMPACT - Safe System Cleanup (18+ GB)**

#### 1. WinSxS Component Store Cleanup (2-5 GB potential)
**Current**: 14.71 GB
**Method**: DISM Component Cleanup
**Safety**: SAFE - Microsoft recommended
**Recovery**: 2-5 GB (removes superseded components)

**Command**:
```powershell
# Run as Administrator
Dism.exe /online /Cleanup-Image /StartComponentCleanup /ResetBase
```

**What it does**:
- Removes old Windows Update components
- Cleans superseded versions of system files
- Cannot be undone (removes ability to uninstall certain updates)

---

#### 2. Windows Installer Cache (1-2 GB potential)
**Current**: 3.01 GB
**Safety**: MEDIUM - Some installers may need these files for repairs
**Recovery**: 1-2 GB

**Method**: Use PatchCleaner tool or manual review
- Download: https://www.homedev.com.au/Free/PatchCleaner
- Identifies orphaned MSI/MSP files
- Safe deletion of unused patches

**Manual check**:
```powershell
# List large MSI files
Get-ChildItem "C:\Windows\Installer" -File |
    Where-Object {$_.Length -gt 100MB} |
    Sort-Object Length -Descending |
    Select-Object Name, @{N='SizeMB';E={[math]::Round($_.Length/1MB,2)}}
```

---

#### 3. AppData\Local\Programs (7.42 GB)
**Applications installed per-user**

Top consumers:
- Unknown applications in Programs folder
- Consider moving to D: or uninstalling unused apps

**Action**: Review and relocate/uninstall
```powershell
Get-ChildItem "C:\Users\szmen\AppData\Local\Programs" -Directory |
    ForEach-Object {
        $size = (Get-ChildItem $_.FullName -Recurse -File -EA 0 | Measure-Object Length -Sum).Sum
        [PSCustomObject]@{Name=$_.Name; SizeGB=[math]::Round($size/1GB,2)}
    } | Sort-Object SizeGB -Descending
```

---

#### 4. npm Cache (1.73 GB)
**Already partially cleared, has regenerated**
**Action**: Clear again
```powershell
npm cache clean --force
```

---

#### 5. Browser Caches (0.9 GB total)
**Chrome**: 0.49 GB
**Edge**: 0.27 GB
**Firefox**: 0.14 GB

**Action**: Clear via browser settings or manually
```powershell
# Clear Chrome cache
Remove-Item "C:\Users\szmen\AppData\Local\Google\Chrome\User Data\Default\Cache\*" -Recurse -Force -EA 0
Remove-Item "C:\Users\szmen\AppData\Local\Google\Chrome\User Data\Default\Code Cache\*" -Recurse -Force -EA 0

# Clear Edge cache
Remove-Item "C:\Users\szmen\AppData\Local\Microsoft\Edge\User Data\Default\Cache\*" -Recurse -Force -EA 0
```

---

#### 6. Crash Dumps (0.21 GB)
**Action**: Delete old crash dumps
```powershell
Remove-Item "C:\Users\szmen\AppData\Local\CrashDumps\*" -Force -EA 0
```

---

### **TIER 2: MEDIUM IMPACT - Application Data (10+ GB)**

#### 7. Google Applications (3.29 GB)
**Location**: `C:\Users\szmen\AppData\Local\Google`

**Breakdown needed**:
- Chrome updater cache
- Google Drive File Stream cache
- Other Google services

**Action**: Analyze subfolder sizes
```powershell
Get-ChildItem "C:\Users\szmen\AppData\Local\Google" -Directory |
    ForEach-Object {
        $size = (Get-ChildItem $_.FullName -Recurse -File -EA 0 | Measure-Object Length -Sum).Sum
        [PSCustomObject]@{Name=$_.Name; SizeGB=[math]::Round($size/1GB,2)}
    } | Sort-Object SizeGB -Descending
```

---

#### 8. OpenFin (1.67 GB)
**Financial desktop application framework**
**Action**: Check if actively used, consider uninstalling or clearing cache

---

#### 9. Bloomberg Terminal Data (1.47 GB)
**Action**: Cannot move, but may have cache that can be cleared
**Check**: Bloomberg terminal settings for cache location

---

#### 10. WebEx (1.28 GB)
**Action**: Clear meeting recordings/cache
**Location**: `C:\Users\szmen\AppData\Local\WebEx`

---

#### 11. Spotify (0.64 GB)
**Action**: Clear offline downloads/cache
- Spotify Settings > Storage > Clear Cache
- Or move cache location to D:

---

### **TIER 3: ADVANCED - Relocations (7+ GB)**

#### 12. Move User Profile Folders via Symlinks

Similar to what we did with Docker/uv/cache/.cache/OST:

**Candidates**:
- **Downloads** (unknown size - check first)
- **Documents** (0.58 GB currently, but grows)
- **Videos** (minimal)
- **Desktop** (check size)

**Method**: Move to D: and create symlinks

**Example for Downloads**:
```powershell
# Create target
New-Item -ItemType Directory -Path "D:\UserData\Downloads" -Force

# Move contents
Move-Item "C:\Users\szmen\Downloads\*" "D:\UserData\Downloads\" -Force

# Create symlink (requires admin)
New-Item -ItemType SymbolicLink -Path "C:\Users\szmen\Downloads" -Target "D:\UserData\Downloads"
```

---

#### 13. OneDrive Cache Location (0.67 GB)
**Action**: Configure OneDrive to use D: drive
- OneDrive Settings > Sync and backup > Advanced settings
- Change cache location to D:\OneDriveCache

---

#### 14. Package Cache (0.51 GB)
**Location**: `C:\ProgramData\Package Cache`
**Contains**: Visual Studio installers, .NET runtime installers
**Safety**: LOW - May break repair/uninstall for some applications
**Action**: Review but do NOT delete without research

---

### **TIER 4: SYSTEM FILES - Advanced Users Only**

#### 15. Hibernation File
**Action**: Disable hibernation if not used
```powershell
# Run as Administrator
powercfg /hibernate off
```
**Recovery**: ~8-16 GB (depends on RAM size)
**Tradeoff**: Lose hibernate capability (keeps sleep/shutdown)

---

#### 16. Page File Relocation
**Current**: Likely on C: (dynamic size)
**Action**: Move to D: drive
**Steps**:
1. System Properties > Advanced > Performance Settings
2. Advanced tab > Virtual Memory > Change
3. Uncheck C:, set custom size on D:
4. Restart required

**Recovery**: Variable (typically 2-16 GB)

---

## Quick Wins Summary (Prioritized)

| Action | Recovery | Time | Risk |
|--------|----------|------|------|
| DISM Component Cleanup | 2-5 GB | 10 min | LOW |
| Clear npm cache | 1.7 GB | 1 min | NONE |
| Clear browser caches | 0.9 GB | 2 min | NONE |
| Clear crash dumps | 0.2 GB | 1 min | NONE |
| Review AppData\Local\Programs | 2-5 GB | 15 min | LOW |
| Disable hibernation | 8-16 GB | 2 min | NONE |
| Move page file to D: | 2-8 GB | 5 min | LOW |
| **TOTAL POTENTIAL** | **17-42 GB** | | |

---

## Recommended Immediate Actions (30 minutes work)

### Phase 4A: Safe Quick Cleanup (5-7 GB)
```powershell
# 1. DISM Cleanup (as admin)
Dism.exe /online /Cleanup-Image /StartComponentCleanup /ResetBase

# 2. Clear caches
npm cache clean --force
Remove-Item "C:\Users\szmen\AppData\Local\Google\Chrome\User Data\Default\Cache\*" -Recurse -Force -EA 0
Remove-Item "C:\Users\szmen\AppData\Local\CrashDumps\*" -Force -EA 0

# 3. Disable hibernation (if not needed)
powercfg /hibernate off
```

### Phase 4B: Application Review (2-5 GB)
- Analyze AppData\Local\Programs
- Uninstall unused applications
- Clear application caches (WebEx, Spotify, etc.)

### Phase 4C: Page File Relocation (2-8 GB)
- Move page file to D: via System Properties
- Restart system

---

## Expected Final Results

**Current**: 20.84 GB free
**After Phase 4A**: ~28-33 GB free
**After Phase 4B**: ~30-38 GB free
**After Phase 4C**: ~32-46 GB free

**Total Possible Recovery**: 30-45 GB additional space

---

## Safety Notes

1. **Always create restore point before system changes**
2. **Test applications after cleanup**
3. **Keep Disk Cleanup results for rollback info**
4. **DISM /ResetBase is irreversible** (can't uninstall old updates after)
5. **Don't touch**:
   - Windows\System32
   - Program Files
   - Windows\WinSxS (except via DISM)

---

Would you like me to execute any of these cleanup operations?
