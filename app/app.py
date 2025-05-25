from flask import Flask, render_template, request, redirect, url_for, flash
import os
import json
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "supersecretkey"

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def load_json_from_path(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            print(f"Loaded {len(data) if isinstance(data, list) else 'entries in dict'} from {file_path}")
            return data
    except Exception as e:
        print(f"Error loading JSON: {e}")
        return None

def extract_usernames(json_data, data_type):
    usernames = set()
    entries = json_data
    if data_type == "following":
        entries = json_data.get("relationships_following", [])
    if isinstance(entries, list):
        for entry in entries:
            string_list = entry.get("string_list_data", [])
            for item in string_list:
                if isinstance(item, dict):
                    value = item.get("value")
                    if value:
                        usernames.add(value.lower().strip())
    return usernames

@app.route('/', methods=['GET', 'POST'])
def index():
    result = None
    if request.method == 'POST':
        followers_file = request.files.get('followers_file')
        following_file = request.files.get('following_file')

        if not followers_file or not following_file:
            flash("Please upload both files: followers_1.json and following.json")
            return redirect(url_for('index'))

        followers_path = os.path.join(app.config['UPLOAD_FOLDER'], 'followers_1_uploaded.json')
        following_path = os.path.join(app.config['UPLOAD_FOLDER'], 'following_uploaded.json')

        followers_file.save(followers_path)
        following_file.save(following_path)

        followers_data = load_json_from_path(followers_path)
        following_data = load_json_from_path(following_path)

        if not followers_data or not following_data:
            flash("Error reading one or both JSON files.")
            return redirect(url_for('index'))

        followers_usernames = extract_usernames(followers_data, data_type="followers")
        following_usernames = extract_usernames(following_data, data_type="following")

        print(f"Followers count: {len(followers_usernames)}")
        print(f"Following count: {len(following_usernames)}")

        not_following_back = sorted(following_usernames - followers_usernames)
        not_followed_back = sorted(followers_usernames - following_usernames)
        mutuals = sorted(followers_usernames & following_usernames)

        result = {
            'not_following_back': not_following_back,
            'not_followed_back': not_followed_back,
            'mutuals': mutuals
        }

    return render_template('index.html', result=result)

if __name__ == '__main__':
    app.run(debug=True)
