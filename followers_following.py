import json
import os
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk

def load_json_from_path(file_path):
    if not os.path.exists(file_path):
        messagebox.showerror("Error", f"File not found: {file_path}")
        return None
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to load {file_path}: {str(e)}")
        return None

def extract_usernames(json_data, file_type="followers"):
    usernames = set()
    
    if not json_data:
        return usernames
    
    # Debug: Print the structure
    print(f"\n=== {file_type.upper()} DATA STRUCTURE ===")
    print(f"Type: {type(json_data)}")
    if isinstance(json_data, dict):
        print(f"Keys: {list(json_data.keys())}")
    elif isinstance(json_data, list):
        print(f"List length: {len(json_data)}")
    
    # Try different possible structures
    usernames = try_all_formats(json_data)
    
    print(f"Extracted {len(usernames)} usernames from {file_type}")
    return usernames

def try_all_formats(data):
    """Try multiple possible JSON structures to extract usernames"""
    usernames = set()
    
    # Structure 1: New Instagram format
    if isinstance(data, dict):
        # Try to find any list that might contain user data
        for key, value in data.items():
            if isinstance(value, list):
                for item in value:
                    usernames.update(extract_from_item(item))
    
    # Structure 2: Direct list
    elif isinstance(data, list):
        for item in data:
            usernames.update(extract_from_item(item))
    
    return usernames

def extract_from_item(item):
    """Extract username from any item structure"""
    usernames = set()
    
    if isinstance(item, dict):
        # Try different possible keys for username
        possible_keys = ['value', 'username', 'string_list_data', 'title', 'name']
        
        for key in possible_keys:
            if key in item:
                value = item[key]
                
                if isinstance(value, str):
                    usernames.add(value)
                elif isinstance(value, list):
                    for subitem in value:
                        if isinstance(subitem, dict):
                            usernames.update(extract_from_item(subitem))
                elif isinstance(value, dict):
                    usernames.update(extract_from_item(value))
        
        # Also check for nested structures
        for key, value in item.items():
            if key not in possible_keys and isinstance(value, dict):
                usernames.update(extract_from_item(value))
            elif key not in possible_keys and isinstance(value, list):
                for subitem in value:
                    usernames.update(extract_from_item(subitem))
    
    elif isinstance(item, str):
        usernames.add(item)
    
    return usernames

def select_base_folder():
    folder_selected = filedialog.askdirectory(title="Select Base Folder")
    if folder_selected:
        global base_folder
        base_folder = folder_selected
        folder_label.config(text=f"📁 {base_folder}")
    else:
        messagebox.showerror("Error", "No folder selected.")

def analyze_structure():
    """Debug function to analyze JSON structure"""
    if not base_folder:
        messagebox.showerror("Error", "Please select a base folder first.")
        return
    
    followers_file = os.path.join(base_folder, "followers_1.json")
    following_file = os.path.join(base_folder, "following.json")
    
    if not os.path.exists(followers_file):
        followers_file = find_file(base_folder, "followers")
    
    if not os.path.exists(following_file):
        following_file = find_file(base_folder, "following")
    
    if not followers_file or not following_file:
        messagebox.showerror("Error", "Could not find follower/following files.")
        return
    
    # Analyze followers file
    followers_data = load_json_from_path(followers_file)
    if followers_data:
        analyze_file_structure(followers_data, "followers")
    
    # Analyze following file
    following_data = load_json_from_path(following_file)
    if following_data:
        analyze_file_structure(following_data, "following")

def analyze_file_structure(data, file_type):
    """Print detailed structure analysis"""
    print(f"\n{'='*50}")
    print(f"ANALYZING {file_type.upper()} STRUCTURE")
    print(f"{'='*50}")
    
    def print_structure(obj, indent=0, max_depth=3, current_depth=0):
        if current_depth >= max_depth:
            print("  " * indent + "...")
            return
        
        if isinstance(obj, dict):
            for key, value in obj.items():
                print("  " * indent + f"{key}: {type(value).__name__}")
                if isinstance(value, (dict, list)) and current_depth < max_depth - 1:
                    print_structure(value, indent + 1, max_depth, current_depth + 1)
        elif isinstance(obj, list):
            print("  " * indent + f"List with {len(obj)} items")
            if obj and current_depth < max_depth - 1:
                if isinstance(obj[0], (dict, list)):
                    print_structure(obj[0], indent + 1, max_depth, current_depth + 1)
    
    print_structure(data)

def find_file(base_folder, pattern):
    """Find a file containing the pattern in its name"""
    for root, dirs, files in os.walk(base_folder):
        for file in files:
            if pattern in file.lower() and file.endswith('.json'):
                return os.path.join(root, file)
    return None

