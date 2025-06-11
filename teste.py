import tkinter as tk
from tkinter import messagebox, ttk, simpledialog, filedialog
import os
import subprocess
import shutil
import json

class THLModLoader:
    def __init__(self, root):
        self.root = root
        self.root.title("The Hundred Line Mod Loader")
        self.root.geometry("600x400")
        self.root.configure(bg="#2b2b2b")  # Dark background

        # Create main directories if they don't exist
        self.mods_dir = "Mods"
        self.original_files_dir = "Original_Files"
        self.thl_tools_dir = "THL-Tools"
        self.output_dir = "Output"
        self.create_directories()

        # Variables
        self.platform_var = tk.StringVar(value="PC")
        self.selected_mod = tk.StringVar(value="No mod selected")
        self.game_path = tk.StringVar(value="Not set")
        self.pack_pc_button = None  # Will be initialized in create_gui
        self.config_file = "config.json"

        # Load saved game path
        self.load_game_path()

        # Apply dark theme
        self.apply_dark_theme()

        # GUI Elements
        self.create_gui()

    def create_directories(self):
        """Create necessary directories if they don't exist."""
        for directory in [self.mods_dir, self.original_files_dir, self.thl_tools_dir, self.output_dir]:
            if not os.path.exists(directory):
                os.makedirs(directory)

    def apply_dark_theme(self):
        """Configure dark theme for the GUI."""
        style = ttk.Style()
        style.theme_use("clam")  # Use clam theme for customization

        # Configure styles
        style.configure("TLabel", background="#2b2b2b", foreground="#ffffff", font=("Arial", 10))
        style.configure("TButton", background="#4a4a4a", foreground="#ffffff", font=("Arial", 10), padding=5)
        style.map("TButton", background=[("active", "#5a5a5a")])
        style.configure("TRadiobutton", background="#2b2b2b", foreground="#ffffff", font=("Arial", 10))
        style.map("TRadiobutton", background=[("active", "#2b2b2b")])
        style.configure("TFrame", background="#2b2b2b")

        # Listbox styling (not ttk, so handled separately)
        self.root.option_add("*Listbox.background", "#3c3f41")
        self.root.option_add("*Listbox.foreground", "#ffffff")
        self.root.option_add("*Listbox.selectBackground", "#0078d7")
        self.root.option_add("*Listbox.selectForeground", "#ffffff")

    def load_game_path(self):
        """Load the game path from config.json if it exists."""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, "r") as f:
                    config = json.load(f)
                    game_path = config.get("game_path", "Not set")
                    if game_path and os.path.exists(os.path.join(game_path, "gamedata")):
                        self.game_path.set(game_path)
        except (json.JSONDecodeError, IOError):
            pass  # Silently ignore invalid or inaccessible config

    def save_game_path(self):
        """Save the game path to config.json."""
        config = {"game_path": self.game_path.get()}
        try:
            with open(self.config_file, "w") as f:
                json.dump(config, f, indent=4)
        except IOError:
            messagebox.showerror("Error", "Failed to save game path to config file!")

    def create_gui(self):
        """Set up the main GUI elements."""
        # Selected Mod Label
        self.selected_mod_label = ttk.Label(self.root, textvariable=self.selected_mod, font=("Arial", 12, "bold"))
        self.selected_mod_label.pack(pady=10)

        # Game Path Frame
        self.game_path_frame = ttk.Frame(self.root)
        self.game_path_frame.pack(pady=5, padx=10, fill=tk.X)
        ttk.Label(self.game_path_frame, text="Game Path:").pack(side=tk.LEFT, padx=5)
        ttk.Label(self.game_path_frame, textvariable=self.game_path).pack(side=tk.LEFT, padx=5)
        ttk.Button(self.game_path_frame, text="Set Game Path", command=self.set_game_path).pack(side=tk.LEFT, padx=5)

        # Mod List Frame
        self.mod_list_frame = ttk.Frame(self.root)
        self.mod_list_frame.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

        self.mod_listbox = tk.Listbox(self.mod_list_frame, height=10, selectmode=tk.SINGLE, exportselection=False, font=("Arial", 10))
        self.mod_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        self.mod_listbox.bind('<<ListboxSelect>>', self.update_selected_mod)

        scrollbar = ttk.Scrollbar(self.mod_list_frame, orient=tk.VERTICAL, command=self.mod_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.mod_listbox.config(yscrollcommand=scrollbar.set)

        # Platform Selection Frame
        self.platform_frame = ttk.Frame(self.root)
        self.platform_frame.pack(pady=5, padx=10, fill=tk.X)
        ttk.Label(self.platform_frame, text="Platform:").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(self.platform_frame, text="PC (.dx11)", variable=self.platform_var, value="PC", command=self.update_pack_pc_button).pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(self.platform_frame, text="Switch (.nx64)", variable=self.platform_var, value="Switch", command=self.update_pack_pc_button).pack(side=tk.LEFT, padx=10)

        # Buttons Frame
        self.button_frame = ttk.Frame(self.root)
        self.button_frame.pack(pady=15, padx=10, fill=tk.X)
        ttk.Button(self.button_frame, text="Create New Mod", command=self.create_new_mod).pack(side=tk.LEFT, padx=5)
        ttk.Button(self.button_frame, text="Extract MVGL Files", command=self.extract_mvgl_files).pack(side=tk.LEFT, padx=5)
        ttk.Button(self.button_frame, text="Pack Mods", command=self.pack_mods).pack(side=tk.LEFT, padx=5)
        self.pack_pc_button = ttk.Button(self.button_frame, text="Pack Mods (PC Only)", command=self.pack_mods_pc, state=tk.NORMAL)
        self.pack_pc_button.pack(side=tk.LEFT, padx=5)

        # Refresh mod list
        self.refresh_mod_list()

    def update_selected_mod(self, event):
        """Update the selected mod label when a mod is selected."""
        selection = self.mod_listbox.curselection()
        if selection:
            mod_name = self.mod_listbox.get(selection[0])
            self.selected_mod.set(f"Selected Mod: {mod_name}")
        else:
            self.selected_mod.set("No mod selected")

    def update_pack_pc_button(self):
        """Enable or disable the Pack Mods (PC Only) button based on platform."""
        if self.platform_var.get() == "PC":
            self.pack_pc_button.config(state=tk.NORMAL)
        else:
            self.pack_pc_button.config(state=tk.DISABLED)

    def set_game_path(self):
        """Prompt user to select the game installation directory."""
        path = filedialog.askdirectory(title="Select Game Directory", parent=self.root)
        if path:
            gamedata_path = os.path.join(path, "gamedata")
            if os.path.exists(gamedata_path):
                self.game_path.set(path)
                self.save_game_path()
            else:
                messagebox.showerror("Error", "Selected directory does not contain a 'gamedata' folder!")

    def refresh_mod_list(self):
        """Update the mod listbox with current mods."""
        self.mod_listbox.delete(0, tk.END)
        if os.path.exists(self.mods_dir):
            for mod in os.listdir(self.mods_dir):
                if os.path.isdir(os.path.join(self.mods_dir, mod)):
                    self.mod_listbox.insert(tk.END, mod)

    def create_new_mod(self):
        """Create a new mod folder with required subfolders."""
        mod_name = simpledialog.askstring("Input", "Enter mod name:", parent=self.root)
        if mod_name:
            mod_path = os.path.join(self.mods_dir, mod_name)
            if os.path.exists(mod_path):
                messagebox.showerror("Error", f"Mod '{mod_name}' already exists!")
                return

            # Create mod folder and subfolders
            os.makedirs(mod_path)
            subfolders = [
                "patch_0",  # Original/Japanese
                "patch_1",  # English
                "patch_2",  # Simplified Chinese
                "patch_3",  # Traditional Chinese
                "patch_text00",
                "patch_text01",
                "patch_text02",
                "patch_text03"
            ]
            for folder in subfolders:
                os.makedirs(os.path.join(mod_path, folder))

            self.refresh_mod_list()
            messagebox.showinfo("Success", f"Mod '{mod_name}' created successfully!")

    def extract_mvgl_files(self):
        """Extract .mvgl files using THL-Tools.exe, removing platform extensions."""
        thl_tools_exe = os.path.join(self.thl_tools_dir, "THL-Tools.exe")
        if not os.path.exists(thl_tools_exe):
            messagebox.showerror("Error", "THL-Tools.exe not found in THL-Tools directory!")
            return

        if not os.path.exists(self.original_files_dir):
            messagebox.showerror("Error", "Original_Files directory not found!")
            return

        mvgl_files = [f for f in os.listdir(self.original_files_dir) if f.endswith((".dx11.mvgl", ".nx64.mvgl"))]
        if not mvgl_files:
            messagebox.showerror("Error", "No .mvgl files found in Original_Files directory!")
            return

        for mvgl_file in mvgl_files:
            # Remove platform extension (.dx11 or .nx64) from the file name
            base_name = mvgl_file.replace(".dx11", "").replace(".nx64", "")
            file_name = os.path.splitext(base_name)[0]
            output_dir = os.path.join(self.original_files_dir, file_name)
            command = [thl_tools_exe, "extract", os.path.join(self.original_files_dir, mvgl_file), output_dir]
            try:
                subprocess.run(command, check=True, capture_output=True, text=True)
            except subprocess.CalledProcessError as e:
                messagebox.showerror("Error", f"Failed to extract {mvgl_file}: {e.stderr}")
                return

        messagebox.showinfo("Success", "All .mvgl files extracted successfully!")

    def has_files(self, directory):
        """Recursively check if a directory contains any files."""
        for root, _, files in os.walk(directory):
            if files:
                return True
        return False

    def copy_files_preserve_existing(self, src_dir, dst_dir):
        """Copy files from src_dir to dst_dir, preserving existing files in dst_dir unless overwritten."""
        for root, dirs, files in os.walk(src_dir):
            # Calculate relative path from src_dir
            rel_path = os.path.relpath(root, src_dir)
            dst_root = os.path.join(dst_dir, rel_path)

            # Create destination directories if they don't exist
            if not os.path.exists(dst_root):
                os.makedirs(dst_root)

            # Copy files
            for file in files:
                src_file = os.path.join(root, file)
                dst_file = os.path.join(dst_root, file)
                shutil.copy2(src_file, dst_file)  # Copy file, overwriting if it exists

    def move_to_gamedata(self, output_file):
        """Move the output .mvgl file to the game's gamedata folder if set."""
        if self.game_path.get() == "Not set":
            return

        gamedata_path = os.path.join(self.game_path.get(), "gamedata")
        if not os.path.exists(gamedata_path):
            messagebox.showerror("Error", f"Game data path '{gamedata_path}' not found!")
            return

        dst_file = os.path.join(gamedata_path, os.path.basename(output_file))
        shutil.copy2(output_file, dst_file)

    def pack_mods(self, platform="both"):
        """Copy files from matching mod subfolders to Original_Files and pack them into .mvgl files."""
        thl_tools_exe = os.path.join(self.thl_tools_dir, "THL-Tools.exe")
        if not os.path.exists(thl_tools_exe):
            messagebox.showerror("Error", "THL-Tools.exe not found in THL-Tools directory!")
            return

        selected_mod = self.mod_listbox.get(tk.ACTIVE)
        if not selected_mod:
            messagebox.showerror("Error", "Please select a mod from the list!")
            return

        mod_path = os.path.join(self.mods_dir, selected_mod)
        if not os.path.exists(mod_path):
            messagebox.showerror("Error", f"Mod '{selected_mod}' directory not found!")
            return

        # Get platform extension
        if platform == "pc":
            if self.platform_var.get() != "PC":
                messagebox.showerror("Error", "PC Only packing requires PC platform to be selected!")
                return
            platform_ext = ".dx11"
        else:
            platform_ext = ".dx11" if self.platform_var.get() == "PC" else ".nx64"

        # Get list of folders in Original_Files
        extracted_folders = [f for f in os.listdir(self.original_files_dir)
                           if os.path.isdir(os.path.join(self.original_files_dir, f))]
        if not extracted_folders:
            messagebox.showerror("Error", "No folders found in Original_Files!")
            return

        # Get list of mod subfolders
        mod_subfolders = [f for f in os.listdir(mod_path)
                         if os.path.isdir(os.path.join(mod_path, f))]

        # Find matching folders
        matching_folders = [f for f in mod_subfolders if f in extracted_folders]
        if not matching_folders:
            messagebox.showerror("Error", "No matching folders found between mod and Original_Files!")
            return

        # Process matching folders with files
        packed_files = []
        for folder in matching_folders:
            src_path = os.path.join(mod_path, folder)
            if not self.has_files(src_path):
                continue  # Skip folders with no files

            dst_path = os.path.join(self.original_files_dir, folder)
            self.copy_files_preserve_existing(src_path, dst_path)

            # Pack the folder into a .mvgl file
            output_file = os.path.join(self.output_dir, f"{folder}{platform_ext}.mvgl")
            command = [thl_tools_exe, "pack", dst_path, output_file]
            try:
                subprocess.run(command, check=True, capture_output=True, text=True)
                packed_files.append(output_file)
            except subprocess.CalledProcessError as e:
                messagebox.showerror("Error", f"Failed to pack {folder}: {e.stderr}")
                return

        if not packed_files:
            messagebox.showerror("Error", "No folders with files were packed!")
            return

        # Move packed files to gamedata if game path is set
        for output_file in packed_files:
            self.move_to_gamedata(output_file)

        messagebox.showinfo("Success", f"Mod '{selected_mod}' packed successfully for {self.platform_var.get()}!")

    def pack_mods_pc(self):
        """Pack mods specifically for PC platform."""
        self.pack_mods(platform="pc")

def main():
    root = tk.Tk()
    app = THLModLoader(root)
    root.mainloop()

if __name__ == "__main__":
    main()