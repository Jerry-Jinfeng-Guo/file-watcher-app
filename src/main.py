import os
import time
import smtplib
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from utils.email_sender import send_email
import threading

class FileWatcher(FileSystemEventHandler):
    def __init__(self, directory_to_watch, email_address, sender_email, sender_password, status_label, scan_interval, progress_bar):
        self.directory_to_watch = directory_to_watch
        self.email_address = email_address
        self.sender_email = sender_email
        self.sender_password = sender_password
        self.status_label = status_label
        self.scan_interval = scan_interval
        self.progress_bar = progress_bar
        self.files_seen = set(os.listdir(directory_to_watch))
        self.running = True

    # def on_created(self, event):
    #     print(f"Event detected: {event}")  # Debugging statement
    #     if event.is_directory:
    #         return
    #     if event.src_path.endswith(('.csv', '.txt')):
    #         self.send_new_files()

    def send_new_files(self):
        new_files = [os.path.join(self.directory_to_watch, f) for f in os.listdir(self.directory_to_watch) if f not in self.files_seen and f.endswith(('.csv', '.txt'))]
        if new_files:
            new_files_str = ", ".join(os.path.basename(f) for f in new_files)
            self.status_label.config(text=f"New file(s) detected: {new_files_str}, sending email")
            send_email(new_files, self.email_address, self.sender_email, self.sender_password)
            self.files_seen.update(os.path.basename(f) for f in new_files)
            self.status_label.config(text="Idle")

    def start(self):
        while self.running:
            self.progress_bar['value'] = 0
            for i in range(self.scan_interval):
                if not self.running:
                    break
                time.sleep(1)
                self.progress_bar['value'] += (100 / self.scan_interval)
            self.send_new_files()

    def stop(self):
        self.running = False

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("File Watcher")
        self.root.geometry("320x280")  # Set fixed window size
        self.root.resizable(False, False)  # Make window not resizable

        self.directory_to_watch = tk.StringVar()
        self.email_address = tk.StringVar()
        self.sender_email = tk.StringVar()
        self.sender_password = tk.StringVar()
        self.scan_interval = tk.StringVar(value="1min")
        self.status = tk.StringVar(value="Idle")

        ttk.Label(root, text="Directory to Watch:").grid(row=0, column=0, padx=10, pady=5)
        
        directory_frame = ttk.Frame(root)
        directory_frame.grid(row=0, column=1, padx=10, pady=5, columnspan=2, sticky="ew")
        ttk.Entry(directory_frame, textvariable=self.directory_to_watch).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(directory_frame, text="...", command=self.browse_directory, width=3).pack(side=tk.LEFT)

        ttk.Label(root, text="Recipient Email:").grid(row=1, column=0, padx=10, pady=5)
        ttk.Entry(root, textvariable=self.email_address).grid(row=1, column=1, padx=10, pady=5, columnspan=2, sticky="ew")

        ttk.Label(root, text="Sender Email:").grid(row=2, column=0, padx=10, pady=5)
        ttk.Entry(root, textvariable=self.sender_email).grid(row=2, column=1, padx=10, pady=5, columnspan=2, sticky="ew")

        ttk.Label(root, text="Sender Password:").grid(row=3, column=0, padx=10, pady=5)
        ttk.Entry(root, textvariable=self.sender_password, show="*").grid(row=3, column=1, padx=10, pady=5, columnspan=2, sticky="ew")

        ttk.Label(root, text="Scan Interval:").grid(row=4, column=0, padx=10, pady=5)
        scan_intervals = ["10s", "30s", "1min", "5min", "10min", "30min", "1h"]
        ttk.Combobox(root, textvariable=self.scan_interval, values=scan_intervals).grid(row=4, column=1, padx=10, pady=5, columnspan=2, sticky="ew")

        self.start_button = ttk.Button(root, text="Start", command=self.start_watching)
        self.start_button.grid(row=5, column=0, padx=10, pady=10)

        self.pause_button = ttk.Button(root, text="Pause", command=self.pause_watching, state=tk.DISABLED)
        self.pause_button.grid(row=5, column=1, padx=10, pady=10)

        self.status_label = ttk.Label(root, textvariable=self.status)
        self.status_label.grid(row=6, column=0, columnspan=3, padx=10, pady=10)

        self.progress_bar = ttk.Progressbar(root, orient="horizontal", length=300, mode="determinate")
        self.progress_bar.grid(row=7, column=0, columnspan=3, padx=10, pady=10)

        self.observer = None
        self.file_watcher = None
        self.watcher_thread = None

    def browse_directory(self):
        directory = filedialog.askdirectory()
        if directory:
            self.directory_to_watch.set(directory)

    def start_watching(self):
        directory_to_watch = self.directory_to_watch.get()
        email_address = self.email_address.get()
        sender_email = self.sender_email.get()
        sender_password = self.sender_password.get()
        scan_interval = self.scan_interval.get()

        if not all([directory_to_watch, email_address, sender_email, sender_password]):
            self.status.set("Please fill in all fields")
            return

        interval_seconds = self.get_interval_seconds(scan_interval)
        self.file_watcher = FileWatcher(directory_to_watch, email_address, sender_email, sender_password, self.status_label, interval_seconds, self.progress_bar)
        self.observer = Observer()
        self.observer.schedule(self.file_watcher, directory_to_watch, recursive=False)
        self.observer.start()

        self.start_button.config(state=tk.DISABLED)
        self.pause_button.config(state=tk.NORMAL)
        self.status.set("Watching directory")

        self.watcher_thread = threading.Thread(target=self.file_watcher.start)
        self.watcher_thread.start()

    def pause_watching(self):
        if self.observer:
            self.file_watcher.stop()
            self.observer.stop()
            self.observer.join()
            self.watcher_thread.join(timeout=1)  # Use timeout to avoid blocking indefinitely

        self.start_button.config(state=tk.NORMAL)
        self.pause_button.config(state=tk.DISABLED)
        self.status.set("Idle")

    def get_interval_seconds(self, interval):
        if interval.endswith("s"):
            return int(interval[:-1])
        elif interval.endswith("min"):
            return int(interval[:-3]) * 60
        elif interval.endswith("h"):
            return int(interval[:-1]) * 3600
        return 60  # Default to 1 minute if no match

def main():
    root = tk.Tk()
    app = App(root)
    root.mainloop()

if __name__ == "__main__":
    main()