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

def extract_followers_usernames(json_data):
    """Extract usernames from followers_1.json"""
    usernames = set()
    
    if not json_data:
        return usernames
    
    print(f"\n=== FOLLOWERS DATA STRUCTURE ===")
    print(f"Type: {type(json_data)}")
    if isinstance(json_data, list):
        print(f"List length: {len(json_data)}")
        if json_data:
            print(f"First item keys: {list(json_data[0].keys())}")
    
    # New Instagram format for followers_1.json
    if isinstance(json_data, list):
        for item in json_data:
            if isinstance(item, dict):
                # Look for string_list_data
                if "string_list_data" in item and isinstance(item["string_list_data"], list):
                    for string_item in item["string_list_data"]:
                        if isinstance(string_item, dict) and "value" in string_item:
                            usernames.add(string_item["value"])
                            print(f"Added follower: {string_item['value']}")
    
    print(f"Extracted {len(usernames)} usernames from followers")
    return usernames

def extract_following_usernames(json_data):
    """Extract usernames from following.json"""
    usernames = set()
    
    if not json_data:
        return usernames
    
    print(f"\n=== FOLLOWING DATA STRUCTURE ===")
    print(f"Type: {type(json_data)}")
    if isinstance(json_data, dict):
        print(f"Keys: {list(json_data.keys())}")
    
    # New Instagram format for following.json
    if isinstance(json_data, dict):
        # Check for relationships_following key
        if "relationships_following" in json_data and isinstance(json_data["relationships_following"], list):
            for item in json_data["relationships_following"]:
                if isinstance(item, dict):
                    # Username is in the "title" field for following.json
                    if "title" in item and item["title"]:
                        usernames.add(item["title"])
                        print(f"Added following: {item['title']}")
        
        # Alternative structure check
        elif "following" in json_data and isinstance(json_data["following"], list):
            for item in json_data["following"]:
                if isinstance(item, dict) and "title" in item:
                    usernames.add(item["title"])
                    print(f"Added following (alternative): {item['title']}")
    
    print(f"Extracted {len(usernames)} usernames from following")
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
                    if isinstance(value, list) and value:
                        print_structure(value[0], indent + 1, max_depth, current_depth + 1)
                    else:
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
    
    followers_usernames = extract_followers_usernames(followers_data)
    following_usernames = extract_following_usernames(following_data)
    
    print(f"\nFinal counts:")
    print(f"Followers found: {len(followers_usernames)}")
    print(f"Following found: {len(following_usernames)}")
    
    not_following_back = following_usernames - followers_usernames
    not_followed_back = followers_usernames - following_usernames
    mutuals = followers_usernames & following_usernames
    
    output_text.configure(state="normal")
    output_text.delete('1.0', tk.END)
    
    # Display results
    output_text.insert(tk.END, f"📊 INSTAGRAM FOLLOWERS ANALYSIS\n")
    output_text.insert(tk.END, f"{'='*60}\n\n")
    
    output_text.insert(tk.END, f"🔍 FILES LOADED:\n")
    output_text.insert(tk.END, f"• Followers: {os.path.basename(followers_file)}\n")
    output_text.insert(tk.END, f"• Following: {os.path.basename(following_file)}\n\n")
    
    output_text.insert(tk.END, f"📈 SUMMARY STATISTICS:\n")
    output_text.insert(tk.END, f"• Your followers: {len(followers_usernames)}\n")
    output_text.insert(tk.END, f"• You follow: {len(following_usernames)}\n")
    output_text.insert(tk.END, f"• Mutual followers: {len(mutuals)}\n")
    output_text.insert(tk.END, f"• Not following you back: {len(not_following_back)}\n")
    output_text.insert(tk.END, f"• You don't follow back: {len(not_followed_back)}\n\n")
    
    output_text.insert(tk.END, f"{'='*60}\n\n")
    
    output_text.insert(tk.END, f"1️⃣ PEOPLE YOU FOLLOW WHO DON'T FOLLOW BACK ({len(not_following_back)}):\n")
    output_text.insert(tk.END, f"{'─'*60}\n")
    if not_following_back:
        sorted_list = sorted(not_following_back)
        for i, username in enumerate(sorted_list[:50], 1):
            output_text.insert(tk.END, f"{i:3}. @{username}\n")
        if len(not_following_back) > 50:
            output_text.insert(tk.END, f"\n... and {len(not_following_back) - 50} more\n")
    else:
        output_text.insert(tk.END, "🎉 No one! Everyone you follow follows you back.\n")
    output_text.insert(tk.END, f"\n{'='*60}\n\n")
    
    output_text.insert(tk.END, f"2️⃣ PEOPLE WHO FOLLOW YOU BUT YOU DON'T FOLLOW BACK ({len(not_followed_back)}):\n")
    output_text.insert(tk.END, f"{'─'*60}\n")
    if not_followed_back:
        sorted_list = sorted(not_followed_back)
        for i, username in enumerate(sorted_list[:50], 1):
            output_text.insert(tk.END, f"{i:3}. @{username}\n")
        if len(not_followed_back) > 50:
            output_text.insert(tk.END, f"\n... and {len(not_followed_back) - 50} more\n")
    else:
        output_text.insert(tk.END, "✅ You follow back all your followers!\n")
    output_text.insert(tk.END, f"\n{'='*60}\n\n")
    
    output_text.insert(tk.END, f"3️⃣ MUTUAL FOLLOWERS ({len(mutuals)}):\n")
    output_text.insert(tk.END, f"{'─'*60}\n")
    if mutuals:
        sorted_list = sorted(mutuals)
        for i, username in enumerate(sorted_list[:50], 1):
            output_text.insert(tk.END, f"{i:3}. @{username}\n")
        if len(mutuals) > 50:
            output_text.insert(tk.END, f"\n... and {len(mutuals) - 50} more\n")
    else:
        output_text.insert(tk.END, "No mutual followers found.\n")
    
    output_text.insert(tk.END, f"\n{'='*60}\n")
    output_text.insert(tk.END, f"✅ Analysis completed successfully!\n")
    output_text.insert(tk.END, f"Generated: {len(following_usernames) - len(mutuals)} unfollow suggestions\n")
    
    output_text.configure(state="disabled")

# Tkinter GUI
root = tk.Tk()
root.title("📊 Instagram Mutuals Checker (Updated for New Format)")
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

title_label = ttk.Label(main_frame, text="📊 Instagram Mutuals Checker (New Format)", style="Title.TLabel")
title_label.pack(pady=10)

instructions = ttk.Label(main_frame, 
    text="Select the folder containing your Instagram data export. Instagram's new format stores:\n• followers_1.json (contains your followers)\n• following.json (contains people you follow)",
    wraplength=800,
    justify="center")
instructions.pack(pady=5)

folder_button = ttk.Button(main_frame, text="📁 Select Instagram Data Folder", command=select_base_folder)
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