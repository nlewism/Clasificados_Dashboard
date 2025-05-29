import difflib
import streamlit as st
import os

def read_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            return file.readlines()
    except FileNotFoundError:
        return [f"# ❌ File not found: {filepath}\n"]

def get_diff(file1_path, file2_path):
    lines1 = read_file(file1_path)
    lines2 = read_file(file2_path)

    return list(difflib.unified_diff(
        lines1,
        lines2,
        fromfile=os.path.basename(file1_path),
        tofile=os.path.basename(file2_path),
        lineterm=''
    ))

# === Streamlit App ===
st.set_page_config(page_title="Compare Two Python Files", layout="wide")
st.title("🔍 Python File Comparator")

file1_path = st.text_input("Path to Original File:")
file2_path = st.text_input("Path to Modified File:")

if file1_path and file2_path:
    if not os.path.exists(file1_path):
        st.error(f"File not found: {file1_path}")
    elif not os.path.exists(file2_path):
        st.error(f"File not found: {file2_path}")
    else:
        diff = get_diff(file1_path, file2_path)

        if not diff:
            st.success("✅ No differences found!")
        else:
            st.code("".join(diff), language="diff")
