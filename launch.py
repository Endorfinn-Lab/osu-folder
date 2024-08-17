import os
import shutil
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from tkinter import ttk  
from PIL import Image, ImageTk

def select_osu_folder():
    """Opens a file dialog to select the osu! beatmap directory."""
    global osu_folder_path
    osu_folder_path = filedialog.askdirectory(
        initialdir=os.path.expanduser("~\\AppData\\Local\\osu!\\Songs"),
        title="Select osu! Beatmap Directory",
    )
    if osu_folder_path:
        osu_folder_label.config(text=f"Selected Directory: {osu_folder_path}")
        update_beatmap_count()


def update_beatmap_count():
    """Counts the number of beatmaps in the selected directory."""
    beatmap_count = 0
    if osu_folder_path:
        for folder_name in os.listdir(osu_folder_path):
            folder_path = os.path.join(osu_folder_path, folder_name)
            if os.path.isdir(folder_path):
                for filename in os.listdir(folder_path):
                    if filename.endswith(".osu"):
                        beatmap_count += 1
    beatmap_count_label.config(text=f"Beatmap Count: {beatmap_count}")


def search_beatmaps(key=None, mode="All", video_only=False):
    """Searches for beatmaps based on title, key, mode, and video_only flag."""
    title = title_entry.get().lower()
    found_beatmaps = []

    if osu_folder_path:
        progress_bar = ttk.Progressbar(window, orient="horizontal", length=300, mode="determinate")
        progress_bar.grid(row=12, column=0, columnspan=2, padx=5, pady=5)
        total_folders = len(os.listdir(osu_folder_path))
        progress_bar["maximum"] = total_folders
        processed_folders = 0

        for entry in os.scandir(osu_folder_path):
            if entry.is_dir():
                folder_name = entry.name
                if any(title in filename.lower() for filename in os.listdir(entry.path)):
                    if key:
                        valid_key_count = False  
                        for filename in os.listdir(entry.path):
                            if filename.endswith(".osu"):
                                with open(os.path.join(entry.path, filename), "r", encoding="utf-8") as f:
                                    content = f.read()
                                    key_count = extract_key_count(content)
                                    if key_count is not None and key_count == int(key):
                                        valid_key_count = True
                                        break
                        if not valid_key_count:
                            continue

                    if mode != "All":
                        valid_mode = False  
                        for filename in os.listdir(entry.path):
                            if filename.endswith(".osu"):
                                with open(os.path.join(entry.path, filename), "r", encoding="utf-8") as f:
                                    content = f.read()
                                    mode_value = extract_mode(content)
                                    if mode_value is not None and mode_value == int(mode.split(" ")[0]):
                                        valid_mode = True
                                        break
                        if not valid_mode:
                            continue

                    if video_only:
                        if not any(filename.lower().endswith((".mp4", ".avi", ".flv")) for filename in os.listdir(entry.path)):
                            continue

                    found_beatmaps.append(folder_name)

            processed_folders += 1
            progress_bar["value"] = processed_folders
            window.update_idletasks()

        progress_bar.destroy()

    display_results(found_beatmaps)


def display_results(beatmaps):
    """Displays the search results in the listbox."""
    result_listbox.delete(0, tk.END)
    for beatmap in beatmaps:
        result_listbox.insert(tk.END, beatmap)
    search_count_label.config(text=f"Found: {len(beatmaps)}")


def delete_selected_beatmaps(key=None, mode="All"):
    """Deletes the selected beatmaps from the listbox, filtering by key and mode."""
    selected_indices = result_listbox.curselection()
    if not selected_indices:
        messagebox.showwarning("No Beatmaps Selected", "Please select beatmaps to delete.")
        return

    if messagebox.askyesno("Confirm Deletion", "Are you sure you want to delete the selected beatmaps?"):
        progress_bar = ttk.Progressbar(window, orient="horizontal", length=300, mode="determinate")
        progress_bar.grid(row=12, column=0, columnspan=2, padx=5, pady=5)
        progress_bar["maximum"] = len(selected_indices)
        deleted_count = 0
        processed_count = 0

        for index in selected_indices:
            folder_name = result_listbox.get(index)
            folder_path = os.path.join(osu_folder_path, folder_name)
            deleted_count += delete_beatmaps_in_folder(folder_path, key, mode)

            processed_count += 1
            progress_bar["value"] = processed_count
            window.update_idletasks()

        update_beatmap_count()
        result_listbox.delete(*selected_indices)

        progress_bar.destroy()

        if deleted_count > 0:
            messagebox.showinfo("Success", f"Deleted {deleted_count} beatmaps successfully.")
        else:
            messagebox.showwarning("No Matching Beatmaps Deleted",
                                   "No beatmaps matching the criteria were deleted. Check your selection and filters.")


