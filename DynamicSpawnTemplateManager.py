import re
import zipfile
import shutil
import os
import sys
import csv
import webbrowser
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("Warning: PIL (Pillow) not available. Buttons will use text only.")
try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

print("="*60)
print("DCS Dynamic Template & Warehouse Manager")
print("="*60)
print("Two-Step Workflow:")
print("  STEP 1: Configure DynSpawn Options & Coalition")
print("    - Select airbases")
print("    - Enable DynSpawn options")
print("    - Set coalitions")
print("    - Creates aircraft inventory for templates")
print("    - Saves as: <mission>_Step1_Options.miz")
print("")
print("  STEP 2: Link Dynamic Templates")
print("    - Load Step1 file")
print("    - Select templates to link")
print("    - Updates linkDynTempl in warehouses")
print("    - Saves as: <mission>_Final.miz")
print("="*60)
print()

class MergedDynamicTemplateManager:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("DCS Dynamic Template & Warehouse Manager")
        self.root.geometry("1800x950")
        
        # Modern dark color scheme
        self.colors = {
            'bg': '#1e1e1e',           # Dark background
            'fg': '#e0e0e0',           # Light gray text
            'primary': '#3498db',      # Blue primary
            'success': '#27ae60',      # Green success
            'danger': '#e74c3c',       # Red danger
            'warning': '#f39c12',      # Orange warning
            'card_bg': '#2d2d30',      # Dark card background
            'border': '#3e3e42',       # Dark gray border
            'accent': '#9b59b6',       # Purple accent
            'secondary_text': '#969696', # Secondary text color
            'separator': '#404040',    # Softer separator color
            'blue_readable': '#5dade2', # Lighter blue for better readability
            'red_readable': '#ec7063',  # Lighter red for better readability
            'neutral_readable': '#aaaaaa' # Lighter gray for neutral
        }
        
        # Configure root window with modern styling
        self.root.configure(bg=self.colors['bg'])
        
        # Load button images
        self.load_button_images()
        
        # Configure modern ttk styles
        self.setup_styles()
        
        # Load button images
        self.load_button_images()
        
        # Store data
        self.templates = []
        self.template_vars = {}
        self.airports = []
        self.airport_vars = {}
        self.csv_loaded = False
        self.miz_loaded = False
        
        # DynSpawn options storage (per airport)
        self.dynspawn_options = {}
        
        # Coalition selection storage (per airport)
        self.coalition_vars = {}
        
        # Track workflow step: 'options' or 'templates'
        self.current_step = 'options'
        
        # Create GUI elements
        self.create_widgets()
    
    def load_button_images(self):
        """Load and resize images for buttons"""
        self.github_image = None
        self.discord_image = None
        
        if not PIL_AVAILABLE:
            print("PIL/Pillow not available - buttons will use text only")
            return
        
        try:
            # Determine script directory (handle both script and executable)
            if getattr(sys, 'frozen', False):
                script_dir = os.path.dirname(sys.executable)
            else:
                script_dir = os.path.dirname(os.path.abspath(__file__))
            
            # Load and resize GitHub image
            github_path = os.path.join(script_dir, 'github-mark.png')
            if os.path.exists(github_path):
                github_img = Image.open(github_path)
                github_img = github_img.resize((16, 16), Image.Resampling.LANCZOS)
                self.github_image = ImageTk.PhotoImage(github_img)
                print(f"Loaded GitHub icon: {github_path}")
            else:
                print(f"GitHub icon not found: {github_path}")
            
            # Load and resize Discord image
            discord_path = os.path.join(script_dir, 'Discord-Symbol-Blurple.png')
            if os.path.exists(discord_path):
                discord_img = Image.open(discord_path)
                discord_img = discord_img.resize((16, 16), Image.Resampling.LANCZOS)
                self.discord_image = ImageTk.PhotoImage(discord_img)
                print(f"Loaded Discord icon: {discord_path}")
            else:
                print(f"Discord icon not found: {discord_path}")
                
        except Exception as e:
            print(f"Error loading button images: {e}")
            self.github_image = None
            self.discord_image = None
    
    def setup_styles(self):
        """Configure modern ttk styles"""
        style = ttk.Style()
        style.theme_use('clam')  # Use clam theme as base for customization
        
        # Configure modern button style with better contrast
        style.configure('Modern.TButton',
                       padding=10,
                       relief='flat',
                       background=self.colors['primary'],
                       foreground='white',
                       borderwidth=0,
                       focuscolor='none',
                       font=('Segoe UI', 10, 'bold'))
        style.map('Modern.TButton',
                 background=[('active', '#2980b9'), ('pressed', '#21618c'), ('disabled', '#4a4a4a')],
                 foreground=[('active', 'white'), ('pressed', 'white'), ('disabled', '#7a7a7a')])
        
        # Configure accent button (for main action) with better contrast
        style.configure('Accent.TButton',
                       padding=12,
                       relief='flat',
                       background=self.colors['success'],
                       foreground='white',
                       borderwidth=0,
                       focuscolor='none',
                       font=('Segoe UI', 11, 'bold'))
        style.map('Accent.TButton',
                 background=[('active', '#229954'), ('pressed', '#1e8449'), ('disabled', '#4a4a4a')],
                 foreground=[('active', 'white'), ('pressed', 'white'), ('disabled', '#7a7a7a')])
        
        # Configure modern label frame
        style.configure('Modern.TLabelframe',
                       background=self.colors['card_bg'],
                       borderwidth=1,
                       relief='solid')
        style.configure('Modern.TLabelframe.Label',
                       background=self.colors['card_bg'],
                       foreground=self.colors['fg'],
                       font=('Segoe UI', 10, 'bold'))
        
        # Configure TFrame to match dark background
        style.configure('TFrame',
                       background=self.colors['card_bg'])
        
        # Configure TLabel to match dark background
        style.configure('TLabel',
                       background=self.colors['card_bg'],
                       foreground=self.colors['fg'],
                       font=('Segoe UI', 9))
        
        # Configure modern checkbutton with better colors for dark theme
        style.configure('Modern.TCheckbutton',
                       background=self.colors['card_bg'],
                       foreground=self.colors['fg'],
                       font=('Segoe UI', 9),
                       bordercolor='#5a5a5c',
                       lightcolor='#4a4a4c',
                       darkcolor='#3a3a3c',
                       indicatorcolor='#3a3a3c')
        style.map('Modern.TCheckbutton',
                 background=[('active', self.colors['card_bg']), ('selected', self.colors['card_bg'])],
                 foreground=[('active', self.colors['fg']), ('selected', self.colors['fg'])],
                 indicatorcolor=[('selected', self.colors['primary']), ('active', '#5dade2')])
        
        # Configure modern combobox with dark background
        style.configure('Modern.TCombobox',
                       fieldbackground='#3a3a3c',
                       background='#4a4a4c',
                       foreground=self.colors['fg'],
                       arrowcolor='#a0a0a0',
                       borderwidth=1,
                       relief='solid',
                       insertcolor=self.colors['fg'])
        style.map('Modern.TCombobox',
                 fieldbackground=[('readonly', '#3a3a3c')],
                 background=[('readonly', '#4a4a4c'), ('active', '#5a5a5c')],
                 arrowcolor=[('disabled', '#606060')],
                 selectbackground=[('readonly', self.colors['primary'])],
                 selectforeground=[('readonly', 'white')])
        
        # Configure separator
        style.configure('Modern.TSeparator',
                       background=self.colors['border'])
        
        # Configure help buttons with softer colors and smaller size
        style.configure('Help.TButton',
                       background='#4A5568',  # Soft gray-blue
                       foreground='#E2E8F0',  # Light gray text
                       borderwidth=1,
                       focuscolor='none',
                       font=('Segoe UI', 8),  # Smaller font
                       padding=(8, 4))       # Smaller padding
        
        style.map('Help.TButton',
                 background=[('active', '#5A6B7D'),    # Slightly lighter on hover
                            ('pressed', '#3A4855')],   # Darker when pressed
                 foreground=[('active', '#F7FAFC'),    # Brighter text on hover
                            ('pressed', '#CBD5E0')])
    
    def load_button_images(self):
        """Load and resize button images"""
        self.github_image = None
        self.discord_image = None
        
        if not PIL_AVAILABLE:
            return
        
        # Get script directory for both script and executable modes
        if getattr(sys, 'frozen', False):
            # Running as compiled executable - use temporary extraction directory
            script_dir = sys._MEIPASS
        else:
            # Running as script
            script_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Try to load GitHub logo
        if getattr(sys, 'frozen', False):
            # In executable, images are in root directory
            github_paths = [os.path.join(script_dir, "github-mark.png")]
        else:
            # In script mode, try multiple paths
            github_paths = [
                os.path.join(script_dir, "github-mark", "github-mark", "github-mark.png"),
                os.path.join(script_dir, "github-mark", "github-mark.png"),
                os.path.join(script_dir, "github-mark.png")
            ]
        
        for github_path in github_paths:
            if os.path.exists(github_path):
                try:
                    github_img = Image.open(github_path)
                    # Resize to fit button (24x24 pixels)
                    github_img = github_img.resize((20, 20), Image.Resampling.LANCZOS)
                    self.github_image = ImageTk.PhotoImage(github_img)
                    print(f"DEBUG: Loaded GitHub icon from {github_path}")
                    break
                except Exception as e:
                    print(f"DEBUG: Failed to load GitHub icon from {github_path}: {e}")
        
        # Try to load Discord logo  
        if getattr(sys, 'frozen', False):
            # In executable, images are in root directory
            discord_paths = [os.path.join(script_dir, "Discord-Symbol-Blurple.png")]
        else:
            # In script mode, try multiple paths
            discord_paths = [
                os.path.join(script_dir, "Discord-Logo", "Discord-Logo", "Symbol_RGB", "Discord-Symbol-Blurple.png"),
                os.path.join(script_dir, "Discord-Logo", "Discord-Symbol-Blurple.png"),
                os.path.join(script_dir, "Discord-Symbol-Blurple.png")
            ]
        
        for discord_path in discord_paths:
            if os.path.exists(discord_path):
                try:
                    discord_img = Image.open(discord_path)
                    # Resize to fit button (24x24 pixels)
                    discord_img = discord_img.resize((20, 20), Image.Resampling.LANCZOS)
                    self.discord_image = ImageTk.PhotoImage(discord_img)
                    print(f"DEBUG: Loaded Discord icon from {discord_path}")
                    break
                except Exception as e:
                    print(f"DEBUG: Failed to load Discord icon from {discord_path}: {e}")
        
    def load_airports(self):
        """Load airports data from selected CSV file"""
        csv_path = filedialog.askopenfilename(
            title="Select Airbases CSV File",
            filetypes=[("CSV files", "*.csv")],
            initialdir=Path(__file__).parent
        )
        
        if not csv_path:
            messagebox.showwarning("Warning", "No CSV file selected!")
            return False
            
        try:
            airports = []
            with open(csv_path, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    airports.append({
                        'id': int(row['ID']),
                        'name': row['Name'],
                        'category': row['Category'],
                        'coalition': row['Coalition']
                    })
            
            self.airports = airports
            self.csv_loaded = True
            return True
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load CSV file:\n{str(e)}")
            return False

    def init_airports(self):
        """Initialize airports data from CSV"""
        if self.load_airports():
            self.miz_btn.configure(state="normal")
            self.status_label.config(text=f"Loaded {len(self.airports)} airbases. Now select .miz file.")
            messagebox.showinfo("Success", f"Loaded {len(self.airports)} airbases from CSV")
        
    def create_widgets(self):
        """Main widget creation with modern styling"""
        # Configure root window with modern background
        self.root.configure(bg=self.colors['bg'])
        
        # Top buttons frame with modern card styling
        btn_frame_container = tk.Frame(self.root, bg=self.colors['bg'])
        btn_frame_container.pack(fill=tk.X, padx=20, pady=(20, 0))
        
        btn_frame = tk.Frame(btn_frame_container, bg=self.colors['card_bg'])
        btn_frame.pack(fill=tk.X, pady=(0, 2))
        
        # Add subtle shadow/border
        border_frame = tk.Frame(btn_frame_container, bg=self.colors['separator'], height=1)
        border_frame.pack(fill=tk.X)
        
        # Inner padding frame
        inner_btn_frame = tk.Frame(btn_frame, bg=self.colors['card_bg'])
        inner_btn_frame.pack(fill=tk.X, padx=15, pady=15)
        
        # Create and store button references with modern styling
        self.csv_btn = ttk.Button(inner_btn_frame, text="📁 Load Airbases CSV", 
                                 command=self.init_airports, style='Modern.TButton')
        self.miz_btn = ttk.Button(inner_btn_frame, text="📦 Load MIZ File", 
                                 command=self.load_miz, state="disabled", style='Modern.TButton')
        
        # Step indicator label with modern styling
        self.step_label = tk.Label(inner_btn_frame, text="STEP 1: Configure DynSpawn Options & Coalition", 
                                   font=("Segoe UI", 11, "bold"), 
                                   bg=self.colors['card_bg'],
                                   fg=self.colors['primary'])
        self.step_label.pack(side=tk.LEFT, padx=20)
        
        self.apply_btn = ttk.Button(inner_btn_frame, text="✓ Apply Options & Save", 
                                   command=self.apply_step1, state="disabled",
                                   style="Accent.TButton")
        
        # Help buttons with images - softer colors and smaller size
        if self.github_image:
            self.github_btn = ttk.Button(inner_btn_frame, text=" GitHub", 
                                        image=self.github_image, compound="left",
                                        command=self.open_github, style='Help.TButton')
        else:
            self.github_btn = ttk.Button(inner_btn_frame, text="📖 GitHub", 
                                        command=self.open_github, style='Help.TButton')
        
        if self.discord_image:
            self.discord_btn = ttk.Button(inner_btn_frame, text=" Discord", 
                                         image=self.discord_image, compound="left",
                                         command=self.open_discord, style='Help.TButton')
        else:
            self.discord_btn = ttk.Button(inner_btn_frame, text="💬 Discord", 
                                         command=self.open_discord, style='Help.TButton')
        
        # Pack buttons
        self.csv_btn.pack(side=tk.LEFT, padx=(0, 8))
        self.miz_btn.pack(side=tk.LEFT, padx=(0, 8))
        self.github_btn.pack(side=tk.RIGHT, padx=(8, 4))
        self.discord_btn.pack(side=tk.RIGHT, padx=(4, 8))
        self.apply_btn.pack(side=tk.RIGHT)
        
        # Status label with modern styling
        status_container = tk.Frame(self.root, bg=self.colors['bg'])
        status_container.pack(side=tk.BOTTOM, fill=tk.X, padx=20, pady=(0, 20))
        
        top_border = tk.Frame(status_container, bg=self.colors['separator'], height=1)
        top_border.pack(fill=tk.X, pady=(0, 2))
        
        status_inner = tk.Frame(status_container, bg=self.colors['card_bg'])
        status_inner.pack(fill=tk.X)
        
        self.status_label = tk.Label(status_inner, 
                                     text="Ready. Please select airbases CSV file.", 
                                     font=("Segoe UI", 9),
                                     bg=self.colors['card_bg'],
                                     fg=self.colors['fg'],
                                     anchor=tk.W)
        self.status_label.pack(fill=tk.X, padx=15, pady=10)
        
        # Create main container with modern styling
        content_container = tk.Frame(self.root, bg=self.colors['bg'])
        content_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=(15, 0))
        
        main_container = ttk.PanedWindow(content_container, orient='horizontal')
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Left panel - Templates with modern styling
        left_card = tk.Frame(main_container, bg=self.colors['card_bg'], relief='flat')
        left_title = tk.Label(left_card, 
                             text="✈ Dynamic Templates",
                             font=("Segoe UI", 10, "bold"),
                             bg=self.colors['card_bg'],
                             fg=self.colors['fg'],
                             anchor='w')
        left_title.pack(fill=tk.X, padx=15, pady=(15, 5))
        
        left_subtitle = tk.Label(left_card, 
                                text="Select templates to link to airbases",
                                font=("Segoe UI", 8),
                                bg=self.colors['card_bg'],
                                fg=self.colors['secondary_text'],
                                anchor='w')
        left_subtitle.pack(fill=tk.X, padx=15, pady=(0, 10))
        
        left_separator = tk.Frame(left_card, bg=self.colors['separator'], height=1)
        left_separator.pack(fill=tk.X, padx=5)
        
        left_content = tk.Frame(left_card, bg=self.colors['card_bg'])
        left_content.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        main_container.add(left_card, weight=1)
        
        # Middle panel - Airports with modern styling
        middle_card = tk.Frame(main_container, bg=self.colors['card_bg'], relief='flat')
        middle_title = tk.Label(middle_card, 
                               text="🏢 Airbases",
                               font=("Segoe UI", 10, "bold"),
                               bg=self.colors['card_bg'],
                               fg=self.colors['fg'],
                               anchor='w')
        middle_title.pack(fill=tk.X, padx=15, pady=(15, 5))
        
        middle_subtitle = tk.Label(middle_card, 
                                  text="Select airbases to update with templates",
                                  font=("Segoe UI", 8),
                                  bg=self.colors['card_bg'],
                                  fg=self.colors['secondary_text'],
                                  anchor='w')
        middle_subtitle.pack(fill=tk.X, padx=15, pady=(0, 10))
        
        middle_separator = tk.Frame(middle_card, bg=self.colors['border'], height=1)
        middle_separator.pack(fill=tk.X, padx=5)
        
        middle_content = tk.Frame(middle_card, bg=self.colors['card_bg'])
        middle_content.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        main_container.add(middle_card, weight=2)
        
        # Create scrollable frames
        # For templates, we'll manage scrolling manually in show_templates(), so just use the frame directly
        self.template_frame = left_content
        self.airport_frame = self.create_scrollable_frame(middle_content)

        
    def create_scrollable_frame(self, parent):
        """Create a scrollable frame with modern styling"""
        canvas = tk.Canvas(parent, bg=self.colors['card_bg'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.colors['card_bg'])
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        return scrollable_frame
        
    def load_miz(self):
        if not self.csv_loaded:
            messagebox.showwarning("Warning", "Please load airbases CSV file first!")
            return
            
        self.miz_path = filedialog.askopenfilename(
            title="Select a DCS .miz Mission File", 
            filetypes=[("MIZ files", "*.miz")]
        )
        if not self.miz_path:
            return
            
        self.miz_path = Path(self.miz_path)
        self.work_dir = self.miz_path.with_name(self.miz_path.stem + "_extracted")
        
        self.status_label.config(text="Extracting .miz file...")
        self.root.update()
        self.extract_miz()
        
        # Always show airports for configuration
        self.status_label.config(text="Loading airbases...")
        self.root.update()
        self.show_airports()
        
        # Only extract and show templates if in step 2
        if self.current_step == 'templates':
            self.status_label.config(text="Extracting templates from mission...")
            self.root.update()
            self.extract_templates()
            
            self.status_label.config(text="Loading templates...")
            self.root.update()
            self.show_templates()
            
            # Enable template selection buttons
            
            self.status_label.config(text=f"Ready! Loaded {len(self.templates)} templates and {len(self.airports)} airbases.")
        else:
            # Step 1: Show message that templates will be available in step 2
            message_label = tk.Label(self.template_frame, 
                     text="Templates will be available in STEP 2\nafter DynSpawn options are applied.",
                     font=("Segoe UI", 10, "italic"),
                     bg=self.colors['card_bg'],
                     fg=self.colors['secondary_text'])
            message_label.pack(pady=50)
            
            self.status_label.config(text=f"Ready! Loaded {len(self.airports)} airbases. Configure options and apply.")
        
        self.miz_loaded = True
        self.apply_btn.configure(state="normal")

    def extract_miz(self):
        if self.work_dir.exists():
            shutil.rmtree(self.work_dir)
            
        with zipfile.ZipFile(self.miz_path, 'r') as zip_ref:
            zip_ref.extractall(self.work_dir)
            
        self.mission_file = self.work_dir / "mission"
        self.warehouses_file = self.work_dir / "warehouses"

    def extract_templates(self):
        self.templates = []
        with open(self.mission_file, encoding="utf-8") as f:
            lines = f.readlines()

        i = 0
        templates_found_count = 0
        while i < len(lines):
            if '["dynSpawnTemplate"] = true' in lines[i]:
                templates_found_count += 1
                print(f"DEBUG: Found dynSpawnTemplate = true at line {i}")
                group_id, aircraft_type, group_name = None, None, None
                start_line = i

                # Look forward for groupId (comes after route section)
                # Increased range to 250 lines to handle complex templates (like F-14 with many waypoint tasks)
                for j in range(i, min(len(lines), i+250)):
                    if '}, -- end of ["route"]' in lines[j] and group_id is None:
                        # groupId is usually on the next line
                        if j + 1 < len(lines) and '["groupId"]' in lines[j + 1]:
                            id_match = re.search(r'\["groupId"\]\s*=\s*(\d+)', lines[j + 1])
                            if id_match:
                                group_id = int(id_match.group(1))
                                print(f"  Found groupId: {group_id}")
                                break

                # Look forward for aircraft type inside units section
                # First find the units section, then find the first type field inside it
                units_start = None
                for j in range(i, min(len(lines), i+250)):
                    if '["units"]' in lines[j] and '=' in lines[j]:
                        units_start = j
                        print(f"  Found units section at line {j}")
                        break
                
                # Now find the first ["type"] field AFTER the units start but BEFORE the route/waypoint type
                # The aircraft type will be inside the units array, before any radio/payload sections
                if units_start:
                    for j in range(units_start, min(len(lines), units_start+100)):
                        # Look for type field, but skip if it's a waypoint type (has "Turning Point" or similar waypoint keywords)
                        if '["type"]' in lines[j] and aircraft_type is None:
                            type_match = re.search(r'\["type"\]\s*=\s*"([^"]+)"', lines[j])
                            if type_match:
                                potential_type = type_match.group(1)
                                # Skip waypoint types - they contain words like "Turning Point", "Fly Over Point", etc.
                                if 'Point' not in potential_type and 'Way' not in potential_type:
                                    aircraft_type = potential_type
                                    print(f"  Found aircraft type: {aircraft_type} at line {j}")
                                    break
                                else:
                                    print(f"  Skipped waypoint type: {potential_type} at line {j}")

                # Look forward for group name (comes AFTER units section ends)
                # Increased range to 500 lines to handle complex multi-unit templates
                for j in range(i, min(len(lines), i+500)):
                    if '}, -- end of ["units"]' in lines[j] and group_name is None:
                        # Group name is usually 3-4 lines after the units section ends
                        # Look in the next 10 lines for a ["name"] field
                        print(f"  Searching for group name after units section (line {j})...")
                        for k in range(j + 1, min(len(lines), j + 15)):
                            if '["name"]' in lines[k] and '=' in lines[k] and 'channelsNames' not in lines[k]:
                                name_match = re.search(r'\["name"\]\s*=\s*"([^"]+)"', lines[k])
                                if name_match:
                                    potential_name = name_match.group(1)
                                    print(f"    Line {k}: Found potential name: '{potential_name}'")
                                    # Skip names with -1, -2, etc suffix (those are unit names, not group names)
                                    # But allow names with double underscores like "Apache__DynTemp"
                                    if re.search(r'-\d+$', potential_name):
                                        print(f"      Skipped: ends with -digit (unit name)")
                                    elif len(potential_name) <= 3 and '_DynTemp' not in potential_name:
                                        print(f"      Skipped: too short (< 3 chars)")
                                    else:
                                        group_name = potential_name
                                        print(f"      ✓ Accepted as group name")
                                        break
                        if group_name:
                            break

                # Only add templates with valid names and complete data
                if group_id and aircraft_type and group_name:
                    self.templates.append({
                        "groupId": group_id,
                        "type": aircraft_type,
                        "name": group_name
                    })
                    print(f"  ✅ Template added: {group_name} ({aircraft_type}, ID: {group_id})")
                else:
                    print(f"  ⚠️ Skipped (incomplete data): groupId={group_id}, type={aircraft_type}, name={group_name}")
            i += 1
        
        print(f"DEBUG: Total dynSpawnTemplate=true lines found: {templates_found_count}")
        print(f"DEBUG: Total valid templates extracted: {len(self.templates)}")
            
    def show_templates(self):
        for widget in self.template_frame.winfo_children():
            widget.destroy()
        
        # Get list of airports with dynamicSpawn=true (from Step 1)
        airports_with_dynspawn = []
        if self.warehouses_file and self.warehouses_file.exists():
            with open(self.warehouses_file, encoding="utf-8") as f:
                warehouse_lines = f.readlines()
            
            current_airport_id = None
            
            for line in warehouse_lines:
                airport_match = re.search(r'^\s{0,20}\[(\d+)\]\s*=\s*$', line)
                if airport_match:
                    current_airport_id = int(airport_match.group(1))
                
                if current_airport_id and '["dynamicSpawn"] = true' in line:
                    if current_airport_id not in airports_with_dynspawn:
                        airports_with_dynspawn.append(current_airport_id)
        
        if not airports_with_dynspawn:
            warning_label = tk.Label(self.template_frame, 
                     text="⚠ No airbases with dynamicSpawn enabled found!\n\nPlease run Step 1 first to enable dynamic spawn on airbases.",
                     font=("Segoe UI", 10), 
                     bg=self.colors['card_bg'],
                     fg=self.colors['danger'])
            warning_label.pack(pady=20)
            return
        
        # Group templates by aircraft type (since only 1 template per type allowed per airbase)
        templates_by_type = {}
        for template in self.templates:
            aircraft_type = template["type"]
            if aircraft_type not in templates_by_type:
                templates_by_type[aircraft_type] = []
            templates_by_type[aircraft_type].append(template)
        
        # Store airbase-aircrafttype selections: {airport_id: {aircraft_type: StringVar}}
        # StringVar will hold template groupId or "None" for disabled
        self.airbase_template_vars = {}
        
        # Store unlimited checkbox vars: {airport_id: {aircraft_type: BooleanVar}}
        self.airbase_unlimited_vars = {}
        
        # Store initial amount vars: {airport_id: {aircraft_type: StringVar}}
        self.airbase_initial_amount_vars = {}
        
        # Master controls for "Select All" functionality per aircraft type
        self.master_unlimited_vars = {}  # {aircraft_type: BooleanVar}
        self.master_amount_vars = {}     # {aircraft_type: StringVar}
        
        for aircraft_type in templates_by_type.keys():
            self.master_unlimited_vars[aircraft_type] = tk.BooleanVar(value=True)
            self.master_amount_vars[aircraft_type] = tk.StringVar(value="100")
        
        # Initialize vars for all airbases and aircraft types
        for airport_id in airports_with_dynspawn:
            self.airbase_template_vars[airport_id] = {}
            self.airbase_unlimited_vars[airport_id] = {}
            self.airbase_initial_amount_vars[airport_id] = {}
            
            for aircraft_type, templates_list in templates_by_type.items():
                # Default: Select first template for this aircraft type
                default_value = str(templates_list[0]["groupId"])
                self.airbase_template_vars[airport_id][aircraft_type] = tk.StringVar(value=default_value)
                
                # Default: unlimited = True, initialAmount = 100
                self.airbase_unlimited_vars[airport_id][aircraft_type] = tk.BooleanVar(value=True)
                self.airbase_initial_amount_vars[airport_id][aircraft_type] = tk.StringVar(value="100")
        
        # Get airport names
        airport_names_dict = {a["id"]: a["name"] for a in self.airports}
        
        # Create header with instructions
        header = tk.Label(self.template_frame, 
                          text="Configure template spawning for each airbase:",
                          font=("Segoe UI", 11, "bold"),
                          bg=self.colors['card_bg'],
                          fg=self.colors['fg'])
        header.pack(pady=(0, 10), anchor="w")
        
        subtitle = tk.Label(self.template_frame,
                 text="For each airbase and aircraft type, select template, unlimited flag, and initial amount.",
                 font=("Segoe UI", 9, "italic"),
                 bg=self.colors['card_bg'],
                 fg=self.colors['secondary_text'])
        subtitle.pack(pady=(0, 5), anchor="w")
        
        help_text = tk.Label(self.template_frame,
                 text="• Template: Which aircraft template to spawn  • ∞: Unlimited aircraft (checked=true)  • Amount: Starting aircraft count",
                 font=("Segoe UI", 8),
                 bg=self.colors['card_bg'],
                 fg=self.colors['secondary_text'])
        help_text.pack(pady=(0, 15), anchor="w")
        
        # Create scrollable container for the table (both horizontal and vertical)
        # Create outer frame with both scrollbars - make it expand to fill space
        table_container = tk.Frame(self.template_frame, bg=self.colors['card_bg'])
        table_container.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Create canvas with scrollbars - removed fixed height to let it expand
        canvas = tk.Canvas(table_container, borderwidth=0, highlightthickness=0, bg=self.colors['card_bg'])
        h_scrollbar = ttk.Scrollbar(table_container, orient="horizontal", command=canvas.xview)
        v_scrollbar = ttk.Scrollbar(table_container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.colors['card_bg'])
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(xscrollcommand=h_scrollbar.set, yscrollcommand=v_scrollbar.set)
        
        # Pack canvas and scrollbars
        canvas.grid(row=0, column=0, sticky="nsew")
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        
        table_container.grid_rowconfigure(0, weight=1)
        table_container.grid_columnconfigure(0, weight=1)
        
        # Create table header
        header_label = tk.Label(scrollable_frame, text="Airbase Name", 
                 font=("Courier New", 9, "bold"), 
                 bg=self.colors['card_bg'],
                 fg=self.colors['fg'],
                 width=32,  # Match the airbase name column width
                 anchor="w")
        header_label.grid(row=0, column=0, sticky="w", padx=5, pady=(0, 5))
        
        # Add column header for each aircraft type (sorted alphabetically)
        # Each aircraft type now has 3 columns: Template, Unlimited, Initial Amount
        sorted_aircraft_types = sorted(templates_by_type.keys())
        col_idx = 1
        for aircraft_type in sorted_aircraft_types:
            # Aircraft type main header (spans 3 columns)
            type_label = tk.Label(scrollable_frame, text=aircraft_type, 
                     font=("Segoe UI", 9, "bold"), 
                     bg=self.colors['card_bg'],
                     fg=self.colors['fg'],
                     anchor="center")
            type_label.grid(row=0, column=col_idx, columnspan=3, sticky="ew", padx=1, pady=(0, 2))
            
            # Sub-headers for Template, Unlimited, Initial Amount
            template_header = tk.Label(scrollable_frame, text="Template", 
                     font=("Segoe UI", 8, "bold"), 
                     bg=self.colors['card_bg'],
                     fg=self.colors['secondary_text'],
                     width=18, anchor="center")
            template_header.grid(row=1, column=col_idx, sticky="w", padx=2, pady=(0, 3))
            
            unlimited_header = tk.Label(scrollable_frame, text="∞", 
                     font=("Segoe UI", 8, "bold"), 
                     bg=self.colors['card_bg'],
                     fg=self.colors['secondary_text'],
                     width=3, anchor="center")
            unlimited_header.grid(row=1, column=col_idx+1, sticky="w", padx=2, pady=(0, 3))
            
            amount_header = tk.Label(scrollable_frame, text="Amount", 
                     font=("Segoe UI", 8, "bold"), 
                     bg=self.colors['card_bg'],
                     fg=self.colors['secondary_text'],
                     width=6, anchor="center")
            amount_header.grid(row=1, column=col_idx+2, sticky="w", padx=2, pady=(0, 3))
            
            col_idx += 3
        
        total_columns = 1 + (len(sorted_aircraft_types) * 3)
        ttk.Separator(scrollable_frame, orient='horizontal').grid(row=2, column=0, columnspan=total_columns, sticky="ew", pady=2)
        
        # Add "Select All" row for master controls
        select_all_label = tk.Label(scrollable_frame, text="Select All →", 
                 font=("Segoe UI", 8, "italic"), 
                 bg=self.colors['card_bg'],
                 fg=self.colors['secondary_text'],
                 anchor="e")
        select_all_label.grid(row=3, column=0, sticky="e", padx=5, pady=2)
        
        # Add master controls for each aircraft type
        col_idx = 1
        for aircraft_type in sorted_aircraft_types:
            # Skip template column (no master control needed)
            col_idx += 1
            
            # Master unlimited checkbox
            def create_unlimited_master_callback(aircraft_type_ref):
                def toggle_unlimited():
                    master_value = self.master_unlimited_vars[aircraft_type_ref].get()
                    for airport_id in airports_with_dynspawn:
                        if airport_id in self.airbase_unlimited_vars and aircraft_type_ref in self.airbase_unlimited_vars[airport_id]:
                            self.airbase_unlimited_vars[airport_id][aircraft_type_ref].set(master_value)
                return toggle_unlimited
            
            master_unlimited_cb = ttk.Checkbutton(scrollable_frame, 
                                                 variable=self.master_unlimited_vars[aircraft_type],
                                                 command=create_unlimited_master_callback(aircraft_type),
                                                 style='Modern.TCheckbutton')
            master_unlimited_cb.grid(row=3, column=col_idx, padx=2, pady=2)
            col_idx += 1
            
            # Master amount entry
            def create_amount_master_callback(aircraft_type_ref):
                def update_amounts(*args):
                    master_value = self.master_amount_vars[aircraft_type_ref].get()
                    if master_value.strip():  # Only update if not empty
                        for airport_id in airports_with_dynspawn:
                            if airport_id in self.airbase_initial_amount_vars and aircraft_type_ref in self.airbase_initial_amount_vars[airport_id]:
                                self.airbase_initial_amount_vars[airport_id][aircraft_type_ref].set(master_value)
                return update_amounts
            
            # Add trace to master amount var to auto-update all fields
            self.master_amount_vars[aircraft_type].trace('w', create_amount_master_callback(aircraft_type))
            
            vcmd_master = (scrollable_frame.register(lambda char: char.isdigit() or char == ""), '%S')
            master_amount_entry = ttk.Entry(scrollable_frame,
                                          textvariable=self.master_amount_vars[aircraft_type],
                                          width=6,
                                          font=("Segoe UI", 9),
                                          validate='key',
                                          validatecommand=vcmd_master)
            master_amount_entry.grid(row=3, column=col_idx, padx=2, pady=2)
            col_idx += 1
        
        # Add another separator after master controls
        ttk.Separator(scrollable_frame, orient='horizontal').grid(row=4, column=0, columnspan=total_columns, sticky="ew", pady=2)
        
        # Create a row for each airbase
        for row_idx, airport_id in enumerate(airports_with_dynspawn):
            airport_name = airport_names_dict.get(airport_id, f"Airport {airport_id}")
            
            # Get coalition for this airbase and determine dot color
            coalition = "NEUTRAL"  # Default
            if airport_id in self.coalition_vars:
                coalition = self.coalition_vars[airport_id].get()
            
            # Set coalition dot color - use more readable colors on dark background
            if coalition == "BLUE":
                dot_color = self.colors['blue_readable']
                dot_symbol = "●"
            elif coalition == "RED":
                dot_color = self.colors['red_readable']
                dot_symbol = "●"
            else:  # NEUTRAL
                dot_color = self.colors['neutral_readable']
                dot_symbol = "○"
            
            # Create airbase name label with fixed width for alignment
            airbase_label = f"{dot_symbol} {airport_name} (ID: {airport_id})"
            name_label = tk.Label(scrollable_frame, 
                     text=airbase_label,
                     font=("Courier New", 9),  # Monospace font for better alignment
                     fg=dot_color,
                     bg=self.colors['card_bg'],
                     width=32,  # Fixed width for consistent alignment
                     anchor="w")
            name_label.grid(row=row_idx+5, column=0, sticky="w", padx=5, pady=2)
            
            # Add controls for each aircraft type (Template dropdown, Unlimited checkbox, Initial Amount entry)
            col_idx = 1
            for aircraft_type in sorted_aircraft_types:
                template_var = self.airbase_template_vars[airport_id][aircraft_type]
                unlimited_var = self.airbase_unlimited_vars[airport_id][aircraft_type]
                amount_var = self.airbase_initial_amount_vars[airport_id][aircraft_type]
                
                # Template dropdown
                templates_list = templates_by_type[aircraft_type]
                choices = ["None (Disabled)"]
                for template in templates_list:
                    choices.append(f"{template['name']} (ID:{template['groupId']})")
                
                # Create callback to store groupId when template is selected
                def create_dropdown_callback(var_ref):
                    def on_select(event):
                        widget = event.widget
                        selected_text = widget.get()
                        if selected_text.startswith("None"):
                            var_ref.set("None")
                        else:
                            # Extract groupId from "TemplateName (ID:X)"
                            match = re.search(r'ID:(\d+)', selected_text)
                            if match:
                                var_ref.set(match.group(1))
                    return on_select
                
                dropdown = ttk.Combobox(scrollable_frame,
                                       values=choices,
                                       width=16,
                                       state="readonly",
                                       style='Modern.TCombobox')
                
                # Set initial display value (show template name, not ID)
                current_id = template_var.get()
                if current_id == "None":
                    dropdown.set("None (Disabled)")
                else:
                    for template in templates_list:
                        if str(template['groupId']) == current_id:
                            dropdown.set(f"{template['name']} (ID:{template['groupId']})")
                            break
                
                dropdown.bind("<<ComboboxSelected>>", create_dropdown_callback(template_var))
                dropdown.grid(row=row_idx+5, column=col_idx, sticky="w", padx=2, pady=2)
                
                # Unlimited checkbox
                unlimited_cb = ttk.Checkbutton(scrollable_frame, 
                                             variable=unlimited_var,
                                             style='Modern.TCheckbutton')
                unlimited_cb.grid(row=row_idx+5, column=col_idx+1, padx=2, pady=2)
                
                # Initial Amount entry with validation
                def create_validate_number(var_ref):
                    def validate_input(char):
                        # Allow only digits and empty string
                        return char.isdigit() or char == ""
                    return validate_input
                
                vcmd = (scrollable_frame.register(create_validate_number(amount_var)), '%S')
                amount_entry = ttk.Entry(scrollable_frame,
                                       textvariable=amount_var,
                                       width=6,
                                       font=("Segoe UI", 9),
                                       validate='key',
                                       validatecommand=vcmd)
                amount_entry.grid(row=row_idx+5, column=col_idx+2, padx=2, pady=2)
                
                col_idx += 3
        
        # Add summary at bottom
        summary_frame = tk.Frame(self.template_frame, bg=self.colors['card_bg'])
        summary_frame.pack(fill="x", pady=(15, 5))
        
        separator = tk.Frame(summary_frame, bg=self.colors['separator'], height=1)
        separator.pack(fill="x", pady=5)
        
        summary_text = f"📊 {len(self.templates)} template(s) available  •  {len(templates_by_type)} aircraft type(s)  •  {len(airports_with_dynspawn)} airbase(s) with dynamic spawn"
        summary_label = tk.Label(summary_frame, text=summary_text, 
                 font=("Segoe UI", 9, "italic"), 
                 bg=self.colors['card_bg'],
                 fg=self.colors['secondary_text'])
        summary_label.pack(pady=5)
                
    def show_airports(self):
        for widget in self.airport_frame.winfo_children():
            widget.destroy()
            
        categories = {"Airdrome": [], "Helipad": [], "Ship": []}
        for airport in self.airports:
            if airport["category"] in categories:
                categories[airport["category"]].append(airport)
        
        # Create master checkboxes for "Select All" functionality
        self.master_checkboxes = {
            'dynamicSpawn': tk.BooleanVar(value=False),
            'allowHotStart': tk.BooleanVar(value=False),
            'dynamicCargo': tk.BooleanVar(value=False),
            'unlimitedMunitions': tk.BooleanVar(value=True),
            'unlimitedAircrafts': tk.BooleanVar(value=True),
            'unlimitedFuel': tk.BooleanVar(value=True)
        }
                
        row = 0
        for category, airports in categories.items():
            if airports:
                category_label = tk.Label(self.airport_frame, text=category, 
                         font=("Segoe UI", 12, "bold"),
                         bg=self.colors['card_bg'],
                         fg=self.colors['primary'])
                category_label.grid(row=row, column=0, columnspan=7, pady=10, sticky="w")
                row += 1
                
                # Column headers for DynSpawn options - modern styling
                headers_data = [
                    ("Select", 0, None),
                    ("Airbase Name", 1, "w"),
                    ("Coalition", 2, None),
                    ("DynSpawn", 3, None),
                    ("HotStart", 4, None),
                    ("DynCargo", 5, None),
                    ("∞Munitions", 6, None),
                    ("∞Aircraft", 7, None),
                    ("∞Fuel", 8, None)
                ]
                
                for text, col, sticky_val in headers_data:
                    header = tk.Label(self.airport_frame, text=text, 
                                    font=("Segoe UI", 9, "bold"),
                                    bg=self.colors['card_bg'],
                                    fg=self.colors['fg'])
                    if sticky_val:
                        header.grid(row=row, column=col, padx=5, sticky=sticky_val)
                    else:
                        header.grid(row=row, column=col, padx=5)
                row += 1
                
                # Add "Select All" row with checkboxes for each option
                # Create a master checkbox variable for selecting all airbases in this category
                category_select_all_var = tk.BooleanVar(value=True)
                
                # Function to toggle all airbase selections in this category
                def create_category_select_all_toggle(category_airports, var):
                    def toggle():
                        value = var.get()
                        for airport in category_airports:
                            if airport["id"] in self.airport_vars:
                                self.airport_vars[airport["id"]].set(value)
                    return toggle
                
                # Add "Select All" checkbox for airbase selection
                ttk.Checkbutton(self.airport_frame, variable=category_select_all_var,
                               command=create_category_select_all_toggle(airports, category_select_all_var),
                               style='Modern.TCheckbutton').grid(row=row, column=0, padx=5)
                
                select_all_label = tk.Label(self.airport_frame, text="Select All →", 
                         font=("Segoe UI", 8, "italic"), 
                         bg=self.colors['card_bg'],
                         fg=self.colors['secondary_text'])
                select_all_label.grid(row=row, column=1, padx=5, sticky="e")
                
                empty_label = tk.Label(self.airport_frame, text="", 
                         bg=self.colors['card_bg'])
                empty_label.grid(row=row, column=2, padx=5)  # Empty coalition cell
                
                # Create toggle functions for each column
                def create_toggle_function(option_key, category_airports):
                    def toggle():
                        value = self.master_checkboxes[option_key].get()
                        for airport in category_airports:
                            if airport["id"] in self.dynspawn_options:
                                self.dynspawn_options[airport["id"]][option_key].set(value)
                    return toggle
                
                # Add "Select All" checkboxes for each option column
                ttk.Checkbutton(self.airport_frame, variable=self.master_checkboxes['dynamicSpawn'],
                               command=create_toggle_function('dynamicSpawn', airports), style='Modern.TCheckbutton').grid(row=row, column=3)
                ttk.Checkbutton(self.airport_frame, variable=self.master_checkboxes['allowHotStart'],
                               command=create_toggle_function('allowHotStart', airports), style='Modern.TCheckbutton').grid(row=row, column=4)
                ttk.Checkbutton(self.airport_frame, variable=self.master_checkboxes['dynamicCargo'],
                               command=create_toggle_function('dynamicCargo', airports), style='Modern.TCheckbutton').grid(row=row, column=5)
                ttk.Checkbutton(self.airport_frame, variable=self.master_checkboxes['unlimitedMunitions'],
                               command=create_toggle_function('unlimitedMunitions', airports), style='Modern.TCheckbutton').grid(row=row, column=6)
                ttk.Checkbutton(self.airport_frame, variable=self.master_checkboxes['unlimitedAircrafts'],
                               command=create_toggle_function('unlimitedAircrafts', airports), style='Modern.TCheckbutton').grid(row=row, column=7)
                ttk.Checkbutton(self.airport_frame, variable=self.master_checkboxes['unlimitedFuel'],
                               command=create_toggle_function('unlimitedFuel', airports), style='Modern.TCheckbutton').grid(row=row, column=8)
                row += 1
                
                for airport in airports:
                    # Main checkbox to select airport
                    var = tk.BooleanVar(value=True)
                    self.airport_vars[airport["id"]] = var
                    
                    # Coalition indicator - use more readable colors
                    if airport["coalition"].lower() == "neutral":
                        color = self.colors['neutral_readable']
                        dot_symbol = "○"
                    else:
                        color = self.colors['blue_readable'] if airport["coalition"].lower() == "blue" else self.colors['red_readable']
                        dot_symbol = "●"
                    
                    label_text = f"{airport['name']} (ID: {airport['id']})"
                    
                    # Create checkboxes for DynSpawn options
                    if airport["id"] not in self.dynspawn_options:
                        self.dynspawn_options[airport["id"]] = {
                            'dynamicSpawn': tk.BooleanVar(value=False),
                            'allowHotStart': tk.BooleanVar(value=False),
                            'dynamicCargo': tk.BooleanVar(value=False),
                            'unlimitedMunitions': tk.BooleanVar(value=True),
                            'unlimitedAircrafts': tk.BooleanVar(value=True),
                            'unlimitedFuel': tk.BooleanVar(value=True)
                        }
                    
                    # Create coalition dropdown variable
                    if airport["id"] not in self.coalition_vars:
                        self.coalition_vars[airport["id"]] = tk.StringVar(value=airport["coalition"].upper())
                    
                    # Airport selection checkbox
                    cb = ttk.Checkbutton(self.airport_frame, variable=var, style='Modern.TCheckbutton')
                    cb.grid(row=row, column=0, padx=5)
                    
                    # Airport name with coalition dot
                    name_frame = ttk.Frame(self.airport_frame)
                    name_frame.grid(row=row, column=1, sticky="w", padx=5)
                    ttk.Label(name_frame, text=dot_symbol, foreground=color).pack(side=tk.LEFT)
                    ttk.Label(name_frame, text=label_text, font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=2)
                    
                    # Coalition dropdown menu with color-coding
                    coalition_menu = ttk.Combobox(self.airport_frame, textvariable=self.coalition_vars[airport["id"]], 
                                                 values=["BLUE", "RED", "NEUTRAL"], state="readonly", width=8,
                                                 style='Modern.TCombobox')
                    coalition_menu.grid(row=row, column=2, padx=5)
                    
                    # Add callback to update coalition dropdown color
                    def create_coalition_callback(menu, airport_id):
                        def update_color(event=None):
                            coalition = self.coalition_vars[airport_id].get()
                            if coalition == "BLUE":
                                menu.configure(foreground=self.colors['blue_readable'])
                            elif coalition == "RED":
                                menu.configure(foreground=self.colors['red_readable'])
                            else:
                                menu.configure(foreground=self.colors['neutral_readable'])
                        return update_color
                    
                    callback = create_coalition_callback(coalition_menu, airport["id"])
                    coalition_menu.bind("<<ComboboxSelected>>", callback)
                    callback()  # Set initial color
                    
                    # DynSpawn options checkboxes
                    ttk.Checkbutton(self.airport_frame, variable=self.dynspawn_options[airport["id"]]['dynamicSpawn'], style='Modern.TCheckbutton').grid(row=row, column=3)
                    ttk.Checkbutton(self.airport_frame, variable=self.dynspawn_options[airport["id"]]['allowHotStart'], style='Modern.TCheckbutton').grid(row=row, column=4)
                    ttk.Checkbutton(self.airport_frame, variable=self.dynspawn_options[airport["id"]]['dynamicCargo'], style='Modern.TCheckbutton').grid(row=row, column=5)
                    ttk.Checkbutton(self.airport_frame, variable=self.dynspawn_options[airport["id"]]['unlimitedMunitions'], style='Modern.TCheckbutton').grid(row=row, column=6)
                    ttk.Checkbutton(self.airport_frame, variable=self.dynspawn_options[airport["id"]]['unlimitedAircrafts'], style='Modern.TCheckbutton').grid(row=row, column=7)
                    ttk.Checkbutton(self.airport_frame, variable=self.dynspawn_options[airport["id"]]['unlimitedFuel'], style='Modern.TCheckbutton').grid(row=row, column=8)
                    
                    row += 1
                    
    def apply_step1(self):
        """Step 1: Apply DynSpawn options and coalition settings only"""
        if not self.miz_loaded:
            messagebox.showwarning("Warning", "Please load a .miz file first!")
            return
        
        if self.current_step == 'templates':
            # If in step 2, call the full apply
            self.apply_step2()
            return
            
        selected_airports = [a["id"] for a in self.airports 
                        if self.airport_vars[a["id"]].get()]
        
        if not selected_airports:
            messagebox.showwarning("Warning", "No airports selected!")
            return
        
        try:
            # Step 1a: Enable dynSpawnTemplate for aircraft groups with '_DynTemp' suffix
            self.status_label.config(text="Enabling dynamic spawn templates in mission...")
            self.root.update()
            template_count = self.enable_dynspawn_templates_in_mission()
            
            # Step 1b: Update warehouses file with DynSpawn options
            self.status_label.config(text="Updating DynSpawn options...")
            self.root.update()
            self.update_warehouse_dynspawn_options(selected_airports)
            
            # Step 1c: Create aircraft inventory for templates in warehouses
            self.status_label.config(text="Creating aircraft inventory for templates...")
            self.root.update()
            inventory_count = self.create_aircraft_inventory_for_templates(selected_airports)
            
            # Step 1d: Update warehouses file with coalition changes
            self.status_label.config(text="Updating coalitions...")
            self.root.update()
            self.update_warehouse_coalitions(selected_airports)
            
            # Step 2: Repack the .miz file
            self.status_label.config(text="Repacking .miz file...")
            self.root.update()
            updated_miz = self.miz_path.with_name(self.miz_path.stem + "_Step1_Options.miz")
            with zipfile.ZipFile(updated_miz, 'w', zipfile.ZIP_DEFLATED) as z:
                for folder, _, files in os.walk(self.work_dir):
                    for file in files:
                        path = Path(folder) / file
                        z.write(path, arcname=path.relative_to(self.work_dir))

            shutil.rmtree(self.work_dir)
            
            self.status_label.config(text=f"Step 1 complete! Options saved.")
            
            # Show message and ask if user wants to continue to step 2
            result = messagebox.askyesno("Step 1 Complete", 
                f"DynSpawn options and coalition settings saved as:\n{updated_miz.name}\n\n"
                f"Applied changes:\n"
                f"- {template_count} dynamic template(s) enabled in mission\n"
                f"- {inventory_count} aircraft inventory entries created in warehouses\n"
                f"- {len(selected_airports)} airbase(s) updated\n"
                f"- DynSpawn options configured\n"
                f"- Coalition assignments updated\n\n"
                f"Do you want to continue to STEP 2 (Link Dynamic Templates)?\n\n"
                f"Click YES to reload the file and configure templates.\n"
                f"Click NO to exit (you can run step 2 later).")
            
            if result:
                # Move to step 2
                self.current_step = 'templates'
                self.miz_path = updated_miz
                self.miz_loaded = False
                
                # Update UI for step 2
                self.step_label.config(text="STEP 2: Link Dynamic Templates")
                self.apply_btn.config(text="Apply Templates & Save Final")
                
                # Clear templates frame
                for widget in self.template_frame.winfo_children():
                    widget.destroy()
                
                # Reload the file
                self.status_label.config(text="Loading updated .miz file for step 2...")
                self.root.update()
                
                self.work_dir = self.miz_path.with_name(self.miz_path.stem + "_extracted")
                self.extract_miz()
                self.extract_templates()
                self.show_templates()
                
                # Enable apply button for step 2
                self.apply_btn.configure(state="normal")
                self.miz_loaded = True
                
                self.status_label.config(text=f"Step 2 ready! Found {len(self.templates)} templates. Select and apply.")
                messagebox.showinfo("Ready for Step 2", 
                    f"Found {len(self.templates)} dynamic templates in the updated mission.\n\n"
                    f"Select the templates you want to link to airbases, then click 'Apply Templates & Save Final'.")
            else:
                # Reset state and exit
                self.miz_loaded = False
                self.apply_btn.configure(state="disabled")
                self.status_label.config(text="Step 1 complete. You can close this window or start over.")
            
        except Exception as e:
            self.status_label.config(text="Error occurred during step 1!")
            messagebox.showerror("Error", f"Failed to apply changes:\n{str(e)}")
    
    def apply_step2(self):
        """Step 2: Apply template links to the already-configured mission"""
        print("\n" + "="*60)
        print("EXECUTING STEP 2: Link Dynamic Templates")
        print("="*60)
        
        if not self.miz_loaded:
            messagebox.showwarning("Warning", "Please load a .miz file first!")
            return
        
        # Build mapping: template -> list of airport IDs to link to
        # Data structure: self.airbase_template_vars[airport_id][aircraft_type] = StringVar(groupId or "None")
        template_airport_mapping = {}
        
        for template in self.templates:
            group_id = template["groupId"]
            aircraft_type = template["type"]
            selected_airports = []
            
            # Check which airbases have this template selected for this aircraft type
            for airport_id, aircraft_type_vars in self.airbase_template_vars.items():
                if aircraft_type in aircraft_type_vars:
                    selected_template_id = aircraft_type_vars[aircraft_type].get()
                    # Check if this template is selected (ID matches and not "None")
                    if selected_template_id == str(group_id):
                        selected_airports.append(airport_id)
            
            if selected_airports:
                # Collect unlimited and initial amount data for each airport
                airport_options = {}
                for airport_id in selected_airports:
                    unlimited_val = self.airbase_unlimited_vars[airport_id][aircraft_type].get()
                    amount_val = self.airbase_initial_amount_vars[airport_id][aircraft_type].get()
                    
                    # Validate amount is a number
                    try:
                        amount_int = int(amount_val) if amount_val.strip() else 100
                    except ValueError:
                        amount_int = 100  # Default fallback
                    
                    airport_options[airport_id] = {
                        "unlimited": unlimited_val,
                        "initialAmount": amount_int
                    }
                    print(f"  DEBUG: Collected options for airport {airport_id}, aircraft {aircraft_type}: unlimited={unlimited_val}, amount={amount_int}")
                
                template_airport_mapping[group_id] = {
                    "template": template,
                    "airports": selected_airports,
                    "airport_options": airport_options
                }
            else:
                print(f"  Template '{template['name']}' (ID:{group_id}) -> DISABLED (not linked to any airbase)")
        
        print(f"DEBUG: Step 2 - Template-Airport mapping:")
        for group_id, mapping in template_airport_mapping.items():
            tpl = mapping["template"]
            airports = mapping["airports"]
            print(f"  Template '{tpl['name']}' (ID:{group_id}, Type:{tpl['type']}) -> Airports: {airports}")
            if "airport_options" in mapping:
                for airport_id, options in mapping["airport_options"].items():
                    print(f"    Airport {airport_id}: unlimited={options['unlimited']}, initialAmount={options['initialAmount']}")
        
        if not template_airport_mapping:
            messagebox.showwarning("Warning", 
                "No templates are selected for linking to any airbases!\n\n"
                "Please check at least one airbase for each template you want to link.")
            return
        
        try:
            # Update warehouses file with template-airport mappings
            self.status_label.config(text="Linking templates to airbases...")
            self.root.update()
            self.update_warehouse_templates_with_mapping(template_airport_mapping)
            
            # Also update unlimited and initialAmount for ALL aircraft types with user-specified options
            self.status_label.config(text="Updating aircraft inventory options...")
            self.root.update()
            self.update_aircraft_inventory_options()
            
            # Repack the final .miz file
            self.status_label.config(text="Creating final .miz file...")
            self.root.update()
            
            # Remove "_Step1_Options" suffix if present
            if "_Step1_Options" in self.miz_path.stem:
                base_name = self.miz_path.stem.replace("_Step1_Options", "")
            else:
                base_name = self.miz_path.stem
                
            final_miz = self.miz_path.with_name(base_name + "_Final.miz")
            
            print(f"DEBUG: Creating final .miz file: {final_miz}")
            print(f"DEBUG: Source directory: {self.work_dir}")
            print(f"DEBUG: Directory exists: {self.work_dir.exists()}")
            
            if not self.work_dir.exists():
                raise Exception(f"Work directory not found: {self.work_dir}")
            
            with zipfile.ZipFile(final_miz, 'w', zipfile.ZIP_DEFLATED) as z:
                for folder, _, files in os.walk(self.work_dir):
                    for file in files:
                        path = Path(folder) / file
                        z.write(path, arcname=path.relative_to(self.work_dir))
            
            print(f"DEBUG: Final .miz file created successfully")

            shutil.rmtree(self.work_dir)
            
            # Delete the Step1 .miz file to clean up
            step1_file_deleted = False
            if "_Step1_Options" in self.miz_path.name:
                try:
                    print(f"DEBUG: Deleting Step1 file: {self.miz_path}")
                    os.remove(self.miz_path)
                    step1_file_deleted = True
                    print(f"DEBUG: Step1 file deleted successfully")
                except Exception as e:
                    print(f"WARNING: Could not delete Step1 file: {e}")
                    # Continue anyway - this is just cleanup
            
            self.status_label.config(text=f"Complete! Final mission saved.")
            
            total_links = sum(len(m["airports"]) for m in template_airport_mapping.values())
            
            cleanup_msg = f"\n✓ Step1 file cleaned up" if step1_file_deleted else ""
            
            messagebox.showinfo("All Steps Complete!", 
                f"Final mission saved as:\n{final_miz.name}\n\n"
                f"All changes applied:\n"
                f"✓ {len(template_airport_mapping)} template(s) linked\n"
                f"✓ {total_links} template-airbase link(s) created\n"
                f"✓ DynSpawn options applied\n"
                f"✓ Coalition assignments updated{cleanup_msg}\n\n"
                f"Your mission is ready to use in DCS!")
            
            # Reset state
            self.miz_loaded = False
            self.apply_btn.configure(state="disabled")
            self.current_step = 'options'
            self.step_label.config(text="STEP 1: Configure DynSpawn Options & Coalition")
            self.apply_btn.config(text="Apply Options & Save")
            
        except Exception as e:
            import traceback
            self.status_label.config(text="Error occurred during step 2!")
            error_details = traceback.format_exc()
            print(f"ERROR in apply_step2:\n{error_details}")
            messagebox.showerror("Error", f"Failed to apply templates:\n{str(e)}\n\nSee console for details.")
    
    def update_warehouse_templates(self, selected_templates, selected_airports):
        """Update warehouse file with template links"""
        
        print(f"\nDEBUG: Starting template linking")
        print(f"DEBUG: Selected templates ({len(selected_templates)}):")
        for tpl in selected_templates:
            print(f"  - {tpl['name']} (ID: {tpl['groupId']}, Type: {tpl['type']})")
        print(f"DEBUG: Selected airports: {selected_airports}")
        
        with open(self.warehouses_file, encoding="utf-8") as f:
            warehouse_lines = f.readlines()

        i = 0
        current_airport_id = None
        in_selected_airport = False
        updates_made = 0
        
        # Track which templates have been processed for each airport
        processed_per_airport = {}

        while i < len(warehouse_lines):
            line = warehouse_lines[i]
            
            # Detect airport entry - only match top-level entries with minimal indentation
            # Airport entries look like:        [18] = 
            # Array indices look like:                                                 [1] = 1,
            # We need to distinguish between them by checking indentation
            airport_id_match = re.search(r'^\s{0,20}\[(\d+)\]\s*=\s*$', line)
            if airport_id_match:
                current_airport_id = int(airport_id_match.group(1))
                in_selected_airport = (current_airport_id in selected_airports)
                if in_selected_airport:
                    print(f"\nDEBUG: Processing airport {current_airport_id}")
                    processed_per_airport[current_airport_id] = set()
            
            # Process only if inside a selected airport
            if in_selected_airport and current_airport_id:
                for tpl in selected_templates:
                    # Skip if already processed this template for this airport
                    if tpl["type"] in processed_per_airport.get(current_airport_id, set()):
                        continue
                    
                    # Check if the line contains the aircraft type (EXACT match to avoid substring issues)
                    # Must match: ["aircraft_type"] = with nothing extra
                    aircraft_pattern = f'\\["{re.escape(tpl["type"])}"\\]\\s*='
                    if re.search(aircraft_pattern, line) and '-- end of' not in line:
                        print(f"  DEBUG: Found aircraft type '{tpl['type']}' at line {i}: {line.strip()}")
                        # Iterate forward to find or add the linkDynTempl line
                        j = i + 1
                        found_link = False
                        while j < len(warehouse_lines) and j < i + 30:  # Look ahead max 30 lines
                            # Check if linkDynTempl exists
                            if '["linkDynTempl"]' in warehouse_lines[j]:
                                # Get old value for debug
                                old_value = warehouse_lines[j].split('=')[1].strip().rstrip(',')
                                # Update existing linkDynTempl
                                indentation = warehouse_lines[j][:len(warehouse_lines[j]) - len(warehouse_lines[j].lstrip())]
                                warehouse_lines[j] = f'{indentation}["linkDynTempl"] = {tpl["groupId"]},\n'
                                found_link = True
                                updates_made += 1
                                print(f"    DEBUG: Updated linkDynTempl at line {j}: {old_value} → {tpl['groupId']}")
                                break
                            
                            # Check if we've reached the end of this aircraft's section
                            if f'-- end of ["{tpl["type"]}"]' in warehouse_lines[j]:
                                # linkDynTempl doesn't exist, insert before closing brace
                                # The line before this comment should be the closing brace
                                insert_line = j - 1
                                indentation = warehouse_lines[insert_line][:len(warehouse_lines[insert_line]) - len(warehouse_lines[insert_line].lstrip())]
                                warehouse_lines.insert(insert_line, f'{indentation}["linkDynTempl"] = {tpl["groupId"]},\n')
                                found_link = True
                                updates_made += 1
                                print(f"    DEBUG: Inserted linkDynTempl at line {insert_line} = {tpl['groupId']}")
                                break
                            
                            j += 1
                        
                        if found_link:
                            # Mark this template as processed for this airport
                            processed_per_airport[current_airport_id].add(tpl["type"])
                            print(f"    DEBUG: Marked '{tpl['type']}' as processed for airport {current_airport_id}")
                            # Don't break - continue checking other templates for this line
                        else:
                            print(f"    WARNING: Could not find linkDynTempl or end marker for '{tpl['type']}'")
            
            i += 1

        # Write the modified content back
        with open(self.warehouses_file, "w", encoding="utf-8") as f:
            f.writelines(warehouse_lines)
        
        print(f"DEBUG: Updated {updates_made} template links")
    
    def update_warehouse_templates_with_mapping(self, template_airport_mapping):
        """Update warehouse file with template links using per-template airport mapping
        
        Args:
            template_airport_mapping: Dict with structure:
                {
                    groupId: {
                        "template": {groupId, type, name},
                        "airports": [airport_id1, airport_id2, ...],
                        "airport_options": {
                            airport_id: {
                                "unlimited": bool,
                                "initialAmount": int
                            }
                        }
                    }
                }
        """
        
        print(f"\nDEBUG: Starting template linking with custom mapping")
        
        with open(self.warehouses_file, encoding="utf-8") as f:
            warehouse_lines = f.readlines()

        i = 0
        current_airport_id = None
        in_selected_airport = False
        updates_made = 0
        
        # Track which templates have been processed for each airport
        processed_per_airport = {}

        while i < len(warehouse_lines):
            line = warehouse_lines[i]
            
            # Detect airport entry - only match top-level entries with minimal indentation
            airport_id_match = re.search(r'^\s{0,20}\[(\d+)\]\s*=\s*$', line)
            if airport_id_match:
                current_airport_id = int(airport_id_match.group(1))
                
                # Check if ANY template should be linked to this airport
                templates_for_this_airport = []
                for group_id, mapping in template_airport_mapping.items():
                    if current_airport_id in mapping["airports"]:
                        templates_for_this_airport.append(mapping["template"])
                
                in_selected_airport = len(templates_for_this_airport) > 0
                
                if in_selected_airport:
                    print(f"\nDEBUG: Processing airport {current_airport_id}")
                    print(f"       Templates to link: {[t['name'] for t in templates_for_this_airport]}")
                    processed_per_airport[current_airport_id] = set()
            
            # Process only if inside a selected airport
            if in_selected_airport and current_airport_id:
                # Check which templates should be linked to THIS specific airport
                for group_id, mapping in template_airport_mapping.items():
                    if current_airport_id not in mapping["airports"]:
                        continue  # Skip this template for this airport
                    
                    tpl = mapping["template"]
                    
                    # Skip if already processed this template for this airport
                    if tpl["type"] in processed_per_airport.get(current_airport_id, set()):
                        continue
                    
                    # Check if the line contains the aircraft type (EXACT match to avoid substring issues)
                    aircraft_pattern = f'\\["{re.escape(tpl["type"])}"\\]\\s*='
                    if re.search(aircraft_pattern, line) and '-- end of' not in line:
                        print(f"  DEBUG: Found aircraft type '{tpl['type']}' at line {i}: {line.strip()}")
                        print(f"  DEBUG: Will update with options: unlimited={mapping['airport_options'][current_airport_id]['unlimited']}, initialAmount={mapping['airport_options'][current_airport_id]['initialAmount']}")
                        # Iterate forward to find or add the linkDynTempl line
                        j = i + 1
                        found_link = False
                        while j < len(warehouse_lines) and j < i + 30:  # Look ahead max 30 lines
                            # Check if linkDynTempl exists
                            if '["linkDynTempl"]' in warehouse_lines[j]:
                                # Get old value for debug
                                old_value = warehouse_lines[j].split('=')[1].strip().rstrip(',')
                                # Update existing linkDynTempl
                                indentation = warehouse_lines[j][:len(warehouse_lines[j]) - len(warehouse_lines[j].lstrip())]
                                warehouse_lines[j] = f'{indentation}["linkDynTempl"] = {tpl["groupId"]},\n'
                                
                                # Update unlimited and initialAmount if they exist in the mapping
                                if "airport_options" in mapping and current_airport_id in mapping["airport_options"]:
                                    options = mapping["airport_options"][current_airport_id]
                                    print(f"    DEBUG: Looking for unlimited/initialAmount fields for {tpl['type']} at airport {current_airport_id}")
                                    
                                    # Look for unlimited and initialAmount in the next few lines
                                    found_unlimited = False
                                    found_initial_amount = False
                                    
                                    for k in range(j+1, min(j+15, len(warehouse_lines))):
                                        line_k = warehouse_lines[k].strip()
                                        print(f"      DEBUG: Line {k}: {line_k[:50]}...")
                                        
                                        if '["unlimited"]' in warehouse_lines[k] and '=' in warehouse_lines[k]:
                                            unlimited_val = "true" if options["unlimited"] else "false"
                                            old_val = line_k.split('=')[1].strip().rstrip(',') if '=' in line_k else "unknown"
                                            indentation_k = warehouse_lines[k][:len(warehouse_lines[k]) - len(warehouse_lines[k].lstrip())]
                                            warehouse_lines[k] = f'{indentation_k}["unlimited"] = {unlimited_val},\n'
                                            print(f"    DEBUG: Updated unlimited at line {k}: {old_val} → {unlimited_val}")
                                            found_unlimited = True
                                            
                                        elif '["initialAmount"]' in warehouse_lines[k] and '=' in warehouse_lines[k]:
                                            old_val = line_k.split('=')[1].strip().rstrip(',') if '=' in line_k else "unknown"
                                            indentation_k = warehouse_lines[k][:len(warehouse_lines[k]) - len(warehouse_lines[k].lstrip())]
                                            warehouse_lines[k] = f'{indentation_k}["initialAmount"] = {options["initialAmount"]},\n'
                                            print(f"    DEBUG: Updated initialAmount at line {k}: {old_val} → {options['initialAmount']}")
                                            found_initial_amount = True
                                            
                                        elif f'-- end of ["{tpl["type"]}"]' in warehouse_lines[k]:
                                            print(f"    DEBUG: Reached end of {tpl['type']} section at line {k}")
                                            break
                                    
                                    if not found_unlimited:
                                        print(f"    WARNING: unlimited field not found for {tpl['type']}")
                                    if not found_initial_amount:
                                        print(f"    WARNING: initialAmount field not found for {tpl['type']}")
                                
                                found_link = True
                                updates_made += 1
                                print(f"    DEBUG: Updated linkDynTempl at line {j}: {old_value} → {tpl['groupId']}")
                                break
                            
                            # Check if we've reached the end of this aircraft's section
                            if f'-- end of ["{tpl["type"]}"]' in warehouse_lines[j]:
                                # linkDynTempl doesn't exist, insert before closing brace
                                insert_line = j - 1
                                indentation = warehouse_lines[insert_line][:len(warehouse_lines[insert_line]) - len(warehouse_lines[insert_line].lstrip())]
                                warehouse_lines.insert(insert_line, f'{indentation}["linkDynTempl"] = {tpl["groupId"]},\n')
                                
                                # Also insert unlimited and initialAmount if specified
                                if "airport_options" in mapping and current_airport_id in mapping["airport_options"]:
                                    options = mapping["airport_options"][current_airport_id]
                                    unlimited_val = "true" if options["unlimited"] else "false"
                                    # Insert in reverse order to maintain correct line numbers
                                    warehouse_lines.insert(insert_line+1, f'{indentation}["initialAmount"] = {options["initialAmount"]},\n')
                                    warehouse_lines.insert(insert_line+1, f'{indentation}["unlimited"] = {unlimited_val},\n')
                                    print(f"    DEBUG: Inserted unlimited = {unlimited_val}, initialAmount = {options['initialAmount']}")
                                
                                found_link = True
                                updates_made += 1
                                print(f"    DEBUG: Inserted linkDynTempl at line {insert_line} = {tpl['groupId']}")
                                break
                            
                            j += 1
                        
                        if found_link:
                            # Mark this template as processed for this airport
                            processed_per_airport[current_airport_id].add(tpl["type"])
                            print(f"    DEBUG: Marked '{tpl['type']}' as processed for airport {current_airport_id}")
                        else:
                            print(f"    WARNING: Could not find linkDynTempl or end marker for '{tpl['type']}'")
            
            i += 1

        # Write the modified content back
        with open(self.warehouses_file, "w", encoding="utf-8") as f:
            f.writelines(warehouse_lines)
        
        print(f"DEBUG: Updated {updates_made} template links across all airbases")
    
    def update_aircraft_inventory_options(self):
        """Update unlimited and initialAmount for all aircraft types with user-specified options"""
        print(f"\nDEBUG: Starting aircraft inventory options update")
        
        with open(self.warehouses_file, encoding="utf-8") as f:
            warehouse_lines = f.readlines()

        # Build a comprehensive mapping of all user options for all airbases and aircraft types
        all_options = {}
        for airport_id in self.airbase_unlimited_vars:
            all_options[airport_id] = {}
            for aircraft_type in self.airbase_unlimited_vars[airport_id]:
                unlimited_val = self.airbase_unlimited_vars[airport_id][aircraft_type].get()
                amount_val = self.airbase_initial_amount_vars[airport_id][aircraft_type].get()
                
                try:
                    amount_int = int(amount_val) if amount_val.strip() else 100
                except ValueError:
                    amount_int = 100
                
                all_options[airport_id][aircraft_type] = {
                    "unlimited": unlimited_val,
                    "initialAmount": amount_int
                }
                print(f"  DEBUG: Airport {airport_id}, Aircraft {aircraft_type}: unlimited={unlimited_val}, amount={amount_int}")

        i = 0
        current_airport_id = None
        updates_made = 0

        while i < len(warehouse_lines):
            line = warehouse_lines[i]
            
            # Detect airport entry
            airport_id_match = re.search(r'^\s{0,20}\[(\d+)\]\s*=\s*$', line)
            if airport_id_match:
                current_airport_id = int(airport_id_match.group(1))
            
            # Process if this airport has user options
            if current_airport_id and current_airport_id in all_options:
                # Look for aircraft types that have user options
                for aircraft_type, options in all_options[current_airport_id].items():
                    aircraft_pattern = f'\\["{re.escape(aircraft_type)}"\\]\\s*='
                    if re.search(aircraft_pattern, line) and '-- end of' not in line:
                        print(f"  DEBUG: Found {aircraft_type} at airport {current_airport_id}, line {i}")
                        
                        # Look for unlimited and initialAmount in the next lines
                        for j in range(i+1, min(i+15, len(warehouse_lines))):
                            if '["unlimited"]' in warehouse_lines[j] and '=' in warehouse_lines[j]:
                                unlimited_val = "true" if options["unlimited"] else "false"
                                old_val = warehouse_lines[j].split('=')[1].strip().rstrip(',') if '=' in warehouse_lines[j] else "unknown"
                                indentation = warehouse_lines[j][:len(warehouse_lines[j]) - len(warehouse_lines[j].lstrip())]
                                warehouse_lines[j] = f'{indentation}["unlimited"] = {unlimited_val},\n'
                                print(f"    DEBUG: Updated unlimited: {old_val} → {unlimited_val}")
                                updates_made += 1
                                
                            elif '["initialAmount"]' in warehouse_lines[j] and '=' in warehouse_lines[j]:
                                old_val = warehouse_lines[j].split('=')[1].strip().rstrip(',') if '=' in warehouse_lines[j] else "unknown"
                                indentation = warehouse_lines[j][:len(warehouse_lines[j]) - len(warehouse_lines[j].lstrip())]
                                warehouse_lines[j] = f'{indentation}["initialAmount"] = {options["initialAmount"]},\n'
                                print(f"    DEBUG: Updated initialAmount: {old_val} → {options['initialAmount']}")
                                updates_made += 1
                                
                            elif f'-- end of ["{aircraft_type}"]' in warehouse_lines[j]:
                                break
            
            i += 1

        # Write the modified content back
        with open(self.warehouses_file, "w", encoding="utf-8") as f:
            f.writelines(warehouse_lines)
        
        print(f"DEBUG: Updated {updates_made} aircraft inventory options across all airbases")
    
    def open_github(self):
        """Open GitHub repository in web browser"""
        github_url = "https://github.com/sevenfifty777/DCS-Dynamic-Template-Manager"
        try:
            webbrowser.open(github_url)
        except Exception as e:
            messagebox.showerror("Error", f"Could not open GitHub link:\n{str(e)}")
    
    def open_discord(self):
        """Open Discord contact information"""
        messagebox.showinfo("Discord Contact", 
                           "You can reach me on Discord:\n\n"
                           "Username: vf142noeztiti\n\n"
                           "Feel free to send me a friend request or message!\n"
                           "I'm happy to help with questions or feedback.")
    
    def update_warehouse_dynspawn_options(self, selected_airports):
        """Update warehouse file with DynSpawn options for selected airports
        
        This method works differently from templates/coalitions:
        - It identifies airport sections by their ID
        - For each selected airport, it updates options within that airport's section only
        - Uses global regex replace within the airport section bounds
        """
        
        # Read the entire warehouses file
        with open(self.warehouses_file, encoding="utf-8") as f:
            warehouse_content = f.read()
        
        # Split into lines for processing
        warehouse_lines = warehouse_content.split('\n')
        
        update_count = 0
        
        # Process each selected airport
        for airport_id in selected_airports:
            if airport_id not in self.dynspawn_options:
                continue
                
            options = self.dynspawn_options[airport_id]
            
            # DEBUG: Print what options are set for this airport
            print(f"DEBUG: Airport ID {airport_id} options:")
            for key, var in options.items():
                print(f"  {key}: {var.get()}")
            
            # Find the start and end of this airport's section
            start_idx = None
            end_idx = None
            depth = 0
            
            for i, line in enumerate(warehouse_lines):
                # Look for airport ID entry (format: [12] = or [12] = {)
                if start_idx is None:
                    # Match either "[ID] = {" or just "[ID] ="
                    airport_match = re.search(r'\[\s*' + str(airport_id) + r'\s*\]\s*=', line)
                    if airport_match:
                        start_idx = i
                        # Check if the opening brace is on this line or the next
                        if '{' in line:
                            depth = 1
                        print(f"  Found start of airport section at line {i}")
                        continue
                
                # If we found the start but haven't counted the first brace yet
                if start_idx is not None and depth == 0:
                    if '{' in line:
                        depth = 1
                    continue
                
                # Track braces to find end of airport section
                if start_idx is not None and depth > 0:
                    depth += line.count('{') - line.count('}')
                    if depth == 0:
                        end_idx = i
                        print(f"  Found end of airport section at line {i}")
                        break
            
            if start_idx is None:
                print(f"  ERROR: Could not find start of airport {airport_id} section!")
            elif end_idx is None:
                print(f"  ERROR: Could not find end of airport {airport_id} section!")
            
            # If we found the airport section, update it
            if start_idx is not None and end_idx is not None:
                # Extract the airport section
                airport_section = '\n'.join(warehouse_lines[start_idx:end_idx+1])
                original_section = airport_section  # For comparison
                
                print(f"DEBUG: Found airport {airport_id} section (lines {start_idx}-{end_idx})")
                
                # Apply each option using the same method as the original script
                # Update dynamicSpawn
                if options['dynamicSpawn'].get():
                    before = airport_section.count('["dynamicSpawn"] = true')
                    airport_section = re.sub(r'\["dynamicSpawn"\] = false,', '["dynamicSpawn"] = true,', airport_section)
                    after = airport_section.count('["dynamicSpawn"] = true')
                    print(f"  dynamicSpawn: {before} -> {after} instances of 'true'")
                else:
                    airport_section = re.sub(r'\["dynamicSpawn"\] = true,', '["dynamicSpawn"] = false,', airport_section)
                
                # Update allowHotStart
                if options['allowHotStart'].get():
                    airport_section = re.sub(r'\["allowHotStart"\] = false,', '["allowHotStart"] = true,', airport_section)
                else:
                    airport_section = re.sub(r'\["allowHotStart"\] = true,', '["allowHotStart"] = false,', airport_section)
                
                # Update dynamicCargo
                if options['dynamicCargo'].get():
                    airport_section = re.sub(r'\["dynamicCargo"\] = false,', '["dynamicCargo"] = true,', airport_section)
                else:
                    airport_section = re.sub(r'\["dynamicCargo"\] = true,', '["dynamicCargo"] = false,', airport_section)
                
                # Update unlimitedMunitions
                if options['unlimitedMunitions'].get():
                    airport_section = re.sub(r'\["unlimitedMunitions"\] = false,', '["unlimitedMunitions"] = true,', airport_section)
                else:
                    airport_section = re.sub(r'\["unlimitedMunitions"\] = true,', '["unlimitedMunitions"] = false,', airport_section)
                
                # Update unlimitedAircrafts
                if options['unlimitedAircrafts'].get():
                    airport_section = re.sub(r'\["unlimitedAircrafts"\] = false,', '["unlimitedAircrafts"] = true,', airport_section)
                else:
                    airport_section = re.sub(r'\["unlimitedAircrafts"\] = true,', '["unlimitedAircrafts"] = false,', airport_section)
                
                # Update unlimitedFuel
                if options['unlimitedFuel'].get():
                    airport_section = re.sub(r'\["unlimitedFuel"\] = false,', '["unlimitedFuel"] = true,', airport_section)
                else:
                    airport_section = re.sub(r'\["unlimitedFuel"\] = true,', '["unlimitedFuel"] = false,', airport_section)
                
                # Count if anything changed
                if airport_section != original_section:
                    update_count += 1
                
                # Replace the section back into the lines
                updated_section_lines = airport_section.split('\n')
                warehouse_lines[start_idx:end_idx+1] = updated_section_lines
        
        # Write the modified content back
        with open(self.warehouses_file, "w", encoding="utf-8") as f:
            f.write('\n'.join(warehouse_lines))
        
        print(f"DEBUG: Updated DynSpawn options for {update_count} airports")
    
    def create_aircraft_inventory_for_templates(self, selected_airports):
        """Copy complete aircraft inventory from reference file to selected airports
        
        This replaces empty ["aircrafts"] = {} with full inventory from aircraft_inventory.lua.
        All linkDynTempl values are set to 0 initially, Step 2 will link templates.
        """
        
        # Read the reference inventory from aircraft_inventory.lua file
        # The file is in the same directory as the script/executable
        # Use sys to handle both script and PyInstaller executable scenarios
        if getattr(sys, 'frozen', False):
            # Running as compiled executable
            script_dir = os.path.dirname(sys.executable)
        else:
            # Running as script
            script_dir = os.path.dirname(os.path.abspath(__file__))
        
        inventory_file = os.path.join(script_dir, 'aircraft_inventory.lua')
        
        if not os.path.exists(inventory_file):
            print(f"ERROR: Reference inventory file not found: {inventory_file}")
            return 0
        
        print(f"DEBUG: Loading reference inventory from: {inventory_file}")
        
        with open(inventory_file, encoding="utf-8") as f:
            reference_inventory = f.read().split('\n')
        
        print(f"DEBUG: Loaded reference inventory from aircraft_inventory.lua ({len(reference_inventory)} lines)")
        
        # Reset all linkDynTempl values to 0 in reference
        reference_inventory_reset = []
        for line in reference_inventory:
            if '["linkDynTempl"]' in line:
                # Replace any linkDynTempl value with 0
                line = re.sub(r'(\["linkDynTempl"\]\s*=\s*)\d+', r'\g<1>0', line)
            reference_inventory_reset.append(line)
        
        # Read the warehouses file
        with open(self.warehouses_file, encoding="utf-8") as f:
            warehouse_content = f.read()
            warehouse_lines = warehouse_content.split('\n')
        
        added_count = 0
        
        # Process each selected airport
        for airport_id in selected_airports:
            # Only add inventory for airports with dynamicSpawn enabled
            if airport_id not in self.dynspawn_options:
                continue
            if not self.dynspawn_options[airport_id]['dynamicSpawn'].get():
                continue
            
            print(f"DEBUG: Creating aircraft inventory for airport {airport_id}")
            
            # Find the aircrafts section for this airport
            i = 0
            found_airport = False
            aircrafts_line = None
            aircrafts_end_line = None
            
            while i < len(warehouse_lines):
                # Look for this airport's section
                if f'[{airport_id}] =' in warehouse_lines[i]:
                    found_airport = True
                
                # If in this airport, find the ["aircrafts"] = line
                if found_airport and '["aircrafts"]' in warehouse_lines[i] and '=' in warehouse_lines[i]:
                    aircrafts_line = i
                    # Check if it's empty {}
                    if '{}' in warehouse_lines[i]:
                        aircrafts_end_line = i
                    elif i+1 < len(warehouse_lines) and '{}' in warehouse_lines[i+1]:
                        aircrafts_end_line = i+1
                    else:
                        # Not empty, find end
                        for j in range(i+1, len(warehouse_lines)):
                            if '}, -- end of ["aircrafts"]' in warehouse_lines[j]:
                                aircrafts_end_line = j
                                break
                    break
                
                # Stop if we've moved to the next airport
                if found_airport and re.search(r'\[\d+\] =', warehouse_lines[i]) and f'[{airport_id}]' not in warehouse_lines[i]:
                    break
                
                i += 1
            
            if aircrafts_line is None:
                print(f"  WARNING: Could not find aircrafts section for airport {airport_id}")
                continue
            
            # Check if aircrafts section is empty: ["aircrafts"] = {},
            is_empty = '{}' in warehouse_lines[aircrafts_line] or (aircrafts_line + 1 < len(warehouse_lines) and '{}' in warehouse_lines[aircrafts_line + 1])
            
            if is_empty:
                print(f"  Aircrafts section is empty, copying reference inventory...")
                
                # Get the indentation of current airport
                base_indent = warehouse_lines[aircrafts_line][:len(warehouse_lines[aircrafts_line]) - len(warehouse_lines[aircrafts_line].lstrip())]
                
                # Determine if base indent uses tabs or spaces
                uses_tabs = '\t' in base_indent
                indent_char = '\t' if uses_tabs else '    '  # 4 spaces per tab
                
                print(f"  Base indentation: {repr(base_indent)}, uses_tabs={uses_tabs}")
                
                # Get reference indentation (from first line of aircraft_inventory.lua)
                ref_first_line = reference_inventory_reset[0]
                ref_indent = ref_first_line[:len(ref_first_line) - len(ref_first_line.lstrip())]
                
                # Count indent levels in reference (spaces or tabs)
                if ' ' in ref_indent and '\t' not in ref_indent:
                    # Reference uses spaces - count spaces divided by 4
                    ref_base_level = len(ref_indent) // 4
                else:
                    # Reference uses tabs or mixed - count tabs
                    ref_base_level = ref_indent.count('\t')
                
                # Count base level in target
                if uses_tabs:
                    base_level = base_indent.count('\t')
                else:
                    base_level = len(base_indent) // 4
                
                print(f"  Reference base level: {ref_base_level}, Target base level: {base_level}")
                
                # Adjust indentation of reference to match this airport
                adjusted_inventory = []
                for line in reference_inventory_reset:
                    if line.strip():  # Non-empty line
                        # Get current line's indent
                        line_indent = line[:len(line) - len(line.lstrip())]
                        
                        # Count indent level (tabs or spaces)
                        if '\t' in line_indent:
                            line_level = line_indent.count('\t')
                        else:
                            line_level = len(line_indent) // 4
                        
                        # Calculate relative level from reference base
                        relative_level = line_level - ref_base_level
                        
                        # Apply to target base level
                        target_level = base_level + relative_level
                        
                        # Build new indent with target character
                        new_indent = indent_char * target_level
                        
                        # Replace indent and keep rest of line
                        adjusted_line = new_indent + line.lstrip()
                        adjusted_inventory.append(adjusted_line)
                    else:
                        adjusted_inventory.append(line)
                
                # Replace empty {} with full inventory
                if '{}' in warehouse_lines[aircrafts_line]:
                    # ["aircrafts"] = {},
                    warehouse_lines[aircrafts_line:aircrafts_line+1] = adjusted_inventory
                else:
                    # ["aircrafts"] =
                    # {},
                    warehouse_lines[aircrafts_line:aircrafts_line+2] = adjusted_inventory
                
                added_count += 1
                print(f"  Copied complete aircraft inventory to airport {airport_id}")
            else:
                print(f"  Airport {airport_id} already has aircraft inventory, skipping")
        
        # Write back the modified content
        with open(self.warehouses_file, "w", encoding="utf-8") as f:
            f.write('\n'.join(warehouse_lines))
        
        print(f"DEBUG: Copied complete inventory to {added_count} airports")
        return added_count
    
    def update_warehouse_coalitions(self, selected_airports):
        """Update warehouse file with coalition changes for selected airports"""
        
        # Read the warehouses file
        with open(self.warehouses_file, encoding="utf-8") as f:
            warehouse_lines = f.readlines()
        
        i = 0
        current_airport_id = None
        in_selected_airport = False
        updates_made = 0
        
        while i < len(warehouse_lines):
            line = warehouse_lines[i]
            
            # Detect airport entry (match with or without brace on same line)
            airport_id_match = re.search(r'\[\s*(\d+)\s*\]\s*=', line)
            if airport_id_match:
                current_airport_id = int(airport_id_match.group(1))
                in_selected_airport = (current_airport_id in selected_airports)
                if in_selected_airport:
                    print(f"DEBUG: Found selected airport {current_airport_id} for coalition update")
            
            # Process coalition line if inside a selected airport
            if in_selected_airport and current_airport_id in self.coalition_vars:
                if '["coalition"]' in line and '=' in line:
                    desired_coalition = self.coalition_vars[current_airport_id].get()
                    print(f"DEBUG: Updating airport {current_airport_id} coalition to {desired_coalition}")
                    # Replace the coalition value, preserving indentation and format
                    new_line = re.sub(
                        r'(\["coalition"\]\s*=\s*")[^"]*(")',
                        f'\\1{desired_coalition}\\2',
                        line
                    )
                    if new_line != line:
                        warehouse_lines[i] = new_line
                        updates_made += 1
            
            i += 1
        
        # Write the modified content back
        with open(self.warehouses_file, "w", encoding="utf-8") as f:
            f.writelines(warehouse_lines)
        
        print(f"DEBUG: Updated {updates_made} coalition assignments")
    
    def enable_dynspawn_templates_in_mission(self):
        """Enable dynSpawnTemplate for all aircraft groups with '_DynTemp' suffix in their name
        
        This searches through the mission file for groups with _DynTemp suffix,
        then looks BACKWARDS to find and enable their dynSpawnTemplate flag.
        """
        
        # Read the mission file
        with open(self.mission_file, encoding="utf-8") as f:
            mission_lines = f.readlines()
        
        updates_made = 0
        
        # First pass: Find all group names with _DynTemp suffix
        dyntemp_groups = []
        for i, line in enumerate(mission_lines):
            if '["name"]' in line and '=' in line and '_DynTemp' in line:
                name_match = re.search(r'\["name"\]\s*=\s*"([^"]+)"', line)
                if name_match:
                    group_name = name_match.group(1)
                    if '_DynTemp' in group_name:
                        dyntemp_groups.append((i, group_name))
                        print(f"DEBUG: Found DynTemp group '{group_name}' at line {i}")
        
        print(f"DEBUG: Found {len(dyntemp_groups)} groups with _DynTemp suffix")
        
        # Second pass: For each group, search backwards to find dynSpawnTemplate
        for name_line, group_name in dyntemp_groups:
            # Search backwards from the name line (up to 500 lines back)
            for i in range(name_line - 1, max(0, name_line - 500), -1):
                if '["dynSpawnTemplate"]' in mission_lines[i]:
                    # Check if it's set to false and update to true
                    if '= false' in mission_lines[i]:
                        # Replace false with true, preserving indentation
                        mission_lines[i] = re.sub(
                            r'(\["dynSpawnTemplate"\]\s*=\s*)false',
                            r'\1true',
                            mission_lines[i]
                        )
                        updates_made += 1
                        print(f"DEBUG: Enabled dynSpawnTemplate at line {i} for group: {group_name}")
                    elif '= true' in mission_lines[i]:
                        print(f"DEBUG: dynSpawnTemplate already true at line {i} for group: {group_name}")
                    
                    # Found it, stop searching backwards for this group
                    break
        
        # Write the modified content back
        with open(self.mission_file, "w", encoding="utf-8") as f:
            f.writelines(mission_lines)
        
        print(f"DEBUG: Enabled dynSpawnTemplate for {updates_made} aircraft groups with '_DynTemp' suffix")
        return updates_made
        
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = MergedDynamicTemplateManager()
    app.run()
