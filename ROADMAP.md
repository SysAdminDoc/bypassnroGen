# bypassnroGen Roadmap

Forward-looking scope for the Windows 11 OOBE bypass generator (GUI for `bypass.cmd` + `unattend.xml`).

## Planned Features

### Generator Core
- Windows 11 25H2 / 26H1 compatibility pass: verify generated `unattend.xml` schema against the latest WAIK.
- Hardware requirements bypass matrix: explicitly version-tag bypasses (LabConfig / BypassTPMCheck / BypassSecureBootCheck / BypassRAMCheck / BypassCPUCheck / BypassStorageCheck).
- Microsoft Account removal in-OOBE (the `ms-cxh://setaddlocalonly` URL handler method) added as a first-class option alongside the existing `BypassNRO` reg approach since Microsoft has already removed that once.
- Audit Mode unattended bootstrap option for building reference images (`Microsoft-Windows-Deployment\Reseal`).
- `specialize` pass first-logon scripts vs `oobeSystem` first-logon scripts surfaced separately with clear guidance.

### Presets & Profiles
- Importable community presets from a curated JSON repo (read-only) with signature verification.
- Diff against a saved profile to see what changed before re-exporting.
- Named profile library saved under `%LOCALAPPDATA%\bypassnroGen\profiles\`.
- "Minimum viable debloat" preset that matches the OOBE-only default most users want.

### Bloatware Removal
- Auto-refresh bloatware catalog from the latest Windows 11 build via `Get-AppxProvisionedPackage` parsed from a donor image.
- Per-app justification tooltip explaining what breaks if removed (e.g., removing `Microsoft.WindowsStore` breaks MS Store entirely).
- Safe-list vs aggressive-list split.
- Provisioning-vs-per-user removal choice per app.

### Output
- Optional `autounattend.xml` output (flat file for USB root) in addition to the existing `bypass.cmd + unattend.xml` GitHub-hosted combo.
- ISO injection helper: drop the generated files into a mounted Windows 11 ISO and re-pack via `oscdimg`.
- One-click USB creator that writes the ISO + autounattend to a FAT32 USB (Rufus-lite path).
- Signed `bypass.cmd` variant (Authenticode on the CMD is cosmetic; sign the accompanying PowerShell bootstrap instead).

## Competitive Research
- **Schneegans Unattend Generator** — reference; mirror its audit-mode toggle, region/keyboard matrix, and `FirstLogonCommands` editor.
- **Chris Titus Tech BypassNRO** — simplest possible; bypassnroGen is the power-user complement — keep a "Schneegans-lite" quick-preset tab.
- **UUP dump + custom ISO builders (NTLite, MSMG Toolkit)** — deeper image surgery; out of scope, but link in README for users who outgrow the tool.
- **Rufus 4.5+** — has a built-in Win11 unattended checkbox; document when to use Rufus vs bypassnroGen.

## Nice-to-Haves
- PowerShell port (drop tkinter) using the same SysAdminDoc WPF stack, matching WinForge visually.
- Discord / Slack webhook on "first logon complete" for deployment fleet operators.
- WinPE phase preset: generate an extra `startnet.cmd` for advanced deployment scenarios.
- Offline documentation of every registry key and its effect (bundled HTML, no network needed).
- Localization: region/keyboard/timezone presets bundled for the top 10 locales.
- Checksum + signed export bundle (`.zip` with all outputs + README hash) for air-gapped deployments.

## Open-Source Research (Round 2)

### Related OSS Projects
- https://github.com/AveYo/MediaCreationTool.bat — canonical `AutoUnattend.xml` with BypassNRO, `bypass11/` dir
- https://github.com/the-P1neapple/WinJS-Microsoft-Account-Bypass — OOBE dev-console method, still works 25H2 incl. S-Mode
- https://github.com/pbatard/rufus — USB media writer with Win11 MSA/TPM/RAM/SB bypass toggles (issue #1981 is required reading)
- https://github.com/asheroto/winget-install — related deployment-flow reference from same author style
- https://github.com/schneegans/unattend-generator — web-based unattend.xml generator with full schema coverage
- https://github.com/memstechtips/Win11Unattended — focused unattend.xml templates
- https://github.com/Raphire/Win11Debloat — companion first-logon debloat
- https://gist.github.com/asheroto/c4a9fb4e5e5bdad10bcb831e3a3daee6 — tested skip-all unattend reference

### Features to Borrow
- `windowsPE` pass present in emitted XML so `specialize` RunSynchronousCommand actually fires (Rufus #1981)
- WinJS dev-console fallback instructions for 25H2+ where BypassNRO patch landed (WinJS-Microsoft-Account-Bypass)
- Rufus-style checkbox grid for TPM/SB/RAM/CPU/MSA bypass toggles, individually selectable (pbatard/rufus)
- Web-based unattend generator UX with schema validation per setting (schneegans/unattend-generator)
- ISO patcher mode: inject `autounattend.xml` directly into an ISO root or `boot.wim` (AveYo)
- Post-install FirstLogonCommands template library: pick debloat / install winget / apply tweaks (Win11Debloat)
- Language/region preset bundle — InputLocale, SystemLocale, UserLocale, UILanguage in one picker
- Export as both `autounattend.xml` (media root) and `unattend.xml` (C:\Windows\Panther) variants
- Built-in XML preview with Windows System Image Manager schema hints / errors
- Signed bundle download: XML + bypass.cmd + README.txt zipped with integrity hash

### Patterns & Architectures Worth Studying
- Pass-based XML model: each pass (windowsPE / offlineServicing / specialize / oobeSystem / auditSystem / auditUser) is a tab (schneegans)
- Dry-run virtualization: mount generated XML against a Hyper-V VHDX, boot, report result, destroy (advanced QA)
- JSON profile ↔ XML serializer: editable JSON is the source of truth, XML is emitted deterministically
- Version-gated output: detect target Windows 11 build (22H2/23H2/24H2/25H2), emit the bypass path that actually works on that build
- Git-versioned profiles: save profile as a JSON file, commit to a private repo, share across a deployment team
