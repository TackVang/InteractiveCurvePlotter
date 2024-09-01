import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox


def copy_files_with_extensions(source_folder, destination_folder, extensions):
    """
    指定された拡張子のファイルをソースフォルダから新しいフォルダにコピーします。

    :param source_folder: コピー元のフォルダパス
    :param destination_folder: コピー先のフォルダパス
    :param extensions: コピーするファイルの拡張子のリスト
    """
    if os.path.exists(destination_folder):
        new_folder_name = destination_folder.split("/")[-1]

        result = messagebox.askyesno(
            "", f"{new_folder_name}/ is already exist. Do you continue?")
        if not result:
            messagebox.showinfo("Process was interapted")
            return

    else:
        os.makedirs(destination_folder)

    for root, dirs, files in os.walk(source_folder):
        for file in files:
            if any(file.lower().endswith(ext.lower()) for ext in extensions):
                source_file = os.path.join(root, file)
                destination_file = os.path.join(destination_folder, file)

                # coupon_sim.keyファイルの場合、内容を置換する
                if file == "sample.key":
                    with open(source_file, 'r', encoding='utf-8') as f:
                        content = f.read()

                    source_folder_name = source_folder.split("/")[-1]
                    destination_folder_name = destination_folder.split("/")[-1]

                    if source_folder_name in content:
                        content = content.replace(
                            source_folder_name, destination_folder_name)
                        with open(destination_file, 'w', encoding='utf-8') as f:
                            f.write(content)
                    else:
                        shutil.copy2(source_file, destination_file)
                else:
                    shutil.copy2(source_file, destination_file)

    messagebox.showinfo("Complete", "New folder was created.")


def select_source_folder():
    folder_selected = filedialog.askdirectory()
    source_folder_entry.delete(0, tk.END)
    source_folder_entry.insert(0, folder_selected)


def select_destination_folder():
    folder_selected = filedialog.askdirectory()
    destination_folder_entry.delete(0, tk.END)
    destination_folder_entry.insert(0, folder_selected)


def start_copy():
    source_folder = source_folder_entry.get()
    destination_folder = destination_folder_entry.get()
    extensions_list = [".key",]
    if not source_folder or not destination_folder:
        messagebox.showwarning("Warning", "Input all arguments")
        return

    copy_files_with_extensions(
        source_folder, destination_folder, extensions_list)


# GUIのセットアップ
root = tk.Tk()
root.title("Sim folder creater")

# コピー元フォルダ選択
tk.Label(root, text="Basis folder path:").grid(row=0, column=0, padx=5, pady=5)
source_folder_entry = tk.Entry(root, width=50)
source_folder_entry.grid(row=0, column=1, padx=5, pady=5)
tk.Button(root, text="Reference", command=select_source_folder).grid(
    row=0, column=2, padx=5, pady=5)

# コピー先フォルダ選択
tk.Label(root, text="New folder path:").grid(row=1, column=0, padx=5, pady=5)
destination_folder_entry = tk.Entry(root, width=50)
destination_folder_entry.grid(row=1, column=1, padx=5, pady=5)
tk.Button(root, text="Reference", command=select_destination_folder).grid(
    row=1, column=2, padx=5, pady=5)


# 実行ボタン
tk.Button(root, text="Create new folder", command=start_copy).grid(
    row=3, column=0, columnspan=3, pady=10)

root.mainloop()
