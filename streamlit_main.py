import os
import streamlit as st

# === Configuration ===
FOLDER_PATH = "/Users/natalielewis/Desktop/Programming/AgentNat/pages"  # Change this to the folder where your .py files are located

# === List all .py files in the folder ===
def get_py_files(folder_path):
    return [f for f in os.listdir(folder_path) if f.endswith(".py") and os.path.isfile(os.path.join(folder_path, f))]

# === Load content from a .py file ===
def load_file_content(filepath):
    with open(filepath, "r", encoding="utf-8") as file:
        return file.read()

# === Streamlit Dashboard ===
st.set_page_config(page_title="Python File Viewer", layout="wide")

st.title("📁 Python File Viewer")

py_files = get_py_files(FOLDER_PATH)

if not py_files:
    st.warning(f"No .py files found in '{FOLDER_PATH}'")
else:
    selected_file = st.sidebar.radio("Select a Python file", py_files)

    full_path = os.path.join(FOLDER_PATH, selected_file)
    content = load_file_content(full_path)

    st.subheader(f"📄 `{selected_file}`")
    st.code(content, language='python')
