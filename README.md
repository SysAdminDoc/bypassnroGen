# Bypass NRO Generator

A professional GUI tool for generating Windows 11 OOBE bypass files (`bypass.cmd` and `unattend.xml`).

![Bypass NRO Generator](https://img.shields.io/badge/Windows%2011-Bypass%20OOBE-brightgreen)
![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![License](https://img.shields.io/badge/License-MIT-yellow)

## Features

- **Complete OOBE Bypass**: Skip Microsoft account requirement, privacy screens, and more
- **System Requirements Bypass**: Bypass TPM, RAM, Secure Boot, and CPU checks
- **User Account Management**: Create local accounts with custom settings
- **Privacy Controls**: Disable telemetry, Cortana, advertising ID, and more
- **Bloatware Removal**: Remove unwanted Windows apps during installation
- **System Tweaks**: Enable long paths, RDP, PowerShell scripts, and more
- **Explorer Customization**: File extensions, hidden files, classic context menu
- **Taskbar Configuration**: Search box, widgets, Copilot, Task View
- **Edge Settings**: Hide first run experience, disable startup boost
- **Custom Scripts**: Add your own system and first-logon scripts
- **GitHub Integration**: Export files ready for GitHub hosting
- **Preset Configurations**: Quick setup with pre-defined configurations

## Requirements

- Python 3.8 or higher
- tkinter (usually included with Python)

## Installation

```bash
git clone https://github.com/SysAdminDoc/bypassnroGen.git
cd bypassnroGen
python BypassNRO_Generator.py
```

## Usage

### 1. Configure Your Settings

1. Open the application
2. Navigate through the tabs to configure:
   - **GitHub Hosting**: Set your GitHub username and repository
   - **Region & Language**: Select language, keyboard, and timezone
   - **User Accounts**: Create your local admin account
   - **OOBE Bypass**: Enable bypass options
   - **Privacy**: Disable telemetry and data collection
   - **System Tweaks**: Configure system settings
   - **Remove Bloatware**: Select apps to remove
   - **Custom Scripts**: Add your own commands

### 2. Export Files

1. Click "Export Files" button
2. Select a directory
3. Upload `bypass.cmd` and `unattend.xml` to your GitHub repository

### 3. Use During Windows 11 Installation

During the OOBE (Out-of-Box Experience) screen:

1. Press `Shift + F10` to open Command Prompt
2. Run the following command (replace with your repo URL after uploading):

```cmd
curl -L https://raw.githubusercontent.com/YourUsername/YourRepo/refs/heads/main/bypass.cmd -o bypass.cmd && bypass.cmd
```

Or create a short URL redirect to make it easier:

```cmd
curl -L yourdomain.com/bypass -o bypass.cmd && bypass.cmd
```

## Presets

The application includes several preset configurations:

| Preset | Description |
|--------|-------------|
| **Minimal** | Just bypass OOBE, no additional changes |
| **Standard** | Recommended settings for most users |
| **Privacy Focused** | Maximum privacy, disable all telemetry |
| **Power User** | Additional tools like RDP, hidden files |
| **Clean Install** | Remove all bloatware apps |

## Generated Files

### bypass.cmd

A batch script that:
- Downloads `unattend.xml` from your GitHub repository
- Sets BypassNRO registry key
- Bypasses system requirements (TPM, RAM, etc.)
- Applies privacy settings
- Reboots to apply changes

### unattend.xml

An answer file that:
- Configures language and regional settings
- Creates local user accounts
- Skips OOBE screens
- Applies system tweaks
- Removes bloatware
- Configures Explorer and taskbar settings

## Related Tools

| Tool | Description |
|------|-------------|
| **bypassnroGen** (this repo) | GUI to generate custom `bypass.cmd` and `unattend.xml` for Windows 11 OOBE bypass |
| [bypassnro](https://github.com/SysAdminDoc/bypassnro) | Pre-built Windows provisioning scripts and deployment assets for automated workstation setup |

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Disclaimer

This tool is provided for educational and legitimate system administration purposes only. Use responsibly and ensure you have the right to modify Windows installations on the target systems.

## Credits

- Inspired by [Schneegans Unattend Generator](https://schneegans.de/windows/unattend-generator/)
- [Chris Titus Tech BypassNRO](https://github.com/ChrisTitusTech/bypassnro)

## Changelog

### v1.0.0
- Initial release
- Full GUI with all major OOBE bypass options
- Support for Windows 11 24H2 and 25H2
- Bloatware removal support
- Custom script support
- GitHub integration