def process_files():
    if not base_folder:
        messagebox.showerror("Error", "Please select a base folder first.")
        return
    
    # First, try to analyze structure for debugging
    analyze_structure()
    
    # Try to find files with various names and locations
    followers_file = find_file(base_folder, "followers")
    following_file = find_file(base_folder, "following")
    
    if not followers_file:
        messagebox.showerror("Error", "Could not find followers file. Look for any JSON file containing 'followers' in the name.")
        return
    
    if not following_file:
        messagebox.showerror("Error", "Could not find following file. Look for any JSON file containing 'following' in the name.")
        return
    
    print(f"\nUsing files:")
    print(f"Followers: {followers_file}")
    print(f"Following: {following_file}")
    
    followers_data = load_json_from_path(followers_file)
    following_data = load_json_from_path(following_file)
    
    if not followers_data or not following_data:
        return
    
    followers_usernames = extract_usernames(followers_data, "followers")
    following_usernames = extract_usernames(following_data, "following")
    
    print(f"\nFinal counts:")
    print(f"Followers found: {len(followers_usernames)}")
    print(f"Following found: {len(following_usernames)}")
    
    not_following_back = following_usernames - followers_usernames
    not_followed_back = followers_usernames - following_usernames
    mutuals = followers_usernames & following_usernames
    
    output_text.configure(state="normal")
    output_text.delete('1.0', tk.END)
    
    # Display results
    output_text.insert(tk.END, f"📊 ANALYSIS RESULTS\n")
    output_text.insert(tk.END, f"{'='*50}\n\n")
    
    output_text.insert(tk.END, f"1️⃣ People You Follow Who Don't Follow Back ({len(not_following_back)}):\n")
    if not_following_back:
        output_text.insert(tk.END, f"{sorted(not_following_back)[:50]}\n")  # Show first 50
        if len(not_following_back) > 50:
            output_text.insert(tk.END, f"... and {len(not_following_back) - 50} more\n")
    output_text.insert(tk.END, f"\n{'─'*50}\n\n")
    
    output_text.insert(tk.END, f"2️⃣ People Who Follow You But You Don't Follow Back ({len(not_followed_back)}):\n")
    if not_followed_back:
        output_text.insert(tk.END, f"{sorted(not_followed_back)[:50]}\n")  # Show first 50
        if len(not_followed_back) > 50:
            output_text.insert(tk.END, f"... and {len(not_followed_back) - 50} more\n")
    output_text.insert(tk.END, f"\n{'─'*50}\n\n")
    
    output_text.insert(tk.END, f"3️⃣ Mutual Followers ({len(mutuals)}):\n")
    if mutuals:
        output_text.insert(tk.END, f"{sorted(mutuals)[:50]}\n")  # Show first 50
        if len(mutuals) > 50:
            output_text.insert(tk.END, f"... and {len(mutuals) - 50} more\n")
    
    output_text.insert(tk.END, f"\n{'='*50}\n")
    output_text.insert(tk.END, f"📈 SUMMARY\n")
    output_text.insert(tk.END, f"• Your followers: {len(followers_usernames)}\n")
    output_text.insert(tk.END, f"• You follow: {len(following_usernames)}\n")
    output_text.insert(tk.END, f"• Not following you back: {len(not_following_back)}\n")
    output_text.insert(tk.END, f"• You don't follow back: {len(not_followed_back)}\n")
    output_text.insert(tk.END, f"• Mutual followers: {len(mutuals)}\n")
    
    output_text.configure(state="disabled")

# Tkinter GUI
root = tk.Tk()
root.title("📊 Instagram Mutuals Checker (Updated)")
root.configure(bg="#f4f6f7")

# Center the window
window_width = 1200
window_height = 900
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

title_label = ttk.Label(main_frame, text="📊 Instagram Mutuals Checker (Updated)", style="Title.TLabel")
title_label.pack(pady=10)

instructions = ttk.Label(main_frame, 
    text="Select the folder containing your Instagram data export (should contain followers and following JSON files)",
    wraplength=800,
    justify="center")
instructions.pack(pady=5)

folder_button = ttk.Button(main_frame, text="📁 Select Base Folder", command=select_base_folder)
folder_button.pack(pady=5)

folder_label = ttk.Label(main_frame, text="No folder selected.", wraplength=800)
folder_label.pack(pady=5)

button_frame = ttk.Frame(main_frame)
button_frame.pack(pady=10)

debug_button = ttk.Button(button_frame, text="🔍 Analyze Structure", command=analyze_structure)
debug_button.pack(side=tk.LEFT, padx=5)

process_button = ttk.Button(button_frame, text="▶️ Process and Show Results", command=process_files)
process_button.pack(side=tk.LEFT, padx=5)

output_frame = ttk.Frame(main_frame, padding=10)
output_frame.pack(fill="both", expand=True)

output_text = scrolledtext.ScrolledText(output_frame, wrap=tk.WORD, font=("Consolas", 11), state="disabled")
output_text.pack(fill="both", expand=True)

base_folder = None

root.mainloop()