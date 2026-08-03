#!/usr/bin/env python3
"""
Bypass NRO Generator - Windows 11 OOBE Bypass Tool
A professional GUI for generating bypass.cmd and unattend.xml files
Author: Generated for Matt's SysAdminDoc projects
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import csv
import hashlib
import os
import re
import json
import base64
import subprocess
import zipfile
from datetime import datetime
from io import StringIO
from xml.etree import ElementTree as ET
from xml.sax.saxutils import escape as xml_escape

APP_VERSION = "1.2.0"
APP_NAME = "Bypass NRO Generator"

class ModernScrollableFrame(ttk.Frame):
    """A scrollable frame with modern styling"""
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        
        self.canvas = tk.Canvas(self, bg='#1e1e1e', highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas_frame = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        self.canvas.bind('<Configure>', self._on_canvas_configure)
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        
    def _on_canvas_configure(self, event):
        self.canvas.itemconfig(self.canvas_frame, width=event.width)
        
    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")


class BypassNROGenerator:
    REGION_PRESETS = {
        "United States": ("en-US", "en-US", "0409:00000409", "Eastern Standard Time"),
        "United Kingdom": ("en-GB", "en-GB", "0809:00000809", "GMT Standard Time"),
        "Germany": ("de-DE", "de-DE", "0407:00000407", "W. Europe Standard Time"),
        "France": ("fr-FR", "fr-FR", "040c:0000040c", "Romance Standard Time"),
        "Spain": ("es-ES", "es-ES", "0c0a:0000040a", "Romance Standard Time"),
        "Italy": ("it-IT", "it-IT", "0410:00000410", "W. Europe Standard Time"),
        "Netherlands": ("nl-NL", "nl-NL", "0413:00000413", "W. Europe Standard Time"),
        "Poland": ("pl-PL", "pl-PL", "0415:00000415", "Central European Standard Time"),
        "Japan": ("ja-JP", "ja-JP", "0411:00000411", "Tokyo Standard Time"),
        "Australia": ("en-AU", "en-AU", "0c09:00000409", "AUS Eastern Standard Time"),
    }

    BLOATWARE_CATALOG = {
        'Microsoft.549981C3F5F10': ('Cortana', 'safe', 'Safe to remove. Cortana is deprecated in Windows 11.'),
        'Microsoft.BingNews': ('News', 'safe', 'Safe to remove. Bing News feed widget.'),
        'Microsoft.BingWeather': ('Weather', 'safe', 'Safe to remove. Taskbar weather widget data source.'),
        'Microsoft.GetHelp': ('Get Help', 'safe', 'Safe to remove. Online help client; does not affect OS stability.'),
        'Microsoft.Getstarted': ('Tips', 'safe', 'Safe to remove. Shows Windows tips and suggestions.'),
        'Microsoft.MicrosoftOfficeHub': ('Office Hub', 'safe', 'Safe to remove. Office promotion hub; does not affect installed Office.'),
        'Microsoft.MicrosoftSolitaireCollection': ('Solitaire', 'safe', 'Safe to remove. Card games with ads.'),
        'Microsoft.MicrosoftStickyNotes': ('Sticky Notes', 'aggressive', 'Caution: some users rely on Sticky Notes for quick notes.'),
        'Microsoft.OutlookForWindows': ('Outlook', 'safe', 'Safe to remove. New Outlook client; does not affect classic Outlook.'),
        'Microsoft.People': ('People', 'safe', 'Safe to remove. Contact manager; Mail app may show reduced functionality.'),
        'Microsoft.PowerAutomateDesktop': ('Power Automate', 'safe', 'Safe to remove. RPA tool for enterprise automation.'),
        'Microsoft.Todos': ('To Do', 'safe', 'Safe to remove. Task management app.'),
        'Microsoft.WindowsAlarms': ('Alarms and Clock', 'aggressive', 'Caution: removes alarms, timer, and world clock functionality.'),
        'Microsoft.WindowsCamera': ('Camera', 'aggressive', 'Caution: removes the default camera app. Webcams still work in other apps.'),
        'Microsoft.WindowsFeedbackHub': ('Feedback Hub', 'safe', 'Safe to remove. Used to send feedback to Microsoft.'),
        'Microsoft.WindowsMaps': ('Maps', 'safe', 'Safe to remove. Offline maps app.'),
        'Microsoft.WindowsSoundRecorder': ('Voice Recorder', 'aggressive', 'Caution: removes the built-in audio recorder.'),
        'Microsoft.Xbox.TCUI': ('Xbox TCUI', 'safe', 'Safe to remove unless using Xbox services. Part of Xbox infrastructure.'),
        'Microsoft.XboxGameOverlay': ('Xbox Game Overlay', 'safe', 'Safe to remove unless using Xbox Game Bar.'),
        'Microsoft.XboxGamingOverlay': ('Xbox Gaming Overlay', 'safe', 'Safe to remove unless using Xbox Game Bar features.'),
        'Microsoft.XboxIdentityProvider': ('Xbox Identity', 'aggressive', 'Warning: removing breaks Xbox sign-in and Microsoft Store game purchases.'),
        'Microsoft.XboxSpeechToTextOverlay': ('Xbox Speech', 'safe', 'Safe to remove. Xbox voice chat transcription.'),
        'Microsoft.YourPhone': ('Phone Link', 'safe', 'Safe to remove. Links Android/iPhone to Windows.'),
        'Microsoft.ZuneMusic': ('Media Player', 'aggressive', 'Caution: removes the default music player.'),
        'Microsoft.ZuneVideo': ('Movies and TV', 'aggressive', 'Caution: removes the default video player.'),
        'Clipchamp.Clipchamp': ('Clipchamp', 'safe', 'Safe to remove. Basic video editor.'),
        'MicrosoftTeams': ('Teams', 'safe', 'Safe to remove. Teams chat integration in taskbar.'),
        'Microsoft.SkypeApp': ('Skype', 'safe', 'Safe to remove. Legacy Skype client.'),
    }

    BLOATWARE_REMOVAL_MODES = ("Provisioned + per-user", "Provisioned only", "Per-user only")

    def __init__(self, root):
        self.root = root
        self.root.title(f"{APP_NAME} v{APP_VERSION} - Windows 11 OOBE Bypass Tool")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 700)
        
        # Apply dark theme
        self.setup_styles()
        
        # Variables for all options
        self.setup_variables()
        
        # Create main interface
        self.create_interface()
        
    @staticmethod
    def _esc(text):
        """Escape text for safe inclusion in XML content."""
        return xml_escape(str(text), {'"': '&quot;', "'": '&apos;'})

    @staticmethod
    def _validate_account_name(name):
        """Validate Windows account name rules.

        Returns (is_valid, error_message).
        """
        if not name:
            return False, "Account name cannot be empty."
        if len(name) > 20:
            return False, "Account name must be 20 characters or fewer."
        invalid_chars = set('|{}~[\\]^\':;<=>?@"')
        found = [c for c in name if c in invalid_chars]
        if found:
            return False, f"Account name contains invalid characters: {''.join(set(found))}"
        if name.startswith('.') or name.endswith('.'):
            return False, "Account name cannot start or end with a period."
        if ' ' in name:
            return False, "Account name cannot contain spaces."
        return True, ""

    @staticmethod
    def _create_tooltip(widget, text):
        """Attach a hover tooltip to a widget."""
        tip_window = [None]

        def show(event):
            if tip_window[0]:
                return
            tw = tk.Toplevel(widget)
            tw.wm_overrideredirect(True)
            tw.wm_geometry(f"+{event.x_root + 15}+{event.y_root + 10}")
            label = tk.Label(tw, text=text, justify='left', background='#ffffe0',
                             foreground='#000000', relief='solid', borderwidth=1,
                             font=('Segoe UI', 9), wraplength=300)
            label.pack()
            tip_window[0] = tw

        def hide(_event):
            tw = tip_window[0]
            if tw:
                tw.destroy()
                tip_window[0] = None

        widget.bind('<Enter>', show)
        widget.bind('<Leave>', hide)

    def setup_styles(self):
        """Configure dark theme styles"""
        self.root.configure(bg='#121212')
        
        style = ttk.Style()
        style.theme_use('clam')
        
        # Colors
        self.colors = {
            'bg_dark': '#121212',
            'bg_medium': '#1e1e1e',
            'bg_light': '#2d2d2d',
            'accent': '#1db954',  # Spotify green
            'accent_hover': '#1ed760',
            'text': '#ffffff',
            'text_dim': '#b3b3b3',
            'border': '#404040',
            'error': '#ff5555',
            'warning': '#ffaa00'
        }
        
        # Configure styles
        style.configure('TFrame', background=self.colors['bg_dark'])
        style.configure('Card.TFrame', background=self.colors['bg_medium'])
        style.configure('TLabel', background=self.colors['bg_dark'], foreground=self.colors['text'], font=('Segoe UI', 10))
        style.configure('Title.TLabel', font=('Segoe UI', 24, 'bold'), foreground=self.colors['accent'])
        style.configure('Header.TLabel', font=('Segoe UI', 14, 'bold'), foreground=self.colors['text'])
        style.configure('Section.TLabel', font=('Segoe UI', 12, 'bold'), foreground=self.colors['accent'])
        style.configure('Dim.TLabel', foreground=self.colors['text_dim'], font=('Segoe UI', 9))
        
        style.configure('TCheckbutton', background=self.colors['bg_dark'], foreground=self.colors['text'], font=('Segoe UI', 10))
        style.map('TCheckbutton', background=[('active', self.colors['bg_medium'])])
        
        style.configure('TRadiobutton', background=self.colors['bg_dark'], foreground=self.colors['text'], font=('Segoe UI', 10))
        style.map('TRadiobutton', background=[('active', self.colors['bg_medium'])])
        
        style.configure('TEntry', fieldbackground=self.colors['bg_light'], foreground=self.colors['text'], insertcolor=self.colors['text'])
        
        style.configure('TCombobox', fieldbackground=self.colors['bg_light'], background=self.colors['bg_light'], foreground=self.colors['text'])
        
        style.configure('TNotebook', background=self.colors['bg_dark'])
        style.configure('TNotebook.Tab', background=self.colors['bg_medium'], foreground=self.colors['text_dim'], padding=[20, 10], font=('Segoe UI', 10))
        style.map('TNotebook.Tab', background=[('selected', self.colors['bg_light'])], foreground=[('selected', self.colors['text'])])
        
        style.configure('Accent.TButton', background=self.colors['accent'], foreground='#000000', font=('Segoe UI', 11, 'bold'), padding=[20, 10])
        style.map('Accent.TButton', background=[('active', self.colors['accent_hover'])])
        
        style.configure('TButton', background=self.colors['bg_light'], foreground=self.colors['text'], font=('Segoe UI', 10), padding=[15, 8])
        style.map('TButton', background=[('active', self.colors['border'])])
        
        style.configure('TLabelframe', background=self.colors['bg_dark'])
        style.configure('TLabelframe.Label', background=self.colors['bg_dark'], foreground=self.colors['accent'], font=('Segoe UI', 11, 'bold'))
        
    def setup_variables(self):
        """Initialize all configuration variables"""
        # GitHub hosting
        self.github_user = tk.StringVar(value="YourUsername")
        self.github_repo = tk.StringVar(value="bypassnro")
        self.github_branch = tk.StringVar(value="main")
        
        # Language settings
        self.region_preset = tk.StringVar(value="United States")
        self.ui_language = tk.StringVar(value="en-US")
        self.locale = tk.StringVar(value="en-US")
        self.keyboard = tk.StringVar(value="0409:00000409")
        self.timezone = tk.StringVar(value="Eastern Standard Time")
        
        # Computer name
        self.computer_name = tk.StringVar(value="*")

        # Windows edition
        self.edition_mode = tk.StringVar(value="Unattended")
        self.windows_edition = tk.StringVar(value="Windows 11 Pro")
        self.product_key = tk.StringVar(value="")
        
        # User accounts
        self.account_name = tk.StringVar(value="Admin")
        self.account_display = tk.StringVar(value="")
        self.account_password = tk.StringVar(value="")
        self.account_group = tk.StringVar(value="Administrators")
        self.auto_logon = tk.BooleanVar(value=True)
        self.obscure_passwords = tk.BooleanVar(value=False)
        
        # OOBE Settings
        self.skip_eula = tk.BooleanVar(value=True)
        self.skip_machine_oobe = tk.BooleanVar(value=True)
        self.skip_user_oobe = tk.BooleanVar(value=True)
        self.hide_online_account = tk.BooleanVar(value=True)
        self.hide_local_account = tk.BooleanVar(value=True)
        self.msa_localonly_bypass = tk.BooleanVar(value=False)
        self.audit_mode = tk.BooleanVar(value=False)
        self.target_architecture = tk.StringVar(value="amd64")
        self.enable_disk_partitioning = tk.BooleanVar(value=False)
        self.protect_your_pc = tk.StringVar(value="3")  # 3 = skip privacy settings
        
        # Privacy settings
        self.disable_telemetry = tk.BooleanVar(value=True)
        self.disable_cortana = tk.BooleanVar(value=True)
        self.disable_consumer_features = tk.BooleanVar(value=True)
        self.disable_wifi_sense = tk.BooleanVar(value=True)
        self.disable_activity_history = tk.BooleanVar(value=True)
        self.disable_location = tk.BooleanVar(value=True)
        self.disable_advertising_id = tk.BooleanVar(value=True)
        
        # System tweaks
        self.bypass_requirements = tk.BooleanVar(value=True)
        self.bypass_nro = tk.BooleanVar(value=True)
        self.enable_long_paths = tk.BooleanVar(value=True)
        self.enable_rdp = tk.BooleanVar(value=False)
        self.allow_powershell_scripts = tk.BooleanVar(value=True)
        self.disable_uac_prompt = tk.BooleanVar(value=False)
        self.disable_defender = tk.BooleanVar(value=False)
        self.prevent_device_encryption = tk.BooleanVar(value=True)
        self.disable_vbs = tk.BooleanVar(value=False)
        self.disable_auto_restart = tk.BooleanVar(value=True)
        self.disable_system_sounds = tk.BooleanVar(value=False)
        self.disable_hibernation = tk.BooleanVar(value=True)
        self.disable_fast_boot = tk.BooleanVar(value=False)
        
        # OneDrive
        self.remove_onedrive = tk.BooleanVar(value=False)

        # Power plan
        self.power_plan = tk.StringVar(value="Default")

        # Security: cleanup Panther password
        self.cleanup_panther_password = tk.BooleanVar(value=True)

        # Edge settings
        self.hide_edge_fre = tk.BooleanVar(value=True)
        self.disable_edge_startup = tk.BooleanVar(value=True)
        self.delete_edge_shortcut = tk.BooleanVar(value=True)
        self.make_edge_uninstallable = tk.BooleanVar(value=False)
        
        # Explorer tweaks
        self.show_file_extensions = tk.BooleanVar(value=True)
        self.show_hidden_files = tk.BooleanVar(value=False)
        self.show_system_files = tk.BooleanVar(value=False)
        self.classic_context_menu = tk.BooleanVar(value=True)
        self.launch_to_this_pc = tk.BooleanVar(value=True)
        
        # Appearance
        self.enable_dark_mode = tk.BooleanVar(value=False)

        # Taskbar settings
        self.taskbar_search = tk.StringVar(value="Hide")
        self.hide_task_view = tk.BooleanVar(value=True)
        self.disable_widgets = tk.BooleanVar(value=True)
        self.hide_copilot = tk.BooleanVar(value=True)
        self.small_taskbar = tk.BooleanVar(value=False)
        
        # Bloatware removal
        self.bloatware_apps = {
            'Microsoft.549981C3F5F10': tk.BooleanVar(value=True),  # Cortana
            'Microsoft.BingNews': tk.BooleanVar(value=True),
            'Microsoft.BingWeather': tk.BooleanVar(value=True),
            'Microsoft.GetHelp': tk.BooleanVar(value=True),
            'Microsoft.Getstarted': tk.BooleanVar(value=True),  # Tips
            'Microsoft.MicrosoftOfficeHub': tk.BooleanVar(value=True),
            'Microsoft.MicrosoftSolitaireCollection': tk.BooleanVar(value=True),
            'Microsoft.MicrosoftStickyNotes': tk.BooleanVar(value=False),
            'Microsoft.OutlookForWindows': tk.BooleanVar(value=True),
            'Microsoft.People': tk.BooleanVar(value=True),
            'Microsoft.PowerAutomateDesktop': tk.BooleanVar(value=True),
            'Microsoft.Todos': tk.BooleanVar(value=True),
            'Microsoft.WindowsAlarms': tk.BooleanVar(value=False),
            'Microsoft.WindowsCamera': tk.BooleanVar(value=False),
            'Microsoft.WindowsFeedbackHub': tk.BooleanVar(value=True),
            'Microsoft.WindowsMaps': tk.BooleanVar(value=True),
            'Microsoft.WindowsSoundRecorder': tk.BooleanVar(value=False),
            'Microsoft.Xbox.TCUI': tk.BooleanVar(value=True),
            'Microsoft.XboxGameOverlay': tk.BooleanVar(value=True),
            'Microsoft.XboxGamingOverlay': tk.BooleanVar(value=True),
            'Microsoft.XboxIdentityProvider': tk.BooleanVar(value=True),
            'Microsoft.XboxSpeechToTextOverlay': tk.BooleanVar(value=True),
            'Microsoft.YourPhone': tk.BooleanVar(value=True),
            'Microsoft.ZuneMusic': tk.BooleanVar(value=False),
            'Microsoft.ZuneVideo': tk.BooleanVar(value=False),
            'Clipchamp.Clipchamp': tk.BooleanVar(value=True),
            'MicrosoftTeams': tk.BooleanVar(value=True),
            'Microsoft.SkypeApp': tk.BooleanVar(value=True),
        }
        self.bloatware_app_modes = {
            app_id: tk.StringVar(value="Provisioned + per-user")
            for app_id in self.bloatware_apps
        }
        
        # Output format
        self.output_autounattend = tk.BooleanVar(value=False)
        self.output_powershell_bootstrap = tk.BooleanVar(value=False)
        self.output_iso_helper = tk.BooleanVar(value=False)
        self.output_usb_helper = tk.BooleanVar(value=False)
        self.output_startnet = tk.BooleanVar(value=False)
        self.output_registry_reference = tk.BooleanVar(value=False)
        self.output_validation_report = tk.BooleanVar(value=True)
        self.output_zip_bundle = tk.BooleanVar(value=False)
        self.sign_powershell_bootstrap = tk.BooleanVar(value=False)
        self.signing_cert_thumbprint = tk.StringVar(value="")

        # Custom scripts
        self.system_script = tk.StringVar(value="")
        self.firstlogon_script = tk.StringVar(value="")
        self.completion_webhook_url = tk.StringVar(value="")
        self.completion_webhook_type = tk.StringVar(value="Generic JSON")
        
    def create_interface(self):
        """Create the main interface"""
        # Main container
        main_frame = ttk.Frame(self.root, style='TFrame')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Header
        header_frame = ttk.Frame(main_frame, style='TFrame')
        header_frame.pack(fill='x', pady=(0, 20))
        
        ttk.Label(header_frame, text=f"{APP_NAME} v{APP_VERSION}", style='Title.TLabel').pack(side='left')
        ttk.Label(header_frame, text="Windows 11 OOBE Bypass Tool", style='Dim.TLabel').pack(side='left', padx=(15, 0), pady=(10, 0))
        
        # Action buttons at top
        btn_frame = ttk.Frame(header_frame, style='TFrame')
        btn_frame.pack(side='right')
        
        ttk.Button(btn_frame, text="Export Files", style='Accent.TButton', command=self.export_files).pack(side='right', padx=5)
        ttk.Button(btn_frame, text="Preview", style='TButton', command=self.preview_files).pack(side='right', padx=5)
        ttk.Button(btn_frame, text="Load Preset", style='TButton', command=self.load_preset).pack(side='right', padx=5)
        ttk.Button(btn_frame, text="Diff Profile", style='TButton', command=self.diff_profile).pack(side='right', padx=5)
        ttk.Button(btn_frame, text="Save Profile", style='TButton', command=self.save_profile).pack(side='right', padx=5)
        ttk.Button(btn_frame, text="Load Profile", style='TButton', command=self.load_profile).pack(side='right', padx=5)
        
        # Notebook for tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill='both', expand=True)
        
        # Create tabs
        self.create_github_tab()
        self.create_region_tab()
        self.create_accounts_tab()
        self.create_oobe_tab()
        self.create_privacy_tab()
        self.create_tweaks_tab()
        self.create_bloatware_tab()
        self.create_scripts_tab()
        self.create_preview_tab()
        
    def create_github_tab(self):
        """GitHub hosting configuration"""
        tab = ttk.Frame(self.notebook, style='TFrame')
        self.notebook.add(tab, text='  GitHub Hosting  ')
        
        scroll = ModernScrollableFrame(tab)
        scroll.pack(fill='both', expand=True)
        frame = scroll.scrollable_frame
        
        # GitHub settings
        group = ttk.LabelFrame(frame, text="GitHub Repository Settings", padding=15)
        group.pack(fill='x', padx=10, pady=10)
        
        ttk.Label(group, text="Your bypass files will be hosted on GitHub and downloaded during OOBE.", style='Dim.TLabel').pack(anchor='w', pady=(0, 15))
        
        row = ttk.Frame(group, style='TFrame')
        row.pack(fill='x', pady=5)
        ttk.Label(row, text="GitHub Username:", width=20).pack(side='left')
        ttk.Entry(row, textvariable=self.github_user, width=40).pack(side='left', padx=10)
        
        row = ttk.Frame(group, style='TFrame')
        row.pack(fill='x', pady=5)
        ttk.Label(row, text="Repository Name:", width=20).pack(side='left')
        ttk.Entry(row, textvariable=self.github_repo, width=40).pack(side='left', padx=10)
        
        row = ttk.Frame(group, style='TFrame')
        row.pack(fill='x', pady=5)
        ttk.Label(row, text="Branch:", width=20).pack(side='left')
        ttk.Entry(row, textvariable=self.github_branch, width=40).pack(side='left', padx=10)
        
        # URL Preview
        preview_group = ttk.LabelFrame(frame, text="Generated URLs", padding=15)
        preview_group.pack(fill='x', padx=10, pady=10)
        
        ttk.Label(preview_group, text="bypass.cmd URL:", style='Dim.TLabel').pack(anchor='w')
        self.bypass_url_label = ttk.Label(preview_group, text="", style='TLabel')
        self.bypass_url_label.pack(anchor='w', pady=(0, 10))
        
        ttk.Label(preview_group, text="unattend.xml URL:", style='Dim.TLabel').pack(anchor='w')
        self.unattend_url_label = ttk.Label(preview_group, text="", style='TLabel')
        self.unattend_url_label.pack(anchor='w')
        
        # Update URLs when values change
        def update_urls(*args):
            user = self.github_user.get()
            repo = self.github_repo.get()
            branch = self.github_branch.get()
            base = f"https://raw.githubusercontent.com/{user}/{repo}/refs/heads/{branch}"
            self.bypass_url_label.config(text=f"{base}/bypass.cmd")
            self.unattend_url_label.config(text=f"{base}/unattend.xml")
            
        self.github_user.trace_add('write', update_urls)
        self.github_repo.trace_add('write', update_urls)
        self.github_branch.trace_add('write', update_urls)
        update_urls()
        
        # Output options
        output_group = ttk.LabelFrame(frame, text="Output Options", padding=15)
        output_group.pack(fill='x', padx=10, pady=10)

        ttk.Checkbutton(output_group, text="Also export autounattend.xml (for USB root -- bypasses OOBE before setup starts)", variable=self.output_autounattend).pack(anchor='w', pady=2)
        ttk.Checkbutton(output_group, text="Export PowerShell bootstrap for optional Authenticode signing", variable=self.output_powershell_bootstrap).pack(anchor='w', pady=2)
        ttk.Checkbutton(output_group, text="Export ISO injection helper script", variable=self.output_iso_helper).pack(anchor='w', pady=2)
        ttk.Checkbutton(output_group, text="Export USB staging helper script", variable=self.output_usb_helper).pack(anchor='w', pady=2)
        ttk.Checkbutton(output_group, text="Export WinPE startnet.cmd", variable=self.output_startnet).pack(anchor='w', pady=2)
        ttk.Checkbutton(output_group, text="Export offline registry reference HTML", variable=self.output_registry_reference).pack(anchor='w', pady=2)
        ttk.Checkbutton(output_group, text="Export validation report", variable=self.output_validation_report).pack(anchor='w', pady=2)
        ttk.Checkbutton(output_group, text="Export checksum ZIP bundle", variable=self.output_zip_bundle).pack(anchor='w', pady=2)

        signing_group = ttk.LabelFrame(frame, text="PowerShell Signing", padding=15)
        signing_group.pack(fill='x', padx=10, pady=10)

        ttk.Checkbutton(signing_group, text="Sign PowerShell bootstrap with certificate thumbprint", variable=self.sign_powershell_bootstrap).pack(anchor='w', pady=2)
        row = ttk.Frame(signing_group, style='TFrame')
        row.pack(fill='x', pady=5)
        ttk.Label(row, text="Certificate Thumbprint:", width=22).pack(side='left')
        ttk.Entry(row, textvariable=self.signing_cert_thumbprint, width=48).pack(side='left', padx=10)

        # Instructions
        info_group = ttk.LabelFrame(frame, text="How to Use", padding=15)
        info_group.pack(fill='x', padx=10, pady=10)
        
        instructions = """1. Export the files using the 'Export Files' button
