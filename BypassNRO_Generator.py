#!/usr/bin/env python3
"""
Bypass NRO Generator - Windows 11 OOBE Bypass Tool
A professional GUI for generating bypass.cmd and unattend.xml files
Author: Generated for Matt's SysAdminDoc projects
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import base64
from datetime import datetime

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
    def __init__(self, root):
        self.root = root
        self.root.title("Bypass NRO Generator - Windows 11 OOBE Bypass Tool")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 700)
        
        # Apply dark theme
        self.setup_styles()
        
        # Variables for all options
        self.setup_variables()
        
        # Create main interface
        self.create_interface()
        
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
        self.ui_language = tk.StringVar(value="en-US")
        self.locale = tk.StringVar(value="en-US")
        self.keyboard = tk.StringVar(value="0409:00000409")
        self.timezone = tk.StringVar(value="Eastern Standard Time")
        
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
        
        # Custom scripts
        self.system_script = tk.StringVar(value="")
        self.firstlogon_script = tk.StringVar(value="")
        
    def create_interface(self):
        """Create the main interface"""
        # Main container
        main_frame = ttk.Frame(self.root, style='TFrame')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Header
        header_frame = ttk.Frame(main_frame, style='TFrame')
        header_frame.pack(fill='x', pady=(0, 20))
        
        ttk.Label(header_frame, text="Bypass NRO Generator", style='Title.TLabel').pack(side='left')
        ttk.Label(header_frame, text="Windows 11 OOBE Bypass Tool", style='Dim.TLabel').pack(side='left', padx=(15, 0), pady=(10, 0))
        
        # Action buttons at top
        btn_frame = ttk.Frame(header_frame, style='TFrame')
        btn_frame.pack(side='right')
        
        ttk.Button(btn_frame, text="Export Files", style='Accent.TButton', command=self.export_files).pack(side='right', padx=5)
        ttk.Button(btn_frame, text="Preview", style='TButton', command=self.preview_files).pack(side='right', padx=5)
        ttk.Button(btn_frame, text="Load Preset", style='TButton', command=self.load_preset).pack(side='right', padx=5)
        
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
        
        languages = [
            ("English (US)", "en-US"),
            ("English (UK)", "en-GB"),
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
            ("German", "0407:00000407"),
            ("French", "040c:0000040c"),
            ("Spanish", "0c0a:0000040a"),
            ("Italian", "0410:00000410"),
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
        
        # Security (with warnings)
        sec_group = ttk.LabelFrame(frame, text="Security Settings (Use with caution)", padding=15)
        sec_group.pack(fill='x', padx=10, pady=10)
        
        ttk.Checkbutton(sec_group, text="Prevent Device Encryption (BitLocker)", variable=self.prevent_device_encryption).pack(anchor='w', pady=2)
        ttk.Checkbutton(sec_group, text="Disable Core Isolation / VBS (improves VM performance)", variable=self.disable_vbs).pack(anchor='w', pady=2)
        ttk.Checkbutton(sec_group, text="Disable UAC prompts (not recommended)", variable=self.disable_uac_prompt).pack(anchor='w', pady=2)
        ttk.Checkbutton(sec_group, text="Disable Windows Defender (not recommended)", variable=self.disable_defender).pack(anchor='w', pady=2)
        
        # Edge settings
        edge_group = ttk.LabelFrame(frame, text="Microsoft Edge", padding=15)
        edge_group.pack(fill='x', padx=10, pady=10)
        
        ttk.Checkbutton(edge_group, text="Hide Edge First Run Experience dialogs", variable=self.hide_edge_fre).pack(anchor='w', pady=2)
        ttk.Checkbutton(edge_group, text="Disable Edge Startup Boost and Background mode", variable=self.disable_edge_startup).pack(anchor='w', pady=2)
        ttk.Checkbutton(edge_group, text="Delete Edge desktop shortcut", variable=self.delete_edge_shortcut).pack(anchor='w', pady=2)
        ttk.Checkbutton(edge_group, text="Make Edge uninstallable (may cause update issues)", variable=self.make_edge_uninstallable).pack(anchor='w', pady=2)
        
        # Explorer
        explorer_group = ttk.LabelFrame(frame, text="File Explorer", padding=15)
        explorer_group.pack(fill='x', padx=10, pady=10)
        
        ttk.Checkbutton(explorer_group, text="Always show file extensions", variable=self.show_file_extensions).pack(anchor='w', pady=2)
        ttk.Checkbutton(explorer_group, text="Show hidden files", variable=self.show_hidden_files).pack(anchor='w', pady=2)
        ttk.Checkbutton(explorer_group, text="Show protected operating system files", variable=self.show_system_files).pack(anchor='w', pady=2)
        ttk.Checkbutton(explorer_group, text="Use classic context menu (right-click)", variable=self.classic_context_menu).pack(anchor='w', pady=2)
        ttk.Checkbutton(explorer_group, text="Open File Explorer to 'This PC'", variable=self.launch_to_this_pc).pack(anchor='w', pady=2)
        
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
        ttk.Button(btn_frame, text="Select All", command=lambda: self.set_all_bloatware(True)).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Deselect All", command=lambda: self.set_all_bloatware(False)).pack(side='left', padx=5)
        
        # App list in columns
        group = ttk.LabelFrame(frame, text="Windows Apps", padding=15)
        group.pack(fill='x', padx=10, pady=10)
        
        app_names = {
            'Microsoft.549981C3F5F10': 'Cortana',
            'Microsoft.BingNews': 'News',
            'Microsoft.BingWeather': 'Weather',
            'Microsoft.GetHelp': 'Get Help',
            'Microsoft.Getstarted': 'Tips',
            'Microsoft.MicrosoftOfficeHub': 'Office Hub',
            'Microsoft.MicrosoftSolitaireCollection': 'Solitaire',
            'Microsoft.MicrosoftStickyNotes': 'Sticky Notes',
            'Microsoft.OutlookForWindows': 'Outlook',
            'Microsoft.People': 'People',
            'Microsoft.PowerAutomateDesktop': 'Power Automate',
            'Microsoft.Todos': 'To Do',
            'Microsoft.WindowsAlarms': 'Alarms & Clock',
            'Microsoft.WindowsCamera': 'Camera',
            'Microsoft.WindowsFeedbackHub': 'Feedback Hub',
            'Microsoft.WindowsMaps': 'Maps',
            'Microsoft.WindowsSoundRecorder': 'Voice Recorder',
            'Microsoft.Xbox.TCUI': 'Xbox TCUI',
            'Microsoft.XboxGameOverlay': 'Xbox Game Overlay',
            'Microsoft.XboxGamingOverlay': 'Xbox Gaming Overlay',
            'Microsoft.XboxIdentityProvider': 'Xbox Identity',
            'Microsoft.XboxSpeechToTextOverlay': 'Xbox Speech',
            'Microsoft.YourPhone': 'Phone Link',
            'Microsoft.ZuneMusic': 'Media Player',
            'Microsoft.ZuneVideo': 'Movies & TV',
            'Clipchamp.Clipchamp': 'Clipchamp',
            'MicrosoftTeams': 'Teams',
            'Microsoft.SkypeApp': 'Skype',
        }
        
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
            display_name = app_names.get(app_id, app_id.split('.')[-1])
            ttk.Checkbutton(col_frames[col_idx], text=display_name, variable=var).pack(anchor='w', pady=1)
            
    def set_all_bloatware(self, value):
        """Set all bloatware checkboxes"""
        for var in self.bloatware_apps.values():
            var.set(value)
            
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
        account_name = self.account_name.get() or "Admin"
        display_name = self.account_display.get() or account_name
        password = self.account_password.get()
        
        # Encode password if needed
        if password and self.obscure_passwords.get():
            password_encoded = base64.b64encode((password + "Password").encode('utf-16-le')).decode()
            password_plain = "false"
        else:
            password_encoded = password
            password_plain = "true"
            
        # Build bloatware removal list
        apps_to_remove = [app_id for app_id, var in self.bloatware_apps.items() if var.get()]
        
        xml = '''<?xml version="1.0" encoding="utf-8"?>
<!--
  Bypass NRO Generator - Windows 11 Unattended Installation
  Generated: {date}
-->
<unattend xmlns="urn:schemas-microsoft-com:unattend">
'''.format(date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

        # Windows PE pass - for system requirements bypass
        if self.bypass_requirements.get():
            xml += '''  <settings pass="windowsPE">
    <component name="Microsoft-Windows-Setup" processorArchitecture="amd64" publicKeyToken="31bf3856ad364e35" language="neutral" versionScope="nonSxS">
      <RunSynchronous>
        <RunSynchronousCommand wcm:action="add">
          <Order>1</Order>
          <Path>reg add "HKLM\\SYSTEM\\Setup\\LabConfig" /v BypassTPMCheck /t REG_DWORD /d 1 /f</Path>
        </RunSynchronousCommand>
        <RunSynchronousCommand wcm:action="add">
          <Order>2</Order>
          <Path>reg add "HKLM\\SYSTEM\\Setup\\LabConfig" /v BypassRAMCheck /t REG_DWORD /d 1 /f</Path>
        </RunSynchronousCommand>
        <RunSynchronousCommand wcm:action="add">
          <Order>3</Order>
          <Path>reg add "HKLM\\SYSTEM\\Setup\\LabConfig" /v BypassSecureBootCheck /t REG_DWORD /d 1 /f</Path>
        </RunSynchronousCommand>
        <RunSynchronousCommand wcm:action="add">
          <Order>4</Order>
          <Path>reg add "HKLM\\SYSTEM\\Setup\\LabConfig" /v BypassStorageCheck /t REG_DWORD /d 1 /f</Path>
        </RunSynchronousCommand>
        <RunSynchronousCommand wcm:action="add">
          <Order>5</Order>
          <Path>reg add "HKLM\\SYSTEM\\Setup\\LabConfig" /v BypassCPUCheck /t REG_DWORD /d 1 /f</Path>
        </RunSynchronousCommand>
      </RunSynchronous>
    </component>
  </settings>

'''

        # Specialize pass
        xml += '''  <settings pass="specialize">
    <component name="Microsoft-Windows-Deployment" processorArchitecture="amd64" publicKeyToken="31bf3856ad364e35" language="neutral" versionScope="nonSxS" xmlns:wcm="http://schemas.microsoft.com/WMIConfig/2002/State">
      <RunSynchronous>
'''
        
        order = 1
        
        # BypassNRO
        if self.bypass_nro.get():
            xml += '''        <RunSynchronousCommand wcm:action="add">
          <Order>{order}</Order>
          <Path>reg add "HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\OOBE" /v BypassNRO /t REG_DWORD /d 1 /f</Path>
        </RunSynchronousCommand>
'''.format(order=order)
            order += 1
            
        # Long paths
        if self.enable_long_paths.get():
            xml += '''        <RunSynchronousCommand wcm:action="add">
          <Order>{order}</Order>
          <Path>reg add "HKLM\\SYSTEM\\CurrentControlSet\\Control\\FileSystem" /v LongPathsEnabled /t REG_DWORD /d 1 /f</Path>
        </RunSynchronousCommand>
'''.format(order=order)
            order += 1
            
        # RDP
        if self.enable_rdp.get():
            xml += '''        <RunSynchronousCommand wcm:action="add">
          <Order>{order}</Order>
          <Path>reg add "HKLM\\SYSTEM\\CurrentControlSet\\Control\\Terminal Server" /v fDenyTSConnections /t REG_DWORD /d 0 /f</Path>
        </RunSynchronousCommand>
        <RunSynchronousCommand wcm:action="add">
          <Order>{order2}</Order>
          <Path>netsh advfirewall firewall set rule group="remote desktop" new enable=Yes</Path>
        </RunSynchronousCommand>
'''.format(order=order, order2=order+1)
            order += 2
            
        # PowerShell execution policy
        if self.allow_powershell_scripts.get():
            xml += '''        <RunSynchronousCommand wcm:action="add">
          <Order>{order}</Order>
          <Path>powershell.exe -Command "Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Force"</Path>
        </RunSynchronousCommand>
'''.format(order=order)
            order += 1
            
        # Disable hibernation
        if self.disable_hibernation.get():
            xml += '''        <RunSynchronousCommand wcm:action="add">
          <Order>{order}</Order>
          <Path>powercfg.exe /HIBERNATE OFF</Path>
        </RunSynchronousCommand>
'''.format(order=order)
            order += 1
            
        # Prevent device encryption
        if self.prevent_device_encryption.get():
            xml += '''        <RunSynchronousCommand wcm:action="add">
          <Order>{order}</Order>
          <Path>reg add "HKLM\\SYSTEM\\CurrentControlSet\\Control\\BitLocker" /v PreventDeviceEncryption /t REG_DWORD /d 1 /f</Path>
        </RunSynchronousCommand>
'''.format(order=order)
            order += 1
            
        # Disable VBS
        if self.disable_vbs.get():
            xml += '''        <RunSynchronousCommand wcm:action="add">
          <Order>{order}</Order>
          <Path>reg add "HKLM\\SYSTEM\\CurrentControlSet\\Control\\DeviceGuard" /v EnableVirtualizationBasedSecurity /t REG_DWORD /d 0 /f</Path>
        </RunSynchronousCommand>
'''.format(order=order)
            order += 1
            
        xml += '''      </RunSynchronous>
    </component>
    <component name="Microsoft-Windows-Shell-Setup" processorArchitecture="amd64" publicKeyToken="31bf3856ad364e35" language="neutral" versionScope="nonSxS">
      <ComputerName>*</ComputerName>
      <TimeZone>{timezone}</TimeZone>
    </component>
  </settings>

'''.format(timezone=self.timezone.get())

        # OOBE System pass
        xml += '''  <settings pass="oobeSystem">
    <component name="Microsoft-Windows-International-Core" processorArchitecture="amd64" publicKeyToken="31bf3856ad364e35" language="neutral" versionScope="nonSxS">
      <InputLocale>{keyboard}</InputLocale>
      <SystemLocale>{locale}</SystemLocale>
      <UILanguage>{ui_lang}</UILanguage>
      <UserLocale>{locale}</UserLocale>
    </component>
    <component name="Microsoft-Windows-Shell-Setup" processorArchitecture="amd64" publicKeyToken="31bf3856ad364e35" language="neutral" versionScope="nonSxS" xmlns:wcm="http://schemas.microsoft.com/WMIConfig/2002/State">
      <OOBE>
        <HideEULAPage>{skip_eula}</HideEULAPage>
        <HideOnlineAccountScreens>{hide_online}</HideOnlineAccountScreens>
        <HideLocalAccountScreen>{hide_local}</HideLocalAccountScreen>
        <HideWirelessSetupInOOBE>true</HideWirelessSetupInOOBE>
        <ProtectYourPC>{protect_pc}</ProtectYourPC>
      </OOBE>
      <UserAccounts>
        <LocalAccounts>
          <LocalAccount wcm:action="add">
            <Name>{account_name}</Name>
            <DisplayName>{display_name}</DisplayName>
            <Group>{group}</Group>
            <Password>
              <Value>{password}</Value>
              <PlainText>{password_plain}</PlainText>
            </Password>
          </LocalAccount>
        </LocalAccounts>
      </UserAccounts>
'''.format(
            keyboard=self.keyboard.get(),
            locale=self.locale.get(),
            ui_lang=self.ui_language.get(),
            skip_eula="true" if self.skip_eula.get() else "false",
            hide_online="true" if self.hide_online_account.get() else "false",
            hide_local="true" if self.hide_local_account.get() else "false",
            protect_pc=self.protect_your_pc.get(),
            account_name=account_name,
            display_name=display_name,
            group=self.account_group.get(),
            password=password_encoded if password else "",
            password_plain=password_plain
        )

        # Auto logon
        if self.auto_logon.get():
            xml += '''      <AutoLogon>
        <Username>{account_name}</Username>
        <Enabled>true</Enabled>
        <LogonCount>1</LogonCount>
        <Password>
          <Value>{password}</Value>
          <PlainText>{password_plain}</PlainText>
        </Password>
      </AutoLogon>
'''.format(
                account_name=account_name,
                password=password_encoded if password else "",
                password_plain=password_plain
            )

        # First logon commands
        xml += '''      <FirstLogonCommands>
'''
        cmd_order = 1
        
        # Bloatware removal
        if apps_to_remove:
            apps_str = "', '".join(apps_to_remove)
            xml += '''        <SynchronousCommand wcm:action="add">
          <Order>{order}</Order>
          <CommandLine>powershell.exe -NoProfile -Command "$apps = @('{apps}'); foreach ($app in $apps) {{ Get-AppxPackage -Name $app -AllUsers | Remove-AppxPackage -AllUsers -ErrorAction SilentlyContinue; Get-AppxProvisionedPackage -Online | Where-Object {{ $_.PackageName -like \\"*$app*\\" }} | Remove-AppxProvisionedPackage -Online -ErrorAction SilentlyContinue }}"</CommandLine>
          <Description>Remove bloatware apps</Description>
        </SynchronousCommand>
'''.format(order=cmd_order, apps=apps_str)
            cmd_order += 1
            
        # Explorer tweaks
        if self.show_file_extensions.get():
            xml += '''        <SynchronousCommand wcm:action="add">
          <Order>{order}</Order>
          <CommandLine>reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced" /v HideFileExt /t REG_DWORD /d 0 /f</CommandLine>
          <Description>Show file extensions</Description>
        </SynchronousCommand>
'''.format(order=cmd_order)
            cmd_order += 1
            
        if self.show_hidden_files.get():
            xml += '''        <SynchronousCommand wcm:action="add">
          <Order>{order}</Order>
          <CommandLine>reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced" /v Hidden /t REG_DWORD /d 1 /f</CommandLine>
          <Description>Show hidden files</Description>
        </SynchronousCommand>
'''.format(order=cmd_order)
            cmd_order += 1
            
        if self.classic_context_menu.get():
            xml += '''        <SynchronousCommand wcm:action="add">
          <Order>{order}</Order>
          <CommandLine>reg add "HKCU\\Software\\Classes\\CLSID\\{{86ca1aa0-34aa-4e8b-a509-50c905bae2a2}}\\InprocServer32" /ve /f</CommandLine>
          <Description>Enable classic context menu</Description>
        </SynchronousCommand>
'''.format(order=cmd_order)
            cmd_order += 1
            
        if self.launch_to_this_pc.get():
            xml += '''        <SynchronousCommand wcm:action="add">
          <Order>{order}</Order>
          <CommandLine>reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced" /v LaunchTo /t REG_DWORD /d 1 /f</CommandLine>
          <Description>Open Explorer to This PC</Description>
        </SynchronousCommand>
'''.format(order=cmd_order)
            cmd_order += 1
            
        # Taskbar settings
        if self.taskbar_search.get() == "Hide":
            xml += '''        <SynchronousCommand wcm:action="add">
          <Order>{order}</Order>
          <CommandLine>reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Search" /v SearchboxTaskbarMode /t REG_DWORD /d 0 /f</CommandLine>
          <Description>Hide search box</Description>
        </SynchronousCommand>
'''.format(order=cmd_order)
            cmd_order += 1
        elif self.taskbar_search.get() == "Icon":
            xml += '''        <SynchronousCommand wcm:action="add">
          <Order>{order}</Order>
          <CommandLine>reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Search" /v SearchboxTaskbarMode /t REG_DWORD /d 1 /f</CommandLine>
          <Description>Show search icon</Description>
        </SynchronousCommand>
'''.format(order=cmd_order)
            cmd_order += 1
            
        if self.hide_task_view.get():
            xml += '''        <SynchronousCommand wcm:action="add">
          <Order>{order}</Order>
          <CommandLine>reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced" /v ShowTaskViewButton /t REG_DWORD /d 0 /f</CommandLine>
          <Description>Hide Task View button</Description>
        </SynchronousCommand>
'''.format(order=cmd_order)
            cmd_order += 1
            
        if self.disable_widgets.get():
            xml += '''        <SynchronousCommand wcm:action="add">
          <Order>{order}</Order>
          <CommandLine>reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced" /v TaskbarDa /t REG_DWORD /d 0 /f</CommandLine>
          <Description>Disable widgets</Description>
        </SynchronousCommand>
'''.format(order=cmd_order)
            cmd_order += 1
            
        if self.hide_copilot.get():
            xml += '''        <SynchronousCommand wcm:action="add">
          <Order>{order}</Order>
          <CommandLine>reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced" /v ShowCopilotButton /t REG_DWORD /d 0 /f</CommandLine>
          <Description>Hide Copilot button</Description>
        </SynchronousCommand>
'''.format(order=cmd_order)
            cmd_order += 1
            
        # Edge settings
        if self.hide_edge_fre.get():
            xml += '''        <SynchronousCommand wcm:action="add">
          <Order>{order}</Order>
          <CommandLine>reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Edge" /v HideFirstRunExperience /t REG_DWORD /d 1 /f</CommandLine>
          <Description>Hide Edge First Run Experience</Description>
        </SynchronousCommand>
'''.format(order=cmd_order)
            cmd_order += 1
            
        if self.disable_edge_startup.get():
            xml += '''        <SynchronousCommand wcm:action="add">
          <Order>{order}</Order>
          <CommandLine>reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Edge" /v StartupBoostEnabled /t REG_DWORD /d 0 /f</CommandLine>
          <Description>Disable Edge Startup Boost</Description>
        </SynchronousCommand>
'''.format(order=cmd_order)
            cmd_order += 1
            
        if self.delete_edge_shortcut.get():
            xml += '''        <SynchronousCommand wcm:action="add">
          <Order>{order}</Order>
          <CommandLine>cmd /c del /q "%PUBLIC%\\Desktop\\Microsoft Edge.lnk" 2>nul</CommandLine>
          <Description>Delete Edge desktop shortcut</Description>
        </SynchronousCommand>
'''.format(order=cmd_order)
            cmd_order += 1
            
        # Privacy settings
        if self.disable_telemetry.get():
            xml += '''        <SynchronousCommand wcm:action="add">
          <Order>{order}</Order>
          <CommandLine>reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\DataCollection" /v AllowTelemetry /t REG_DWORD /d 0 /f</CommandLine>
          <Description>Disable telemetry</Description>
        </SynchronousCommand>
'''.format(order=cmd_order)
            cmd_order += 1
            
        if self.disable_advertising_id.get():
            xml += '''        <SynchronousCommand wcm:action="add">
          <Order>{order}</Order>
          <CommandLine>reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\AdvertisingInfo" /v Enabled /t REG_DWORD /d 0 /f</CommandLine>
          <Description>Disable advertising ID</Description>
        </SynchronousCommand>
'''.format(order=cmd_order)
            cmd_order += 1

        xml += '''      </FirstLogonCommands>
    </component>
  </settings>
</unattend>
'''
        
        return xml
        
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
        # Ask for directory
        directory = filedialog.askdirectory(title="Select Export Directory")
        if not directory:
            return
            
        try:
            # Export bypass.cmd
            bypass_path = os.path.join(directory, "bypass.cmd")
            with open(bypass_path, 'w', encoding='utf-8') as f:
                f.write(self.generate_bypass_cmd())
                
            # Export unattend.xml
            unattend_path = os.path.join(directory, "unattend.xml")
            with open(unattend_path, 'w', encoding='utf-8') as f:
                f.write(self.generate_unattend_xml())
                
            messagebox.showinfo("Export Complete", 
                f"Files exported successfully!\n\n"
                f"bypass.cmd: {bypass_path}\n"
                f"unattend.xml: {unattend_path}\n\n"
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


def main():
    root = tk.Tk()
    app = BypassNROGenerator(root)
    root.mainloop()


if __name__ == "__main__":
    main()
