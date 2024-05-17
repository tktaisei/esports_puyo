import logging
import os
import json

from PIL import Image, ImageTk
import pandas as pd
import cv2
import yt_dlp
import tkinter as tk
from tkinter import filedialog, ttk, Canvas, messagebox

import entryFrame

class MovieFrame(tk.Frame):

    def __init__(
        self, 
        master=None,
        path:str=None,
        go_forward_one_frame_button_text: str="+1",
        go_back_one_frame_button_text: str="-1",
        skip_movie_button_text: str="SKIP", 
        **kwargs
    ):
        super().__init__(master, **kwargs)

        #動画情報の保持
        self.path = tk.StringVar(value=path)
        self.canvas = tk.Canvas(self, width=640, height=360)
        self.canvas.frame = None
        self.cap = None
        self.tick = tk.IntVar(value=0)

        #動画操作ウィジェット
        self.scale = tk.Scale(
            self, 
            from_=0,
            to=0,
            orient=tk.HORIZONTAL,
            command=self.on_scale,
            length=640
        )
        self.load_button = tk.Button(
            self,
            text = "load",
            command = self.on_load_movie_button_clicked
        )

        self.download_button = tk.Button(
            self,
            text= "download",
            command=self.download_video
        )
        self.go_forward_one_frame_button = tk.Button(
            self,
            text=go_forward_one_frame_button_text,
            command=self.on_go_forward_one_frame_button_clicked
        )
        self.go_back_one_frame_button = tk.Button(
            self,
            text=go_back_one_frame_button_text,
            command=self.on_go_back_one_frame_button_clicked
        )
        self.skip_movie_button = tk.Button(
            self,
            text=skip_movie_button_text,
            command=self.on_skip_movie_button_clicked
        )
        self.skip_movie_entry = tk.Entry(self, width=5)
        
        #tickの変動と関数をバインド
        self.tick.trace_add("write", self.update_scale)
        self.tick.trace_add("write", self.update_canvas)

        # #マウスホイールの回転でコマ送りを実行
        # self.bind("<MouseWheel>", self.on_mousewheel)
        # self.bind("<Button-1>", lambda event: self.focus_set())

        #読み込みボタンの配置
        self.load_button.grid(row=0, column=0)
        self.download_button.grid(row=0, column=1)
    
    def download_video(self, game_id, download_directory, excel_path) -> None:
        # ダウンロードオプションの設定
        ydl_opts = {
            'format': 'best',  # 最高品質のフォーマットを選択
            'outtmpl': f'{download_directory}/{game_id}.%(ext)s',  # ダウンロードしたファイルのフォーマット
            'noplaylist': True,  # プレイリストではなく、単一のビデオのみをダウンロード
        }
        
        #Excelファイルを読み込む
        df = pd.read_excel(excel_path)

        # A列とC列を結合して新しいIDを作成
        df['new_id'] = df['compe_id'].astype(str) + df['match_id'].apply(lambda x: f'{x:02}')

        # game_idと一致する行を検索
        matching_row = df[df['new_id'] == game_id]

        # 一致する行のD列の値を返す
        url = matching_row.iloc[0]['URL']

        # yt-dlpのインスタンスを作成し、ビデオをダウンロード
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
            
    def on_mousewheel(self, event):
        # Windowsの場合は event.delta、MacやLinuxの場合は event.deltaY を使用
        delta = event.delta if os.name == 'nt' else event.deltaY
        print("Mouse wheel:", delta)

    #動画ファイルを読み込む
    def on_load_movie_button_clicked(self):
        try:
            if not os.path.isfile(self.path.get()):
                raise FileNotFoundError(f"File not found.")
            cap = cv2.VideoCapture(self.path.get())
            ret, frame = cap.read()
            if not cap.isOpened():
                raise IOError("the video could not be opened.")
                
            if not ret:
                raise ValueError("Failed to load first frame")
            
            self.cap= cap
            self.frame = frame
            self.tick.set(0)
            self.scale.config(to=int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT)) - 1)
            
            self.canvas.grid(row=1, column=0, columnspan=4)
            self.scale.grid(row=2, column=0, columnspan=4)
            self.go_back_one_frame_button.grid(row=3, column=0)
            self.go_forward_one_frame_button.grid(row=3, column=1)
            self.skip_movie_entry.grid(row=3, column=2)
            self.skip_movie_button.grid(row=3, column=3)
            
        except FileNotFoundError as e:
            logging.error(f"FileNotFound: {e}")
            messagebox.showerror("FileNotFound", e)

        except IOError as e:
            logging.error(f"IOError: {e}")
            messagebox.showerror("IOError", e)

        except ValueError as e:
            logging.error(f"ValueError: {e}")
            messagebox.showerror("ValueError", e)

        except Exception as e:
            logging.error(f"An unexpected error has occurred. Details: {e}")
            messagebox.showerror("An unexpected error has occurred", e)
            
    #1コマ進める
    def on_go_forward_one_frame_button_clicked(self):
        if self.tick.get() == int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT)) - 1:
            return
        self.tick.set(self.tick.get() + 1)

    #1コマ戻す
    def on_go_back_one_frame_button_clicked(self):
        if self.tick.get() == 0:
            return
        self.tick.set(self.tick.get() - 1)

    #指定したtickまで飛ばす
    def on_skip_movie_button_clicked(self):
        try:
            entry_value = int(self.skip_movie_entry.get())
            if self.cap and entry_value:              
                if entry_value < 0:
                    raise ValueError(f"The input value must be a non-negative integer: {entry_value}")
                
                self.tick.set(min(int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT)) - 1, int(entry_value)))


        except ValueError as e:
            logging.error(f"valueerror: {e}")
            messagebox.showerror("ValueError", f"The input value must be a non-negative integer\n{e}")
        
        except Exception as e:
            logging.error(f"An unexpected error has occurred. Details: {e}")
            messagebox.showerror("Exception", e)

    #シークバー
    def on_scale(self, val):
        self.tick.set(int(val))

    #tickの変動をscaleに反映
    def update_scale(self, *args):
        self.scale.set(self.tick.get())

    #tickの変動をcanvasに反映
    def update_canvas(self, *args):

        # 動画から指定フレームを読み込む関数
        def load_frame(cap: cv2.VideoCapture, tick: int):
            cap.set(cv2.CAP_PROP_POS_FRAMES, tick)
            ret, frame = cap.read()
            if ret:
                frame = cv2.resize(frame, (640,360))
                return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # RGBに変換
            else:
                cap.release()
                return None
            
        image = load_frame(self.cap, self.tick.get())
        if type(image) != None:
            image = Image.fromarray(image)
            photo_image = ImageTk.PhotoImage(image=image)
            self.canvas.delete("all")
            self.canvas.frame=photo_image
            self.canvas.create_image(0, 0, anchor=tk.NW, image=photo_image)


