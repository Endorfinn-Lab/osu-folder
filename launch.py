import os
import shutil
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
import time

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
    for folder_name in os.listdir(osu_folder_path):
        folder_path = os.path.join(osu_folder_path, folder_name)
        if os.path.isdir(folder_path):
            for filename in os.listdir(folder_path):
                if filename.endswith(".osu"):
                    beatmap_count += 1
    beatmap_count_label.config(text=f"Beatmap Count: {beatmap_count}")

def search_beatmaps(key, mode):
    """Searches for beatmaps based on title, key, and mode."""
    title = title_entry.get().lower()
    search_all = all_beatmaps_var.get()
    found_beatmaps = []

    for folder_name in os.listdir(osu_folder_path):
        folder_path = os.path.join(osu_folder_path, folder_name)
        if os.path.isdir(folder_path):
            for filename in os.listdir(folder_path):
                if filename.endswith(".osu"):
                    with open(os.path.join(folder_path, filename), "r", encoding="utf-8") as f:
                        content = f.read()
                        key_count = extract_key_count(content)
                        if (
                            (search_all or title in content.lower())
                            and (not key or key_count == int(key))
                        ):
                            if mode:
                                mode_value = extract_mode(content)
                                if mode_value == int(mode):
                                    found_beatmaps.append(folder_name)
                            else:
                                found_beatmaps.append(folder_name)
    display_results(found_beatmaps)

def display_results(beatmaps):
    """Displays the search results in the listbox."""
    result_listbox.delete(0, tk.END)
    for beatmap in beatmaps:
        result_listbox.insert(tk.END, beatmap)
    search_count_label.config(text=f"Found: {len(beatmaps)}")

def delete_selected_beatmaps(key, mode):
    """Deletes the selected beatmaps."""
    selected_indices = result_listbox.curselection()

    if messagebox.askyesno("Confirm Deletion", "Are you sure you want to delete the selected beatmaps?"):
        deleted_count = 0
        for index in selected_indices:
            folder_name = result_listbox.get(index)
            folder_path = os.path.join(osu_folder_path, folder_name)
            for filename in os.listdir(folder_path):
                if filename.endswith(".osu"):
                    file_path = os.path.join(folder_path, filename)
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            content = f.read()
                            key_count = extract_key_count(content)
                            mode_value = extract_mode(content)
                            if (not key or key_count == int(key)) and (
                                not mode or mode_value == int(mode)
                            ):
                                os.remove(file_path)
                                deleted_count += 1
                                print(f"Deleted beatmap file: {filename}")
                    except FileNotFoundError:
                        print(f"Error: File not found for {filename}")
                    except PermissionError:
                        print(f"Waiting for process to release '{filename}'...")
                        time.sleep(2)
                        try:
                            os.remove(file_path)
                            deleted_count += 1
                            print(f"Deleted beatmap file: {filename}")
                        except FileNotFoundError:
                            print(f"Error: File not found for {filename}")
                        except Exception as e:
                            print(f"An error occurred while deleting {filename}: {e}")
                    except Exception as e:
                        print(f"An error occurred while deleting {filename}: {e}")
            update_beatmap_count()
        if deleted_count > 0:
            messagebox.showinfo("Success", f"Deleted {deleted_count} beatmaps successfully.")
        else:
            messagebox.showwarning("No Files Deleted", "No files were deleted. Please check your selection.")

def delete_all_beatmaps():
    """Deletes all beatmaps in the listbox."""
    key = key_entry.get()
    mode = mode_entry.get()
    if messagebox.askyesno("Confirm Deletion", "Are you sure you want to delete all beatmaps in the list?"):
        beatmaps_to_delete = [result_listbox.get(i) for i in range(result_listbox.size())]
        deleted_count = 0
        for folder_name in beatmaps_to_delete:
            folder_path = os.path.join(osu_folder_path, folder_name)
            try:
                for filename in os.listdir(folder_path):
                    if filename.endswith(".osu"):
                        file_path = os.path.join(folder_path, filename)
                        try:
                            with open(file_path, "r", encoding="utf-8") as f:
                                content = f.read()
                                key_count = extract_key_count(content)
                                mode_value = extract_mode(content)
                                if (not key or key_count == int(key)) and (
                                    not mode or mode_value == int(mode)
                                ):
                                    os.remove(file_path)
                                    deleted_count += 1
                                    print(f"Deleted beatmap file: {filename}")
                        except FileNotFoundError:
                            print(f"Error: File not found for {filename}")
                        except PermissionError:
                            print(f"Waiting for process to release '{filename}'...")
                            time.sleep(2)
                            try:
                                os.remove(file_path)
                                deleted_count += 1
                                print(f"Deleted beatmap file: {filename}")
                            except FileNotFoundError:
                                print(f"Error: File not found for {filename}")
                            except Exception as e:
                                print(f"An error occurred while deleting {filename}: {e}")
                        except Exception as e:
                            print(f"An error occurred while deleting {filename}: {e}")
                update_beatmap_count()
            except FileNotFoundError:
                print(f"Error: Folder not found for {folder_name}")
            except Exception as e:
                print(f"An error occurred while deleting {folder_name}: {e}")

        if deleted_count > 0:
            messagebox.showinfo("Success", f"Deleted {deleted_count} beatmaps successfully.")
        else:
            messagebox.showwarning("No Files Deleted", "No files were deleted. Please check your selection.")

