"""
File Integrity Monitor (FIM) - Professional Edition
A complete file integrity monitoring system with GUI, email alerts, and continuous monitoring
"""

import os
import json
import hashlib
import time
import logging
import smtplib
import threading
from datetime import datetime
from pathlib import Path
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from tkinter import filedialog, messagebox
from tkinter import ttk

import customtkinter as ctk

# Configure CustomTkinter appearance
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class FileIntegrityMonitor:
    """Main application class for File Integrity Monitor"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("File Integrity Monitor - Professional Edition")
        self.root.geometry("900x700")
        self.root.minsize(800, 600)
        
        # Application variables
        self.monitoring = False
        self.monitor_thread = None
        self.selected_folder = None
        self.baseline_file = None
        self.log_file = "fim.log"
        self.interval = 10  # seconds between checks
        
        # Email configuration (optional)
        self.email_config = {
            'enabled': False,
            'smtp_server': 'smtp.gmail.com',
            'smtp_port': 587,
            'sender_email': '',
            'sender_password': '',
            'recipient_email': ''
        }
        
        # Setup logging
        self.setup_logging()
        
        # Initialize GUI
        self.setup_ui()
        
        # Load saved configuration
        self.load_config()
        
    def setup_logging(self):
        """Configure logging to file and console"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def setup_ui(self):
        """Create the main user interface"""
        # Main container
        self.main_frame = ctk.CTkFrame(self.root)
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title_label = ctk.CTkLabel(
            self.main_frame, 
            text="🔒 File Integrity Monitor",
            font=ctk.CTkFont(size=28, weight="bold")
        )
        title_label.pack(pady=(0, 20))
        
        # Control Panel
        self.control_frame = ctk.CTkFrame(self.main_frame)
        self.control_frame.pack(fill="x", pady=(0, 15))
        
        # Folder selection
        folder_frame = ctk.CTkFrame(self.control_frame)
        folder_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(folder_frame, text="📁 Target Folder:", font=ctk.CTkFont(size=14)).pack(side="left", padx=(0, 10))
        self.folder_entry = ctk.CTkEntry(folder_frame, width=400, placeholder_text="Select a folder to monitor...")
        self.folder_entry.pack(side="left", padx=(0, 10), fill="x", expand=True)
        
        browse_btn = ctk.CTkButton(folder_frame, text="Browse", command=self.browse_folder, width=100)
        browse_btn.pack(side="left")
        
        # Control buttons
        button_frame = ctk.CTkFrame(self.control_frame)
        button_frame.pack(fill="x", padx=10, pady=10)
        
        self.create_baseline_btn = ctk.CTkButton(
            button_frame, 
            text="📊 Create Baseline",
            command=self.create_baseline,
            fg_color="#2ecc71",
            hover_color="#27ae60",
            width=150
        )
        self.create_baseline_btn.pack(side="left", padx=(0, 10))
        
        self.start_btn = ctk.CTkButton(
            button_frame, 
            text="▶️ Start Monitoring",
            command=self.start_monitoring,
            fg_color="#3498db",
            hover_color="#2980b9",
            width=150
        )
        self.start_btn.pack(side="left", padx=(0, 10))
        
        self.stop_btn = ctk.CTkButton(
            button_frame, 
            text="⏹️ Stop Monitoring",
            command=self.stop_monitoring,
            fg_color="#e74c3c",
            hover_color="#c0392b",
            width=150,
            state="disabled"
        )
        self.stop_btn.pack(side="left", padx=(0, 10))
        
        # Email settings button
        self.email_btn = ctk.CTkButton(
            button_frame,
            text="📧 Email Settings",
            command=self.show_email_settings,
            fg_color="#9b59b6",
            hover_color="#8e44ad",
            width=150
        )
        self.email_btn.pack(side="left")
        
        # Status bar
        self.status_label = ctk.CTkLabel(
            self.control_frame,
            text="✅ Ready",
            font=ctk.CTkFont(size=12)
        )
        self.status_label.pack(pady=(0, 10))
        
        # Results display
        results_frame = ctk.CTkFrame(self.main_frame)
        results_frame.pack(fill="both", expand=True, pady=(10, 0))
        
        # Results header
        header_frame = ctk.CTkFrame(results_frame)
        header_frame.pack(fill="x", padx=10, pady=(10, 5))
        
        ctk.CTkLabel(header_frame, text="📋 Monitoring Results", font=ctk.CTkFont(size=16, weight="bold")).pack(side="left")
        
        # Clear button
        clear_btn = ctk.CTkButton(
            header_frame,
            text="Clear Results",
            command=self.clear_results,
            width=100,
            fg_color="#95a5a6",
            hover_color="#7f8c8d"
        )
        clear_btn.pack(side="right")
        
        # Results text area with scrollbar
        text_frame = ctk.CTkFrame(results_frame)
        text_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        self.results_text = ctk.CTkTextbox(text_frame, font=ctk.CTkFont(size=12))
        self.results_text.pack(fill="both", expand=True)
        
        # Configure text tags for colors
        self.results_text.tag_config("new", foreground="#2ecc71")
        self.results_text.tag_config("modified", foreground="#f1c40f")
        self.results_text.tag_config("deleted", foreground="#e74c3c")
        self.results_text.tag_config("info", foreground="#3498db")
        self.results_text.tag_config("warning", foreground="#e67e22")
        self.results_text.tag_config("error", foreground="#e74c3c")
        self.results_text.tag_config("success", foreground="#2ecc71")
        
        # Status bar at bottom
        status_bar = ctk.CTkFrame(self.root, height=30)
        status_bar.pack(fill="x", side="bottom")
        
        self.status_message = ctk.CTkLabel(
            status_bar, 
            text="Ready to monitor files",
            font=ctk.CTkFont(size=11)
        )
        self.status_message.pack(side="left", padx=10)
        
        self.monitor_status = ctk.CTkLabel(
            status_bar,
            text="● Stopped",
            font=ctk.CTkFont(size=11),
            text_color="#e74c3c"
        )
        self.monitor_status.pack(side="right", padx=10)
        
    def browse_folder(self):
        """Open folder selection dialog"""
        folder = filedialog.askdirectory(title="Select Folder to Monitor")
        if folder:
            self.selected_folder = folder
            self.folder_entry.delete(0, "end")
            self.folder_entry.insert(0, folder)
            self.baseline_file = os.path.join(folder, "hashes.json")
            self.update_status(f"📁 Selected folder: {folder}")
            self.logger.info(f"Selected folder: {folder}")
            
    def browse_email_attachment(self):
        """Browse for attachment file (placeholder for future use)"""
        pass
        
    def create_baseline(self):
        """Create a baseline hash file for the selected folder"""
        if not self.selected_folder:
            messagebox.showerror("Error", "Please select a folder first!")
            return
            
        try:
            self.update_status("📊 Creating baseline...")
            self.logger.info("Creating baseline for folder: %s", self.selected_folder)
            
            hashes = {}
            file_count = 0
            
            # Walk through all files in the selected folder
            for root, dirs, files in os.walk(self.selected_folder):
                for file in files:
                    file_path = os.path.join(root, file)
                    try:
                        # Calculate SHA-256 hash
                        sha256_hash = self.calculate_hash(file_path)
                        if sha256_hash:
                            # Store relative path to make it portable
                            rel_path = os.path.relpath(file_path, self.selected_folder)
                            hashes[rel_path] = sha256_hash
                            file_count += 1
                    except Exception as e:
                        self.logger.error(f"Error hashing {file_path}: {e}")
                        
            # Save baseline to JSON file
            with open(self.baseline_file, 'w') as f:
                json.dump(hashes, f, indent=2)
                
            self.log_result(f"✅ Baseline created successfully!", "success")
            self.log_result(f"📊 Total files hashed: {file_count}", "info")
            self.logger.info(f"Baseline created with {file_count} files")
            self.update_status(f"✅ Baseline created: {file_count} files hashed")
            
            messagebox.showinfo("Success", f"Baseline created successfully!\nTotal files: {file_count}")
            
        except Exception as e:
            error_msg = f"Error creating baseline: {e}"
            self.log_result(f"❌ {error_msg}", "error")
            self.logger.error(error_msg)
            messagebox.showerror("Error", error_msg)
            
    def calculate_hash(self, file_path, block_size=65536):
        """Calculate SHA-256 hash of a file"""
        try:
            sha256 = hashlib.sha256()
            with open(file_path, 'rb') as f:
                for block in iter(lambda: f.read(block_size), b''):
                    sha256.update(block)
            return sha256.hexdigest()
        except Exception as e:
            self.logger.error(f"Hash calculation failed for {file_path}: {e}")
            return None
            
    def load_baseline(self):
        """Load the baseline hash file"""
        if not self.baseline_file or not os.path.exists(self.baseline_file):
            return None
            
        try:
            with open(self.baseline_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"Error loading baseline: {e}")
            return None
            
    def scan_files(self):
        """Scan current folder and compare with baseline"""
        if not self.selected_folder:
            return
            
        baseline = self.load_baseline()
        if not baseline:
            self.log_result("⚠️ No baseline found! Please create one first.", "warning")
            return
            
        current_files = {}
        new_files = []
        modified_files = []
        deleted_files = []
        
        # Scan current files
        for root, dirs, files in os.walk(self.selected_folder):
            for file in files:
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, self.selected_folder)
                
                try:
                    hash_value = self.calculate_hash(file_path)
                    if hash_value:
                        current_files[rel_path] = hash_value
                except Exception as e:
                    self.logger.error(f"Error scanning {file_path}: {e}")
                    
        # Compare with baseline
        for file_path, hash_value in current_files.items():
            if file_path not in baseline:
                new_files.append(file_path)
            elif hash_value != baseline[file_path]:
                modified_files.append(file_path)
                
        for file_path in baseline:
            if file_path not in current_files:
                deleted_files.append(file_path)
                
        # Log results
        changes_detected = False
        
        if new_files:
            self.log_result(f"📄 New files detected ({len(new_files)}):", "new")
            for file in new_files[:10]:  # Show first 10
                self.log_result(f"  + {file}", "new")
            if len(new_files) > 10:
                self.log_result(f"  ... and {len(new_files) - 10} more", "info")
            changes_detected = True
            
        if modified_files:
            self.log_result(f"✏️ Modified files detected ({len(modified_files)}):", "modified")
            for file in modified_files[:10]:
                self.log_result(f"  * {file}", "modified")
            if len(modified_files) > 10:
                self.log_result(f"  ... and {len(modified_files) - 10} more", "info")
            changes_detected = True
            
        if deleted_files:
            self.log_result(f"🗑️ Deleted files detected ({len(deleted_files)}):", "deleted")
            for file in deleted_files[:10]:
                self.log_result(f"  - {file}", "deleted")
            if len(deleted_files) > 10:
                self.log_result(f"  ... and {len(deleted_files) - 10} more", "info")
            changes_detected = True
            
        if not changes_detected:
            self.log_result("✅ No changes detected", "success")
            
        # Send email alert if changes detected and email is enabled
        if changes_detected and self.email_config['enabled']:
            self.send_email_alert(new_files, modified_files, deleted_files)
            
        return changes_detected
        
    def log_result(self, message, tag=None):
        """Add a message to the results text area with timestamp"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        formatted_message = f"[{timestamp}] {message}\n"
        
        self.results_text.insert("end", formatted_message, tag if tag else "info")
        self.results_text.see("end")
        self.root.update_idletasks()
        
        # Also log to file
        self.logger.info(message)
        
    def clear_results(self):
        """Clear the results text area"""
        self.results_text.delete("1.0", "end")
        self.log_result("🧹 Results cleared", "info")
        
    def update_status(self, message):
        """Update the status bar message"""
        self.status_message.configure(text=message)
        
    def start_monitoring(self):
        """Start continuous monitoring in a separate thread"""
        if not self.selected_folder:
            messagebox.showerror("Error", "Please select a folder first!")
            return
            
        if not os.path.exists(self.baseline_file):
            messagebox.showerror("Error", "No baseline found! Please create one first.")
            return
            
        if self.monitoring:
            return
            
        self.monitoring = True
        self.start_btn.configure(state="disabled")
        self.stop_btn.configure(state="normal")
        self.monitor_status.configure(text="● Running", text_color="#2ecc71")
        self.update_status("🔄 Monitoring started...")
        
        self.log_result("🚀 Starting continuous monitoring...", "info")
        self.log_result(f"📁 Monitoring folder: {self.selected_folder}", "info")
        self.log_result(f"⏱️ Check interval: {self.interval} seconds", "info")
        
        # Start monitoring thread
        self.monitor_thread = threading.Thread(target=self.monitoring_loop, daemon=True)
        self.monitor_thread.start()
        
    def stop_monitoring(self):
        """Stop continuous monitoring"""
        self.monitoring = False
        self.start_btn.configure(state="normal")
        self.stop_btn.configure(state="disabled")
        self.monitor_status.configure(text="● Stopped", text_color="#e74c3c")
        self.update_status("⏹️ Monitoring stopped")
        self.log_result("⏹️ Monitoring stopped", "warning")
        
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=2)
            
    def monitoring_loop(self):
        """Main monitoring loop running in separate thread"""
        while self.monitoring:
            try:
                # Perform scan
                self.root.after(0, lambda: self.update_status("🔄 Scanning for changes..."))
                changes = self.scan_files()
                
                if changes:
                    self.root.after(0, lambda: self.update_status("⚠️ Changes detected!"))
                else:
                    self.root.after(0, lambda: self.update_status("✅ No changes detected"))
                    
                # Wait for next scan
                time.sleep(self.interval)
                
            except Exception as e:
                error_msg = f"Monitoring error: {e}"
                self.logger.error(error_msg)
                self.root.after(0, lambda: self.log_result(f"❌ {error_msg}", "error"))
                time.sleep(self.interval)
                
    def show_email_settings(self):
        """Show email configuration dialog"""
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("Email Settings")
        dialog.geometry("500x450")
        dialog.resizable(False, False)
        
        # Make dialog modal
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Main frame
        frame = ctk.CTkFrame(dialog)
        frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(frame, text="📧 Email Alert Settings", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=(0, 20))
        
        # Enable/disable email
        email_enabled = ctk.BooleanVar(value=self.email_config['enabled'])
        enable_check = ctk.CTkCheckBox(frame, text="Enable Email Alerts", variable=email_enabled)
        enable_check.pack(pady=(0, 15))
        
        # Email fields
        fields = [
            ("SMTP Server:", "smtp_server", "smtp.gmail.com"),
            ("SMTP Port:", "smtp_port", "587"),
            ("Sender Email:", "sender_email", "your.email@gmail.com"),
            ("Sender Password:", "sender_password", "password", True),
            ("Recipient Email:", "recipient_email", "recipient@email.com")
        ]
        
        entries = {}
        for field_info in fields:
            label = field_info[0]
            key = field_info[1]
            placeholder = field_info[2]
            is_password = len(field_info) > 3 and field_info[3]
            
            field_frame = ctk.CTkFrame(frame)
            field_frame.pack(fill="x", pady=5)
            
            ctk.CTkLabel(field_frame, text=label, width=120, anchor="w").pack(side="left", padx=(0, 10))
            
            entry = ctk.CTkEntry(
                field_frame, 
                placeholder_text=placeholder,
                show="*" if is_password else ""
            )
            entry.pack(side="left", fill="x", expand=True)
            
            # Set current value if exists
            if key in self.email_config:
                entry.insert(0, str(self.email_config[key]))
                
            entries[key] = entry
            
        # Save button
        def save_email_settings():
            self.email_config['enabled'] = email_enabled.get()
            self.email_config['smtp_server'] = entries['smtp_server'].get()
            self.email_config['smtp_port'] = int(entries['smtp_port'].get() or 587)
            self.email_config['sender_email'] = entries['sender_email'].get()
            self.email_config['sender_password'] = entries['sender_password'].get()
            self.email_config['recipient_email'] = entries['recipient_email'].get()
            
            self.save_config()
            
            status = "enabled" if self.email_config['enabled'] else "disabled"
            messagebox.showinfo("Success", f"Email settings saved! Alerts {status}.")
            self.logger.info(f"Email settings updated: {status}")
            dialog.destroy()
            
        # Test email button
        def test_email():
            if not self.email_config['enabled']:
                messagebox.showwarning("Warning", "Email alerts are not enabled. Enable them first.")
                return
                
            try:
                self.send_email_alert(
                    new_files=["test_file.txt"], 
                    modified_files=[], 
                    deleted_files=[],
                    test_mode=True
                )
                messagebox.showinfo("Success", "Test email sent successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to send test email: {e}")
                
        button_frame = ctk.CTkFrame(frame)
        button_frame.pack(fill="x", pady=(20, 0))
        
        ctk.CTkButton(button_frame, text="💾 Save", command=save_email_settings, width=100).pack(side="left", padx=(0, 10))
        ctk.CTkButton(button_frame, text="📧 Test Email", command=test_email, width=100, fg_color="#f39c12").pack(side="left")
        ctk.CTkButton(button_frame, text="❌ Cancel", command=dialog.destroy, width=100, fg_color="#95a5a6").pack(side="right")
        
    def send_email_alert(self, new_files, modified_files, deleted_files, test_mode=False):
        """Send email alert with changes detected"""
        if not self.email_config['enabled'] and not test_mode:
            return
            
        try:
            # Create email message
            msg = MIMEMultipart()
            msg['From'] = self.email_config['sender_email']
            msg['To'] = self.email_config['recipient_email']
            
            if test_mode:
                msg['Subject'] = "FIM - Test Email"
            else:
                msg['Subject'] = f"🔔 FIM Alert - Changes Detected at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                
            # Email body
            body = f"""