class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("movieFrameTest")
        self.geometry("1280x720")
        self.initialize_frames()


    def initialize_frames(self):

        #動画ファイルのディレクトリと大会番号が設定されているならば自動で動画ファイルのパスを設定する
        def update_movie_file_path(*args):
            if (self.movie_directory_entry_frame.var.get() and 
                self.excel_entry_frame.var_game_id.get()
            ):
                self.movie_file_path_entry_frame.var.set(os.path.join(
                    self.movie_directory_entry_frame.var.get(), 
                    "/"+self.excel_entry_frame.var_game_id.get() + ".webm")
                )
                self.movie_frame.path.set(os.path.join(
                    self.movie_directory_entry_frame.var.get(),
                    "/"+self.excel_entry_frame.var_game_id.get() + ".webm")
                )

        with open("config.json", "r") as fp:
            config = json.load(fp)
        self.excel_entry_frame = entryFrame.EntryFrame(
            self,
            label_text="Excel File :",
            entry_text= config["excel_path"],
            button_text="Select"
        )
        self.excel_entry_frame.button.config(command=self.excel_entry_frame.set_excel_file)
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
        self.json_entry_frame = entryFrame.EntryFrame(
            self,
            label_text="Json File :",
            button_text= "select"
        )
        self.json_entry_frame.button.config(command=self.json_entry_frame.set_json_file)
        self.movie_file_path_entry_frame = entryFrame.EntryFrame(
            self,
            label_text="Movie path:",
            button_text="select",
        )
        self.movie_file_path_entry_frame.button.config(command= self.movie_file_path_entry_frame.set_movie_file_path)
        self.movie_frame = MovieFrame(self)

        #動画パスの自動変更
        self.excel_entry_frame.set_excel_file(self.excel_entry_frame.entry.get())
        self.movie_directory_entry_frame.var.trace_add("write", update_movie_file_path)
        self.excel_entry_frame.var_game_id.trace_add("write", update_movie_file_path)

        #ウィジェットの配置
        self.excel_entry_frame.grid(row=0, column=0, padx=0, pady=0, sticky=tk.W)
        self.movie_directory_entry_frame.grid(row=1, column=0, padx=0, pady=0, sticky=tk.W)
        self.json_directory_entry_frame.grid(row=2, column=0, padx=0, pady=0, sticky=tk.W)
        self.json_entry_frame.grid(row=3, column=0, padx=0, pady=0, sticky=tk.W)
        self.movie_file_path_entry_frame.grid(row=4, column=0, sticky=tk.W)
        self.movie_frame.grid(row=5, column=0, padx=0, pady=0, sticky=tk.W)



        
        
if __name__ == "__main__":
    logging.basicConfig(filename='error.log', level=logging.ERROR, format='%(asctime)s:%(levelname)s:%(message)s')
    app = Application()
    app.mainloop()