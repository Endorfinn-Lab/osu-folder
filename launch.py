import os
import shutil
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox


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
    search_all = all_beatmaps_var.get()
    found_beatmaps = []

    if osu_folder_path:  
        for folder_name in os.listdir(osu_folder_path):
            folder_path = os.path.join(osu_folder_path, folder_name)
            if os.path.isdir(folder_path):
                if search_all or any(title in filename.lower() for filename in os.listdir(folder_path)):
                    if key:
                        key_counts = set()
                        for filename in os.listdir(folder_path):
                            if filename.endswith(".osu"):
                                with open(os.path.join(folder_path, filename), "r", encoding="utf-8") as f:
                                    content = f.read()
                                    key_count = extract_key_count(content)
                                    if key_count is not None:
                                        key_counts.add(key_count)
                        if len(key_counts) == 1 and int(key) in key_counts:
                            found_beatmaps.append(folder_name)
                        elif int(key) in key_counts:  
                            found_beatmaps.append(folder_name)

                    if mode != "All":
                        for filename in os.listdir(folder_path):
                            if filename.endswith(".osu"):
                                with open(os.path.join(folder_path, filename), "r", encoding="utf-8") as f:
                                    content = f.read()
                                    mode_value = extract_mode(content)
                                    if mode_value is not None and mode_value == int(mode.split(" ")[0]):
                                        found_beatmaps.append(folder_name)
                                        break  
                    else:
                        found_beatmaps.append(folder_name)

                if video_only and folder_name in found_beatmaps:
                    if not any(filename.lower().endswith((".mp4", ".avi", ".flv")) for filename in os.listdir(folder_path)):
                        found_beatmaps.remove(folder_name)

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
        deleted_count = 0
        for index in selected_indices:
            folder_name = result_listbox.get(index)
            folder_path = os.path.join(osu_folder_path, folder_name)

            if key:  
                deleted_count += delete_beatmaps_in_folder(folder_path, key, mode)
            else:
                try:
                    shutil.rmtree(folder_path)
                    deleted_count += 1
                    print(f"Deleted folder: {os.path.basename(folder_path)}")
                except (FileNotFoundError, PermissionError) as e:
                    print(f"Error deleting {os.path.basename(folder_path)}: {e}")
                    if isinstance(e, PermissionError):
                        messagebox.showwarning("Permission Error",
                                               f"Could not delete {os.path.basename(folder_path)}. It might be in use.")

        update_beatmap_count()
        result_listbox.delete(*selected_indices)
        if deleted_count > 0:
            messagebox.showinfo("Success", f"Deleted {deleted_count} beatmaps successfully.")
        else:
            messagebox.showwarning("No Matching Beatmaps Deleted",
                                    "No beatmaps matching the criteria were deleted. Check your selection and filters.")

def delete_all_beatmaps(key=None, mode="All"):
    """Deletes all beatmaps matching the specified key and mode."""
    if messagebox.askyesno("Confirm Deletion",
                           "Are you sure you want to delete all matching beatmaps? This cannot be undone."):
        deleted_count = 0
        if key:
            try:
                key = int(key)
            except ValueError:
                messagebox.showwarning("Invalid Input", "Key Count must be a number.")
                return

        for folder_name in os.listdir(osu_folder_path):
            folder_path = os.path.join(osu_folder_path, folder_name)
            if os.path.isdir(folder_path):
                if key:
                    deleted_count += delete_beatmaps_in_folder(folder_path, key, mode)
                else:
                    try:
                        shutil.rmtree(folder_path)
                        deleted_count += 1
                        print(f"Deleted folder: {os.path.basename(folder_path)}")
                    except (FileNotFoundError, PermissionError) as e:
                        print(f"Error deleting {os.path.basename(folder_path)}: {e}")
                        if isinstance(e, PermissionError):
                            messagebox.showwarning("Permission Error",
                                                   f"Could not delete {os.path.basename(folder_path)}. It might be in use.")

        update_beatmap_count()
        clear_list()
        if deleted_count > 0:
            messagebox.showinfo("Success", f"Deleted {deleted_count} beatmaps successfully.")
        else:
            messagebox.showwarning("No Folders Deleted", "No folders were deleted. Check your search criteria.")

def delete_beatmaps_in_folder(folder_path, key=None, mode="All"):
    """Deletes beatmaps within a folder based on key and mode."""
    deleted_in_folder = 0
    if key:  
        key_counts = set()
        for filename in os.listdir(folder_path):
            if filename.endswith(".osu"):
                file_path = os.path.join(folder_path, filename)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                        key_count = extract_key_count(content)  
                        mode_value = extract_mode(content)
                        key_counts.add(key_count)
                        if key_count == int(key) and (mode == "All" or mode_value == int(mode.split(" ")[0])):
                            os.remove(file_path)
                            deleted_in_folder += 1
                            print(f"Deleted beatmap file: {os.path.basename(file_path)}")
                except (FileNotFoundError, PermissionError) as e:
                    print(f"Error deleting {filename}: {e}")
                    if isinstance(e, PermissionError):
                        messagebox.showwarning("Permission Error", f"Could not delete {filename}. It might be in use.")

        if not os.listdir(folder_path):
            try:
                os.rmdir(folder_path)
                print(f"Deleted empty folder: {os.path.basename(folder_path)}")
            except OSError as e:
                print(f"Error deleting empty folder {os.path.basename(folder_path)}: {e}")
        elif len(key_counts) == 1 and int(key) in key_counts:  
            try:
                shutil.rmtree(folder_path)
                deleted_in_folder += 1
                print(f"Deleted folder: {os.path.basename(folder_path)}")
            except (FileNotFoundError, PermissionError) as e:
                print(f"Error deleting {os.path.basename(folder_path)}: {e}")
                if isinstance(e, PermissionError):
                    messagebox.showwarning("Permission Error",
                                           f"Could not delete {os.path.basename(folder_path)}. It might be in use.")
    else:  
        try:
            shutil.rmtree(folder_path)
            deleted_in_folder += 1
            print(f"Deleted folder: {os.path.basename(folder_path)}")
        except (FileNotFoundError, PermissionError) as e:
            print(f"Error deleting {os.path.basename(folder_path)}: {e}")
            if isinstance(e, PermissionError):
                messagebox.showwarning("Permission Error",
                                       f"Could not delete {os.path.basename(folder_path)}. It might be in use.")
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

# --- GUI Elements ---
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
all_beatmaps_var = tk.BooleanVar(value=False)
all_beatmaps_checkbox = tk.Checkbutton(window, text="Search All Beatmaps", variable=all_beatmaps_var, bg="#f0f0f0")
video_only_var = tk.BooleanVar(value=False)
video_only_checkbox = tk.Checkbutton(window, text="Video Only", variable=video_only_var, bg="#f0f0f0")
search_button = tk.Button(window, text="Search Beatmaps", command=lambda: search_beatmaps(key_entry.get(), mode_var.get(), video_only_var.get()), bg="#4CAF50", fg="white")
result_listbox = tk.Listbox(window, width=50, height=10)
clear_button = tk.Button(window, text="Clear List", command=clear_list, bg="#f44336", fg="white")
refresh_button = tk.Button(window, text="Refresh Folder", command=refresh_folder, bg="#2196F3", fg="white")
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
