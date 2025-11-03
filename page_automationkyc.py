import csv
import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

DEFAULT_PATH = r"D:\Python Programs\automation_task\kyc_data.csv"


class KYCApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Router KYC Automation")
        self.geometry("680x520")
        self.resizable(False, False)

        # file path variable
        self.file_path = tk.StringVar(value=DEFAULT_PATH)

        # form variables
        self.customer_id = tk.StringVar()
        self.location = tk.StringVar()
        self.data_throughput = tk.StringVar()
        self.latency = tk.StringVar()

        self.create_widgets()

    def create_widgets(self):
        frm_top = ttk.Frame(self, padding=12)
        frm_top.pack(fill="x")

        # File selection row
        ttk.Label(frm_top, text="CSV file:").grid(row=0, column=0, sticky="w")
        file_entry = ttk.Entry(frm_top, textvariable=self.file_path, width=60)
        file_entry.grid(row=0, column=1, padx=6, sticky="w")
        ttk.Button(frm_top, text="Browse...", command=self.browse_file).grid(row=0, column=2, padx=6)

        # Form fields
        frm_form = ttk.LabelFrame(self, text="Customer Details", padding=12)
        frm_form.pack(fill="x", padx=12, pady=8)

        ttk.Label(frm_form, text="Customer ID:").grid(row=0, column=0, sticky="w", pady=4)
        ttk.Entry(frm_form, textvariable=self.customer_id, width=40).grid(row=0, column=1, sticky="w", pady=4)

        ttk.Label(frm_form, text="Location:").grid(row=1, column=0, sticky="w", pady=4)
        ttk.Entry(frm_form, textvariable=self.location, width=40).grid(row=1, column=1, sticky="w", pady=4)

        ttk.Label(frm_form, text="Data Throughput (Mbps):").grid(row=2, column=0, sticky="w", pady=4)
        ttk.Entry(frm_form, textvariable=self.data_throughput, width=20).grid(row=2, column=1, sticky="w", pady=4)

        ttk.Label(frm_form, text="Latency (ms):").grid(row=3, column=0, sticky="w", pady=4)
        ttk.Entry(frm_form, textvariable=self.latency, width=20).grid(row=3, column=1, sticky="w", pady=4)

        # Buttons
        frm_buttons = ttk.Frame(self, padding=12)
        frm_buttons.pack(fill="x")

        ttk.Button(frm_buttons, text="Save Record", command=self.save_record).grid(row=0, column=0, padx=6)
        ttk.Button(frm_buttons, text="Clear Fields", command=self.clear_fields).grid(row=0, column=1, padx=6)
        ttk.Button(frm_buttons, text="View Records", command=self.load_records).grid(row=0, column=2, padx=6)
        ttk.Button(frm_buttons, text="Open Folder", command=self.open_folder).grid(row=0, column=3, padx=6)
        ttk.Button(frm_buttons, text="Exit", command=self.quit).grid(row=0, column=4, padx=6)

        # Treeview for CSV display
        frm_table = ttk.LabelFrame(self, text="Saved Records", padding=8)
        frm_table.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        columns = ("customer_id", "location", "data_throughput", "latency")
        self.tree = ttk.Treeview(frm_table, columns=columns, show="headings", height=12)
        for col in columns:
            heading = col.replace("_", " ").title()
            self.tree.heading(col, text=heading)
            self.tree.column(col, width=150, anchor="center")

        vsb = ttk.Scrollbar(frm_table, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=vsb.set)
        self.tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        # load existing records on start (if any)
        self.load_records()

    def browse_file(self):
        file = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialfile=os.path.basename(self.file_path.get()) or "kyc_data.csv",
            title="Select / Create CSV file"
        )
        if file:
            self.file_path.set(file)
            self.load_records()

    def ensure_csv(self):
        path = self.file_path.get().strip()
        if not path:
            raise FileNotFoundError("No file path specified.")
        directory = os.path.dirname(path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
        # If file doesn't exist, create and write header
        if not os.path.exists(path):
            with open(path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["customer_id", "location", "data_throughput", "latency"])
        return path

    def save_record(self):
        # basic validation
        cid = self.customer_id.get().strip()
        loc = self.location.get().strip()
        dt = self.data_throughput.get().strip()
        lat = self.latency.get().strip()

        if not cid:
            messagebox.showwarning("Validation", "Customer ID cannot be empty.")
            return
        if not loc:
            messagebox.showwarning("Validation", "Location cannot be empty.")
            return

        # optional numeric validation
        if dt:
            try:
                float(dt)
            except ValueError:
                messagebox.showwarning("Validation", "Data Throughput must be a number (e.g., 100 or 50.5).")
                return
        if lat:
            try:
                float(lat)
            except ValueError:
                messagebox.showwarning("Validation", "Latency must be a number (e.g., 10 or 12.3).")
                return

        try:
            path = self.ensure_csv()
            with open(path, mode="a", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerow([cid, loc, dt, lat])
            messagebox.showinfo("Saved", f"KYC data for customer {cid} added successfully!")
            self.clear_fields()
            self.load_records()
        except PermissionError:
            messagebox.showerror("Permission Error", f"Insufficient permissions to write to:\n{self.file_path.get()}")
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred:\n{type(e).__name__} - {e}")

    def clear_fields(self):
        self.customer_id.set("")
        self.location.set("")
        self.data_throughput.set("")
        self.latency.set("")

    def load_records(self):
        # clear tree
        for row in self.tree.get_children():
            self.tree.delete(row)

        path = self.file_path.get().strip()
        if not path or not os.path.exists(path):
            return  # nothing to load

        try:
            with open(path, "r", newline="", encoding="utf-8") as f:
                reader = csv.reader(f)
                header = next(reader, None)  # skip header if present
                for row in reader:
                    # ensure row has 4 columns
                    while len(row) < 4:
                        row.append("")
                    self.tree.insert("", "end", values=(row[0], row[1], row[2], row[3]))
        except Exception as e:
            messagebox.showerror("Error", f"Could not load records:\n{type(e).__name__} - {e}")

    def open_folder(self):
        path = self.file_path.get().strip()
        if not path:
            messagebox.showinfo("No file", "Please select or enter a CSV file path first.")
            return
        folder = os.path.dirname(path) or "."
        try:
            if os.name == 'nt':
                os.startfile(folder)
            elif os.name == 'posix':
                # mac and linux - try xdg-open / open
                try:
                    os.system(f'xdg-open "{folder}"')
                except Exception:
                    os.system(f'open "{folder}"')
            else:
                messagebox.showinfo("Folder Path", folder)
        except Exception as e:
            messagebox.showerror("Error", f"Could not open folder:\n{e}")


if __name__ == "__main__":
    app = KYCApp()
    app.mainloop()
