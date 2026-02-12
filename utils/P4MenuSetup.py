"""
P4 Context Menu Setup Tool
A simple Qt-based installer for the "Show in P4" context menu feature in Unreal Engine 5
"""

import sys
import os
import subprocess
import shutil
from pathlib import Path


def install_qt_dependency():
    """Automatically install Qt dependencies if not available"""
    print("Checking Qt dependencies...")
    
    # Try PySide6 first
    try:
        import PySide6
        print("✓ PySide6 already installed")
        return True
    except ImportError:
        pass
    
    # Try PyQt5
    try:
        import PyQt5
        print("✓ PyQt5 already installed")
        return True
    except ImportError:
        pass
    
    # Neither installed, install PySide6
    print("Qt library not found. Installing PySide6...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--quiet", "PySide6"])
        print("✓ PySide6 installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to install PySide6: {e}")
        print("\nPlease install manually:")
        print("  pip install PySide6")
        print("  or")
        print("  pip install PyQt5")
        return False


# Install dependencies before importing Qt
if not install_qt_dependency():
    sys.exit(1)


# Now import Qt libraries
try:
    from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                                   QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                                   QTextEdit, QFileDialog, QMessageBox, QComboBox)
    from PySide6.QtCore import Qt
    from PySide6.QtGui import QFont
    QMessageBox_Yes = QMessageBox.StandardButton.Yes
    QMessageBox_No = QMessageBox.StandardButton.No
except ImportError:
    from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                                 QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                                 QTextEdit, QFileDialog, QMessageBox, QComboBox)
    from PyQt5.QtCore import Qt
    from PyQt5.QtGui import QFont
    QMessageBox_Yes = QMessageBox.Yes
    QMessageBox_No = QMessageBox.No