def delete_all_beatmaps(key=None, mode="All"):
    """Deletes all beatmaps matching the specified key and mode from the current search results."""
    if messagebox.askyesno("Confirm Deletion",
                           "Are you sure you want to delete all matching beatmaps from the current search results? This cannot be undone."):
        progress_bar = ttk.Progressbar(window, orient="horizontal", length=300, mode="determinate")
        progress_bar.grid(row=12, column=0, columnspan=2, padx=5, pady=5)
        total_items = result_listbox.size()
        progress_bar["maximum"] = total_items
        deleted_count = 0
        processed_items = 0

        for index in range(total_items):
            folder_name = result_listbox.get(index)
            folder_path = os.path.join(osu_folder_path, folder_name)

            if os.path.isdir(folder_path):
                should_delete = True  

                if key:
                    valid_key_count = False
                    for filename in os.listdir(folder_path):
                        if filename.endswith(".osu"):
                            with open(os.path.join(folder_path, filename), "r", encoding="utf-8") as f:
                                content = f.read()
                                key_count = extract_key_count(content)
                                if key_count is not None and key_count == int(key):
                                    valid_key_count = True
                                    break
                    if not valid_key_count:
                        should_delete = False

                if mode != "All":
                    valid_mode = False
                    for filename in os.listdir(folder_path):
                        if filename.endswith(".osu"):
                            with open(os.path.join(folder_path, filename), "r", encoding="utf-8") as f:
                                content = f.read()
                                mode_value = extract_mode(content)
                                if mode_value is not None and mode_value == int(mode.split(" ")[0]):
                                    valid_mode = True
                                    break
                    if not valid_mode:
                        should_delete = False

                if should_delete:
                    deleted_count += delete_beatmaps_in_folder(folder_path)

            processed_items += 1
            progress_bar["value"] = processed_items
            window.update_idletasks()

        update_beatmap_count()
        clear_list()

        progress_bar.destroy()

        if deleted_count > 0:
            messagebox.showinfo("Success", f"Deleted {deleted_count} beatmaps successfully.")
        else:
            messagebox.showwarning("No Matching Beatmaps Deleted", "No beatmaps matching the criteria were deleted. Check your search criteria.")


def delete_beatmaps_in_folder(folder_path, key=None, mode="All"):
    """Helper function to delete beatmaps within a folder based on key and mode."""
    deleted_in_folder = 0

    if key or mode != "All":
        valid_criteria = True
        for filename in os.listdir(folder_path):
            if filename.endswith(".osu"):
                with open(os.path.join(folder_path, filename), "r", encoding="utf-8") as f:
                    content = f.read()
                    if key:
                        key_count = extract_key_count(content)
                        if key_count is None or key_count != int(key):
                            valid_criteria = False
                            break
                    if mode != "All":
                        mode_value = extract_mode(content)
                        if mode_value is None or mode_value != int(mode.split(" ")[0]):
                            valid_criteria = False
                            break
                if key and mode != "All":
                    break

        if valid_criteria:
            try:
                shutil.rmtree(folder_path)
                deleted_in_folder += 1
            except (FileNotFoundError, PermissionError) as e:
                print(f"Error deleting {os.path.basename(folder_path)}: {e}")
                if isinstance(e, PermissionError):
                    messagebox.showwarning("Permission Error", f"Could not delete {os.path.basename(folder_path)}. It might be in use.")
    else:
        try:
            shutil.rmtree(folder_path)
            deleted_in_folder += 1
        except (FileNotFoundError, PermissionError) as e:
            print(f"Error deleting {os.path.basename(folder_path)}: {e}")
            if isinstance(e, PermissionError):
                messagebox.showwarning("Permission Error", f"Could not delete {os.path.basename(folder_path)}. It might be in use.")

    return deleted_in_folder

    
