import logging
import os
import json

from PIL import Image, ImageTk
import pandas as pd
import cv2

import tkinter as tk
from tkinter import filedialog, ttk, Canvas, messagebox

import entryFrame
import movieFrame
import editFrame
        
class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("mainTest")
        self.geometry("1280x720")
        self.initialize_frames()

    def initialize_frames(self):
        #動画ファイルのディレクトリと大会番号が設定されているならば自動で動画ファイルのパスを設定する
        def update_movie_file_path(*args):
            if (self.movie_directory_entry_frame.var.get() and 
                self.excel_entry_frame.var_game_id.get()
            ):  

                self.movie_file_path_entry_frame.var.set(self.movie_directory_entry_frame.var.get()+
                    "/"+self.excel_entry_frame.var_game_id.get() + 
                    config["movie_extension"])
                
                self.movie_frame.path.set(self.movie_directory_entry_frame.var.get()+
                    "/"+self.excel_entry_frame.var_game_id.get() + 
                    config["movie_extension"])
            
        
        def synchronize_vars(source_var: tk.IntVar, target_var:tk.IntVar) -> None:
            if source_var.get() != target_var.get():
                target_var.set(source_var.get())
            return None
        
        def update_saved_file_name(game_id):
            self.editframe.save_frame.entry.delete(0, tk.END)
            self.editframe.save_frame.entry.insert(0, game_id+".json")       

        def update_game_id():
            current_index = self.excel_entry_frame.combobox.current()
            self.excel_entry_frame.combobox.current(current_index)

        with open("config.json", "r") as fp:
            config = json.load(fp)

        self.excel_entry_frame = entryFrame.EntryFrame(
            self,
            label_text="Excel File :",
            entry_text= config["excel_path"],
            button_text="Select"
        )
        self.excel_entry_frame.button.config(command=self.excel_entry_frame.set_excel_file)
        self.excel_entry_frame.reload_button = tk.Button(self.excel_entry_frame, text="reload", command=update_game_id)
        self.excel_entry_frame.reload_button.grid(row=0, column=4)
        self.movie_directory_entry_frame = entryFrame.EntryFrame(
            self,
            label_text="Movie Directory :",
            entry_text= config["movie_directory"],
            button_text="select"
        )
        self.movie_directory_entry_frame.button.config(command=self.movie_directory_entry_frame.set_directory)
        self.json_directory_entry_frame = entryFrame.EntryFrame(
            self,
            label_text="Json Directory :",
            entry_text= config["json_directory"],
            button_text="select"
        )
        self.json_directory_entry_frame.button.config(command=self.json_directory_entry_frame.set_directory)
        self.movie_file_path_entry_frame = entryFrame.EntryFrame(
            self,
            label_text="Movie path:",
            button_text="select",
        )
        self.movie_file_path_entry_frame.button.config(command= self.movie_file_path_entry_frame.set_movie_file_path)
        self.movie_frame = movieFrame.MovieFrame(self)

        #editframeの配置
        self.editframe = editFrame.EditFrame(self, data_path=self.json_directory_entry_frame.entry.get()+"/S10303.json")

        #各同期
        self.trace_ids = {}
        #動画パスの自動変更
        self.excel_entry_frame.set_excel_file(self.excel_entry_frame.entry.get())
        self.movie_directory_entry_frame.var.trace_add("write", update_movie_file_path)
        self.excel_entry_frame.var_game_id.trace_add("write", update_movie_file_path)
        
        #editframeを紐付け
        trace_id = self.excel_entry_frame.var_game_id.trace_add(
            "write",
            lambda *args:
                self.editframe.field_left.reset(
                    data_path=self.json_directory_entry_frame.entry.get()
                    +"/"
                    +self.excel_entry_frame.var_game_id.get()
                    +".json"
                )
        )
        self.trace_ids[trace_id] = self.excel_entry_frame.var_game_id
        trace_id = self.editframe.tick_frame.tick.trace_add(
            "write", 
            lambda *args: 
            synchronize_vars(
                source_var=self.editframe.tick_frame.tick, 
                target_var = self.movie_frame.tick
                )
        )
        self.trace_ids[trace_id] = self.editframe.tick_frame.tick
        trace_id = self.movie_frame.tick.trace_add(
            "write", 
            lambda *args: 
            synchronize_vars(
                source_var=self.movie_frame.tick, 
                target_var=self.editframe.tick_frame.tick
                )
        )
        self.trace_ids[trace_id] = self.movie_frame.tick
        self.excel_entry_frame.var_game_id.trace_add("write", lambda *args: update_saved_file_name(self.excel_entry_frame.var_game_id.get()))

        #ダウンロードの設定
        self.movie_frame.download_button.config(
            command=lambda *args:
                self.movie_frame.download_video(
                    game_id=self.excel_entry_frame.combobox.get(),
                    download_directory=self.movie_directory_entry_frame.entry.get(),
                    excel_path=self.excel_entry_frame.entry.get()
                )
        )
        
        #ウィジェットの配置
        self.excel_entry_frame.grid(row=0, column=0, padx=0, pady=0, sticky=tk.W)
        self.movie_directory_entry_frame.grid(row=1, column=0, padx=0, pady=0, sticky=tk.W)
        self.json_directory_entry_frame.grid(row=2, column=0, padx=0, pady=0, sticky=tk.W)
        self.movie_file_path_entry_frame.grid(row=3, column=0, sticky=tk.W)
        self.movie_frame.grid(row=4, column=0, padx=0, pady=0, sticky=tk.W)
        self.editframe.grid(row=4, column=1)

if __name__ == "__main__":
    logging.basicConfig(filename='error.log', level=logging.ERROR, format='%(asctime)s:%(levelname)s:%(message)s')
    app = Application()
    app.mainloop()