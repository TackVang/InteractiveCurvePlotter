import tkinter as tk
from tkinter import ttk
import pandas as pd


def convert_ascii_to_table(data):
    lines = data.strip().split('\n')
    table_data = []
    for line in lines:
        cleaned_line = ' '.join(line.split())
        row = []
        for item in cleaned_line.split():
            try:
                # E表記を含む場合はfloatに変換
                row.append(float(item))
            except ValueError:
                row.append(item)
        table_data.append(row)
    return table_data


def on_convert():
    # テーブルをクリア
    for i in tree.get_children():
        tree.delete(i)

    ascii_data = text_area.get("1.0", tk.END)
    table_data = convert_ascii_to_table(ascii_data)
    for row in table_data:
        tree.insert("", tk.END, values=row)

    # DataFrameに変換してクリップボードにコピー
    df = pd.DataFrame(table_data, columns=["X", "Y"])
    df.to_clipboard(index=False, header=False)
    copied_label.config(text="Data copied to clipboard!")


def add_leading_spaces(number, total_length=16):
    num_str = str(number)
    print(num_str.rjust(total_length))
    return num_str.rjust(total_length)


def convert_table_to_text():
    table_data = []
    for row in tree.get_children():
        row_data = tree.item(row)['values']
        formatted_row = [add_leading_spaces(item) for item in row_data]
        table_data.append(" ".join(formatted_row))

    formatted_text = "\n".join(table_data)
    root.clipboard_clear()
    root.clipboard_append(formatted_text)
    copied_label.config(text="Formatted data copied to clipboard!")


root = tk.Tk()
root.title("ASCII to Table Converter")

# ASCIIデータを入力するテキストエリア
text_area = tk.Text(root, height=10, width=50)
text_area.pack(pady=10)

# 変換ボタン
convert_button = tk.Button(root, text="Convert", command=on_convert)
convert_button.pack(pady=5)

# クリップボードにコピーされたことを示すラベル
copied_label = tk.Label(root, text="")
copied_label.pack(pady=5)

# テーブル表示用のTreeviewウィジェット
columns = ("X", "Y")
tree = ttk.Treeview(root, columns=columns, show='headings')
tree.heading("X", text="X")
tree.heading("Y", text="Y")
tree.pack(pady=10)

# テーブルからテキストデータに変換してコピーするボタン
copy_button = tk.Button(root, text="Format and Copy",
                        command=convert_table_to_text)
copy_button.pack(pady=5)

root.mainloop()