class P4MenuSetupWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("P4 Context Menu Setup")
        self.setFixedSize(500, 400)
        
        # Initialize variables
        self.project_root = None
        self.workspace_root = None
        self.available_workspaces = []
        
        # Initialize UI first
        self.init_ui()
        
        # Then detect project and workspaces
        self.project_root = self.detect_project_root()
        self.project_label.setText(self.project_root or "Not detected")
        self.load_available_workspaces()
        
        # If project wasn't found from script location, try workspace
        if not self.project_root and self.available_workspaces:
            # Try first workspace
            first_workspace = self.available_workspaces[0]['root']
            self.find_project_in_workspace(first_workspace)
        
        self.auto_detect_workspace()
    
    def init_ui(self):
        """Initialize the user interface"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Title
        title = QLabel("P4 Context Menu Setup")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        # Project root display
        layout.addWidget(QLabel("Unreal Project:"))
        project_layout = QHBoxLayout()
        self.project_label = QLabel("Detecting...")
        self.project_label.setStyleSheet("background-color: #f0f0f0; padding: 5px; border-radius: 3px;")
        project_layout.addWidget(self.project_label)
        
        browse_project_btn = QPushButton("Browse")
        browse_project_btn.clicked.connect(self.browse_project)
        browse_project_btn.setMaximumWidth(80)
        project_layout.addWidget(browse_project_btn)
        layout.addLayout(project_layout)
        
        # Workspace directory with dropdown
        layout.addWidget(QLabel("P4 Workspace:"))
        workspace_layout = QHBoxLayout()
        
        self.workspace_combo = QComboBox()
        self.workspace_combo.setEditable(True)
        self.workspace_combo.setPlaceholderText("Loading workspaces...")
        self.workspace_combo.currentTextChanged.connect(self.on_workspace_selected)
        workspace_layout.addWidget(self.workspace_combo)
        
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.load_available_workspaces)
        refresh_btn.setMaximumWidth(80)
        workspace_layout.addWidget(refresh_btn)
        
        browse_btn = QPushButton("Browse")
        browse_btn.clicked.connect(self.browse_workspace)
        browse_btn.setMaximumWidth(80)
        workspace_layout.addWidget(browse_btn)
        layout.addLayout(workspace_layout)
        
        # Status/Log area
        layout.addWidget(QLabel("Status:"))
        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        self.log_area.setMaximumHeight(150)
        self.log_area.setStyleSheet("background-color: #2b2b2b; color: #d4d4d4; font-family: Consolas, monospace;")
        layout.addWidget(self.log_area)
        
        # Install button
        self.install_btn = QPushButton("Install P4 Context Menu")
        self.install_btn.clicked.connect(self.install)
        self.install_btn.setStyleSheet("""
            QPushButton {
                background-color: #0e639c;
                color: white;
                padding: 10px;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #1177bb;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)
        layout.addWidget(self.install_btn)
        
        self.log("Ready to install...")
    
    def detect_project_root(self):
        """Detect the Unreal project root directory"""
        # Start from current script location
        current_dir = Path(__file__).resolve().parent
        
        # Search upward for .uproject file
        for parent in [current_dir] + list(current_dir.parents):
            uproject_files = list(parent.glob("*.uproject"))
            if uproject_files:
                self.log(f"✓ Found Unreal project: {parent}")
                return str(parent)
        
        self.log("⚠ Could not auto-detect project root")
        return None
    
    def load_available_workspaces(self):
        """Load all available P4 workspaces and populate dropdown"""
        self.log("Loading P4 workspaces...")
        self.workspace_combo.clear()
        self.available_workspaces = []
        
        try:
            # Get current user
            user_result = subprocess.run(
                ['p4', 'info'],
                capture_output=True,
                text=True,
                timeout=10,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )
            
            current_user = None
            if user_result.returncode == 0:
                for line in user_result.stdout.splitlines():
                    if line.lower().startswith('user name:') or line.lower().startswith('client name:'):
                        if 'user name' in line.lower():
                            current_user = line.split(':', 1)[1].strip()
                            break
            
            # Get list of clients/workspaces
            clients_result = subprocess.run(
                ['p4', 'clients', '-u', current_user] if current_user else ['p4', 'clients'],
                capture_output=True,
                text=True,
                timeout=10,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )
            
            if clients_result.returncode == 0:
                # Parse client list
                for line in clients_result.stdout.splitlines():
                    if line.startswith('Client '):
                        # Format: "Client <name> <date> root <root_path> '<description>'"
                        parts = line.split()
                        if len(parts) >= 5 and 'root' in parts:
                            client_name = parts[1]
                            root_idx = parts.index('root') + 1
                            if root_idx < len(parts):
                                root_path = parts[root_idx]
                                # Normalize path
                                root_path = os.path.normpath(root_path)
                                self.available_workspaces.append({
                                    'name': client_name,
                                    'root': root_path
                                })
                                # Add to dropdown
                                self.workspace_combo.addItem(f"{client_name} ({root_path})", root_path)
                
                if self.available_workspaces:
                    self.log(f"✓ Found {len(self.available_workspaces)} workspace(s)")
                else:
                    self.log("⚠ No workspaces found")
                    # Add manual entry option
                    if self.project_root:
                        self.workspace_combo.addItem(f"Manual: {self.project_root}", self.project_root)
            else:
                self.log(f"⚠ Could not list workspaces: {clients_result.stderr[:200]}")
                if self.project_root:
                    self.workspace_combo.addItem(f"Manual: {self.project_root}", self.project_root)
                    
        except FileNotFoundError:
            self.log("⚠ P4 command not found")
            if self.project_root:
                self.workspace_combo.addItem(f"Manual: {self.project_root}", self.project_root)
        except Exception as e:
            self.log(f"⚠ Error loading workspaces: {str(e)}")
            if self.project_root:
                self.workspace_combo.addItem(f"Manual: {self.project_root}", self.project_root)
    
    def on_workspace_selected(self, text):
        """Handle workspace selection from dropdown"""
        # Get the data (root path) associated with the selected item
        index = self.workspace_combo.currentIndex()
        if index >= 0:
            root_path = self.workspace_combo.itemData(index)
            if root_path:
                self.workspace_root = root_path
                self.log(f"Selected workspace: {root_path}")
                # Try to find Unreal project in the workspace
                self.find_project_in_workspace(root_path)
    
    def find_project_in_workspace(self, workspace_path):
        """Search for Unreal project files within the workspace"""
        self.log(f"Searching for Unreal projects in workspace...")
        
        try:
            workspace_dir = Path(workspace_path)
            if not workspace_dir.exists():
                self.log(f"⚠ Workspace path does not exist: {workspace_path}")
                return
            
            # Search for .uproject files (limit depth to avoid long searches)
            uproject_files = []
            
            # Search up to 3 levels deep
            for depth in range(3):
                pattern = "**/" * depth + "*.uproject"
                found = list(workspace_dir.glob(pattern))
                uproject_files.extend(found)
                if found:
                    break  # Stop at first level where we find projects
            
            if uproject_files:
                # Use the first project found
                project_path = uproject_files[0].parent
                self.project_root = str(project_path)
                self.project_label.setText(str(project_path))
                self.log(f"✓ Found Unreal project: {project_path}")
                
                if len(uproject_files) > 1:
                    self.log(f"ℹ Found {len(uproject_files)} projects, using: {uproject_files[0].name}")
            else:
                self.log(f"⚠ No .uproject files found in workspace")
                self.log(f"Please use the Browse button to select your project folder")
                
        except Exception as e:
            self.log(f"⚠ Error searching workspace: {str(e)}")
    
    def auto_detect_workspace(self):
        """Auto-detect P4 workspace root"""
        if not self.project_root:
            self.log("⚠ No project root set, cannot detect workspace")
            return
        
        self.log("Detecting P4 workspace...")
        
        try:
            # Method 1: Try p4 info command
            result = subprocess.run(
                ['p4', 'info'],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=10,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )
            
            if result.returncode == 0:
                self.log(f"P4 info output:\n{result.stdout[:500]}")
                
                # Try different possible field names
                for line in result.stdout.splitlines():
                    line_lower = line.lower()
                    # Match: "Client root:", "Client Root:", "client root:", etc.
                    if 'client root' in line_lower and ':' in line:
                        workspace_root = line.split(':', 1)[1].strip()
                        # Remove any trailing slashes and convert to proper path
                        workspace_root = os.path.normpath(workspace_root)
                        
                        if workspace_root and workspace_root != '.':
                            self.workspace_root = workspace_root
                            # Try to select it in the combo box
                            self.select_workspace_in_combo(workspace_root)
                            self.log(f"✓ Auto-detected workspace: {workspace_root}")
                            return
            else:
                self.log(f"P4 info returned error code {result.returncode}")
                if result.stderr:
                    self.log(f"Error: {result.stderr[:200]}")
            
            # Method 2: Try to find P4CONFIG file
            self.log("Trying P4CONFIG method...")
            p4config_name = os.environ.get('P4CONFIG', '.p4config')
            current = Path(self.project_root)
            
            for parent in [current] + list(current.parents):
                p4config_path = parent / p4config_name
                if p4config_path.exists():
                    self.workspace_root = str(parent)
                    self.select_workspace_in_combo(str(parent))
                    self.log(f"✓ Found P4CONFIG at: {parent}")
                    self.log(f"✓ Using workspace: {parent}")
                    return
            
            # Method 3: Use project root as fallback
            self.log("Using project root as workspace fallback")
            self.workspace_root = self.project_root
            self.select_workspace_in_combo(self.project_root)
            self.log(f"⚠ Using project root as workspace: {self.project_root}")
            self.log("Please verify this is correct or select from dropdown.")
            
        except FileNotFoundError:
            self.log("⚠ P4 command not found. Please ensure Perforce is installed and in PATH.")
            self.log(f"Using project root as workspace: {self.project_root}")
            self.workspace_root = self.project_root
            self.select_workspace_in_combo(self.project_root)
        except Exception as e:
            self.log(f"⚠ P4 detection failed: {str(e)}")
            self.log(f"Using project root as workspace: {self.project_root}")
            self.workspace_root = self.project_root
            self.select_workspace_in_combo(self.project_root)
    
    def select_workspace_in_combo(self, workspace_path):
        """Select a workspace in the combo box by its path"""
        if not workspace_path:
            return
        
        # Normalize the path for comparison
        workspace_path = os.path.normpath(workspace_path)
        
        # Try to find and select the matching workspace
        for i in range(self.workspace_combo.count()):
            item_data = self.workspace_combo.itemData(i)
            if item_data and os.path.normpath(item_data) == workspace_path:
                self.workspace_combo.setCurrentIndex(i)
                return
        
        # If not found, set as custom text
        self.workspace_combo.setEditText(workspace_path)
    
    def browse_project(self):
        """Browse for Unreal project directory"""
        directory = QFileDialog.getExistingDirectory(
            self,
            "Select Unreal Project Root (containing .uproject file)",
            self.project_root or ""
        )
        if directory:
            # Verify it contains a .uproject file
            uproject_files = list(Path(directory).glob("*.uproject"))
            if uproject_files:
                self.project_root = directory
                self.project_label.setText(directory)
                self.log(f"✓ Project set to: {directory}")
                # Reload workspaces and auto-detect
                self.load_available_workspaces()
                self.auto_detect_workspace()
            else:
                QMessageBox.warning(
                    self,
                    "Invalid Project",
                    "Selected directory does not contain a .uproject file!"
                )
    
    def browse_workspace(self):
        """Browse for workspace directory"""
        current_text = self.workspace_combo.currentText()
        directory = QFileDialog.getExistingDirectory(
            self,
            "Select P4 Workspace Root",
            current_text or self.project_root or ""
        )
        if directory:
            self.workspace_combo.setEditText(directory)
            self.workspace_root = directory
            self.log(f"✓ Manually selected workspace: {directory}")
            # Try to find project in the selected workspace
            self.find_project_in_workspace(directory)
    
    def log(self, message):
        """Add message to log area"""
        self.log_area.append(message)
        self.log_area.verticalScrollBar().setValue(
            self.log_area.verticalScrollBar().maximum()
        )
    
    def install(self):
        """Perform the installation"""
        if not self.project_root:
            reply = QMessageBox.question(
                self,
                "Project Not Detected",
                "Could not auto-detect Unreal project root.\n\nWould you like to browse for the project folder?",
                QMessageBox_Yes | QMessageBox_No
            )
            if reply == QMessageBox_Yes:
                self.browse_project()
                if not self.project_root:
                    return
            else:
                return
        
        workspace = self.workspace_combo.currentText().strip()
        if not workspace:
            QMessageBox.warning(self, "Warning", "Please specify P4 workspace root!")
            return
        
        self.install_btn.setEnabled(False)
        self.log("\n--- Starting Installation ---")
        
        try:
            # Step 1: Create Python directory
            self.log("\n[1/3] Creating Python directory...")
            python_dir = Path(self.project_root) / "Content" / "Python"
            python_dir.mkdir(parents=True, exist_ok=True)
            self.log(f"✓ Created: {python_dir}")
            
            # Step 2: Copy/Create Python scripts
            self.log("\n[2/3] Installing Python scripts...")
            self.create_p4_context_menu_script(python_dir)
            self.create_init_script(python_dir)
            self.log("✓ Scripts installed successfully")
            
            # Step 3: Update DefaultEngine.ini
            self.log("\n[3/3] Updating DefaultEngine.ini...")
            config_path = Path(self.project_root) / "Config" / "DefaultEngine.ini"
            self.update_engine_ini(config_path)
            self.log("✓ Configuration updated")
            
            self.log("\n✓✓✓ Installation Complete! ✓✓✓")
            self.log("\nRestart Unreal Engine to see the 'Show in P4' context menu.")
            
            QMessageBox.information(
                self,
                "Success",
                "P4 Context Menu installed successfully!\n\nRestart Unreal Engine to activate."
            )
            
        except Exception as e:
            self.log(f"\n✗ Error: {str(e)}")
            QMessageBox.critical(self, "Installation Error", str(e))
        finally:
            self.install_btn.setEnabled(True)
    
    def create_p4_context_menu_script(self, python_dir):
        """Create the p4_context_menu.py script"""
        script_content = '''import unreal
import subprocess
import os

class P4ContextMenu:
    """
    Adds a 'Show in P4' context menu option to the Content Browser
    that opens P4V and selects the file in Perforce.
    """
    
    @staticmethod
    def show_in_p4(asset_paths):
        """
        Opens P4V and navigates to the selected asset(s).
        
        Args:
            asset_paths: List of asset paths in Unreal format (/Game/...)
        """
        for asset_path in asset_paths:
            # Convert Unreal asset path to file system path
            file_path = P4ContextMenu.get_file_path_from_asset(asset_path)
            
            if file_path and os.path.exists(file_path):
                try:
                    # Use p4vc with CMD to ensure proper execution
                    # Set working directory to project root to inherit P4 connection settings
                    project_dir = unreal.Paths.project_dir()
                    cmd = f'p4vc workspacewindow -s "{file_path}"'
                    subprocess.Popen(cmd, shell=True, cwd=project_dir)
                    unreal.log(f"Opening P4V for: {file_path}")
                except Exception as e:
                    unreal.log_error(f"Failed to open P4V: {str(e)}")
                    unreal.log_error(f"Command was: p4vc workspacewindow -s \\"{file_path}\\"")
            else:
                unreal.log_error(f"File not found: {file_path}")
    
    @staticmethod
    def get_file_path_from_asset(asset_path):
        """
        Converts an Unreal asset path to a file system path.
        
        Args:
            asset_path: Unreal asset path (e.g., /Game/MyFolder/MyAsset)
            
        Returns:
            Full file system path to the .uasset file
        """
        # Remove any sub-object references (e.g., /Game/Asset.Asset:SubObject)
        package_name = asset_path.split('.')[0]
        
        # Convert /Game/ path to Content/ path
        if package_name.startswith('/Game/'):
            relative_path = package_name.replace('/Game/', '', 1)
            
            # Get the full project content directory and normalize it
            content_dir = unreal.Paths.project_content_dir()
            content_dir = os.path.abspath(content_dir)
            
            # Build the full file path
            file_path = os.path.join(content_dir, relative_path + '.uasset')
            
            # Normalize the path to resolve any .. or . components
            file_path = os.path.abspath(file_path)
            
            unreal.log(f"Converted {asset_path} to {file_path}")
            return file_path
        else:
            # Handle engine content or plugin content
            unreal.log_warning(f"Non-game content path: {package_name}")
            return None
    
    @staticmethod
    def register_menu():
        """
        Registers the context menu extension with Unreal's Content Browser.
        """
        # Create a new menu entry
        menus = unreal.ToolMenus.get()
        
        # Find the Content Browser asset context menu
        # The menu name for right-click on assets is "ContentBrowser.AssetContextMenu"
        menu_name = "ContentBrowser.AssetContextMenu"
        menu = menus.find_menu(menu_name)
        
        if not menu:
            unreal.log_error(f"Could not find menu: {menu_name}")
            return
        
        # Add a new section for source control operations
        entry = unreal.ToolMenuEntry(
            name="ShowInP4",
            type=unreal.MultiBlockType.MENU_ENTRY,
        )
        entry.set_label(unreal.Text("Show in P4"))
        entry.set_tool_tip(unreal.Text("Open Perforce and select this file"))
        
        # Set the menu entry to call our function
        entry.set_string_command(
            type=unreal.ToolMenuStringCommandType.PYTHON,
            custom_type="",
            string="import p4_context_menu; p4_context_menu.on_show_in_p4_clicked()"
        )
        
        # Add to the source control section (or create new section)
        menu.add_menu_entry("SourceControl", entry)
        
        menus.refresh_all_widgets()
        unreal.log("P4 Context Menu registered successfully!")


def on_show_in_p4_clicked():
    """
    Called when the 'Show in P4' menu item is clicked.
    Gets the selected assets and opens them in P4V.
    """
    # Get the currently selected assets in Content Browser
    utility = unreal.EditorUtilityLibrary()
    selected_assets = utility.get_selected_assets()
    
    if not selected_assets:
        unreal.log_warning("No assets selected")
        return
    
    # Get asset paths
    asset_paths = [asset.get_path_name() for asset in selected_assets]
    
    # Show in P4
    P4ContextMenu.show_in_p4(asset_paths)


# Register the menu when this script is executed
if __name__ == '__main__':
    P4ContextMenu.register_menu()
'''
        
        script_path = python_dir / "p4_context_menu.py"
        script_path.write_text(script_content, encoding='utf-8')
        self.log(f"  ✓ Created p4_context_menu.py")
    
    def create_init_script(self, python_dir):
        """Create the init_unreal.py script"""
        init_content = '''"""
Startup script for Unreal Engine Python
This file is automatically executed when the editor starts.
"""

import unreal

# Register the P4 context menu
try:
    import p4_context_menu
    p4_context_menu.P4ContextMenu.register_menu()
    unreal.log("P4 Context Menu initialized on startup")
except Exception as e:
    unreal.log_error(f"Failed to initialize P4 Context Menu: {str(e)}")
'''
        
        init_path = python_dir / "init_unreal.py"
        init_path.write_text(init_content, encoding='utf-8')
        self.log(f"  ✓ Created init_unreal.py")
    
    def update_engine_ini(self, config_path):
        """Update DefaultEngine.ini with Python startup script"""
        if not config_path.exists():
            self.log(f"  ⚠ {config_path} not found, creating new file...")
            config_path.parent.mkdir(parents=True, exist_ok=True)
            config_path.write_text("[Python]\n+StartupScripts=init_unreal.py\n", encoding='utf-8')
            return
        
        # Read existing config
        config_content = config_path.read_text(encoding='utf-8')
        
        # Check if Python section exists
        if '[Python]' in config_content:
            # Check if startup script is already added
            if 'init_unreal.py' in config_content:
                self.log("  ℹ init_unreal.py already configured")
                return
            
            # Add to existing Python section
            config_content = config_content.replace(
                '[Python]',
                '[Python]\n+StartupScripts=init_unreal.py'
            )
        else:
            # Add new Python section at the end
            config_content += '\n[Python]\n+StartupScripts=init_unreal.py\n'
        
        # Backup original
        backup_path = config_path.with_suffix('.ini.backup')
        shutil.copy2(config_path, backup_path)
        self.log(f"  ✓ Backup created: {backup_path.name}")
        
        # Write updated config
        config_path.write_text(config_content, encoding='utf-8')
        self.log(f"  ✓ Updated DefaultEngine.ini")


def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    window = P4MenuSetupWindow()
    window.show()
    
    sys.exit(app.exec() if hasattr(app, 'exec') else app.exec_())


if __name__ == '__main__':
    main()
