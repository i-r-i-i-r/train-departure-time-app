# -- coding: utf-8 --
# https://zenn.dev/takahashi_m/articles/d0fb009398e92c562662
import tkinter as tk
from tkinter import ttk
from traininfo.traininfo import make_station_property, make_disp_text


FONT = "Yu Gothic UI"
FONT_SIZE = 12
DEFAULT_DIRECTION = [0,0,0,0,0,0,0,0,0,0,0] # 駅ごとに指定しておく

N_DISP = 5
STATION_NAMES = ["三軒茶屋", "表参道", "新宿"] # ★★入力してください




class Application(tk.Frame):
    def __init__(self, master, station_property):
        super().__init__(master)
        self.pack()
        self.master.geometry("300x300")
        self.master.title("Train Departure Time")
        self.station_property = station_property
        
        self.create_widgets()
    
    def create_widgets(self):
        # 出発駅
        self.frame_station_dep = tk.Frame(self, pady=10)
        self.frame_station_dep.pack()
        self.label_station_dep = tk.Label(self.frame_station_dep, font=(FONT,FONT_SIZE), text="出発駅")
        self.label_station_dep.pack(side="left")
        self.com_station_dep = ttk.Combobox(self.frame_station_dep, justify="center", state='readonly', font=(FONT,FONT_SIZE))
        self.com_station_dep["values"] = list(self.station_property)
        self.com_station_dep.current(0)
        self.com_station_dep.pack()
        self.com_station_dep.bind('<<ComboboxSelected>>', self.update_com_direction)
        
        # 行先
        self.frame_direction = tk.Frame(self, pady=10)
        self.frame_direction.pack()
        self.label_direction = tk.Label(self.frame_direction, font=(FONT,FONT_SIZE), text="行先")
        self.label_direction.pack(side="left")
        self.com_direction = ttk.Combobox(self.frame_direction, justify="center", state='readonly', font=(FONT,FONT_SIZE))
        self.update_com_direction()
        self.com_direction.pack()
        
        # 表示ボタン
        self.frame_button = tk.Frame(self, pady=10)
        self.frame_button.pack()
        self.button = tk.Button(self.frame_button, text="表示",font=(FONT,FONT_SIZE))
        self.button.pack()
        self.button.bind("<Button-1>", self.disp)
        
        # 結果表示部
        self.label_result = tk.Label(self, font=(FONT,FONT_SIZE)) # 
        self.label_result.pack() # 
    
    # 出発駅が更新されたら行先の選択肢も変更する
    def update_com_direction(self, event=None):
        self.com_direction["values"] = list(self.station_property[self.com_station_dep.get()]["direction"])
        self.com_direction.current(DEFAULT_DIRECTION[0])
        self.com_direction.pack()
    
    # 結果を表示する
    def disp(self, event=None):
        text_disp = make_disp_text(self.com_station_dep.get(), self.com_direction.get(), self.station_property, N_DISP)
        #print(text_disp)
        #textField.delete(0, tk.END)
        self.label_result.config(text = "\n".join(text_disp))
        

def main():
    root = tk.Tk()
    app = Application(root, make_station_property(STATION_NAMES))
    app.mainloop()

if __name__ == "__main__":
    main()