def delete_selected_videos():
    """Deletes video files from selected beatmaps."""
    selected_indices = result_listbox.curselection()
    if not selected_indices:
        messagebox.showwarning("No Beatmaps Selected", "Please select beatmaps from the list to delete videos from.")
        return

    if messagebox.askyesno("Confirm Deletion", "Are you sure you want to delete video files from the selected beatmaps?"):
        deleted_count = 0
        for index in selected_indices:
            folder_name = result_listbox.get(index)
            folder_path = os.path.join(osu_folder_path, folder_name)
            for filename in os.listdir(folder_path):
                if filename.lower().endswith((".mp4", ".avi", ".flv")):
                    file_path = os.path.join(folder_path, filename)
                    try:
                        os.remove(file_path)
                        deleted_count += 1
                        print(f"Deleted video file: {filename}")
                    except (FileNotFoundError, PermissionError) as e:
                        print(f"Error deleting {filename}: {e}")
                        if isinstance(e, PermissionError):
                            messagebox.showwarning("Permission Error", f"Could not delete {filename}. Make sure the file is not in use.")

        if deleted_count > 0:
            messagebox.showinfo("Success", f"Deleted {deleted_count} video files successfully.")
        else:
            messagebox.showwarning("No Video Files Deleted", "No video files were deleted. Please check your selection.")

def delete_all_videos():
    """Deletes all video files from all beatmaps."""
    if messagebox.askyesno("Confirm Deletion", "Are you sure you want to delete all video files from all beatmaps? This action cannot be undone."):
        deleted_count = 0
        for folder_name in os.listdir(osu_folder_path):
            folder_path = os.path.join(osu_folder_path, folder_name)
            if os.path.isdir(folder_path):
                for filename in os.listdir(folder_path):
                    if filename.lower().endswith((".mp4", ".avi", ".flv")):
                        file_path = os.path.join(folder_path, filename)
                        try:
                            os.remove(file_path)
                            deleted_count += 1
                            print(f"Deleted video file: {filename}")
                        except (FileNotFoundError, PermissionError) as e:
                            print(f"Error deleting {filename}: {e}")
                            if isinstance(e, PermissionError):
                                messagebox.showwarning("Permission Error", f"Could not delete {filename}. Make sure the file is not in use.")

        if deleted_count > 0:
            messagebox.showinfo("Success", f"Deleted {deleted_count} video files successfully.")
        else:
            messagebox.showwarning("No Video Files Deleted", "No video files were found.")

def clear_list():
    """Clears the listbox of search results."""
    result_listbox.delete(0, tk.END)
    search_count_label.config(text="Found: 0")

def refresh_folder():
    """Refreshes the beatmap count and updates the listbox."""
    if osu_folder_path:
        update_beatmap_count()
        search_beatmaps(key_entry.get(), mode_var.get(), video_only_var.get())

def extract_key_count(content):
    """Extracts the key count from the .osu file content based on the 'CircleSize:' line."""
    for line in content.splitlines():
        if line.startswith("CircleSize:"):
            try:
                return int(line.split(":")[1].strip())
            except ValueError:
                return None
    return None

def extract_mode(content):
    """Extracts the mode from the .osu file content."""
    for line in content.splitlines():
        if line.startswith("Mode:"):
            try:
                return int(line.split(":")[1].strip())
            except ValueError:
                return None
    return None

# --- Main Window ---
window = tk.Tk()
window.title("osu!Folder")
window.configure(bg="#f0f0f0")

# --- Icons ---
refresh_icon = Image.open("icons8-refresh-30.png")  # Replace with your refresh icon path
refresh_icon = refresh_icon.resize((20, 20), Image.LANCZOS)  # Resize as needed
refresh_photo = ImageTk.PhotoImage(refresh_icon)

