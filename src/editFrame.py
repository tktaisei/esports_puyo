import logging
import json
from itertools import chain
import bisect
from PIL import Image, ImageTk

import tkinter as tk
from tkinter import filedialog, ttk, Canvas, messagebox


class EditFrame(tk.Frame):
    def __init__(
        self, 
        master=None,
        data_path="../data/fieldJSON/S10605.json",
        output_directory="../data/outPuts",
        **kwargs
    ):
        super().__init__(master, **kwargs)
        if data_path:
            with open(data_path, "r") as fp:
                self.games = json.load(fp)

        #色選択用のフレーム
        self.color_selector = self.create_color_selector()

        #ゲームの勝者
        self.winner_frame = tk.Frame(self)
        selected_winner = tk.IntVar(value=0)
        self.winner_frame.label = tk.Label(self.winner_frame, text="勝者")
        self.winner_frame.winner_rb_0 = tk.Radiobutton(self.winner_frame, text=0, variable=selected_winner, value=0)
        self.winner_frame.winner_rb_1 = tk.Radiobutton(self.winner_frame, text=1, variable=selected_winner, value=1)
        self.winner_frame.label.grid(row=0, column=0)
        self.winner_frame.winner_rb_0.grid(row=0, column=1)
        self.winner_frame.winner_rb_1.grid(row=0, column=2)

        #現在のtickを管理するフレーム
        self.tick_frame = tk.Frame(self)
        self.tick_frame.tick = tk.IntVar(value=0)
        self.tick_frame.tick.trace_add("write", self.on_tick_change)#tickの変動をトリガーにfieldを設定
        self.tick_frame.label = tk.Label(self.tick_frame, text="tick : ")
        self.tick_frame.combobox = ttk.Combobox(self.tick_frame, textvariable=self.tick_frame.tick,width=5)
        self.tick_frame.step_forward_button = tk.Button(self.tick_frame, text="->", command=self.step_forward)
        self.tick_frame.step_back_button = tk.Button(self.tick_frame, text="<-", command=self.step_back)
        self.tick_frame.label.grid(row=0, column=0)
        self.tick_frame.combobox.grid(row=0, column=1)
        self.tick_frame.step_back_button.grid(row=0, column=2)
        self.tick_frame.step_forward_button.grid(row=0, column=3)

        #1p, 2p盤面
        self.FieldFrame.set_games(games=self.games)
        self.field_left = self.FieldFrame(master=self, tick_combobox=self.tick_frame.combobox, side_selection="left")
        self.field_right = self.FieldFrame(master=self, tick_combobox=self.tick_frame.combobox, side_selection="right")
    
        #ファイル保存フレーム
        self.save_frame = tk.Frame(self)
        self.save_frame.label = tk.Label(self.save_frame, text="ファイル名")
        self.save_frame.file_name = tk.StringVar(value=data_path.split("/")[-1])
        self.save_frame.output_directory = output_directory
        self.save_frame.entry = tk.Entry(self.save_frame, textvariable=self.save_frame.file_name)
        self.save_frame.button = tk.Button(self.save_frame, text="保存", command=self.save_file)
        self.save_frame.label.grid(row=0, column=0)
        self.save_frame.entry.grid(row=0, column=1)
        self.save_frame.button.grid(row=0, column=2)

        self.tick_frame.grid(row=0, column=0, sticky=tk.W)
        self.field_left.grid(row=1, column=0, sticky=tk.W)
        self.field_right.grid(row=1, column=1, sticky=tk.W)
        self.color_selector.grid(row=2, column=0, columnspan=2, sticky=tk.W)
        self.save_frame.grid(row=3, column=0, sticky=tk.W)

    def on_tick_change(self, *args) -> None:
            '''
                tickの変動をトリガーにしてdraw_field, get_game_numbersを実行するラッパーメソッド

            '''

            EditFrame.FieldFrame.set_tick(self.tick_frame.tick.get())

    def create_color_selector(self) -> tk.Frame:
        '''
            色選択ラジオボタンを生成

            return:
        '''
        self.selected_color = tk.StringVar()
        self.selected_color.trace_add("write", lambda *args: EditFrame.FieldFrame.set_selected_color(color = self.selected_color.get()))
        color_selector = tk.Frame(self)
        self.image_paths = {
            "red": "../data/images/red.png",
            "blue": "../data/images/blue.png",
            "green": "../data/images/green.png",
            "yellow": "../data/images/yellow.png",
            "purple": "../data/images/purple.png",
            "ojama": "../data/images/ojama.png",
            "back": "../data/images/back.png",
        }
        # 初期選択色
        self.selected_color.set("red")
        self.images = {}
        for color in self.image_paths:
            image = Image.open(self.image_paths[color])
            resized_image = image.resize((17, 17), Image.Resampling.LANCZOS)
            self.images[color] = ImageTk.PhotoImage(resized_image)
            rb = tk.Radiobutton(color_selector, image=self.images[color], variable=self.selected_color, value=color)
            rb.pack(side="left") 
        return color_selector
    
    def step_forward(self) -> None:
        '''
        コンボボックスのインデックスを1増やす

        Returns: None
        '''
        current_index = self.tick_frame.combobox.current()
        if len(self.tick_frame.combobox["values"]) - 1 == current_index:
            return
        else: 
            self.tick_frame.combobox.current(current_index+1)
            return
    
    def step_back(self) -> None:
        '''
        コンボボックスのインデックスを1減らす

        Returns: None
        '''
        current_index = self.tick_frame.combobox.current()
        if current_index == 0:
            return
        else: 
            self.tick_frame.combobox.current(current_index-1)
            return
        
    def save_file(self) -> None:
        name = self.save_frame.entry.get()
        self.field_left.save_games(self.save_frame.output_directory, name)
        return
    
            
    class FieldFrame(tk.Frame):
        images = None
        selected_color = "red"
        tick = 0
        games = None
        callbacks = []
        #TODO: tickに連動してdraw_field

        @classmethod
        def load_images(cls) -> None:
            image_paths = {
            "red": "../data/images/red.png",
            "blue": "../data/images/blue.png",
            "green": "../data/images/green.png",
            "yellow": "../data/images/yellow.png",
            "purple": "../data/images/purple.png",
            "ojama": "../data/images/ojama.png",
            "back": "../data/images/back.png",
        }
            if cls.images is None:
                cls.images = {}
                for color in image_paths:
                    image = Image.open(image_paths[color])
                    resized_image = image.resize((17, 17), Image.Resampling.LANCZOS)
                    cls.images[color] = ImageTk.PhotoImage(resized_image)
            return
            
        @classmethod
        def set_selected_color(cls, color:"str", *args) -> None:
            cls.selected_color = color
            return
        
        @classmethod
        def set_tick(cls, tick:int):
            cls.tick = tick
            for callback in cls.callbacks:
                callback()
            return

        @classmethod
        def set_games(cls, games:dict) -> None:
            cls.games = games

        @classmethod
        def save_games(cls, output_directory:str, name:str) -> None:
            with open(output_directory+"/"+name, "w") as f:
                json.dump(cls.games, f, indent=4)
            return

        @classmethod
        def add_callback_function(cls, callback):
            cls.callbacks.append(callback)

        def __init__(
            self, 
            tick_combobox:ttk.Combobox,
            master=None,
            side_selection:str="left",
            **kwargs
        ):
            super().__init__(master, **kwargs)

            #変数の初期化
            self.load_images()
            if side_selection == "left":
                self.side_selection = 0
            else:
                self.side_selection = 1
            self.combobox = tick_combobox
            self.images = {}  # 辞書を使用して画像オブジェクトを保持
            self.game_no = 0
            self.field_no = 0

            #ページ読み込み時のコールバック関数の追加
            EditFrame.FieldFrame.add_callback_function(self.set_game_ids)
            EditFrame.FieldFrame.add_callback_function(self.draw_field)
            EditFrame.FieldFrame.add_callback_function(self.set_selected_state)
            EditFrame.FieldFrame.add_callback_function(self.set_selected_allclear)
            
            #現在のgame_no, field_no表示
            self.ids_frame = tk.Frame(self)
            self.ids_frame.game_no_label = tk.Label(self.ids_frame, text="ゲーム")
            self.ids_frame.field_no_label = tk.Label(self.ids_frame, text="盤番号")
            self.ids_frame.tick_label = tk.Label(self.ids_frame, text="tick")
            self.ids_frame.game_no_entry = tk.Entry(self.ids_frame, width=5)
            self.ids_frame.field_no_entry= tk.Entry(self.ids_frame, width=5)
            self.ids_frame.tick_entry = tk.Entry(self.ids_frame, width=5)
            self.ids_frame.delete_button = tk.Button(self.ids_frame, text="削除", command=self.delete_field)
            self.ids_frame.set_new_tick_button = tk.Button(self.ids_frame, text="変更", command=self.set_new_tick)
            self.ids_frame.insert_button = tk.Button(self.ids_frame, text="挿入", command=self.insert_field)
            self.ids_frame.game_no_label.grid(row=0, column=0)
            self.ids_frame.field_no_label.grid(row=0, column=1)
            self.ids_frame.tick_label.grid(row=0, column=2)
            self.ids_frame.game_no_entry.grid(row=1, column=0)
            self.ids_frame.field_no_entry.grid(row=1, column=1)
            self.ids_frame.tick_entry.grid(row=1, column=2)
            self.ids_frame.set_new_tick_button.grid(row=2, column=0, sticky=tk.W)
            self.ids_frame.delete_button.grid(row=2, column=1, sticky=tk.W)
            self.ids_frame.insert_button.grid(row=2, column=2, sticky=tk.W)

            #ゲームの状態を選択するフレーム
            self.state_frame = tk.Frame(self)
            self.state_frame.selected_state = tk.IntVar(value=0)
            self.state_frame.selected_state.trace_add("write", self.on_selected_state_change)
            self.state_frame.label = tk.Label(self.state_frame, text="状態")
            self.state_frame.state_rb_set = tk.Radiobutton(self.state_frame, text="set", variable=self.state_frame.selected_state, value=0)
            self.state_frame.state_rb_rensa = tk.Radiobutton(self.state_frame, text="rensa", variable=self.state_frame.selected_state, value=1)
            self.state_frame.label.grid(row=0, column=0)
            self.state_frame.state_rb_set.grid(row=0, column=1)
            self.state_frame.state_rb_rensa.grid(row=0, column=2)

            #全消し状態か選択するフレーム
            self.allclear_frame = tk.Frame(self)
            self.allclear_frame.selected_allclear = tk.IntVar(value=0)
            self.allclear_frame.selected_allclear.trace_add("write", self.on_selected_allclear_change)
            self.allclear_frame.label = tk.Label(self.allclear_frame, text="全消し")
            self.allclear_frame.allclear_rb_false = tk.Radiobutton(self.allclear_frame, text="False", variable=self.allclear_frame.selected_allclear, value=0)
            self.allclear_frame.allclear_rb_true = tk.Radiobutton(self.allclear_frame, text="True", variable=self.allclear_frame.selected_allclear, value=1)
            self.allclear_frame.label.grid(row=0, column=0)
            self.allclear_frame.allclear_rb_false.grid(row=0, column=1)
            self.allclear_frame.allclear_rb_true.grid(row=0, column=2)
        
            #盤面
            self.field_frame= self.create_board()
            self.update_combobox()
            self.combobox.current(0)

            #フレームの配置
            self.ids_frame.grid(row=0, column=0, sticky=tk.W)
            self.state_frame.grid(row=1, column=0, sticky=tk.W)
            self.allclear_frame.grid(row=2, column=0, sticky=tk.W)
            self.field_frame.grid(row=3, column=0, sticky=tk.W)

        def reset(self, data_path):
            EditFrame.FieldFrame.tick = 0
            with open(data_path, "r") as fp:
                self.games = json.load(fp)
                EditFrame.FieldFrame.set_games(self.games)
            self.update_combobox()
            self.combobox.current(0)

        def get_tick(self) -> int:
            return EditFrame.FieldFrame.tick
        
        def get_field(self) -> list:
            return EditFrame.FieldFrame.games["games"][self.game_no]["fields"][self.side_selection][self.field_no]["field"]
        
        def get_game_ids(self) -> tuple:
            return self.game_no, self.field_no
               
        def set_selected_state(self) -> None:
            game_no, field_no = self.get_game_ids()
            if self.games["games"][game_no]["fields"][self.side_selection][field_no]["rensa"]:
                self.state_frame.selected_state.set(1)
            else:
                self.state_frame.selected_state.set(0)

        def set_selected_allclear(self) -> None:
            game_no, field_no = self.get_game_ids()
            if "allclear" not in self.games["games"][game_no]["fields"][self.side_selection][field_no]:
                self.games["games"][game_no]["fields"][self.side_selection][field_no]["allclear"] = False
                return None
            if self.games["games"][game_no]["fields"][self.side_selection][field_no]["allclear"]:
                self.allclear_frame.selected_allclear.set(1)
            else:
                self.allclear_frame.selected_allclear.set(0)

        def set_game_ids(self) -> None:

            """
            tick_frameの値が変更されたとき, 対応するgame_no, field_noを検索する.

            左右で番号が違う場合は試合が終了している可能性があるので注意すること.
            
            """
            tick = self.get_tick()
            last_reference_game_no = self.game_no
            last_reference_field_no = self.field_no
            for game_no, game in enumerate(self.games["games"]):
                for field_no, field in enumerate(game["fields"][self.side_selection]):
                    if field["tick"] > tick:
                        if field_no != 0:
                            field_no -= 1
                        self.game_no = game_no
                        self.field_no = field_no

                        if last_reference_field_no != self.field_no or last_reference_game_no != self.game_no:
                            self.config(highlightbackground="#999999", highlightcolor="#999999", highlightthickness=3)
                        else:
                            self.config(highlightbackground="#E5E5E5", highlightcolor="#E5E5E5", highlightthickness=3)
                        self.ids_frame.game_no_entry.delete(0, tk.END)
                        self.ids_frame.game_no_entry.insert(0, game_no)
                        self.ids_frame.field_no_entry.delete(0, tk.END)
                        self.ids_frame.field_no_entry.insert(0, field_no)
                        self.ids_frame.tick_entry.delete(0, tk.END)
                        self.ids_frame.tick_entry.insert(0, game["fields"][self.side_selection][field_no]["tick"])
                        return
            
        def set_new_tick(self):
            game_no, field_no = self.get_game_ids()
            new_tick = int(self.ids_frame.tick_entry.get())
            self.games["games"][game_no]["fields"][self.side_selection][field_no]["tick"] = new_tick
            self.update_combobox()
            deleted_index = self.combobox["values"].index(str(new_tick))
            self.combobox.current(deleted_index)
            return None

        
        def insert_field(self) -> None:
            """
            fieldをself.gamesに挿入する
            """
            tick = self.ids_frame.tick_entry.get()
            game_no = int(self.ids_frame.game_no_entry.get())
            field_no = int(self.ids_frame.field_no_entry.get())
            side_selection = self.side_selection
            if tick in self.combobox["values"]:
                print(f'the tick:{tick} is already exist.')
                return None
            if field_no != 0:
                if int(tick) <=  self.games["games"][game_no]["fields"][side_selection][field_no-1]["tick"]:
                    messagebox.showerror("ValueError", "挿入するtickは1手前のtickより大きい必要があります")
                    return None
            if field_no < len(self.games["games"][game_no]["fields"][side_selection])-1:
                if int(tick) >=  self.games["games"][game_no]["fields"][side_selection][field_no]["tick"]:
                    messagebox.showerror("ValueError", "挿入するtickは1手先のtickより小さい必要があります")
                    return None
            inserted_field = {"tick":int(tick), "rensa":False, "field":[[color for color in row] for row in self.games["games"][game_no]["fields"][side_selection][field_no]["field"]]}
            EditFrame.FieldFrame.games["games"][game_no]["fields"][side_selection].insert(field_no, inserted_field)
            for field in self.games["games"][game_no]["fields"][side_selection][:field_no+2]:
                print(field)
            self.update_combobox()
            deleted_index = self.combobox["values"].index(str(tick))
            self.combobox.current(deleted_index)
            return
        
        def delete_field(self) -> None:
            game_no = int(self.ids_frame.game_no_entry.get())
            field_no = int(self.ids_frame.field_no_entry.get())
            tick = self.games["games"][game_no]["fields"][self.side_selection][field_no]["tick"]
            deleted_index = self.combobox["values"].index(str(tick))
            EditFrame.FieldFrame.games["games"][game_no]["fields"][self.side_selection].pop(field_no)
            self.update_combobox()
            self.combobox.current(deleted_index)
            return None
        
        def on_selected_state_change(self, *args) -> None:
            game_no, field_no = self.get_game_ids()
            state = self.state_frame.selected_state.get()

            if state == 0:
                self.games["games"][game_no]["fields"][self.side_selection][field_no]["rensa"] = False
                return None
            else:
                self.games["games"][game_no]["fields"][self.side_selection][field_no]["rensa"] = True
                return None
            
        def on_selected_allclear_change(self, *args) -> None:
            game_no, field_no = self.get_game_ids()
            allclear = self.allclear_frame.selected_allclear.get()

            if allclear == 0:
                self.games["games"][game_no]["fields"][self.side_selection][field_no]["allclear"] = False
                return None
            else:
                self.games["games"][game_no]["fields"][self.side_selection][field_no]["allclear"] = True
                return None

        def create_board(self, width:int=6, hight:int=12) -> tk.Frame:
            puyo_field = tk.Frame(self, borderwidth=1, relief="solid")
            puyo_field.canvas_dict = {}
            for row in range(hight):
                for col in range(width):
                    canvas = tk.Canvas(puyo_field, borderwidth=1, relief="groove", width=17, height=17)
                    canvas.color = tk.StringVar(value="back")
                    canvas.grid(row=row, column=col, padx=0, pady=0, sticky=tk.NW)
                    canvas.bind("<Button-1>", lambda e, r=row, c=col: self.on_panel_click(r, c))
                    puyo_field.canvas_dict[(row, col)] = canvas 

            return puyo_field

        
        #描画とfieldの書き換え
        def on_panel_click(self, row:int, column:int) -> None:
            color = self.selected_color
            self.update_field_canvas(row, column, color)
            self.update_games_field(row, column, color)
            return
        
        #盤面の描画
        def draw_field(self):
            colors = ["red", "yellow", "green", "blue", "purple", "ojama", "back"]
            for i, row in enumerate(self.get_field()):
                print(row)
                for j, cell in enumerate(row):
                    if cell is None:
                        color = "back"
                    else:
                        color = colors[cell]         
                    self.update_field_canvas(i, j, color)
            print("------------------------------")
            return

        def update_field_canvas(self, row:int, column:int, color:str) -> None:
            photo = EditFrame.FieldFrame.images[color]
            self.field_frame.canvas_dict[(row, column)].color = color
            self.field_frame.canvas_dict[(row, column)].image = photo
            self.field_frame.canvas_dict[(row, column)].delete("all")
            self.field_frame.canvas_dict[(row, column)].create_image(11, 11, image=photo)

        
        def update_games_field(self, row:int, column:int, color:str) -> None:
            colors = ["red", "yellow", "green", "blue", "purple", "ojama", "back"]
            if color == "back":
                color = None
            else:
                color = colors.index(color)
            self.games["games"][self.game_no]["fields"][self.side_selection][self.field_no]["field"][row][column] = color
            return
        
        def update_combobox(self):
            left_tick_list = [int(field["tick"]) for game in self.games["games"] for field in game["fields"][0]]
            right_tick_list = [int(field["tick"]) for game in self.games["games"] for field in game["fields"][1]]
            self.combobox['values'] = sorted(list(set(left_tick_list + right_tick_list)))
    

class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("movieFrameTest")
        self.geometry("640x720")
        self.initialize_frames()
    
    def initialize_frames(self):
        editframe = EditFrame(self)
        editframe.grid(row=0, column=0)
        

if __name__ == "__main__":
    logging.basicConfig(filename='error.log', level=logging.ERROR, format='%(asctime)s:%(levelname)s:%(message)s')
    app = Application()
    app.mainloop()



