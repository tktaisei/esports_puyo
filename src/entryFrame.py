import logging
import json

import pandas as pd

import tkinter as tk
from tkinter import filedialog, ttk



class EntryFrame(tk.Frame): #パスの設定に関するウィジェットをまとめたクラス
    def __init__(
        self,
        master: tk.Frame=None,
        label_text: str="",
        entry_text: str="",
        button_text: str="",
        button_command=None,
        **kwargs
    ):
        super().__init__(master, **kwargs)
        self.label = tk.Label(self, text=label_text, width=15, anchor=tk.E)
        self.var = tk.StringVar(value=entry_text)
        self.entry = tk.Entry(self, textvariable=self.var, state="readonly", width=25)
        self.button = tk.Button(self, text=button_text, command=button_command)
        self.var_game_id = tk.StringVar()
        self.combobox = ttk.Combobox(self, textvariable=self.var_game_id, width=6)
        self.label.grid(row=0, column=0)
        self.entry.grid(row=0, column=1)
        self.button.grid(row=0, column=2)

    
    
    #動画ファイルパスを設定
    def set_movie_file_path(self):
        movie_file_path = filedialog.askopenfilename(filetypes=[("Webm files", "*.webm")])
        if movie_file_path:
            self.entry.config(state='normal')
            self.entry.delete(0, tk.END)
            self.entry.insert(0, movie_file_path)
            self.entry.config(state='readonly')

    #excelファイルを設定する
    def set_excel_file(self, file_path:str=None):

        def read_excel_file():

            def update_combobox():
                compe_id_column_data = df['compe_id']
                match_id_column_data = df['match_id']
                game_id_column_data = [
                    compe_id + f'{match_id:02d}'
                    for compe_id, match_id in zip(compe_id_column_data, match_id_column_data)
                ]
                self.combobox['values'] = game_id_column_data
                self.combobox.current(0)  # デフォルトで最初の項目を選択
            try:
                global df
                df = pd.read_excel(file_path)

                self.combobox.grid(row=0, column=3, padx=0, pady=0)
                update_combobox()

            except Exception as e:
                logging.error(f"excelの読み込み中にエラーが発生しました: {e}")
        
        if file_path: #インスタンス化用
            read_excel_file()
            return 
        
        else:
            file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx;*.xls")])
            if file_path:  # ファイルが選択された場合
                self.entry.config(state='normal')
                self.entry.delete(0, tk.END)  # 既存のパスをクリア
                self.entry.insert(0, file_path)  # 選択したファイルパスを入力
                self.entry.config(state='readonly')
                read_excel_file()  # Excelファイルを読み込む

    #ディレクトリを指定
    def set_directory(self):
        directory_path = filedialog.askdirectory()
        if directory_path:
            self.entry.config(state='normal')
            self.entry.delete(0, tk.END)
            self.entry.insert(0, directory_path)
            self.entry.config(state='readonly')

    #jsonファイルの読み込み
    def set_json_file(self):

        def read_json_file(file_path):
            def insert_items(parent, data, parent_name=''):
                if isinstance(data, dict):
                    for key, value in data.items():
                        # 辞書のキーを親ノードとして追加し、そのノードIDを取得
                        node = tree.insert(parent, 'end', text=str(key))
                        # 値が辞書またはリストなら再帰的に処理、親ノードの名前を伝達
                        insert_items(node, value, str(key))
                elif isinstance(data, list):
                    for i, item in enumerate(data):
                        # リスト内のアイテム用のノードを作成（親ノードの名前を使用）
                        node_text = f'{parent_name} {i}' if parent_name else f'Item {i}'
                        node = tree.insert(parent, 'end', text=node_text)
                        # アイテムが辞書またはリストなら再帰的に処理
                        insert_items(node, item, parent_name)
                else:
                    # 単純な値は直接子ノードとして追加
                    tree.insert(parent, 'end', text=str(data))

            tree = ttk.Treeview(self)  # Treeviewのインスタンスを作成
            with open(file_path, "r") as fp:
                data = json.load(fp)
                insert_items("", data)  # JSONデータをTreeviewに挿入
            tree.grid(row=0, column=5)  # Treeviewを配置
            self.tree = tree  # インスタンス変数にtreeを保存

        file_path = filedialog.askopenfilename(filetypes=[("Json files", "*.json")])
        if file_path:
            self.entry.config(state='normal')
            self.entry.delete(0, tk.END)
            self.entry.insert(0, file_path)
            self.entry.config(state='readonly')
            read_json_file(file_path)

class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("entryFrameTest")
        self.geometry("1280x720")
        self.initialize_frames()

    def initialize_frames(self):
        with open("config.json", "r") as fp:
            config = json.load(fp)
        self.excel_entry_frame = EntryFrame(
            self,
            label_text="Excel File :",
            entry_text= config["excel_path"],
            button_text="Select"
        )
        self.excel_entry_frame.button.config(command=self.excel_entry_frame.set_excel_file)
        self.movie_dorectory_entry_frame = EntryFrame(
            self,
            label_text= "Movie Directory :",
            entry_text= config["movie_directory"],
            button_text= "select"
        )
        self.movie_dorectory_entry_frame.button.config(command=self.movie_dorectory_entry_frame.set_directory)
        self.json_directory_entry_frame = EntryFrame(
            self,
            label_text="Json Directory :",
            entry_text= config["json_directory"],
            button_text="select"
        )
        self.json_directory_entry_frame.button.config(command=self.json_directory_entry_frame.set_directory)  
        self.json_entry_frame = EntryFrame(
            self,
            label_text="Json File :",
            button_text= "select"
        )
        self.json_entry_frame.button.config(command=self.json_entry_frame.set_json_file)

        self.excel_entry_frame.grid(row=0, column=0, padx=0, pady=0, sticky=tk.W)
        self.movie_dorectory_entry_frame.grid(row=1, column=0, padx=0, pady=0, sticky=tk.W)
        self.json_directory_entry_frame.grid(row=2, column=0, padx=0, pady=0, sticky=tk.W)
        self.json_entry_frame.grid(row=3, column=0, padx=0, pady=0, sticky=tk.W)
        
        self.excel_entry_frame.set_excel_file(self.excel_entry_frame.entry.get())


if __name__ == "__main__":
    app = Application()
    app.mainloop()