File Integrity Monitor Alert
{'=' * 40}

Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Folder: {self.selected_folder}

{'=' * 40}
Summary:
{'=' * 40}

New Files: {len(new_files)}
Modified Files: {len(modified_files)}
Deleted Files: {len(deleted_files)}

"""
            
            if new_files:
                body += f"\n📄 New Files ({len(new_files)}):\n"
                for file in new_files[:20]:
                    body += f"  + {file}\n"
                if len(new_files) > 20:
                    body += f"  ... and {len(new_files) - 20} more\n"
                    
            if modified_files:
                body += f"\n✏️ Modified Files ({len(modified_files)}):\n"
                for file in modified_files[:20]:
                    body += f"  * {file}\n"
                if len(modified_files) > 20:
                    body += f"  ... and {len(modified_files) - 20} more\n"
                    
            if deleted_files:
                body += f"\n🗑️ Deleted Files ({len(deleted_files)}):\n"
                for file in deleted_files[:20]:
                    body += f"  - {file}\n"
                if len(deleted_files) > 20:
                    body += f"  ... and {len(deleted_files) - 20} more\n"
                    
            body += f"\n{'=' * 40}\nThis is an automated alert from File Integrity Monitor."
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Send email
            with smtplib.SMTP(self.email_config['smtp_server'], self.email_config['smtp_port']) as server:
                server.starttls()
                server.login(self.email_config['sender_email'], self.email_config['sender_password'])
                server.send_message(msg)
                
            self.logger.info("Email alert sent successfully")
            if test_mode:
                self.log_result("📧 Test email sent successfully", "success")
            else:
                self.log_result("📧 Email alert sent", "info")
                
        except Exception as e:
            error_msg = f"Failed to send email: {e}"
            self.logger.error(error_msg)
            self.log_result(f"❌ {error_msg}", "error")
            
    def save_config(self):
        """Save configuration to file"""
        config = {
            'email_config': self.email_config,
            'interval': self.interval,
            'selected_folder': self.selected_folder
        }
        
        try:
            config_file = os.path.join(os.path.dirname(__file__), 'fim_config.json')
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=2)
            self.logger.info("Configuration saved")
        except Exception as e:
            self.logger.error(f"Error saving config: {e}")
            
    def load_config(self):
        """Load configuration from file"""
        try:
            config_file = os.path.join(os.path.dirname(__file__), 'fim_config.json')
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    config = json.load(f)
                    
                if 'email_config' in config:
                    self.email_config.update(config['email_config'])
                if 'interval' in config:
                    self.interval = config['interval']
                if 'selected_folder' in config and config['selected_folder']:
                    self.selected_folder = config['selected_folder']
                    self.folder_entry.insert(0, self.selected_folder)
                    self.baseline_file = os.path.join(self.selected_folder, "hashes.json")
                    
                self.logger.info("Configuration loaded")
        except Exception as e:
            self.logger.error(f"Error loading config: {e}")
            
    def on_closing(self):
        """Handle application shutdown"""
        if self.monitoring:
            self.stop_monitoring()
        self.save_config()
        self.logger.info("Application shutting down")
        self.root.destroy()


def main():
    """Main entry point for the application"""
    try:
        root = ctk.CTk()
        app = FileIntegrityMonitor(root)
        root.protocol("WM_DELETE_WINDOW", app.on_closing)
        root.mainloop()
    except Exception as e:
        print(f"Fatal error: {e}")
        logging.error(f"Fatal error: {e}")


if __name__ == "__main__":
    main()