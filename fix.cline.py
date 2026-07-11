import json
import glob
import os

# Automatically locate all Cline task histories
tasks_path = os.path.expandvars(r"%APPDATA%\Code\User\globalStorage\saoudrizwan.claude-dev\tasks\*\api_conversation_history.json")
files = glob.glob(tasks_path)

def clean_images(obj):
    modified = False
    if isinstance(obj, dict):
        if obj.get("type") in ["image", "image_url"]:
            obj["type"] = "text"
            obj["text"] = "[System: Image removed for DeepSeek compatibility]"
            obj.pop("source", None)
            obj.pop("image_url", None)
            modified = True
        for k, v in obj.items():
            if clean_images(v):
                modified = True
    elif isinstance(obj, list):
        for item in obj:
            if clean_images(item):
                modified = True
    return modified

found_issue = False
for file_path in files:
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        if clean_images(data):
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            print(f"✅ Successfully cleaned: {os.path.basename(os.path.dirname(file_path))}")
            found_issue = True
    except Exception as e:
        print(f"Could not read {file_path}: {e}")

if not found_issue:
    print("No image tags found. The error might be cached in VS Code's memory.")
else:
    print("✨ All done! Please restart VS Code and hit Retry.")