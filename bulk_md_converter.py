import os
import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path
import concurrent.futures

PACKAGE_SIGNATURES = {
    'node_modules', 'venv', '.venv', 'env', '.git', '__pycache__', '.egg-info',
    'package-lock.json', 'yarn.lock', 'pnpm-lock.yaml', 'requirements.txt', 
    'Pipfile.lock', '.env', 'dist', 'build', '.idea', '.vscode', '.DS_Store'
}

class MarkdownConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Smart Bulk Markdown Converter (Flat Output)")
        self.root.geometry("700x600")
        
        self.source_dir = None
        self.files_found = []
        
        # --- UI Elements ---
        self.lbl_instruction = tk.Label(root, text="1. Select a folder to scan for files:", font=("Arial", 10, "bold"))
        self.lbl_instruction.pack(pady=(15, 0))
        
        self.btn_select = tk.Button(root, text="Select Folder", command=self.select_folder, width=20)
        self.btn_select.pack(pady=5)
        
        self.lbl_list = tk.Label(root, text="2. Manage the files found below:", font=("Arial", 10, "bold"))
        self.lbl_list.pack(pady=(15, 0))
        
        btn_frame = tk.Frame(root)
        btn_frame.pack(pady=5)
        
        self.btn_select_all = tk.Button(btn_frame, text="Select All", command=self.select_all, state=tk.DISABLED)
        self.btn_select_all.pack(side=tk.LEFT, padx=5)
        
        self.btn_deselect_all = tk.Button(btn_frame, text="Deselect All", command=self.deselect_all, state=tk.DISABLED)
        self.btn_deselect_all.pack(side=tk.LEFT, padx=5)
        
        self.btn_remove_selected = tk.Button(btn_frame, text="Remove Selected from List", command=self.remove_selected, state=tk.DISABLED, fg="red")
        self.btn_remove_selected.pack(side=tk.LEFT, padx=5)
        
        self.btn_reset = tk.Button(btn_frame, text="Reset / Start Over", command=self.reset_app, state=tk.DISABLED)
        self.btn_reset.pack(side=tk.LEFT, padx=5)
        
        frame = tk.Frame(root)
        frame.pack(padx=15, pady=5, fill=tk.BOTH, expand=True)
        
        scrollbar = tk.Scrollbar(frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.listbox = tk.Listbox(frame, selectmode=tk.MULTIPLE, yscrollcommand=scrollbar.set, exportselection=False)
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.listbox.yview)
        
        self.btn_convert = tk.Button(root, text="3. Convert Selected in Parallel", command=self.convert_files, state=tk.DISABLED, bg="green", fg="white", font=("Arial", 11, "bold"), height=2)
        self.btn_convert.pack(pady=20, fill=tk.X, padx=15)

    def select_folder(self):
        folder_selected = filedialog.askdirectory()
        if not folder_selected:
            return
            
        self.source_dir = Path(folder_selected)
        self.clear_list_data()
        
        all_files = []
        has_packages = False
        
        for file_path in self.source_dir.rglob('*'):
            if file_path.is_file():
                path_parts = set(file_path.parts)
                if any(sig in path_parts for sig in PACKAGE_SIGNATURES) or file_path.name in PACKAGE_SIGNATURES:
                    has_packages = True
                all_files.append(file_path)
        
        ignore_packages = False
        if has_packages:
            ignore_packages = messagebox.askyesno(
                "Packages Detected", 
                "I noticed package, dependency, or environment files/folders.\n\n"
                "Would you like me to AUTOMATICALLY IGNORE them so you only convert your own source code?"
            )
            
        for file_path in all_files:
            path_parts = set(file_path.parts)
            is_package_file = any(sig in path_parts for sig in PACKAGE_SIGNATURES) or file_path.name in PACKAGE_SIGNATURES
            
            if ignore_packages and is_package_file:
                continue 
                
            if file_path.name == '.DS_Store':
                continue
                
            self.files_found.append(file_path)
            rel_path = file_path.relative_to(self.source_dir)
            self.listbox.insert(tk.END, str(rel_path))
            
        self.select_all()
        self.update_ui_states()
        
        if not self.files_found:
            messagebox.showinfo("Empty", "No valid files found matching your criteria.")

    def select_all(self):
        for i in range(self.listbox.size()):
            self.listbox.selection_set(i)

    def deselect_all(self):
        self.listbox.selection_clear(0, tk.END)

    def remove_selected(self):
        selected_indices = list(self.listbox.curselection())
        if not selected_indices:
            messagebox.showwarning("No Selection", "Please click on items in the list to select what you want to remove.")
            return
            
        for index in reversed(selected_indices):
            self.listbox.delete(index)
            del self.files_found[index]
            
        self.update_ui_states()

    def clear_list_data(self):
        self.listbox.delete(0, tk.END)
        self.files_found = []

    def reset_app(self):
        self.clear_list_data()
        self.source_dir = None
        self.update_ui_states()

    def update_ui_states(self):
        state = tk.NORMAL if self.files_found else tk.DISABLED
        self.btn_select_all.config(state=state)
        self.btn_deselect_all.config(state=state)
        self.btn_remove_selected.config(state=state)
        self.btn_reset.config(state=state)
        self.btn_convert.config(state=state)

    def convert_files(self):
        selected_indices = self.listbox.curselection()
        if not selected_indices:
            messagebox.showwarning("No Files", "Your list has files, but none are selected for conversion. Highlight them or click 'Select All'.")
            return
            
        selected_files = [self.files_found[i] for i in selected_indices]
        
        # Create a single FLAT destination folder
        dest_root = self.source_dir.parent / f"{self.source_dir.name}_md_converted_flat"
        dest_root.mkdir(parents=True, exist_ok=True)
        
        self.btn_convert.config(text="Converting...", state=tk.DISABLED)
        self.root.update()
        
        # --- Pre-calculate safe filenames to avoid overwrites in the single folder ---
        file_mapping = []
        used_filenames = set()
        
        for file_path in selected_files:
            base_name = f"new_{file_path.stem}"
            ext = ".md"
            new_filename = f"{base_name}{ext}"
            counter = 1
            
            # If the filename is already taken by another file, append a number
            while new_filename in used_filenames:
                new_filename = f"{base_name}_{counter}{ext}"
                counter += 1
                
            used_filenames.add(new_filename)
            dest_file_path = dest_root / new_filename
            file_mapping.append((file_path, dest_file_path))
        
        # --- Parallel Execution ---
        with concurrent.futures.ThreadPoolExecutor() as executor:
            # We now pass the pre-calculated, guaranteed-unique destination path
            futures = [
                executor.submit(self.process_single_file, file_path, self.source_dir, dest_path) 
                for file_path, dest_path in file_mapping
            ]
            concurrent.futures.wait(futures)
            
        messagebox.showinfo("Success", f"Processing complete!\nAll files saved flatly to:\n{dest_root}")
        self.btn_convert.config(text="3. Convert Selected in Parallel", state=tk.NORMAL)
        self.update_ui_states()

    def process_single_file(self, file_path, source_root, dest_file_path):
        try:
            rel_path = file_path.relative_to(source_root)
            rel_dir = rel_path.parent
            
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
            except Exception:
                content = "[File could not be parsed as text]"
            
            # Calculate the original path string to inject into the file
            if str(rel_dir) == '.':
                folder_path_str = source_root.name
            else:
                folder_path_str = f"{source_root.name}/{str(rel_dir).replace(os.sep, '/')}"
                
            # Write everything directly into the single destination file
            with open(dest_file_path, 'w', encoding='utf-8') as f:
                f.write(f"this file is from {folder_path_str}/\n\n")
                f.write(content)
                
        except Exception as e:
            print(f"Error processing {file_path.name}: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = MarkdownConverterApp(root)
    root.mainloop()