2. Create a GitHub repository with the name specified above
3. Upload bypass.cmd and unattend.xml to the repository root
4. During Windows 11 OOBE, press Shift+F10 to open Command Prompt
5. Run: curl -L [your-shortlink] -o bypass.cmd && bypass.cmd

Or use the full command:
curl -L https://raw.githubusercontent.com/[user]/[repo]/refs/heads/main/bypass.cmd -o bypass.cmd && bypass.cmd"""
        
        ttk.Label(info_group, text=instructions, style='Dim.TLabel', justify='left').pack(anchor='w')
        
    def create_region_tab(self):
        """Region and language settings"""
        tab = ttk.Frame(self.notebook, style='TFrame')
        self.notebook.add(tab, text='  Region & Language  ')
        
        scroll = ModernScrollableFrame(tab)
        scroll.pack(fill='both', expand=True)
        frame = scroll.scrollable_frame
        
        # Language settings
        group = ttk.LabelFrame(frame, text="Language Settings", padding=15)
        group.pack(fill='x', padx=10, pady=10)

        preset_row = ttk.Frame(group, style='TFrame')
        preset_row.pack(fill='x', pady=5)
        ttk.Label(preset_row, text="Region Preset:", width=20).pack(side='left')
        ttk.Combobox(preset_row, textvariable=self.region_preset, values=list(self.REGION_PRESETS.keys()), width=37, state='readonly').pack(side='left', padx=10)
        ttk.Button(preset_row, text="Apply", command=self.apply_region_preset).pack(side='left', padx=5)
        
        languages = [
            ("English (US)", "en-US"),
            ("English (UK)", "en-GB"),
            ("English (Australia)", "en-AU"),
            ("German", "de-DE"),
            ("French", "fr-FR"),
            ("Spanish", "es-ES"),
            ("Italian", "it-IT"),
            ("Portuguese (Brazil)", "pt-BR"),
            ("Dutch", "nl-NL"),
            ("Polish", "pl-PL"),
            ("Russian", "ru-RU"),
            ("Japanese", "ja-JP"),
            ("Chinese (Simplified)", "zh-CN"),
            ("Korean", "ko-KR"),
        ]
        
        row = ttk.Frame(group, style='TFrame')
        row.pack(fill='x', pady=5)
        ttk.Label(row, text="Display Language:", width=20).pack(side='left')
        lang_combo = ttk.Combobox(row, textvariable=self.ui_language, values=[l[1] for l in languages], width=37)
        lang_combo.pack(side='left', padx=10)
        
        row = ttk.Frame(group, style='TFrame')
        row.pack(fill='x', pady=5)
        ttk.Label(row, text="Locale:", width=20).pack(side='left')
        ttk.Combobox(row, textvariable=self.locale, values=[l[1] for l in languages], width=37).pack(side='left', padx=10)
        
        # Keyboard layouts
        keyboards = [
            ("US English", "0409:00000409"),
            ("UK English", "0809:00000809"),
            ("Australian English", "0c09:00000409"),
            ("German", "0407:00000407"),
            ("French", "040c:0000040c"),
            ("Spanish", "0c0a:0000040a"),
            ("Italian", "0410:00000410"),
            ("Dutch", "0413:00000413"),
            ("Polish", "0415:00000415"),
            ("Japanese", "0411:00000411"),
            ("US International", "0409:00020409"),
        ]
        
        row = ttk.Frame(group, style='TFrame')
        row.pack(fill='x', pady=5)
        ttk.Label(row, text="Keyboard Layout:", width=20).pack(side='left')
        ttk.Combobox(row, textvariable=self.keyboard, values=[k[1] for k in keyboards], width=37).pack(side='left', padx=10)
        
        # Timezone
        timezones = [
            "Eastern Standard Time",
            "Central Standard Time", 
            "Mountain Standard Time",
            "Pacific Standard Time",
            "UTC",
            "GMT Standard Time",
            "Romance Standard Time",
            "W. Europe Standard Time",
            "Central European Standard Time",
            "Tokyo Standard Time",
            "China Standard Time",
            "AUS Eastern Standard Time",
        ]
        
        tz_group = ttk.LabelFrame(frame, text="Time Zone", padding=15)
        tz_group.pack(fill='x', padx=10, pady=10)
        
        row = ttk.Frame(tz_group, style='TFrame')
        row.pack(fill='x', pady=5)
        ttk.Label(row, text="Time Zone:", width=20).pack(side='left')
        ttk.Combobox(row, textvariable=self.timezone, values=timezones, width=37).pack(side='left', padx=10)
        
    def create_accounts_tab(self):
        """User account settings"""
        tab = ttk.Frame(self.notebook, style='TFrame')
        self.notebook.add(tab, text='  User Accounts  ')
        
        scroll = ModernScrollableFrame(tab)
        scroll.pack(fill='both', expand=True)
        frame = scroll.scrollable_frame
        
        # Computer name
        cn_group = ttk.LabelFrame(frame, text="Computer Name", padding=15)
        cn_group.pack(fill='x', padx=10, pady=10)

        ttk.Label(cn_group, text="Set a custom hostname or leave as * for Windows to auto-generate one.", style='Dim.TLabel').pack(anchor='w', pady=(0, 10))

        row = ttk.Frame(cn_group, style='TFrame')
        row.pack(fill='x', pady=5)
        ttk.Label(row, text="Computer Name:", width=20).pack(side='left')
        ttk.Entry(row, textvariable=self.computer_name, width=30).pack(side='left', padx=10)
        ttk.Label(row, text="(* = auto-generate, max 15 chars)", style='Dim.TLabel').pack(side='left')

        # Primary account
        group = ttk.LabelFrame(frame, text="Primary Local Account", padding=15)
        group.pack(fill='x', padx=10, pady=10)

        ttk.Label(group, text="This account will be created automatically during setup.", style='Dim.TLabel').pack(anchor='w', pady=(0, 15))
        
        row = ttk.Frame(group, style='TFrame')
        row.pack(fill='x', pady=5)
        ttk.Label(row, text="Account Name:", width=20).pack(side='left')
        ttk.Entry(row, textvariable=self.account_name, width=30).pack(side='left', padx=10)
        ttk.Label(row, text="(max 20 characters)", style='Dim.TLabel').pack(side='left')
        
        row = ttk.Frame(group, style='TFrame')
        row.pack(fill='x', pady=5)
        ttk.Label(row, text="Display Name:", width=20).pack(side='left')
        ttk.Entry(row, textvariable=self.account_display, width=30).pack(side='left', padx=10)
        ttk.Label(row, text="(optional, leave empty to use account name)", style='Dim.TLabel').pack(side='left')
        
        row = ttk.Frame(group, style='TFrame')
        row.pack(fill='x', pady=5)
        ttk.Label(row, text="Password:", width=20).pack(side='left')
        ttk.Entry(row, textvariable=self.account_password, width=30, show='*').pack(side='left', padx=10)
        ttk.Label(row, text="(leave empty for no password)", style='Dim.TLabel').pack(side='left')
        
        row = ttk.Frame(group, style='TFrame')
        row.pack(fill='x', pady=5)
        ttk.Label(row, text="Account Type:", width=20).pack(side='left')
        ttk.Combobox(row, textvariable=self.account_group, values=["Administrators", "Users"], width=27).pack(side='left', padx=10)
        
        # Options
        options_group = ttk.LabelFrame(frame, text="Account Options", padding=15)
        options_group.pack(fill='x', padx=10, pady=10)
        
        ttk.Checkbutton(options_group, text="Auto-logon to this account after setup", variable=self.auto_logon).pack(anchor='w', pady=2)
        ttk.Checkbutton(options_group, text="Obscure passwords with Base64 encoding", variable=self.obscure_passwords).pack(anchor='w', pady=2)

        extra_group = ttk.LabelFrame(frame, text="Additional Local Accounts", padding=15)
        extra_group.pack(fill='x', padx=10, pady=10)

        ttk.Label(extra_group, text="CSV rows: name,display name,group,password. Up to 98 additional accounts.", style='Dim.TLabel').pack(anchor='w', pady=(0, 10))
        self.additional_accounts_text = tk.Text(extra_group, height=7, bg='#2d2d2d', fg='#ffffff', insertbackground='#ffffff', font=('Consolas', 10))
        self.additional_accounts_text.pack(fill='x', pady=5)
        self.additional_accounts_text.insert('1.0', '# Technician,Technician,Administrators,\n# StandardUser,Standard User,Users,')
        
    def create_oobe_tab(self):
        """OOBE bypass settings"""
        tab = ttk.Frame(self.notebook, style='TFrame')
        self.notebook.add(tab, text='  OOBE Bypass  ')
        
        scroll = ModernScrollableFrame(tab)
        scroll.pack(fill='both', expand=True)
        frame = scroll.scrollable_frame
        
        # Core bypass options
        group = ttk.LabelFrame(frame, text="Core OOBE Bypass Settings", padding=15)
        group.pack(fill='x', padx=10, pady=10)
        
        ttk.Label(group, text="These settings skip various OOBE screens during Windows setup.", style='Dim.TLabel').pack(anchor='w', pady=(0, 15))
        
        ttk.Checkbutton(group, text="Bypass Windows 11 system requirements (TPM, RAM, Secure Boot)", variable=self.bypass_requirements).pack(anchor='w', pady=2)
        ttk.Checkbutton(group, text="Bypass Network Requirement (BypassNRO) - Allow offline installation", variable=self.bypass_nro).pack(anchor='w', pady=2)
        ttk.Checkbutton(group, text="Skip EULA/License Agreement screen", variable=self.skip_eula).pack(anchor='w', pady=2)
        ttk.Checkbutton(group, text="Skip Machine OOBE (device setup screens)", variable=self.skip_machine_oobe).pack(anchor='w', pady=2)
        ttk.Checkbutton(group, text="Skip User OOBE (user setup screens)", variable=self.skip_user_oobe).pack(anchor='w', pady=2)
        ttk.Checkbutton(group, text="Hide Online Account creation screen", variable=self.hide_online_account).pack(anchor='w', pady=2)
        ttk.Checkbutton(group, text="Hide Local Account creation screen (use predefined account)", variable=self.hide_local_account).pack(anchor='w', pady=2)
        ttk.Checkbutton(group, text="Launch local-only Microsoft account bypass URI from bypass.cmd", variable=self.msa_localonly_bypass).pack(anchor='w', pady=2)
        
        # Privacy during OOBE
        privacy_group = ttk.LabelFrame(frame, text="Privacy Settings (During OOBE)", padding=15)
        privacy_group.pack(fill='x', padx=10, pady=10)
        
        ttk.Label(privacy_group, text="ProtectYourPC setting controls privacy screen behavior:", style='Dim.TLabel').pack(anchor='w', pady=(0, 10))
        
        ttk.Radiobutton(privacy_group, text="Show privacy settings screen (1)", variable=self.protect_your_pc, value="1").pack(anchor='w', pady=2)
        ttk.Radiobutton(privacy_group, text="Use recommended settings (2)", variable=self.protect_your_pc, value="2").pack(anchor='w', pady=2)
        ttk.Radiobutton(privacy_group, text="Skip privacy settings entirely (3) - Recommended", variable=self.protect_your_pc, value="3").pack(anchor='w', pady=2)
        
        # Windows Edition
        edition_group = ttk.LabelFrame(frame, text="Windows Edition", padding=15)
        edition_group.pack(fill='x', padx=10, pady=10)
        
        editions = [
            "Windows 11 Home",
            "Windows 11 Pro", 
            "Windows 11 Pro for Workstations",
            "Windows 11 Enterprise",
            "Windows 11 Education",
        ]
        
        row = ttk.Frame(edition_group, style='TFrame')
        row.pack(fill='x', pady=5)
        ttk.Label(row, text="Target Edition:", width=20).pack(side='left')
        ttk.Combobox(row, textvariable=self.windows_edition, values=editions, width=37).pack(side='left', padx=10)
        
        row = ttk.Frame(edition_group, style='TFrame')
        row.pack(fill='x', pady=5)
        ttk.Label(row, text="Product Key:", width=20).pack(side='left')
        ttk.Entry(row, textvariable=self.product_key, width=40).pack(side='left', padx=10)
        ttk.Label(row, text="(optional)", style='Dim.TLabel').pack(side='left')

        advanced_group = ttk.LabelFrame(frame, text="Advanced Setup", padding=15)
        advanced_group.pack(fill='x', padx=10, pady=10)

        row = ttk.Frame(advanced_group, style='TFrame')
        row.pack(fill='x', pady=5)
        ttk.Label(row, text="Target Architecture:", width=20).pack(side='left')
        ttk.Combobox(row, textvariable=self.target_architecture, values=["amd64", "arm64"], width=12, state='readonly').pack(side='left', padx=10)

        ttk.Checkbutton(advanced_group, text="Boot into Audit Mode for reference image work", variable=self.audit_mode).pack(anchor='w', pady=2)
        ttk.Checkbutton(advanced_group, text="Add Disk 0 UEFI/GPT clean-install partition layout", variable=self.enable_disk_partitioning).pack(anchor='w', pady=2)
        
    def create_privacy_tab(self):
        """Privacy and telemetry settings"""
        tab = ttk.Frame(self.notebook, style='TFrame')
        self.notebook.add(tab, text='  Privacy  ')
        
        scroll = ModernScrollableFrame(tab)
        scroll.pack(fill='both', expand=True)
        frame = scroll.scrollable_frame
        
        # Telemetry
        group = ttk.LabelFrame(frame, text="Telemetry & Data Collection", padding=15)
        group.pack(fill='x', padx=10, pady=10)
        
        ttk.Checkbutton(group, text="Disable Windows Telemetry", variable=self.disable_telemetry).pack(anchor='w', pady=2)
        ttk.Checkbutton(group, text="Disable Cortana", variable=self.disable_cortana).pack(anchor='w', pady=2)
        ttk.Checkbutton(group, text="Disable Consumer Features / Content Delivery Manager", variable=self.disable_consumer_features).pack(anchor='w', pady=2)
        ttk.Checkbutton(group, text="Disable Wi-Fi Sense (automatic hotspot connections)", variable=self.disable_wifi_sense).pack(anchor='w', pady=2)
        ttk.Checkbutton(group, text="Disable Activity History", variable=self.disable_activity_history).pack(anchor='w', pady=2)
        ttk.Checkbutton(group, text="Disable Location Services", variable=self.disable_location).pack(anchor='w', pady=2)
        ttk.Checkbutton(group, text="Disable Advertising ID", variable=self.disable_advertising_id).pack(anchor='w', pady=2)
        
    def create_tweaks_tab(self):
        """System tweaks and optimizations"""
        tab = ttk.Frame(self.notebook, style='TFrame')
        self.notebook.add(tab, text='  System Tweaks  ')
        
        scroll = ModernScrollableFrame(tab)
        scroll.pack(fill='both', expand=True)
        frame = scroll.scrollable_frame
        
        # System settings
        sys_group = ttk.LabelFrame(frame, text="System Settings", padding=15)
        sys_group.pack(fill='x', padx=10, pady=10)
        
        ttk.Checkbutton(sys_group, text="Enable Long Paths (32,767 character limit)", variable=self.enable_long_paths).pack(anchor='w', pady=2)
        ttk.Checkbutton(sys_group, text="Enable Remote Desktop (RDP)", variable=self.enable_rdp).pack(anchor='w', pady=2)
        ttk.Checkbutton(sys_group, text="Allow PowerShell script execution (RemoteSigned)", variable=self.allow_powershell_scripts).pack(anchor='w', pady=2)
        ttk.Checkbutton(sys_group, text="Prevent Windows Update automatic reboots", variable=self.disable_auto_restart).pack(anchor='w', pady=2)
        ttk.Checkbutton(sys_group, text="Disable system sounds", variable=self.disable_system_sounds).pack(anchor='w', pady=2)
        ttk.Checkbutton(sys_group, text="Disable hibernation", variable=self.disable_hibernation).pack(anchor='w', pady=2)

        # Power plan
        power_group = ttk.LabelFrame(frame, text="Power Plan", padding=15)
        power_group.pack(fill='x', padx=10, pady=10)

        ttk.Label(power_group, text="Select the active power plan after setup:", style='Dim.TLabel').pack(anchor='w', pady=(0, 5))
        power_frame = ttk.Frame(power_group, style='TFrame')
        power_frame.pack(fill='x', pady=5)
        for text, value in [("Default", "Default"), ("High Performance", "High"), ("Ultimate Performance", "Ultimate")]:
            ttk.Radiobutton(power_frame, text=text, variable=self.power_plan, value=value).pack(side='left', padx=10)

        # Security (with warnings)
        sec_group = ttk.LabelFrame(frame, text="Security Settings (Use with caution)", padding=15)
        sec_group.pack(fill='x', padx=10, pady=10)

        ttk.Checkbutton(sec_group, text="Prevent Device Encryption (BitLocker)", variable=self.prevent_device_encryption).pack(anchor='w', pady=2)
        ttk.Checkbutton(sec_group, text="Disable Core Isolation / VBS (improves VM performance)", variable=self.disable_vbs).pack(anchor='w', pady=2)
        ttk.Checkbutton(sec_group, text="Disable UAC prompts (not recommended)", variable=self.disable_uac_prompt).pack(anchor='w', pady=2)
        ttk.Checkbutton(sec_group, text="Disable Windows Defender (not recommended)", variable=self.disable_defender).pack(anchor='w', pady=2)
        ttk.Checkbutton(sec_group, text="Clean up Panther unattend.xml after first logon (removes stored password)", variable=self.cleanup_panther_password).pack(anchor='w', pady=2)
        
        # Edge settings
        edge_group = ttk.LabelFrame(frame, text="Microsoft Edge", padding=15)
        edge_group.pack(fill='x', padx=10, pady=10)
        
        ttk.Checkbutton(edge_group, text="Hide Edge First Run Experience dialogs", variable=self.hide_edge_fre).pack(anchor='w', pady=2)
        ttk.Checkbutton(edge_group, text="Disable Edge Startup Boost and Background mode", variable=self.disable_edge_startup).pack(anchor='w', pady=2)
        ttk.Checkbutton(edge_group, text="Delete Edge desktop shortcut", variable=self.delete_edge_shortcut).pack(anchor='w', pady=2)
        ttk.Checkbutton(edge_group, text="Make Edge uninstallable (may cause update issues)", variable=self.make_edge_uninstallable).pack(anchor='w', pady=2)
        ttk.Checkbutton(edge_group, text="Remove OneDrive", variable=self.remove_onedrive).pack(anchor='w', pady=2)
        
        # Explorer
        explorer_group = ttk.LabelFrame(frame, text="File Explorer", padding=15)
        explorer_group.pack(fill='x', padx=10, pady=10)
        
        ttk.Checkbutton(explorer_group, text="Always show file extensions", variable=self.show_file_extensions).pack(anchor='w', pady=2)
        ttk.Checkbutton(explorer_group, text="Show hidden files", variable=self.show_hidden_files).pack(anchor='w', pady=2)
        ttk.Checkbutton(explorer_group, text="Show protected operating system files", variable=self.show_system_files).pack(anchor='w', pady=2)
        ttk.Checkbutton(explorer_group, text="Use classic context menu (right-click)", variable=self.classic_context_menu).pack(anchor='w', pady=2)
        ttk.Checkbutton(explorer_group, text="Open File Explorer to 'This PC'", variable=self.launch_to_this_pc).pack(anchor='w', pady=2)
        
        # Appearance
        appearance_group = ttk.LabelFrame(frame, text="Appearance", padding=15)
        appearance_group.pack(fill='x', padx=10, pady=10)

        ttk.Checkbutton(appearance_group, text="Enable Dark Mode (apps and system)", variable=self.enable_dark_mode).pack(anchor='w', pady=2)

        # Taskbar
        taskbar_group = ttk.LabelFrame(frame, text="Taskbar", padding=15)
        taskbar_group.pack(fill='x', padx=10, pady=10)
        
        ttk.Label(taskbar_group, text="Search box style:", style='Dim.TLabel').pack(anchor='w')
        search_frame = ttk.Frame(taskbar_group, style='TFrame')
        search_frame.pack(fill='x', pady=5)
        for text, value in [("Full", "Box"), ("Icon", "Icon"), ("Hidden", "Hide")]:
            ttk.Radiobutton(search_frame, text=text, variable=self.taskbar_search, value=value).pack(side='left', padx=10)
        
        ttk.Checkbutton(taskbar_group, text="Hide Task View button", variable=self.hide_task_view).pack(anchor='w', pady=2)
        ttk.Checkbutton(taskbar_group, text="Disable Widgets", variable=self.disable_widgets).pack(anchor='w', pady=2)
        ttk.Checkbutton(taskbar_group, text="Hide Copilot button", variable=self.hide_copilot).pack(anchor='w', pady=2)
        ttk.Checkbutton(taskbar_group, text="Use small taskbar icons", variable=self.small_taskbar).pack(anchor='w', pady=2)

    def create_bloatware_tab(self):
        """Bloatware removal settings"""
        tab = ttk.Frame(self.notebook, style='TFrame')
        self.notebook.add(tab, text='  Remove Bloatware  ')
        
        scroll = ModernScrollableFrame(tab)
        scroll.pack(fill='both', expand=True)
        frame = scroll.scrollable_frame
        
        # Header
        header = ttk.Frame(frame, style='TFrame')
        header.pack(fill='x', padx=10, pady=10)
        ttk.Label(header, text="Select apps to remove during Windows installation", style='Dim.TLabel').pack(side='left')
        
        btn_frame = ttk.Frame(header, style='TFrame')
        btn_frame.pack(side='right')
        ttk.Button(btn_frame, text="Safe List", command=lambda: self.set_bloatware_level("safe")).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Aggressive List", command=lambda: self.set_bloatware_level("aggressive")).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Select All", command=lambda: self.set_all_bloatware(True)).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Deselect All", command=lambda: self.set_all_bloatware(False)).pack(side='left', padx=5)
        
        # App list in columns
        group = ttk.LabelFrame(frame, text="Windows Apps", padding=15)
        group.pack(fill='x', padx=10, pady=10)
        
        # Create 3-column layout
        apps_list = list(self.bloatware_apps.items())
        cols = 3
        rows_per_col = (len(apps_list) + cols - 1) // cols

        col_frames = []
        for i in range(cols):
            col_frame = ttk.Frame(group, style='TFrame')
            col_frame.pack(side='left', fill='both', expand=True, padx=5)
            col_frames.append(col_frame)

        for idx, (app_id, var) in enumerate(apps_list):
            col_idx = idx // rows_per_col
            if col_idx >= cols:
                col_idx = cols - 1
            display_name, risk, tooltip_text = self.BLOATWARE_CATALOG.get(app_id, (app_id.split('.')[-1], 'aggressive', ''))
            row = ttk.Frame(col_frames[col_idx], style='TFrame')
            row.pack(fill='x', pady=1)
            cb = ttk.Checkbutton(row, text=f"{display_name} ({risk})", variable=var)
            cb.pack(side='left', anchor='w')
            ttk.Combobox(row, textvariable=self.bloatware_app_modes[app_id], values=self.BLOATWARE_REMOVAL_MODES, width=19, state='readonly').pack(side='right', padx=(5, 0))
            if tooltip_text:
                self._create_tooltip(cb, tooltip_text)
            
    def set_all_bloatware(self, value):
        """Set all bloatware checkboxes"""
        for var in self.bloatware_apps.values():
            var.set(value)

    def set_bloatware_level(self, level):
        """Select bloatware entries by risk level."""
        self.set_all_bloatware(False)
        for app_id, var in self.bloatware_apps.items():
            if self.BLOATWARE_CATALOG.get(app_id, ("", "", ""))[1] == level:
                var.set(True)

    def apply_region_preset(self):
        """Apply a bundled language/locale/keyboard/timezone preset."""
        preset = self.REGION_PRESETS.get(self.region_preset.get())
        if not preset:
            return
        ui_language, locale, keyboard, timezone = preset
        self.ui_language.set(ui_language)
        self.locale.set(locale)
        self.keyboard.set(keyboard)
        self.timezone.set(timezone)

    @staticmethod
    def _ps_single_quote(value):
        """Quote a value for a PowerShell single-quoted string."""
        return str(value).replace("'", "''")

    def _component_open(self, name, include_wcm=False):
        attrs = (
            f'name="{name}" processorArchitecture="{self.target_architecture.get()}" '
            'publicKeyToken="31bf3856ad364e35" language="neutral" versionScope="nonSxS"'
        )
        if include_wcm:
            attrs += ' xmlns:wcm="http://schemas.microsoft.com/WMIConfig/2002/State"'
        return f'    <component {attrs}>\n'

    def _format_password(self, password):
        if password and self.obscure_passwords.get():
            encoded = base64.b64encode((password + "Password").encode('utf-16-le')).decode()
            return encoded, "false"
        return password, "true"

    def _get_text_widget_value(self, attr_name):
        widget = getattr(self, attr_name, None)
        if widget is None:
            return ""
        try:
            return widget.get('1.0', 'end').rstrip('\n')
        except Exception:
            return ""

    def _get_additional_accounts(self):
        raw = self._get_text_widget_value('additional_accounts_text')
        accounts = []
        if not raw.strip():
            return accounts

        reader = csv.reader(StringIO(raw))
        for row in reader:
            if not row:
                continue
            first = row[0].strip()
            if not first or first.startswith('#'):
                continue
            if len(accounts) >= 98:
                break
            name = first
            display_name = row[1].strip() if len(row) > 1 and row[1].strip() else name
            group = row[2].strip() if len(row) > 2 and row[2].strip() else "Users"
            password = row[3] if len(row) > 3 else ""
            accounts.append({
                "name": name,
                "display_name": display_name,
                "group": group,
                "password": password,
            })
        return accounts

    @staticmethod
    def _validate_computer_name(name):
        if not name or name == "*":
            return True, ""
        if len(name) > 15:
            return False, "Computer name must be 15 characters or fewer."
        if name.isdigit():
            return False, "Computer name cannot contain only numbers."
        invalid_chars = set(r'"\[]:;|=,+*?<>/\\')
        found = [c for c in name if c in invalid_chars]
        if found:
            return False, f"Computer name contains invalid characters: {''.join(sorted(set(found)))}"
        return True, ""

    def validate_configuration(self):
        """Return a list of user-correctable configuration errors."""
        errors = []
        account_name = self.account_name.get() or "Admin"
        valid, err = self._validate_account_name(account_name)
        if not valid:
            errors.append(f"Primary account invalid: {err}")

        valid, err = self._validate_computer_name(self.computer_name.get() or "*")
        if not valid:
            errors.append(err)

        seen = {account_name.lower()}
        for account in self._get_additional_accounts():
            valid, err = self._validate_account_name(account["name"])
            if not valid:
                errors.append(f"Additional account '{account['name']}' invalid: {err}")
            key = account["name"].lower()
            if key in seen:
                errors.append(f"Duplicate account name: {account['name']}")
            seen.add(key)
            if account["group"] not in ("Administrators", "Users"):
                errors.append(f"Additional account '{account['name']}' group must be Administrators or Users.")

        if self.target_architecture.get() not in ("amd64", "arm64"):
            errors.append("Target architecture must be amd64 or arm64.")

        return errors

    def _selected_bloatware_by_mode(self):
        grouped = {mode: [] for mode in self.BLOATWARE_REMOVAL_MODES}
        for app_id, var in self.bloatware_apps.items():
            if not var.get():
                continue
            mode = self.bloatware_app_modes[app_id].get()
            if mode not in grouped:
                mode = "Provisioned + per-user"
            grouped[mode].append(app_id)
        return {mode: apps for mode, apps in grouped.items() if apps}

    def _build_bloatware_command(self, apps, mode):
        apps_str = "', '".join(self._ps_single_quote(app) for app in apps)
        remove_per_user = mode in ("Provisioned + per-user", "Per-user only")
        remove_provisioned = mode in ("Provisioned + per-user", "Provisioned only")
        commands = [
            f"$apps = @('{apps_str}')",
            "foreach ($app in $apps) {",
        ]
        if remove_per_user:
            commands.append("  Get-AppxPackage -Name $app -AllUsers | Remove-AppxPackage -AllUsers -ErrorAction SilentlyContinue")
        if remove_provisioned:
            commands.append("  Get-AppxProvisionedPackage -Online | Where-Object { $_.DisplayName -eq $app -or $_.PackageName -like \"*$app*\" } | Remove-AppxProvisionedPackage -Online -ErrorAction SilentlyContinue")
        commands.append("}")
        return 'powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "{}"'.format("; ".join(commands).replace('"', '\\"'))

    def _build_webhook_command(self):
        url = self.completion_webhook_url.get().strip()
        if not url:
            return ""
        payload_type = self.completion_webhook_type.get()
        quoted_url = self._ps_single_quote(url)
        if payload_type == "Discord":
            body = "@{content=('Windows setup complete on ' + $env:COMPUTERNAME)} | ConvertTo-Json -Compress"
        elif payload_type == "Slack":
            body = "@{text=('Windows setup complete on ' + $env:COMPUTERNAME)} | ConvertTo-Json -Compress"
        else:
            body = "@{status='complete'; hostname=$env:COMPUTERNAME; generatedBy='bypassnroGen'} | ConvertTo-Json -Compress"
        ps = f"$body = {body}; Invoke-RestMethod -Uri '{quoted_url}' -Method Post -ContentType 'application/json' -Body $body"
        return 'powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "{}"'.format(ps.replace('"', '\\"'))

    def validate_generated_xml(self):
        """Validate generated XML for well-formedness and local compatibility checks."""
        errors = []
        try:
            ET.fromstring(self.generate_unattend_xml())
        except ET.ParseError as exc:
            errors.append(f"unattend.xml is not well-formed XML: {exc}")
        if self.target_architecture.get() not in ("amd64", "arm64"):
            errors.append("Unsupported target architecture.")
        return errors
            
    def create_scripts_tab(self):
        """Custom scripts tab"""
        tab = ttk.Frame(self.notebook, style='TFrame')
        self.notebook.add(tab, text='  Custom Scripts  ')
        
        scroll = ModernScrollableFrame(tab)
        scroll.pack(fill='both', expand=True)
        frame = scroll.scrollable_frame
        
        # System script
        group = ttk.LabelFrame(frame, text="System Script (runs before user accounts are created)", padding=15)
        group.pack(fill='x', padx=10, pady=10)
        
        ttk.Label(group, text="Add custom commands to run during the specialize phase:", style='Dim.TLabel').pack(anchor='w', pady=(0, 10))
        
        self.system_script_text = tk.Text(group, height=8, bg='#2d2d2d', fg='#ffffff', insertbackground='#ffffff', font=('Consolas', 10))
        self.system_script_text.pack(fill='x', pady=5)
        self.system_script_text.insert('1.0', ':: Add your custom commands here\n:: Example: powercfg.exe /HIBERNATE OFF')
        
        # First logon script
        group2 = ttk.LabelFrame(frame, text="First Logon Script (runs when first user logs in)", padding=15)
        group2.pack(fill='x', padx=10, pady=10)
        
        ttk.Label(group2, text="Add custom commands to run after the first user logs in:", style='Dim.TLabel').pack(anchor='w', pady=(0, 10))
        
        self.firstlogon_script_text = tk.Text(group2, height=8, bg='#2d2d2d', fg='#ffffff', insertbackground='#ffffff', font=('Consolas', 10))
        self.firstlogon_script_text.pack(fill='x', pady=5)
        self.firstlogon_script_text.insert('1.0', ':: Add your custom commands here\n:: Example: setx DIRCMD "/A /O:GN /C /N"')

        webhook_group = ttk.LabelFrame(frame, text="Deployment Completion Webhook", padding=15)
        webhook_group.pack(fill='x', padx=10, pady=10)

        row = ttk.Frame(webhook_group, style='TFrame')
        row.pack(fill='x', pady=5)
        ttk.Label(row, text="Webhook URL:", width=20).pack(side='left')
        ttk.Entry(row, textvariable=self.completion_webhook_url, width=70).pack(side='left', padx=10)

        row = ttk.Frame(webhook_group, style='TFrame')
        row.pack(fill='x', pady=5)
        ttk.Label(row, text="Payload Type:", width=20).pack(side='left')
        ttk.Combobox(row, textvariable=self.completion_webhook_type, values=["Generic JSON", "Discord", "Slack"], width=20, state='readonly').pack(side='left', padx=10)
        
    def create_preview_tab(self):
        """Preview generated files"""
        tab = ttk.Frame(self.notebook, style='TFrame')
        self.notebook.add(tab, text='  Preview Output  ')
        
        # Create paned window for side-by-side view
        paned = ttk.PanedWindow(tab, orient='horizontal')
        paned.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Bypass.cmd preview
        left_frame = ttk.LabelFrame(paned, text="bypass.cmd", padding=10)
        paned.add(left_frame, weight=1)
        
        self.bypass_preview = tk.Text(left_frame, bg='#1e1e1e', fg='#00ff00', insertbackground='#00ff00', font=('Consolas', 9), wrap='none')
        self.bypass_preview.pack(fill='both', expand=True)
        
        # Unattend.xml preview
        right_frame = ttk.LabelFrame(paned, text="unattend.xml", padding=10)
        paned.add(right_frame, weight=1)
        
        self.unattend_preview = tk.Text(right_frame, bg='#1e1e1e', fg='#87ceeb', insertbackground='#87ceeb', font=('Consolas', 9), wrap='none')
        self.unattend_preview.pack(fill='both', expand=True)
        
        # Refresh button
        btn_frame = ttk.Frame(tab, style='TFrame')
        btn_frame.pack(fill='x', padx=10, pady=5)
        ttk.Button(btn_frame, text="Refresh Preview", command=self.update_preview).pack(side='right')
        
    def generate_bypass_cmd(self):
        """Generate the bypass.cmd content"""
        user = self.github_user.get()
        repo = self.github_repo.get()
        branch = self.github_branch.get()
        unattend_url = f"https://raw.githubusercontent.com/{user}/{repo}/refs/heads/{branch}/unattend.xml"
        
        cmd = '''@echo off
:: Bypass NRO Generator - Windows 11 OOBE Bypass Script
:: Version: {version}
:: Generated: {date}
:: GitHub: https://github.com/{user}/{repo}

echo ============================================
echo  Windows 11 OOBE Bypass Script
echo  Generated by Bypass NRO Generator
echo ============================================
echo.

:: Download unattend.xml from GitHub
echo Downloading unattend.xml...
curl -L -o C:\\Windows\\Panther\\unattend.xml "{unattend_url}"

if %errorlevel% neq 0 (
    echo Failed to download unattend.xml. Trying alternative method...
    powershell -Command "Invoke-WebRequest -Uri '{unattend_url}' -OutFile 'C:\\Windows\\Panther\\unattend.xml'"
)

if exist C:\\Windows\\Panther\\unattend.xml (
    echo unattend.xml downloaded successfully!
) else (
    echo ERROR: Failed to download unattend.xml
    pause
    exit /b 1
)

        '''.format(
            version=APP_VERSION,
            date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            user=user,
            repo=repo,
            unattend_url=unattend_url
        )
        
        # Add BypassNRO registry key
        if self.bypass_nro.get():
            cmd += ''':: Set BypassNRO registry key
echo Setting BypassNRO registry key...
reg add "HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\OOBE" /v BypassNRO /t REG_DWORD /d 1 /f

'''

        if self.msa_localonly_bypass.get():
            cmd += ''':: Launch local-only account flow URI
echo Launching local-only account flow...
start "" "ms-cxh://setaddlocalonly"

'''
        
        # Add system requirements bypass
        if self.bypass_requirements.get():
            cmd += ''':: Bypass Windows 11 system requirements
echo Bypassing system requirements...
reg add "HKLM\\SYSTEM\\Setup\\LabConfig" /v BypassTPMCheck /t REG_DWORD /d 1 /f
reg add "HKLM\\SYSTEM\\Setup\\LabConfig" /v BypassRAMCheck /t REG_DWORD /d 1 /f
reg add "HKLM\\SYSTEM\\Setup\\LabConfig" /v BypassSecureBootCheck /t REG_DWORD /d 1 /f
reg add "HKLM\\SYSTEM\\Setup\\LabConfig" /v BypassStorageCheck /t REG_DWORD /d 1 /f
reg add "HKLM\\SYSTEM\\Setup\\LabConfig" /v BypassCPUCheck /t REG_DWORD /d 1 /f

'''
        
        # Add privacy/telemetry settings
        if self.disable_telemetry.get():
            cmd += ''':: Disable telemetry
reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\DataCollection" /v AllowTelemetry /t REG_DWORD /d 0 /f

'''
        
        if self.disable_cortana.get():
            cmd += ''':: Disable Cortana
reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\Windows Search" /v AllowCortana /t REG_DWORD /d 0 /f

'''
        
        if self.disable_consumer_features.get():
            cmd += ''':: Disable Consumer Features / Content Delivery Manager
reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\CloudContent" /v DisableWindowsConsumerFeatures /t REG_DWORD /d 1 /f
reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\CloudContent" /v DisableSoftLanding /t REG_DWORD /d 1 /f

'''

        if self.disable_wifi_sense.get():
            cmd += ''':: Disable Wi-Fi Sense
reg add "HKLM\\SOFTWARE\\Microsoft\\WcmSvc\\wifinetworkmanager\\config" /v AutoConnectAllowedOEM /t REG_DWORD /d 0 /f

'''

        if self.disable_activity_history.get():
            cmd += ''':: Disable Activity History
reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\System" /v EnableActivityFeed /t REG_DWORD /d 0 /f
reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\System" /v PublishUserActivities /t REG_DWORD /d 0 /f

'''

        if self.disable_location.get():
            cmd += ''':: Disable Location Services
reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\LocationAndSensors" /v DisableLocation /t REG_DWORD /d 1 /f

'''

        # Reboot command
        cmd += ''':: Reboot to apply changes
echo.
echo Setup complete! The system will restart in 5 seconds...
echo Press Ctrl+C to cancel.
timeout /t 5
shutdown /r /t 0
'''
        
        return cmd
        
    def generate_unattend_xml(self):
        """Generate the unattend.xml content"""
        esc = self._esc
        account_name = self.account_name.get() or "Admin"
        display_name = self.account_display.get() or account_name
        password = self.account_password.get()
        computer_name = self.computer_name.get() or "*"
        additional_accounts = self._get_additional_accounts()

        password_encoded, password_plain = self._format_password(password)

        # Build bloatware removal list grouped by removal method
        apps_by_mode = self._selected_bloatware_by_mode()

        # Collect custom scripts from text widgets (not the unused StringVars)
        system_script_lines = []
        firstlogon_script_lines = []
        try:
            raw = self.system_script_text.get('1.0', 'end').strip()
            for line in raw.splitlines():
                stripped = line.strip()
                if stripped and not stripped.startswith('::'):
                    system_script_lines.append(stripped)
        except Exception:
            pass
        try:
            raw = self.firstlogon_script_text.get('1.0', 'end').strip()
            for line in raw.splitlines():
                stripped = line.strip()
                if stripped and not stripped.startswith('::'):
                    firstlogon_script_lines.append(stripped)
        except Exception:
            pass

        xml = '<?xml version="1.0" encoding="utf-8"?>\n'
        xml += '<!--\n'
        xml += '  Bypass NRO Generator - Windows 11 Unattended Installation\n'
        xml += '  Version: {}\n'.format(APP_VERSION)
        xml += '  Generated: {}\n'.format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        xml += '-->\n'
        xml += '<unattend xmlns="urn:schemas-microsoft-com:unattend">\n'

        # Windows PE pass - for system requirements bypass and disk layout
        if self.bypass_requirements.get() or self.enable_disk_partitioning.get():
            xml += '  <settings pass="windowsPE">\n'
            xml += self._component_open("Microsoft-Windows-Setup", include_wcm=True)
            if self.enable_disk_partitioning.get():
                xml += '      <DiskConfiguration>\n'
                xml += '        <Disk wcm:action="add">\n'
                xml += '          <DiskID>0</DiskID>\n'
                xml += '          <WillWipeDisk>true</WillWipeDisk>\n'
                xml += '          <CreatePartitions>\n'
                xml += '            <CreatePartition wcm:action="add"><Order>1</Order><Type>EFI</Type><Size>100</Size></CreatePartition>\n'
                xml += '            <CreatePartition wcm:action="add"><Order>2</Order><Type>MSR</Type><Size>16</Size></CreatePartition>\n'
                xml += '            <CreatePartition wcm:action="add"><Order>3</Order><Type>Primary</Type><Extend>true</Extend></CreatePartition>\n'
                xml += '          </CreatePartitions>\n'
                xml += '          <ModifyPartitions>\n'
                xml += '            <ModifyPartition wcm:action="add"><Order>1</Order><PartitionID>1</PartitionID><Format>FAT32</Format><Label>System</Label></ModifyPartition>\n'
                xml += '            <ModifyPartition wcm:action="add"><Order>2</Order><PartitionID>3</PartitionID><Format>NTFS</Format><Label>Windows</Label><Letter>C</Letter></ModifyPartition>\n'
                xml += '          </ModifyPartitions>\n'
                xml += '        </Disk>\n'
                xml += '        <WillShowUI>OnError</WillShowUI>\n'
                xml += '      </DiskConfiguration>\n'
                xml += '      <ImageInstall>\n'
                xml += '        <OSImage>\n'
                xml += '          <InstallTo><DiskID>0</DiskID><PartitionID>3</PartitionID></InstallTo>\n'
                xml += '          <WillShowUI>OnError</WillShowUI>\n'
                xml += '        </OSImage>\n'
                xml += '      </ImageInstall>\n'
            if self.bypass_requirements.get():
                xml += '      <RunSynchronous>\n'
                for i, check in enumerate(["BypassTPMCheck", "BypassRAMCheck", "BypassSecureBootCheck", "BypassStorageCheck", "BypassCPUCheck"], 1):
                    xml += '        <RunSynchronousCommand wcm:action="add">\n'
                    xml += '          <Order>{}</Order>\n'.format(i)
                    xml += '          <Path>reg add "HKLM\\SYSTEM\\Setup\\LabConfig" /v {} /t REG_DWORD /d 1 /f</Path>\n'.format(check)
                    xml += '        </RunSynchronousCommand>\n'
                xml += '      </RunSynchronous>\n'
            xml += '    </component>\n'
            xml += '  </settings>\n\n'

        # Specialize pass
        xml += '  <settings pass="specialize">\n'
        xml += self._component_open("Microsoft-Windows-Deployment", include_wcm=True)
        xml += '      <RunSynchronous>\n'

        order = 1

        def _add_spec_cmd(path_str):
            nonlocal order, xml
            xml += '        <RunSynchronousCommand wcm:action="add">\n'
            xml += '          <Order>{}</Order>\n'.format(order)
            xml += '          <Path>{}</Path>\n'.format(esc(path_str))
            xml += '        </RunSynchronousCommand>\n'
            order += 1

        # BypassNRO
        if self.bypass_nro.get():
            _add_spec_cmd('reg add "HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\OOBE" /v BypassNRO /t REG_DWORD /d 1 /f')

        # Long paths
        if self.enable_long_paths.get():
            _add_spec_cmd('reg add "HKLM\\SYSTEM\\CurrentControlSet\\Control\\FileSystem" /v LongPathsEnabled /t REG_DWORD /d 1 /f')

        # RDP
        if self.enable_rdp.get():
            _add_spec_cmd('reg add "HKLM\\SYSTEM\\CurrentControlSet\\Control\\Terminal Server" /v fDenyTSConnections /t REG_DWORD /d 0 /f')
            _add_spec_cmd('netsh advfirewall firewall set rule group="remote desktop" new enable=Yes')

        # PowerShell execution policy
        if self.allow_powershell_scripts.get():
            _add_spec_cmd('powershell.exe -Command "Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Force"')

        # Disable hibernation
        if self.disable_hibernation.get():
            _add_spec_cmd('powercfg.exe /HIBERNATE OFF')

        # Prevent device encryption
        if self.prevent_device_encryption.get():
            _add_spec_cmd('reg add "HKLM\\SYSTEM\\CurrentControlSet\\Control\\BitLocker" /v PreventDeviceEncryption /t REG_DWORD /d 1 /f')

        # Disable VBS
        if self.disable_vbs.get():
            _add_spec_cmd('reg add "HKLM\\SYSTEM\\CurrentControlSet\\Control\\DeviceGuard" /v EnableVirtualizationBasedSecurity /t REG_DWORD /d 0 /f')

        # Disable UAC prompt
        if self.disable_uac_prompt.get():
            _add_spec_cmd('reg add "HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\System" /v EnableLUA /t REG_DWORD /d 0 /f')

        # Disable Defender
        if self.disable_defender.get():
            _add_spec_cmd('reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows Defender" /v DisableAntiSpyware /t REG_DWORD /d 1 /f')

        # Disable fast boot
        if self.disable_fast_boot.get():
            _add_spec_cmd('reg add "HKLM\\SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Power" /v HiberbootEnabled /t REG_DWORD /d 0 /f')

        # Custom system scripts (specialize phase)
        for line in system_script_lines:
            _add_spec_cmd(line)

        xml += '      </RunSynchronous>\n'
        xml += '    </component>\n'
        xml += self._component_open("Microsoft-Windows-Shell-Setup")
        xml += '      <ComputerName>{}</ComputerName>\n'.format(esc(computer_name))
        xml += '      <TimeZone>{}</TimeZone>\n'.format(esc(self.timezone.get()))
        xml += '    </component>\n'
        xml += '  </settings>\n\n'

        # OOBE System pass
        xml += '  <settings pass="oobeSystem">\n'
        xml += self._component_open("Microsoft-Windows-International-Core")
        xml += '      <InputLocale>{}</InputLocale>\n'.format(esc(self.keyboard.get()))
        xml += '      <SystemLocale>{}</SystemLocale>\n'.format(esc(self.locale.get()))
        xml += '      <UILanguage>{}</UILanguage>\n'.format(esc(self.ui_language.get()))
        xml += '      <UserLocale>{}</UserLocale>\n'.format(esc(self.locale.get()))
        xml += '    </component>\n'
        xml += self._component_open("Microsoft-Windows-Shell-Setup", include_wcm=True)
        xml += '      <OOBE>\n'
        xml += '        <HideEULAPage>{}</HideEULAPage>\n'.format("true" if self.skip_eula.get() else "false")
        xml += '        <HideOnlineAccountScreens>{}</HideOnlineAccountScreens>\n'.format("true" if self.hide_online_account.get() else "false")
        xml += '        <HideLocalAccountScreen>{}</HideLocalAccountScreen>\n'.format("true" if self.hide_local_account.get() else "false")
        xml += '        <HideWirelessSetupInOOBE>true</HideWirelessSetupInOOBE>\n'
        xml += '        <ProtectYourPC>{}</ProtectYourPC>\n'.format(self.protect_your_pc.get())
        xml += '      </OOBE>\n'
        xml += '      <UserAccounts>\n'
        xml += '        <LocalAccounts>\n'
        local_accounts = [{
            "name": account_name,
            "display_name": display_name,
            "group": self.account_group.get(),
            "password": password,
        }] + additional_accounts
        for account in local_accounts:
            account_password_encoded, account_password_plain = self._format_password(account["password"])
            xml += '          <LocalAccount wcm:action="add">\n'
            xml += '            <Name>{}</Name>\n'.format(esc(account["name"]))
            xml += '            <DisplayName>{}</DisplayName>\n'.format(esc(account["display_name"]))
            xml += '            <Group>{}</Group>\n'.format(esc(account["group"]))
            xml += '            <Password>\n'
            xml += '              <Value>{}</Value>\n'.format(esc(account_password_encoded) if account["password"] else "")
            xml += '              <PlainText>{}</PlainText>\n'.format(account_password_plain)
            xml += '            </Password>\n'
            xml += '          </LocalAccount>\n'
        xml += '        </LocalAccounts>\n'
        xml += '      </UserAccounts>\n'

        # Auto logon
        if self.auto_logon.get():
            xml += '      <AutoLogon>\n'
            xml += '        <Username>{}</Username>\n'.format(esc(account_name))
            xml += '        <Enabled>true</Enabled>\n'
            xml += '        <LogonCount>1</LogonCount>\n'
            xml += '        <Password>\n'
            xml += '          <Value>{}</Value>\n'.format(esc(password_encoded) if password else "")
            xml += '          <PlainText>{}</PlainText>\n'.format(password_plain)
            xml += '        </Password>\n'
            xml += '      </AutoLogon>\n'

        # First logon commands
        xml += '      <FirstLogonCommands>\n'
        cmd_order = 1

        def _add_firstlogon_cmd(cmdline, description):
            nonlocal cmd_order, xml
            xml += '        <SynchronousCommand wcm:action="add">\n'
            xml += '          <Order>{}</Order>\n'.format(cmd_order)
            xml += '          <CommandLine>{}</CommandLine>\n'.format(esc(cmdline))
            xml += '          <Description>{}</Description>\n'.format(esc(description))
            xml += '        </SynchronousCommand>\n'
            cmd_order += 1

        # Bloatware removal
        for mode, apps in apps_by_mode.items():
            _add_firstlogon_cmd(
                self._build_bloatware_command(apps, mode),
                f"Remove bloatware apps ({mode})"
            )

        # Explorer tweaks
        if self.show_file_extensions.get():
            _add_firstlogon_cmd('reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced" /v HideFileExt /t REG_DWORD /d 0 /f', "Show file extensions")

        if self.show_hidden_files.get():
            _add_firstlogon_cmd('reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced" /v Hidden /t REG_DWORD /d 1 /f', "Show hidden files")

        if self.show_system_files.get():
            _add_firstlogon_cmd('reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced" /v ShowSuperHidden /t REG_DWORD /d 1 /f', "Show protected operating system files")

        if self.classic_context_menu.get():
            _add_firstlogon_cmd('reg add "HKCU\\Software\\Classes\\CLSID\\{86ca1aa0-34aa-4e8b-a509-50c905bae2a2}\\InprocServer32" /ve /f', "Enable classic context menu")

        if self.launch_to_this_pc.get():
            _add_firstlogon_cmd('reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced" /v LaunchTo /t REG_DWORD /d 1 /f', "Open Explorer to This PC")

        # Dark mode
        if self.enable_dark_mode.get():
            _add_firstlogon_cmd('reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize" /v AppsUseLightTheme /t REG_DWORD /d 0 /f', "Enable dark mode for apps")
            _add_firstlogon_cmd('reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize" /v SystemUsesLightTheme /t REG_DWORD /d 0 /f', "Enable dark mode for system")

        # Taskbar settings
        if self.taskbar_search.get() == "Hide":
            _add_firstlogon_cmd('reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Search" /v SearchboxTaskbarMode /t REG_DWORD /d 0 /f', "Hide search box")
        elif self.taskbar_search.get() == "Icon":
            _add_firstlogon_cmd('reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Search" /v SearchboxTaskbarMode /t REG_DWORD /d 1 /f', "Show search icon")

        if self.hide_task_view.get():
            _add_firstlogon_cmd('reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced" /v ShowTaskViewButton /t REG_DWORD /d 0 /f', "Hide Task View button")

        if self.disable_widgets.get():
            _add_firstlogon_cmd('reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced" /v TaskbarDa /t REG_DWORD /d 0 /f', "Disable widgets")

        if self.hide_copilot.get():
            _add_firstlogon_cmd('reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced" /v ShowCopilotButton /t REG_DWORD /d 0 /f', "Hide Copilot button")

        if self.small_taskbar.get():
            _add_firstlogon_cmd('reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced" /v TaskbarSi /t REG_DWORD /d 0 /f', "Use small taskbar icons")

        # Edge settings
        if self.hide_edge_fre.get():
            _add_firstlogon_cmd('reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Edge" /v HideFirstRunExperience /t REG_DWORD /d 1 /f', "Hide Edge First Run Experience")

        if self.disable_edge_startup.get():
            _add_firstlogon_cmd('reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Edge" /v StartupBoostEnabled /t REG_DWORD /d 0 /f', "Disable Edge Startup Boost")

        if self.delete_edge_shortcut.get():
            _add_firstlogon_cmd('cmd /c del /q "%PUBLIC%\\Desktop\\Microsoft Edge.lnk" 2>nul', "Delete Edge desktop shortcut")

        if self.make_edge_uninstallable.get():
            _add_firstlogon_cmd('reg add "HKLM\\SOFTWARE\\WOW6432Node\\Microsoft\\EdgeUpdate" /v Allowsxs /t REG_DWORD /d 1 /f', "Allow Edge side-by-side (make uninstallable)")

        # OneDrive removal
        if self.remove_onedrive.get():
            _add_firstlogon_cmd('powershell.exe -NoProfile -Command "Get-Process OneDrive -ErrorAction SilentlyContinue | Stop-Process -Force; Start-Sleep 2; if (Test-Path \\"$env:SystemRoot\\SysWOW64\\OneDriveSetup.exe\\") { & \\"$env:SystemRoot\\SysWOW64\\OneDriveSetup.exe\\" /uninstall } elseif (Test-Path \\"$env:SystemRoot\\System32\\OneDriveSetup.exe\\") { & \\"$env:SystemRoot\\System32\\OneDriveSetup.exe\\" /uninstall }"', "Remove OneDrive")

        # Power plan
        if self.power_plan.get() == "High":
            _add_firstlogon_cmd('powercfg /setactive 8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c', "Set High Performance power plan")
        elif self.power_plan.get() == "Ultimate":
            _add_firstlogon_cmd('powercfg -duplicatescheme e9a42b02-d5df-448d-aa00-03f14749eb61', "Add Ultimate Performance power plan")
            _add_firstlogon_cmd('powercfg /setactive e9a42b02-d5df-448d-aa00-03f14749eb61', "Set Ultimate Performance power plan")

        # Privacy settings in FirstLogonCommands
        if self.disable_telemetry.get():
            _add_firstlogon_cmd('reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\DataCollection" /v AllowTelemetry /t REG_DWORD /d 0 /f', "Disable telemetry")

        if self.disable_advertising_id.get():
            _add_firstlogon_cmd('reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\AdvertisingInfo" /v Enabled /t REG_DWORD /d 0 /f', "Disable advertising ID")

        if self.disable_wifi_sense.get():
            _add_firstlogon_cmd('reg add "HKLM\\SOFTWARE\\Microsoft\\WcmSvc\\wifinetworkmanager\\config" /v AutoConnectAllowedOEM /t REG_DWORD /d 0 /f', "Disable Wi-Fi Sense")

        if self.disable_activity_history.get():
            _add_firstlogon_cmd('reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\System" /v EnableActivityFeed /t REG_DWORD /d 0 /f', "Disable activity history")
            _add_firstlogon_cmd('reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\System" /v PublishUserActivities /t REG_DWORD /d 0 /f', "Disable publish user activities")

        if self.disable_location.get():
            _add_firstlogon_cmd('reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\LocationAndSensors" /v DisableLocation /t REG_DWORD /d 1 /f', "Disable location services")

        # System tweaks in FirstLogonCommands
        if self.disable_auto_restart.get():
            _add_firstlogon_cmd('reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\WindowsUpdate\\AU" /v NoAutoRebootWithLoggedOnUsers /t REG_DWORD /d 1 /f', "Prevent automatic restart after updates")

        if self.disable_system_sounds.get():
            _add_firstlogon_cmd('reg add "HKCU\\AppEvents\\Schemes" /ve /t REG_SZ /d ".None" /f', "Disable system sounds")

        # Custom first-logon scripts
        for line in firstlogon_script_lines:
            _add_firstlogon_cmd(line, "Custom script")

        webhook_cmd = self._build_webhook_command()
        if webhook_cmd:
            _add_firstlogon_cmd(webhook_cmd, "Send deployment completion webhook")

        # Panther password cleanup (should run last)
        if self.cleanup_panther_password.get():
            _add_firstlogon_cmd('cmd /c del /q /f "C:\\Windows\\Panther\\unattend.xml" 2>nul', "Clean up Panther unattend.xml (remove stored password)")

        xml += '      </FirstLogonCommands>\n'
        xml += '    </component>\n'
        if self.audit_mode.get():
            xml += self._component_open("Microsoft-Windows-Deployment")
            xml += '      <Reseal>\n'
            xml += '        <Mode>Audit</Mode>\n'
            xml += '      </Reseal>\n'
            xml += '    </component>\n'
        xml += '  </settings>\n'
        xml += '</unattend>\n'

        return xml

    def generate_autounattend_xml(self):
        """Generate autounattend.xml for USB root.

        This is essentially the same as unattend.xml but is named
        autounattend.xml so that Windows Setup picks it up automatically
        from the USB root before the user interacts with OOBE at all.
        The content is identical -- the difference is purely in the
        filename and placement.
        """
        return self.generate_unattend_xml()

    def generate_powershell_bootstrap(self):
        """Generate an optional PowerShell bootstrap that can be Authenticode signed."""
        user = self.github_user.get()
        repo = self.github_repo.get()
        branch = self.github_branch.get()
        unattend_url = f"https://raw.githubusercontent.com/{user}/{repo}/refs/heads/{branch}/unattend.xml"
        lines = [
            "#requires -version 5.1",
            f"# {APP_NAME} v{APP_VERSION} bootstrap",
            "$ErrorActionPreference = 'Stop'",
            "$panther = 'C:\\Windows\\Panther'",
            "New-Item -ItemType Directory -Path $panther -Force | Out-Null",
            f"$unattendUrl = '{self._ps_single_quote(unattend_url)}'",
            "$unattendPath = Join-Path $panther 'unattend.xml'",
            "Invoke-WebRequest -Uri $unattendUrl -OutFile $unattendPath",
        ]
        if self.bypass_nro.get():
            lines.append("reg add 'HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\OOBE' /v BypassNRO /t REG_DWORD /d 1 /f | Out-Null")
        if self.msa_localonly_bypass.get():
            lines.append("Start-Process 'ms-cxh://setaddlocalonly'")
        if self.bypass_requirements.get():
            for check in ["BypassTPMCheck", "BypassRAMCheck", "BypassSecureBootCheck", "BypassStorageCheck", "BypassCPUCheck"]:
                lines.append(f"reg add 'HKLM\\SYSTEM\\Setup\\LabConfig' /v {check} /t REG_DWORD /d 1 /f | Out-Null")
        if self.disable_telemetry.get():
            lines.append("reg add 'HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\DataCollection' /v AllowTelemetry /t REG_DWORD /d 0 /f | Out-Null")
        lines.extend([
            "Write-Host 'Setup complete. Restarting in 5 seconds...'",
            "Start-Sleep -Seconds 5",
            "Restart-Computer -Force",
            "",
        ])
        return "\n".join(lines)

    def generate_startnet_cmd(self):
        return """@echo off
wpeinit
set SCRIPTROOT=%~dp0
if exist "%SCRIPTROOT%bypass.cmd" call "%SCRIPTROOT%bypass.cmd"
"""

    def generate_iso_helper_ps1(self):
        return f"""# {APP_NAME} v{APP_VERSION} ISO injection helper
param(
    [Parameter(Mandatory=$true)][string]$IsoPath,
    [string]$WorkDir = (Join-Path $PSScriptRoot 'iso-work'),
    [string]$OutputIso = (Join-Path $PSScriptRoot 'bypassnro-custom.iso'),
    [string]$OscdimgPath = 'oscdimg.exe'
)
$ErrorActionPreference = 'Stop'
if (-not (Test-Path $IsoPath)) {{ throw "ISO not found: $IsoPath" }}
$oscdimg = Get-Command $OscdimgPath -ErrorAction SilentlyContinue
if (-not $oscdimg) {{
    $candidate = "${{env:ProgramFiles(x86)}}\\Windows Kits\\10\\Assessment and Deployment Kit\\Deployment Tools\\amd64\\Oscdimg\\oscdimg.exe"
    if (Test-Path $candidate) {{ $OscdimgPath = $candidate }} else {{ throw 'oscdimg.exe not found. Install the Windows ADK Deployment Tools or pass -OscdimgPath.' }}
}}
if (Test-Path $WorkDir) {{ Remove-Item -LiteralPath $WorkDir -Recurse -Force }}
New-Item -ItemType Directory -Path $WorkDir | Out-Null
$image = Mount-DiskImage -ImagePath $IsoPath -PassThru
try {{
    $volume = $image | Get-Volume
    robocopy "$($volume.DriveLetter):\\" $WorkDir /MIR | Out-Null
}} finally {{
    Dismount-DiskImage -ImagePath $IsoPath | Out-Null
}}
Copy-Item -LiteralPath (Join-Path $PSScriptRoot 'autounattend.xml') -Destination (Join-Path $WorkDir 'autounattend.xml') -Force
Copy-Item -LiteralPath (Join-Path $PSScriptRoot 'bypass.cmd') -Destination (Join-Path $WorkDir 'bypass.cmd') -Force
Copy-Item -LiteralPath (Join-Path $PSScriptRoot 'unattend.xml') -Destination (Join-Path $WorkDir 'unattend.xml') -Force
& $OscdimgPath -m -o -u2 -udfver102 -bootdata:2#p0,e,b"$WorkDir\\boot\\etfsboot.com"#pEF,e,b"$WorkDir\\efi\\microsoft\\boot\\efisys.bin" $WorkDir $OutputIso
Write-Host "Created $OutputIso"
"""

    def generate_usb_helper_ps1(self):
        return f"""# {APP_NAME} v{APP_VERSION} USB staging helper
param(
    [Parameter(Mandatory=$true)][ValidatePattern('^[A-Z]$')][string]$DriveLetter,
    [string]$IsoPath = ''
)
$ErrorActionPreference = 'Stop'
$target = "$DriveLetter`:\\"
$volume = Get-Volume -DriveLetter $DriveLetter -ErrorAction Stop
if ($volume.DriveType -ne 'Removable') {{ throw "$target is not a removable volume." }}
if ($volume.FileSystem -ne 'FAT32') {{ throw "$target must be FAT32 for UEFI boot." }}
if ($IsoPath) {{
    $image = Mount-DiskImage -ImagePath $IsoPath -PassThru
    try {{
        $sourceVolume = $image | Get-Volume
        robocopy "$($sourceVolume.DriveLetter):\\" $target /E | Out-Null
    }} finally {{
        Dismount-DiskImage -ImagePath $IsoPath | Out-Null
    }}
}}
Copy-Item -LiteralPath (Join-Path $PSScriptRoot 'autounattend.xml') -Destination (Join-Path $target 'autounattend.xml') -Force
Copy-Item -LiteralPath (Join-Path $PSScriptRoot 'bypass.cmd') -Destination (Join-Path $target 'bypass.cmd') -Force
Copy-Item -LiteralPath (Join-Path $PSScriptRoot 'unattend.xml') -Destination (Join-Path $target 'unattend.xml') -Force
Write-Host "Staged bypass files to $target"
"""

    def generate_registry_reference_html(self):
        rows = [
            ("BypassNRO", "HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\OOBE", "Allows offline OOBE flow where supported."),
            ("LabConfig bypass values", "HKLM\\SYSTEM\\Setup\\LabConfig", "Bypasses TPM, RAM, Secure Boot, storage, and CPU setup checks."),
            ("AllowTelemetry", "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\DataCollection", "Disables optional telemetry when set to 0 on supported editions."),
            ("LongPathsEnabled", "HKLM\\SYSTEM\\CurrentControlSet\\Control\\FileSystem", "Enables Win32 long path support."),
            ("PreventDeviceEncryption", "HKLM\\SYSTEM\\CurrentControlSet\\Control\\BitLocker", "Prevents automatic device encryption during setup."),
            ("HideFirstRunExperience", "HKLM\\SOFTWARE\\Policies\\Microsoft\\Edge", "Suppresses Microsoft Edge first-run dialogs."),
            ("SearchboxTaskbarMode", "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Search", "Controls taskbar search visibility."),
        ]
        body_rows = "\n".join(
            f"<tr><td>{xml_escape(name)}</td><td><code>{xml_escape(path)}</code></td><td>{xml_escape(effect)}</td></tr>"
            for name, path, effect in rows
        )
        return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>{APP_NAME} v{APP_VERSION} Registry Reference</title>
