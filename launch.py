import os
import shutil
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
import time

def select_osu_folder():
    """
    Opens a file dialog to select the osu! beatmap directory.
    """
    global osu_folder_path
    osu_folder_path = filedialog.askdirectory(
        initialdir=os.path.expanduser("~\\AppData\\Local\\osu!\\Songs"),
        title="Select osu! Beatmap Directory",
    )
    if osu_folder_path:
        osu_folder_label.config(text=f"Selected Directory: {osu_folder_path}")
        update_beatmap_count()

def update_beatmap_count():
    """
    Counts the number of beatmaps in the selected directory and updates the label.
    """
    beatmap_count = 0
    for folder_name in os.listdir(osu_folder_path):
        folder_path = os.path.join(osu_folder_path, folder_name)
        if os.path.isdir(folder_path):
            for filename in os.listdir(folder_path):
                if filename.endswith(".osu"):
                    beatmap_count += 1
    beatmap_count_label.config(text=f"Beatmap Count: {beatmap_count}")

def search_beatmaps(key):
    """
    Searches for beatmaps based on the entered title, key, and selection.
    """
    title = title_entry.get().lower()  # Convert title to lowercase for case-insensitive search
    search_all = all_beatmaps_var.get()
    found_beatmaps = []

    for folder_name in os.listdir(osu_folder_path):
        folder_path = os.path.join(osu_folder_path, folder_name)
        if os.path.isdir(folder_path):
            for filename in os.listdir(folder_path):
                if filename.endswith(".osu"):
                    with open(os.path.join(folder_path, filename), "r", encoding="utf-8") as f:
                        content = f.read()
                        # Check for title and key (same as before)
                        if (
                            (search_all or title.lower() in content.lower())
                            and (not key or key in content)
                        ):
                            # Check for key count (optional)
                            if key:
                                if "CircleSize:" in content:
                                    key_count = int(content.split("CircleSize:")[1].split()[0])
                                    if key_count == int(key):
                                        found_beatmaps.append(folder_name)
                            else:
                                found_beatmaps.append(folder_name)

    display_results(found_beatmaps)

def display_results(beatmaps):
    result_listbox.delete(0, tk.END)
    for beatmap in beatmaps:
        result_listbox.insert(tk.END, beatmap)
    search_count_label.config(text=f"Found: {len(beatmaps)}")

def delete_selected_beatmaps(key):
    """
    Deletes the selected beatmaps from the osu! directory.
    """
    selected_indices = result_listbox.curselection()

    if messagebox.askyesno("Confirm Deletion", "Are you sure you want to delete the selected beatmaps?"):
        for index in selected_indices:
            folder_name = result_listbox.get(index)
            folder_path = os.path.join(osu_folder_path, folder_name)
            for filename in os.listdir(folder_path):
                if filename.endswith(".osu"):
                    file_path = os.path.join(folder_path, filename)
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            content = f.read()
                            if "CircleSize:" in content:
                                key_count = int(content.split("CircleSize:")[1].split()[0])
                                if key_count == int(key):
                                    os.remove(file_path)
                                    print(f"Deleted beatmap file: {filename}")
                    except FileNotFoundError:
                        print(f"Error: File not found for {filename}")
                    except PermissionError:
                        # Add a delay for potential process lock
                        print(f"Waiting for process to release '{filename}'...")
                        time.sleep(2)
                        try:
                            os.remove(file_path)
                            print(f"Deleted beatmap file: {filename}")
                        except FileNotFoundError:
                            print(f"Error: File not found for {filename}")
                        except Exception as e:
                            print(f"An error occurred while deleting {filename}: {e}")
                    except Exception as e:
                        print(f"An error occurred while deleting {filename}: {e}")
            # After deleting .osu files, update beatmap count (if necessary)
            update_beatmap_count()