def clear_list():
    """Clears the listbox of search results."""
    result_listbox.delete(0, tk.END)
    search_count_label.config(text="Found: 0")

def refresh_folder():
    """Refreshes the beatmap count and updates the listbox."""
    if osu_folder_path:
        update_beatmap_count()
        search_beatmaps(key_entry.get(), mode_entry.get())

def extract_key_count(content):
    """Extracts the key count from the .osu file content."""
    if "CircleSize:" in content:
        parts = content.split("CircleSize:")[1].split()
        for part in parts:
            if part.isdigit():
                return int(part)
    return None

def extract_mode(content):
    """Extracts the mode from the .osu file content."""
    if "Mode:" in content:
        return int(content.split("Mode:")[1].split()[0])
    return None

# Create the main window
window = tk.Tk()
window.title("osu! Folder Manager")

# Add a background color for aesthetics
window.configure(bg="#f0f0f0") 

# osu! Folder Selection
osu_folder_label = tk.Label(
    window, text="Select osu! Beatmap Directory (osu!/Songs/):", bg="#f0f0f0"
)
osu_folder_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")

osu_folder_button = tk.Button(window, text="Select Directory", command=select_osu_folder)
osu_folder_button.grid(row=0, column=1, padx=5, pady=5)

# Beatmap Count Display
beatmap_count_label = tk.Label(window, text="Beatmap Count:", bg="#f0f0f0")
beatmap_count_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")

# Search Parameters
title_label = tk.Label(window, text="Title:", bg="#f0f0f0")
title_label.grid(row=2, column=0, padx=5, pady=5, sticky="w")

title_entry = tk.Entry(window, width=40)
title_entry.grid(row=2, column=1, padx=5, pady=5)

key_label = tk.Label(window, text="Key Count:", bg="#f0f0f0")
key_label.grid(row=3, column=0, padx=5, pady=5, sticky="w")

key_entry = tk.Entry(window, width=40)
key_entry.grid(row=3, column=1, padx=5, pady=5)

mode_label = tk.Label(window, text="Mode (0=Std, 1=Taiko, 2=CTB, 3=Mania):", bg="#f0f0f0")
mode_label.grid(row=4, column=0, padx=5, pady=5, sticky="w")

mode_entry = tk.Entry(window, width=40)
mode_entry.grid(row=4, column=1, padx=5, pady=5)

all_beatmaps_var = tk.BooleanVar(value=False)
all_beatmaps_checkbox = tk.Checkbutton(
    window, text="Search All Beatmaps", variable=all_beatmaps_var, bg="#f0f0f0"
)

# Search Button
search_button = tk.Button(
    window,
    text="Search Beatmaps (leave blank for any)",
    command=lambda: search_beatmaps(key_entry.get(), mode_entry.get()),
    bg="#4CAF50",  # Green color
    fg="white",  # White text
)
search_button.grid(row=6, column=0, columnspan=2, padx=5, pady=5)

# Results Display
result_listbox = tk.Listbox(window, width=50, height=10)
result_listbox.grid(row=7, column=0, columnspan=2, padx=5, pady=5)

# Clear List Button
clear_button = tk.Button(
    window, text="Clear List", command=clear_list, bg="#f44336", fg="white"
)  # Red color
clear_button.grid(row=8, column=0, padx=5, pady=5)

# Refresh Folder Button
refresh_button = tk.Button(
    window, text="Refresh Folder", command=refresh_folder, bg="#2196F3", fg="white"
)  # Blue color
refresh_button.grid(row=8, column=1, padx=5, pady=5)

# Search Count Display
search_count_label = tk.Label(window, text="Found: 0", bg="#f0f0f0")
search_count_label.grid(row=9, column=0, padx=5, pady=5, sticky="w")

# Delete Selected Button
delete_button = tk.Button(
    window,
    text="Delete Selected",
    command=lambda: delete_selected_beatmaps(key_entry.get(), mode_entry.get()),
    bg="#ff9800",  # Orange color
    fg="white",
)
delete_button.grid(row=10, column=0, padx=5, pady=5)

# Delete All Button
delete_all_button = tk.Button(
    window, text="Delete All", command=delete_all_beatmaps, bg="#ff9800", fg="white"
)
delete_all_button.grid(row=10, column=1, padx=5, pady=5)

window.mainloop()