<style>
body {{ background:#121212; color:#f5f5f5; font-family:Segoe UI,Arial,sans-serif; margin:32px; }}
table {{ border-collapse:collapse; width:100%; }}
th,td {{ border:1px solid #404040; padding:10px; text-align:left; }}
th {{ background:#1e1e1e; }}
code {{ color:#1ed760; }}
</style>
</head>
<body>
<h1>{APP_NAME} v{APP_VERSION} Registry Reference</h1>
<table><thead><tr><th>Setting</th><th>Registry Path</th><th>Effect</th></tr></thead><tbody>
{body_rows}
</tbody></table>
</body>
</html>
"""

    def generate_validation_report(self):
        errors = self.validate_generated_xml()
        lines = [
            f"{APP_NAME} v{APP_VERSION} validation report",
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "Local checks:",
            "- unattend.xml well-formed: {}".format("no" if errors else "yes"),
            f"- target architecture: {self.target_architecture.get()}",
            f"- Disk 0 partitioning enabled: {self.enable_disk_partitioning.get()}",
            "",
            "Windows ADK / WSIM schema validation: not run here; requires the target Windows image catalog from the Windows ADK.",
        ]
        if errors:
            lines.append("")
            lines.append("Errors:")
            lines.extend(f"- {err}" for err in errors)
        return "\n".join(lines) + "\n"

    def _sign_powershell_file(self, path):
        thumbprint = self.signing_cert_thumbprint.get().replace(" ", "")
        if not self.sign_powershell_bootstrap.get() or not thumbprint:
            return
        ps = (
            "$cert = Get-ChildItem Cert:\\CurrentUser\\My\\{} -ErrorAction Stop; "
            "Set-AuthenticodeSignature -FilePath '{}' -Certificate $cert -TimestampServer 'http://timestamp.digicert.com' | Out-String"
        ).format(thumbprint, path.replace("'", "''"))
        subprocess.run(
            ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps],
            check=True,
            capture_output=True,
            text=True,
        )

    @staticmethod
    def _sha256_file(path):
        digest = hashlib.sha256()
        with open(path, 'rb') as f:
            for chunk in iter(lambda: f.read(1024 * 1024), b''):
                digest.update(chunk)
        return digest.hexdigest()

    def _write_checksum_bundle(self, directory, exported_paths):
        checksum_path = os.path.join(directory, "SHA256SUMS.txt")
        with open(checksum_path, 'w', encoding='utf-8') as f:
            for path in exported_paths:
                f.write(f"{self._sha256_file(path)}  {os.path.basename(path)}\n")
        bundle_path = os.path.join(directory, f"bypassnroGen-v{APP_VERSION}-bundle.zip")
        with zipfile.ZipFile(bundle_path, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
            for path in exported_paths + [checksum_path]:
                zf.write(path, arcname=os.path.basename(path))
        return checksum_path, bundle_path

    def _get_profile_dict(self):
        """Serialize all current settings into a JSON-serializable dict."""
        profile = {}
        # Collect all BooleanVar / StringVar attributes
        bool_keys = [
            'skip_eula', 'skip_machine_oobe', 'skip_user_oobe',
            'hide_online_account', 'hide_local_account', 'auto_logon',
            'msa_localonly_bypass', 'audit_mode', 'enable_disk_partitioning',
            'obscure_passwords', 'disable_telemetry', 'disable_cortana',
            'disable_consumer_features', 'disable_wifi_sense',
            'disable_activity_history', 'disable_location',
            'disable_advertising_id', 'bypass_requirements', 'bypass_nro',
            'enable_long_paths', 'enable_rdp', 'allow_powershell_scripts',
            'disable_uac_prompt', 'disable_defender',
            'prevent_device_encryption', 'disable_vbs',
            'disable_auto_restart', 'disable_system_sounds',
            'disable_hibernation', 'disable_fast_boot',
            'remove_onedrive', 'cleanup_panther_password',
            'hide_edge_fre', 'disable_edge_startup',
            'delete_edge_shortcut', 'make_edge_uninstallable',
            'show_file_extensions', 'show_hidden_files',
            'show_system_files', 'classic_context_menu',
            'launch_to_this_pc', 'enable_dark_mode',
            'hide_task_view', 'disable_widgets', 'hide_copilot',
            'small_taskbar', 'output_autounattend',
            'output_powershell_bootstrap', 'output_iso_helper',
            'output_usb_helper', 'output_startnet',
            'output_registry_reference', 'output_validation_report',
            'output_zip_bundle', 'sign_powershell_bootstrap',
        ]
        str_keys = [
            'github_user', 'github_repo', 'github_branch',
            'region_preset', 'target_architecture',
            'ui_language', 'locale', 'keyboard', 'timezone',
            'edition_mode', 'windows_edition', 'product_key',
            'account_name', 'account_display', 'account_password',
            'account_group', 'protect_your_pc', 'taskbar_search',
            'computer_name', 'power_plan',
            'completion_webhook_url', 'completion_webhook_type',
            'signing_cert_thumbprint',
        ]
        for key in bool_keys:
            profile[key] = getattr(self, key).get()
        for key in str_keys:
            profile[key] = getattr(self, key).get()
        # Bloatware
        profile['bloatware'] = {app_id: var.get() for app_id, var in self.bloatware_apps.items()}
        profile['bloatware_modes'] = {app_id: var.get() for app_id, var in self.bloatware_app_modes.items()}
        profile['additional_accounts'] = self._get_text_widget_value('additional_accounts_text')
        # Custom scripts (from text widgets)
        try:
            profile['system_script'] = self.system_script_text.get('1.0', 'end').rstrip('\n')
        except Exception:
            profile['system_script'] = ''
        try:
            profile['firstlogon_script'] = self.firstlogon_script_text.get('1.0', 'end').rstrip('\n')
        except Exception:
            profile['firstlogon_script'] = ''
        return profile

    def _load_profile_dict(self, profile):
        """Apply a profile dict to the current settings."""
        for key, value in profile.items():
            if key == 'bloatware':
                for app_id, checked in value.items():
                    if app_id in self.bloatware_apps:
                        self.bloatware_apps[app_id].set(checked)
            elif key == 'bloatware_modes':
                for app_id, mode in value.items():
                    if app_id in self.bloatware_app_modes and mode in self.BLOATWARE_REMOVAL_MODES:
                        self.bloatware_app_modes[app_id].set(mode)
            elif key == 'additional_accounts':
                try:
                    self.additional_accounts_text.delete('1.0', 'end')
                    self.additional_accounts_text.insert('1.0', value)
                except Exception:
                    pass
            elif key == 'system_script':
                try:
                    self.system_script_text.delete('1.0', 'end')
                    self.system_script_text.insert('1.0', value)
                except Exception:
                    pass
            elif key == 'firstlogon_script':
                try:
                    self.firstlogon_script_text.delete('1.0', 'end')
                    self.firstlogon_script_text.insert('1.0', value)
                except Exception:
                    pass
            else:
                attr = getattr(self, key, None)
                if attr is not None and hasattr(attr, 'set'):
                    attr.set(value)

    def save_profile(self):
        """Save current settings to a JSON profile file."""
        path = filedialog.asksaveasfilename(
            title="Save Profile",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if not path:
            return
        try:
            profile = self._get_profile_dict()
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(profile, f, indent=2)
            messagebox.showinfo("Profile Saved", f"Profile saved to:\n{path}")
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save profile:\n{str(e)}")

    def load_profile(self):
        """Load settings from a JSON profile file."""
        path = filedialog.askopenfilename(
            title="Load Profile",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if not path:
            return
        try:
            with open(path, 'r', encoding='utf-8') as f:
                profile = json.load(f)
            self._load_profile_dict(profile)
            messagebox.showinfo("Profile Loaded", f"Profile loaded from:\n{path}")
        except Exception as e:
            messagebox.showerror("Load Error", f"Failed to load profile:\n{str(e)}")

    def _flatten_profile(self, data, prefix=""):
        flat = {}
        for key, value in data.items():
            full_key = f"{prefix}.{key}" if prefix else key
            if isinstance(value, dict):
                flat.update(self._flatten_profile(value, full_key))
            else:
                flat[full_key] = value
        return flat

    def diff_profile(self):
        """Show a diff between current settings and a saved JSON profile."""
        path = filedialog.askopenfilename(
            title="Diff Against Profile",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if not path:
            return
        try:
            with open(path, 'r', encoding='utf-8') as f:
                saved = json.load(f)
            current = self._flatten_profile(self._get_profile_dict())
            other = self._flatten_profile(saved)
            keys = sorted(set(current) | set(other))
            changes = []
            for key in keys:
                left = other.get(key, "<missing>")
                right = current.get(key, "<missing>")
                if left != right:
                    changes.append(f"{key}\n  saved:  {left}\n  current: {right}")
            text = "\n\n".join(changes) if changes else "No differences."

            dialog = tk.Toplevel(self.root)
            dialog.title("Profile Diff")
            dialog.geometry("900x600")
            dialog.configure(bg=self.colors['bg_dark'])
            diff_text = tk.Text(dialog, bg='#1e1e1e', fg='#ffffff', insertbackground='#ffffff', font=('Consolas', 10), wrap='none')
            diff_text.pack(fill='both', expand=True, padx=10, pady=10)
            diff_text.insert('1.0', text)
            diff_text.configure(state='disabled')
        except Exception as e:
            messagebox.showerror("Diff Error", f"Failed to diff profile:\n{str(e)}")

    def update_preview(self):
        """Update the preview texts"""
        self.bypass_preview.delete('1.0', 'end')
        self.bypass_preview.insert('1.0', self.generate_bypass_cmd())
        
        self.unattend_preview.delete('1.0', 'end')
        self.unattend_preview.insert('1.0', self.generate_unattend_xml())
        
    def preview_files(self):
        """Show preview tab with updated content"""
        self.update_preview()
        self.notebook.select(8)  # Select preview tab
        
    def export_files(self):
        """Export bypass.cmd and unattend.xml files"""
        errors = self.validate_configuration()
        if not errors:
            errors.extend(self.validate_generated_xml())
        if errors:
            messagebox.showerror("Validation Error", "\n".join(errors))
            return

        # Ask for directory
        directory = filedialog.askdirectory(title="Select Export Directory")
        if not directory:
            return

        try:
            files = [
                ("bypass.cmd", self.generate_bypass_cmd()),
                ("unattend.xml", self.generate_unattend_xml()),
            ]

            if self.output_autounattend.get():
                files.append(("autounattend.xml", self.generate_autounattend_xml()))
            if self.output_powershell_bootstrap.get():
                files.append(("bypass-bootstrap.ps1", self.generate_powershell_bootstrap()))
            if self.output_iso_helper.get():
                if not self.output_autounattend.get():
                    files.append(("autounattend.xml", self.generate_autounattend_xml()))
                files.append(("inject-iso.ps1", self.generate_iso_helper_ps1()))
            if self.output_usb_helper.get():
                if not self.output_autounattend.get() and not any(name == "autounattend.xml" for name, _ in files):
                    files.append(("autounattend.xml", self.generate_autounattend_xml()))
                files.append(("stage-usb.ps1", self.generate_usb_helper_ps1()))
            if self.output_startnet.get():
                files.append(("startnet.cmd", self.generate_startnet_cmd()))
            if self.output_registry_reference.get():
                files.append(("registry-reference.html", self.generate_registry_reference_html()))
            if self.output_validation_report.get():
                files.append(("validation-report.txt", self.generate_validation_report()))

            exported_paths = []
            exported = []
            seen = set()
            for filename, content in files:
                if filename in seen:
                    continue
                seen.add(filename)
                path = os.path.join(directory, filename)
                with open(path, 'w', encoding='utf-8', newline='') as f:
                    f.write(content)
                exported_paths.append(path)
                exported.append(f"{filename}: {path}")

            bootstrap_path = os.path.join(directory, "bypass-bootstrap.ps1")
            if self.output_powershell_bootstrap.get() and os.path.exists(bootstrap_path):
                self._sign_powershell_file(bootstrap_path)

            if self.output_zip_bundle.get():
                checksum_path, bundle_path = self._write_checksum_bundle(directory, exported_paths)
                exported.append(f"SHA256SUMS.txt: {checksum_path}")
                exported.append(f"{os.path.basename(bundle_path)}: {bundle_path}")

            files_list = "\n".join(exported)
            messagebox.showinfo("Export Complete",
                f"Files exported successfully!\n\n"
                f"{files_list}\n\n"
                f"Upload these files to your GitHub repository.")
                
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export files:\n{str(e)}")
            
    def load_preset(self):
        """Load a preset configuration"""
        presets = {
            "Minimal (Skip OOBE Only)": self.preset_minimal,
            "Standard (Recommended)": self.preset_standard,
            "Privacy Focused": self.preset_privacy,
            "Power User": self.preset_power_user,
            "Clean Install (Remove All Bloat)": self.preset_clean,
        }
        
        # Create preset selection dialog
        dialog = tk.Toplevel(self.root)
        dialog.title("Load Preset")
        dialog.geometry("400x300")
        dialog.configure(bg=self.colors['bg_dark'])
        dialog.transient(self.root)
        dialog.grab_set()
        
        ttk.Label(dialog, text="Select a preset configuration:", style='Header.TLabel').pack(pady=20)
        
        preset_var = tk.StringVar(value="Standard (Recommended)")
        
        for name in presets.keys():
            ttk.Radiobutton(dialog, text=name, variable=preset_var, value=name).pack(anchor='w', padx=30, pady=5)
            
        def apply_preset():
            presets[preset_var.get()]()
            dialog.destroy()
            messagebox.showinfo("Preset Loaded", f"'{preset_var.get()}' preset has been applied.")
            
        ttk.Button(dialog, text="Apply Preset", style='Accent.TButton', command=apply_preset).pack(pady=20)
        
    def preset_minimal(self):
        """Minimal preset - just bypass OOBE"""
        self.bypass_nro.set(True)
        self.bypass_requirements.set(True)
        self.skip_eula.set(True)
        self.hide_online_account.set(True)
        self.hide_local_account.set(True)
        for var in self.bloatware_apps.values():
            var.set(False)
            
    def preset_standard(self):
        """Standard recommended preset"""
        self.bypass_nro.set(True)
        self.bypass_requirements.set(True)
        self.skip_eula.set(True)
        self.hide_online_account.set(True)
        self.hide_local_account.set(True)
        self.protect_your_pc.set("3")
        self.disable_telemetry.set(True)
        self.disable_consumer_features.set(True)
        self.enable_long_paths.set(True)
        self.allow_powershell_scripts.set(True)
        self.show_file_extensions.set(True)
        self.classic_context_menu.set(True)
        self.taskbar_search.set("Hide")
        self.hide_task_view.set(True)
        self.disable_widgets.set(True)
        self.hide_copilot.set(True)
        
    def preset_privacy(self):
        """Privacy-focused preset"""
        self.preset_standard()
        self.disable_telemetry.set(True)
        self.disable_cortana.set(True)
        self.disable_consumer_features.set(True)
        self.disable_wifi_sense.set(True)
        self.disable_activity_history.set(True)
        self.disable_location.set(True)
        self.disable_advertising_id.set(True)
        
    def preset_power_user(self):
        """Power user preset"""
        self.preset_standard()
        self.enable_rdp.set(True)
        self.show_hidden_files.set(True)
        self.launch_to_this_pc.set(True)
        self.disable_hibernation.set(True)
        
    def preset_clean(self):
        """Clean install - remove all bloatware"""
        self.preset_privacy()
        for var in self.bloatware_apps.values():
            var.set(True)
        self.remove_onedrive.set(True)
        self.enable_dark_mode.set(True)


def main():
    root = tk.Tk()
    app = BypassNROGenerator(root)
    root.mainloop()


if __name__ == "__main__":
    main()
