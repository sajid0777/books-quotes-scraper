"""Prompt for an Atlas URI in a masked local window, then run the scraper."""
import os
import tkinter as tk
from tkinter import messagebox
from urllib.parse import quote_plus

ATLAS_HOST = "cluster0.v6kg77c.mongodb.net"


def main():
    root = tk.Tk()
    root.title("Connect scraper to MongoDB Atlas")
    root.resizable(False, False)
    root.geometry("520x205")

    tk.Label(root, text="Enter your Atlas database username:").pack(
        anchor="w", padx=16, pady=(16, 4)
    )
    username_entry = tk.Entry(root, width=68)
    username_entry.pack(fill="x", padx=16)
    tk.Label(root, text="Enter that database user's password:").pack(
        anchor="w", padx=16, pady=(10, 4)
    )
    password_entry = tk.Entry(root, show="*", width=68)
    password_entry.pack(fill="x", padx=16)
    tk.Label(root, text="Credentials stay on this computer and are not saved in the project.").pack(
        anchor="w", padx=16, pady=8
    )

    def run_scraper():
        username = username_entry.get().strip()
        password = password_entry.get()
        if not username or not password:
            messagebox.showerror("Missing credentials", "Enter both the database username and password.")
            return
        uri = f"mongodb+srv://{quote_plus(username)}:{quote_plus(password)}@{ATLAS_HOST}/?appName=Cluster0"
        try:
            from pymongo.uri_parser import parse_uri
            parse_uri(uri)
        except Exception as exc:
            messagebox.showerror(
                "Invalid connection string",
                f"The credentials could not be formatted for Atlas. Check them and try again.\n\nDetails: {exc}",
            )
            return
        try:
            from pymongo import MongoClient
            with MongoClient(uri, serverSelectionTimeoutMS=10000) as client:
                client.admin.command("ping")
        except Exception:
            messagebox.showerror(
                "Atlas connection failed",
                "Atlas did not accept the connection. Check the database username/password "
                "and the project's IP Access List, then try again.",
            )
            return
        os.environ["MONGODB_URI"] = uri
        username_entry.delete(0, tk.END)
        password_entry.delete(0, tk.END)
        root.destroy()
        import main as scraper_main
        scraper_main.run()

    tk.Button(root, text="Connect and run scraper", command=run_scraper).pack(
        anchor="e", padx=16, pady=(0, 12)
    )
    username_entry.focus_set()
    root.mainloop()


if __name__ == "__main__":
    main()
