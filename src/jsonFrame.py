import logging
import json
from itertools import chain

from PIL import Image, ImageTk

import tkinter as tk
from tkinter import filedialog, ttk, Canvas, messagebox


class FieldFrame(tk.Frame):

    def __init__(
        self, 
        master=None,
        data_path="../data/fieldJSON/S10605.json",
        output_directory="../data/outPuts/",
        **kwargs
    ):
        super().__init__(master, **kwargs)
        
        if data_path:
            with open(data_path, "r") as fp:
                self.games = json.load(fp)

        #ゲーム情報
        
        #left
        #左右選択
        self.side_selection_frame = tk.Frame(self)
        self.side_selection_frame.side_selection = tk.StringVar(value="left")
        self.side_selection_frame.side_selection_rb_right = tk.Radiobutton(self.side_selection_frame, text="right", variable=self.side_selection_frame.side_selection, value="right")
        self.side_selection_frame.side_selection_rb_left = tk.Radiobutton(self.side_selection_frame, text="left", variable=self.side_selection_frame.side_selection, value="left")

        #ウィジェットの配置
        self.side_selection_frame.side_selection_rb_left.grid(row=0, column=1)
        self.side_selection_frame.side_selection_rb_right.grid(row=0, column=2)

        #fieldを挿入
        self.insert_frame = tk.Frame(self)
        self.insert_frame.label = tk.Label(self.insert_frame, text="挿入")
        self.insert_frame.entry = tk.Entry(self.insert_frame)
        self.insert_frame.button = tk.Button(self.insert_frame, text="挿入", command=self.insert_field)

        #ウィジェットの配置
        self.insert_frame.label.grid(row=0, column=0)
        self.insert_frame.entry.grid(row=0, column=3)
        self.insert_frame.button.grid(row=0, column=4)

        #ゲームの状態を選択するフレーム
        self.state_frame = tk.Frame(self)
        self.state_frame.selected_state = tk.IntVar(value=0)#のちにjsonから代入するようにすること
        self.state_frame.selected_state.trace_add("write", self.on_selected_state_change)
        self.state_frame.label = tk.Label(self.state_frame, text="状態")
        self.state_frame.state_rb_set = tk.Radiobutton(self.state_frame, text="set", variable=self.state_frame.selected_state, value=0)
        self.state_frame.state_rb_rensa = tk.Radiobutton(self.state_frame, text="rensa", variable=self.state_frame.selected_state, value=1)
        
        
        #ウィジェットの配置
        self.state_frame.label.grid(row=0, column=0)
        self.state_frame.state_rb_set.grid(row=0, column=1)
        self.state_frame.state_rb_rensa.grid(row=0, column=2)

        #ゲームの勝者
        self.winner_frame = tk.Frame(self)
        selected_winner = tk.IntVar(value=0)
        self.winner_frame.label = tk.Label(self.winner_frame, text="勝者")
        self.winner_frame.winner_rb_0 = tk.Radiobutton(self.winner_frame, text=0, variable=selected_winner, value=0)
        self.winner_frame.winner_rb_1 = tk.Radiobutton(self.winner_frame, text=1, variable=selected_winner, value=1)

        #ウィジェットの配置
        self.winner_frame.label.grid(row=0, column=0)
        self.winner_frame.winner_rb_0.grid(row=0, column=1)
        self.winner_frame.winner_rb_1.grid(row=0, column=2)

        #全消し状態か選択するフレーム
        self.zenkeshi_frame = tk.Frame(self)
        selected_zenkeshi = tk.IntVar(value=0)#のちにjsonから代入するようにすること
        self.images = {}  # 辞書を使用して画像オブジェクトを保持
        self.zenkeshi_frame.label = tk.Label(self.zenkeshi_frame, text="全消し")
        self.zenkeshi_frame.zenkeshi_rb_false = tk.Radiobutton(self.zenkeshi_frame, text="False", variable=selected_zenkeshi, value=0)
        self.zenkeshi_frame.zenkeshi_rb_true = tk.Radiobutton(self.zenkeshi_frame, text="True", variable=selected_zenkeshi, value=1)

        #ウィジェットの配置
        self.zenkeshi_frame.label.grid(row=0, column=0)
        self.zenkeshi_frame.zenkeshi_rb_false.grid(row=0, column=1)
        self.zenkeshi_frame.zenkeshi_rb_true.grid(row=0, column=2)
    
        #盤面
        self.selected_color = tk.StringVar()
        self.color_selector_frame = self.create_color_selector()
        self.field_frame = tk.Frame(self)
        self.field_frame.left = self.create_field(self.field_frame, "left")
        self.field_frame.right = self.create_field(self.field_frame, "right")

        #ウィジェットの配置
        self.field_frame.left.grid(row=0, column=0, padx=10)
        self.field_frame.right.grid(row=0, column=1)

        #現在のtickを管理するフレーム
        self.tick_frame = tk.Frame(self)
        self.tick_frame.tick = tk.IntVar(value=0)
        self.tick_frame.tick.trace_add("write", self.on_tick_change)#tickの変動をトリガーにfieldを設定
        self.tick_frame.label = tk.Label(self.tick_frame, text="tick")
        self.tick_frame.combobox = ttk.Combobox(self.tick_frame, textvariable=self.tick_frame.tick,width=5)
        self.tick_frame.step_forward_button = tk.Button(self.tick_frame, text="->", command=self.step_forward)
        self.tick_frame.step_back_button = tk.Button(self.tick_frame, text="<-", command=self.step_back)

        #ウィジェットの配置
        self.tick_frame.label.grid(row=0, column=0)
        self.tick_frame.combobox.grid(row=0, column=1)
        self.tick_frame.step_back_button.grid(row=0, column=2)
        self.tick_frame.step_forward_button.grid(row=0, column=3)
        self.update_combobox()

        #ファイル保存
        self.save_frame = tk.Frame(self)
        self.save_frame.label = tk.Label(self.save_frame, text="ファイル名")
        self.save_frame.file_name = tk.StringVar(value=data_path.split("/")[-1])
        self.save_frame.output_directory = output_directory
        self.save_frame.entry = tk.Entry(self.save_frame, textvariable=self.save_frame.file_name)
        self.save_frame.button = tk.Button(self.save_frame, text="保存", command=self.save_file)
        self.save_frame.label.grid(row=0, column=0)
        self.save_frame.entry.grid(row=0, column=1)
        self.save_frame.button.grid(row=0, column=2)

        #フレームの配置
        self.side_selection_frame.grid(row=0, column=0, sticky=tk.W)
        self.insert_frame.grid(row=1, column=0, sticky=tk.W)
        self.tick_frame.grid(row=2, column=0, sticky=tk.W)
        self.state_frame.grid(row=3, column=0, sticky=tk.W)
        self.winner_frame.grid(row=4, column=0, sticky=tk.W)
        self.zenkeshi_frame.grid(row=5, column=0, sticky=tk.W)
        self.color_selector_frame.grid(row=6, column=0, sticky=tk.W)
        self.field_frame.grid(row=7, column=0, sticky=tk.W)
        self.save_frame.grid(row=8, column=0)

    def insert_field(self) -> None:
        """
        fieldをself.gamesに挿入する. その際にinsert_frame.tick, side_selection_frame.side_selectionの値を使用する
        """

        tick = int(self.insert_frame.entry.get())
        side_selection = self.side_selection_frame.side_selection.get()
        inserted_field = {"tick":tick, "rensa":False, "field":[[None]*6 for _ in range(12)]}
        if side_selection == "left":
            for game_no, game in enumerate(self.games["games"]):
                for field_no, field in enumerate(game["fields"][0]):
                    if field["tick"] > tick:
                        self.games["games"][game_no]["fields"][0].insert(field_no, inserted_field)
                        self.update_combobox(tick)
                        return
            self.games["games"][game_no]["fields"][0].insert(field_no, inserted_field)
            self.update_combobox(tick)
            return
        if side_selection == "right":
            for game_no, game in enumerate(self.games["games"]):
                for field_no, field in enumerate(game["fields"][1]):
                    if field["tick"] > tick:
                        self.games["games"][game_no]["fields"][1].insert(field_no, inserted_field)
                        self.update_combobox(tick)
                        return
            self.games["games"][game_no]["fields"][1].insert(field_no, inserted_field)
            self.update_combobox(tick)
            return

    def on_selected_state_change(self) -> None:
        # TODO: selected_stateの値が変更されたときjsonファイルの対応するtickの辞書にselected_stateの値を記録する
        pass
    
    def on_tick_change(self, *args) -> None:
        '''
            tickの変動をトリガーにしてset_field, get_game_numbersを実行するラッパーメソッド

        '''
        self.set_field()
        self.game_no_left, self.field_no_left, self.game_no_right, self.field_no_right = self.get_game_numbers()

    def get_game_numbers(self) -> tuple[int, int, int, int]:
        #TODO: 各番号のペアが異なる場合警告を表示

        """
        tick_frameの値が変更されたとき, 対応するgame_no, field_noを検索する.

        左右で番号が違う場合は試合が終了している可能性があるので注意すること.
        
        Returns:
            tuple: (game_no_left, field_no_left, game_no_right, field_no_right)
        """

        tick = self.tick_frame.tick.get()
        found = False
        for game_no_left, game in enumerate(self.games["games"]):
            for field_no_left, field in enumerate(game["fields"][0]):
                if field["tick"] >= tick:
                    found = True
                    break
            if found:
                break

        for game_no_right, game in enumerate(self.games["games"]):
            for field_no_right, field in enumerate(game["fields"][1]):
                if field["tick"] >= tick:
                    print(game_no_left, field_no_left, game_no_right, field_no_right)
                    return game_no_left, field_no_left, game_no_right, field_no_right


    def update_combobox(self, tick:int = None) -> None:
        """
        tickのコンボボックスを作成する

        デフォルトでは最初の項目が選択される

        Args:
            tick (int): 作成後に選択したいtickを入力する(任意)
        Returns:
            None
        """
        tick_set ={
            field["tick"] for game in self.games["games"] for field in game["fields"][0]} | {field["tick"] for game in self.games["games"] for field in game["fields"][1]}
        
        self.tick_frame.combobox['values'] = sorted(list(tick_set))
        if tick is None:# デフォルトで最初の項目を選択
            self.tick_frame.combobox.current(0) 
        else:
            index = self.tick_frame.combobox["values"].index(str(tick))
            self.tick_frame.combobox.current(index)
            self.tick_frame.tick.set(tick)
        return None

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
        
    def create_color_selector(self) -> tk.Frame:
        '''
            色選択ラジオボタンを生成

            return:
        '''
        color_selector_frame = tk.Frame(self)
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
        for color in self.image_paths:
            image = Image.open(self.image_paths[color])
            resized_image = image.resize((17, 17), Image.Resampling.LANCZOS)
            self.images[color] = ImageTk.PhotoImage(resized_image)
            rb = tk.Radiobutton(color_selector_frame, image=self.images[color], variable=self.selected_color, value=color)
            rb.pack(side="left") 
        return color_selector_frame


    def create_field(self, master: tk.Frame, side_selection: str,  width:int=6, hight:int=12) -> tk.Frame:
        image_frame = tk.Frame(master, borderwidth=1, relief="solid")
        image_frame.canvas_dict = {}  # このインスタンスのキャンバスウィジェットを保持する新しい辞書
        image_frame.canvas_dict["side_selection"] = side_selection
        for row in range(hight):
            for col in range(width):
                canvas = tk.Canvas(image_frame, borderwidth=1, relief="groove", width=17, height=17)
                canvas.color = tk.StringVar(value="back")
                canvas.grid(row=row, column=col, padx=0, pady=0, sticky=tk.NW)
                canvas.bind("<Button-1>", lambda e, r=row, c=col: self.on_panel_click(r, c, image_frame.canvas_dict))
                image_frame.canvas_dict[(row, col)] = canvas 

        return image_frame

    #描画とfieldの書き換え
    def on_panel_click(self, row:int, col:int, canvas_dict:dict) -> None:
        #キャンバスへの描画
        color = self.selected_color.get()
        self.update_field_canvas(canvas_dict["side_selection"], row, col, color)

        #fieldの書き換え
        side_selection = canvas_dict["side_selection"]
        tick = self.tick_frame.tick.get()
        if side_selection == "left":
            for game_no, game in enumerate(self.games["games"]):
                for field_no, field in enumerate(game["fields"][0]):
                    if field["tick"] >= tick:
                        self.update_games_field("left", game_no, field_no, row, col, color)

                        for row in self.games["games"][game_no]["fields"][0][field_no]["field"]:
                            print(row)
                        print("--------------------------------------------------")
                        return
            
        elif side_selection == "right":
            for game_no, game in enumerate(self.games["games"]):
                for field_no, field in enumerate(game["fields"][1]):
                    if field["tick"] >= tick:
                        self.update_games_field("right", game_no, field_no, row, col, color)

                        for row in self.games["games"][game_no]["fields"][1][field_no]["field"]:
                            print(row)
                        print("--------------------------------------")
                        return
                    
    #盤面の読み込み
    def set_field(self):
        tick = self.tick_frame.tick.get()
        colors = ["red", "blue", "green", "yellow", "purple", "ojama", "back"]
        
        found_left = False
        for game in self.games["games"]:
            for field in game["fields"][0]:
                if field["tick"] >= tick:
                    print(field["tick"])
                    for i, row in enumerate(field["field"]):
                        print(row)
                        for j, cell in enumerate(row):
                            if cell is None:
                                color = "back"
                            else:
                                color = colors[cell]
                            
                            self.update_field_canvas("left", i, j, color)
                    found_left = True
                    break
            if found_left:
                break
                    
        for game in self.games["games"]:
            for field in game["fields"][1]:
                if field["tick"] >= tick:
                    print(field["tick"])
                    for i, row in enumerate(field["field"]):
                        for j, cell in enumerate(row):
                            if cell is None:
                                color = "back"
                            else:
                                color = colors[cell]

                            self.update_field_canvas("right", i, j, color)
                    return None
                   

        
        

    def update_field_canvas(self, side_selection:str, row:int, column:int, color:str) -> None:
        if side_selection == "right":
            photo = self.images[color]
            self.field_frame.right.canvas_dict[(row, column)].color = color
            self.field_frame.right.canvas_dict[(row, column)].image = photo
            self.field_frame.right.canvas_dict[(row, column)].delete("all")
            self.field_frame.right.canvas_dict[(row, column)].create_image(11, 11, image=photo)

        elif side_selection == "left":
            photo = self.images[color]
            self.field_frame.left.canvas_dict[(row, column)].color = color
            self.field_frame.left.canvas_dict[(row, column)].image = photo
            self.field_frame.left.canvas_dict[(row, column)].delete("all")
            self.field_frame.left.canvas_dict[(row, column)].create_image(11, 11, image=photo)
        return
    
    def update_games_field(self, side_selection:str, game_no:int, field_no:int, row:int, column:int, color:str) -> None:
        colors = ["red", "blue", "green", "yellow", "purple", "ojama", "back"]
        if color == "back":
            color = None
        else:
            color = colors.index(color)
        if side_selection == "right":
            self.games["games"][game_no]["fields"][1][field_no]["field"][row][column] = color
        elif side_selection == "left":
            self.games["games"][game_no]["fields"][0][field_no]["field"][row][column] = color
        return
    
    def save_file(self) -> None:
        name = self.save_frame.entry.get()
        with open(self.save_frame.output_directory+name, "w") as f:
            json.dump(self.games, f, indent=4)
        return


class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("movieFrameTest")
        self.geometry("1280x720")
        self.initialize_frames()
    
    def initialize_frames(self):
        game_data = FieldFrame(self)
        game_data.grid(row=0, column=0)
        

if __name__ == "__main__":
    logging.basicConfig(filename='error.log', level=logging.ERROR, format='%(asctime)s:%(levelname)s:%(message)s')
    app = Application()
    app.mainloop()

