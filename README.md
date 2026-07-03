"""# Smart Bulk Markdown Converter

A lightweight, high-performance Python desktop utility designed to bulk-convert source code and text files into a flat list of Markdown (`.md`) files. 

This tool is specifically optimized for developers who need to prepare entire codebases for text-processing workflows, documentation generation, or feeding context into Large Language Models (LLMs), without the hassle of copying and pasting files one by one.

## ✨ Features

* **Zero Dependencies:** Built entirely using Python's Standard Library. No need for `pip install` or virtual environments.
* **Smart Package Detection:** Automatically detects and offers to filter out heavy dependency folders (e.g., `node_modules`, `venv`, `.git`) and lockfiles so you only convert your actual source code.
* **Flat Output Structure:** Extracts files from any folder depth and outputs them into a single, easy-to-access destination folder.
* **Collision Resolution:** Automatically renames files with identical names (e.g., `index.html` and `index.js` become `new_index.md` and `new_index_1.md`) to prevent overwriting.
* **Internal Path Injection:** Injects the original relative directory path at the very top of each generated `.md` file so context is never lost.
* **Parallel Processing:** Uses multi-threading to process large batches of files concurrently, ensuring maximum speed without UI freezing.
* **Non-Destructive:** Creates a completely separate `[FolderName]_md_converted_flat` directory. Your original files are never altered or deleted.

---

## 🚀 Getting Started

### Prerequisites
You only need **Python 3.x** installed on your system.
* **Windows:** Download from [python.org](https://www.python.org/downloads/) (ensure you check "Add Python to PATH" during installation).
* **Mac/Linux:** Python 3 is typically pre-installed.

### Installation
1. Clone or download this repository.
2. Ensure the script file is named `bulk_md_converter.py`.

### How to Run
Open your terminal or command prompt, navigate to the folder containing the script, and execute:


# On Windows
python bulk_md_converter.py

# On Mac/Linux
python3 bulk_md_converter.py
