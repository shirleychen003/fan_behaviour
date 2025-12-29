import json
import os
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk

def load_json_from_path(file_path):
    if not os.path.exists(file_path):
        messagebox.showerror("Error", f"File not found: {file_path}")
        return None
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

def extract_usernames(json_data):
    usernames = set()

    # Handle following.json structure
    if isinstance(json_data, dict):
        json_data = json_data.get("relationships_following", [])

    if not isinstance(json_data, list):
        return usernames

    for entry in json_data:
        for item in entry.get("string_list_data", []):
            value = item.get("value")
            if value:
                usernames.add(value)

    return usernames


def select_base_folder():
    folder_selected = filedialog.askdirectory(title="Select Base Folder")
    if folder_selected:
        global base_folder
        base_folder = folder_selected
        folder_label.config(text=f"📁 {base_folder}")
    else:
        messagebox.showerror("Error", "No folder selected.")

def process_files():
    if not base_folder:
        messagebox.showerror("Error", "Please select a base folder first.")
        return

    possible_paths = [
        os.path.join(base_folder, "connections", "followers_and_following"),
        os.path.join(base_folder, "followers_and_following")
    ]

    for path in possible_paths:
        followers_file = os.path.join(path, "followers_1.json")
        following_file = os.path.join(path, "following.json")
        if os.path.exists(followers_file) and os.path.exists(following_file):
            break
    else:
        messagebox.showerror("Error", "followers_1.json and following.json not found.")
        return

    followers_data = load_json_from_path(followers_file)
    following_data = load_json_from_path(following_file)

    if not followers_data or not following_data:
        return

    followers_usernames = extract_usernames(followers_data)
    following_usernames = extract_usernames(following_data)

    not_following_back = following_usernames - followers_usernames
    not_followed_back = followers_usernames - following_usernames
    mutuals = followers_usernames & following_usernames

    output_text.configure(state="normal")
    output_text.delete('1.0', tk.END)
    output_text.insert(tk.END, f"1️⃣ People You Follow Who Don't Follow Back ({len(not_following_back)}):\n{sorted(not_following_back)}\n\n")
    output_text.insert(tk.END, f"2️⃣ People Who Follow You But You Don't Follow Back ({len(not_followed_back)}):\n{sorted(not_followed_back)}\n\n")
    output_text.insert(tk.END, f"3️⃣ Mutual Followers ({len(mutuals)}):\n{sorted(mutuals)}\n\n")
    output_text.configure(state="disabled")

# Tkinter GUI
root = tk.Tk()
root.title("📊 Instagram Mutuals Checker")
root.configure(bg="#f4f6f7")

# Center the window
window_width = 1000
window_height = 800
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
x_position = int((screen_width / 2) - (window_width / 2))
y_position = int((screen_height / 2) - (window_height / 2))
root.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")

# 📚 Fonts and style
style = ttk.Style()
style.configure("TButton", font=("Helvetica", 12), padding=6)
style.configure("TLabel", font=("Helvetica", 12), background="#f4f6f7")
style.configure("Title.TLabel", font=("Helvetica", 20, "bold"), background="#f4f6f7")
style.configure("TFrame", background="#f4f6f7")

main_frame = ttk.Frame(root, padding=20)
main_frame.pack(fill="both", expand=True)

title_label = ttk.Label(main_frame, text="📊 Instagram Mutuals Checker", style="Title.TLabel")
title_label.pack(pady=10)

folder_button = ttk.Button(main_frame, text="📁 Select Base Folder", command=select_base_folder)
folder_button.pack(pady=5)

folder_label = ttk.Label(main_frame, text="No folder selected.", wraplength=800)
folder_label.pack(pady=5)

process_button = ttk.Button(main_frame, text="▶️ Process and Show Results", command=process_files)
process_button.pack(pady=10)

output_frame = ttk.Frame(main_frame, padding=10)
output_frame.pack(fill="both", expand=True)

output_text = scrolledtext.ScrolledText(output_frame, wrap=tk.WORD, font=("Consolas", 11), state="disabled")
output_text.pack(fill="both", expand=True)

base_folder = None

root.mainloop()