clear_icon = Image.open("icons8-clear-30.png")  # Replace with your clear icon path
clear_icon = clear_icon.resize((20, 20), Image.LANCZOS)  # Resize as needed
clear_photo = ImageTk.PhotoImage(clear_icon)

# --- GUI ---
osu_folder_label = tk.Label(window, text="Select osu! Beatmap Directory (osu!/Songs/):", bg="#f0f0f0")
osu_folder_button = tk.Button(window, text="Select Directory", command=select_osu_folder)
beatmap_count_label = tk.Label(window, text="Beatmap Count:", bg="#f0f0f0")
title_label = tk.Label(window, text="Title:", bg="#f0f0f0")
title_entry = tk.Entry(window, width=40)
key_label = tk.Label(window, text="Key Count:", bg="#f0f0f0")
key_entry = tk.Entry(window, width=5)
mode_label = tk.Label(window, text="Mode:", bg="#f0f0f0")
mode_options = ["All", "0 (Std)", "1 (Taiko)", "2 (CTB)", "3 (Mania)"]
mode_var = tk.StringVar(window)
mode_var.set(mode_options[0])
mode_dropdown = tk.OptionMenu(window, mode_var, *mode_options)
video_only_var = tk.BooleanVar(value=False)
video_only_checkbox = tk.Checkbutton(window, text="Video Only", variable=video_only_var, bg="#f0f0f0")
search_button = tk.Button(window, text="Search Beatmaps", command=lambda: search_beatmaps(key_entry.get(), mode_var.get(), video_only_var.get()), bg="#4CAF50", fg="white")
result_listbox = tk.Listbox(window, width=50, height=10)
clear_button = tk.Button(window, image=clear_photo, command=clear_list, bg="#f44336")  # Use image for clear button
refresh_button = tk.Button(window, image=refresh_photo, command=refresh_folder, bg="#2196F3")  # Use image for refresh button
search_count_label = tk.Label(window, text="Found: 0", bg="#f0f0f0")
delete_button = tk.Button(window, text="Delete Selected Beatmaps", command=lambda: delete_selected_beatmaps(key_entry.get(), mode_var.get()), bg="#ff9800", fg="white")
delete_all_button = tk.Button(window, text="Delete All Matching Beatmaps", command=lambda: delete_all_beatmaps(key_entry.get(), mode_var.get()), bg="#ff9800", fg="white")
delete_selected_videos_button = tk.Button(window, text="Delete Selected Videos", command=delete_selected_videos, bg="#ff9800", fg="white")
delete_all_videos_button = tk.Button(window, text="Delete All Videos", command=delete_all_videos, bg="#ff9800", fg="white")

# --- Layout ---
osu_folder_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
osu_folder_button.grid(row=0, column=1, padx=5, pady=5)
beatmap_count_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")
title_label.grid(row=2, column=0, padx=5, pady=5, sticky="w")
title_entry.grid(row=2, column=1, padx=5, pady=5)
key_label.grid(row=3, column=0, padx=5, pady=5, sticky="w")
key_entry.grid(row=3, column=1, padx=5, pady=5)
mode_label.grid(row=4, column=0, padx=5, pady=5, sticky="w")
mode_dropdown.grid(row=4, column=1, padx=5, pady=5, sticky="w")
video_only_checkbox.grid(row=5, column=0, columnspan=2, padx=5, pady=5)
search_button.grid(row=6, column=0, columnspan=2, padx=5, pady=5)
result_listbox.grid(row=7, column=0, columnspan=2, padx=5, pady=5)
clear_button.grid(row=8, column=0, padx=5, pady=5)
refresh_button.grid(row=8, column=1, padx=5, pady=5)
search_count_label.grid(row=9, column=0, padx=5, pady=5, sticky="w")
delete_button.grid(row=10, column=0, padx=5, pady=5)
delete_all_button.grid(row=10, column=1, padx=5, pady=5)
delete_selected_videos_button.grid(row=11, column=0, padx=5, pady=5)
delete_all_videos_button.grid(row=11, column=1, padx=5, pady=5)

window.mainloop()