def delete_all_beatmaps():
    """
    Deletes all beatmaps in the listbox, considering key count if specified.
    """
    key = key_entry.get()
    if messagebox.askyesno("Confirm Deletion", "Are you sure you want to delete all beatmaps in the list?"):
        # Get a list of beatmaps before modifying the listbox
        beatmaps_to_delete = [result_listbox.get(i) for i in range(result_listbox.size())]
        for folder_name in beatmaps_to_delete:
            folder_path = os.path.join(osu_folder_path, folder_name)
            try:
                # Only delete if key count matches, if a key is specified
                if key:
                    # Check if the folder only contains files with the same key count
                    all_files_match_key = True
                    for filename in os.listdir(folder_path):
                        if filename.endswith(".osu"):
                            file_path = os.path.join(folder_path, filename)
                            try:
                                with open(file_path, "r", encoding="utf-8") as f:
                                    content = f.read()
                                    if "CircleSize:" in content:
                                        key_count = int(content.split("CircleSize:")[1].split()[0])
                                        if key_count != int(key):
                                            all_files_match_key = False
                                            break  # No need to check further in this folder
                            except FileNotFoundError:
                                print(f"Error: File not found for {filename}")
                            except PermissionError:
                                # Add a delay for potential process lock
                                print(f"Waiting for process to release '{filename}'...")
                                time.sleep(2)
                                try:
                                    os.remove(file_path)
                                    print(f"Deleted beatmap file: {filename}")
                                except FileNotFoundError:
                                    print(f"Error: File not found for {filename}")
                                except Exception as e:
                                    print(f"An error occurred while deleting {filename}: {e}")
                            except Exception as e:
                                print(f"An error occurred while deleting {filename}: {e}")
                    if all_files_match_key:
                        # Delete the entire folder if all files have the same key count
                        shutil.rmtree(folder_path)
                        print(f"Deleted beatmap folder: {folder_name}")
                    else:
                        # Only delete files with the specified key count
                        for filename in os.listdir(folder_path):
                            if filename.endswith(".osu"):
                                file_path = os.path.join(folder_path, filename)
                                try:
                                    with open(file_path, "r", encoding="utf-8") as f:
                                        content = f.read()
                                        if "CircleSize:" in content:
                                            key_count = int(content.split("CircleSize:")[1].split()[0])
                                            if key_count == int(key):
                                                os.remove(file_path)
                                                print(f"Deleted beatmap file: {filename}")
                                except FileNotFoundError:
                                    print(f"Error: File not found for {filename}")
                                except PermissionError:
                                    # Add a delay for potential process lock
                                    print(f"Waiting for process to release '{filename}'...")
                                    time.sleep(2)
                                    try:
                                        os.remove(file_path)
                                        print(f"Deleted beatmap file: {filename}")
                                    except FileNotFoundError:
                                        print(f"Error: File not found for {filename}")
                                    except Exception as e:
                                        print(f"An error occurred while deleting {filename}: {e}")
                                except Exception as e:
                                    print(f"An error occurred while deleting {filename}: {e}")
                else:  # If no key is specified, delete the whole folder
                    shutil.rmtree(folder_path)
                    print(f"Deleted beatmap folder: {folder_name}")
                # Delete from listbox after deleting files
                result_listbox.delete(0, tk.END)
                update_beatmap_count()
            except FileNotFoundError:
                print(f"Error: Folder not found for {folder_name}")
            except Exception as e:
                print(f"An error occurred while deleting {folder_name}: {e}")

def clear_list():
    """
    Clears the listbox of results.
    """
    result_listbox.delete(0, tk.END)
    search_count_label.config(text="Found: 0")

def refresh_folder():
    """
    Refreshes the beatmap count and updates the listbox based on the current directory.
    """
    if osu_folder_path:
        update_beatmap_count()
        search_beatmaps(key_entry.get())

# Create the main window
window = tk.Tk()
window.title("osu! Beatmap Deleter")

# osu! Folder Selection
osu_folder_label = tk.Label(window, text="Select osu! Beatmap Directory:")
osu_folder_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")

osu_folder_button = tk.Button(window, text="Select Directory", command=select_osu_folder)
osu_folder_button.grid(row=0, column=1, padx=5, pady=5)

# Beatmap Count Display
beatmap_count_label = tk.Label(window, text="Beatmap Count:")
beatmap_count_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")

# Search Parameters
title_label = tk.Label(window, text="Beatmap Title:")
title_label.grid(row=2, column=0, padx=5, pady=5, sticky="w")

title_entry = tk.Entry(window, width=40)
title_entry.grid(row=2, column=1, padx=5, pady=5)

key_label = tk.Label(window, text="Key Count (CircleSize):")
key_label.grid(row=3, column=0, padx=5, pady=5, sticky="w")

key_entry = tk.Entry(window, width=40)
key_entry.grid(row=3, column=1, padx=5, pady=5)

all_beatmaps_var = tk.BooleanVar(value=False)
all_beatmaps_checkbox = tk.Checkbutton(
    window, text="Search All Beatmaps", variable=all_beatmaps_var
)

# Search
search_button = tk.Button(window, text="Search Beatmaps", command=lambda: search_beatmaps(key_entry.get()))
search_button.grid(row=5, column=0, columnspan=2, padx=5, pady=5)

# Results Display
result_listbox = tk.Listbox(window, width=50, height=10)
result_listbox.grid(row=6, column=0, columnspan=2, padx=5, pady=5)

# Search Count Display
search_count_label = tk.Label(window, text="Found: 0")
search_count_label.grid(row=7, column=0, padx=5, pady=5, sticky="w")

# Delete Selected
delete_button = tk.Button(window, text="Delete Selected", command=lambda: delete_selected_beatmaps(key_entry.get()))
delete_button.grid(row=9, column=0, padx=5, pady=5)

# Delete All
delete_all_button = tk.Button(window, text="Delete All", command=delete_all_beatmaps)
delete_all_button.grid(row=9, column=1, padx=5, pady=5)

# Clear List
clear_button = tk.Button(window, text="Clear List", command=clear_list)
clear_button.grid(row=10, column=0, padx=5, pady=5)

# Refresh Folder
refresh_button = tk.Button(window, text="Refresh Folder", command=refresh_folder)
refresh_button.grid(row=10, column=1, padx=5, pady=5)

window.mainloop()
