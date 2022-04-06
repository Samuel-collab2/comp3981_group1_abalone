import tkinter
import time
import threading
from tkinter import *

from ab_search_optimize import Search
from abalone import Abalone
from board import BoardTile
from heuristic import Heuristic
from heuristic2 import Heuristic2
from move import Move


class GUI:
    def __init__(self):
        self.move_string = ""
        self.dict = None
        self.abalone = Abalone()
        self.root = Tk()
        print(self.abalone)
        self.timer_frame = None
        self.keep_looping = True
        self.time_limit = 20
        self._lock = threading.Lock()

    def reset_completed(self):
        self.move_string = ""

    def reset_move(self, event):
        self.move_string = ""

    def add_to_move_string(self, content):
        if self.move_string:
            self.move_string += ","
        self.move_string += content

    def add_to_group(self, event):
        if event.widget.cget("bg") in ["blue", "red"]:
            self.add_to_move_string(event.widget.cget("text"))

    def cd(self, timer_label_obj, ts):
        while ts > 0:
            timer_label_obj.config(text=ts)
            ts -= 1
            timer_label_obj.place(x=600, y=30)
            time.sleep(1)
            if ts == 0 or not self.keep_looping:
                # timer_label_obj.config(text="Time is complete!")
                # timer_label_obj.place(x=600, y=30)

                ts = self.time_limit
                self.keep_looping = True

                # timer_label_obj.destroy()
                # completeTimer = Label(self.timer_frame, text="Time is complete")
                # completeTimer.place(x=600, y=30)
        # if not self.keep_looping:
        #     self.cd(timer_label_obj, self.time_limit)

    def countdown(self, t):
        timer = Label(self.timer_frame)
        ts = int(t)
        # th = threading.Thread(target=cd,args=[timer, ts])
        th = threading.Thread(target=self.cd, args=[self.timer_frame, ts])
        th.start()

    def add_direction(self, event):
        # resets timer after player has made a choice
        self.keep_looping = False

        name = event.widget.cget("text")

        if "NORTH" in name:
            self.add_to_move_string("1")
            if "EAST" in name:
                self.add_to_move_string("1")
            else:
                self.add_to_move_string("0")

        if "SOUTH" in name:
            self.add_to_move_string("-1")
            if "WEST" in name:
                self.add_to_move_string("-1")
            else:
                self.add_to_move_string("0")

        if "NORTH" not in name and "SOUTH" not in name:
            self.add_to_move_string("0")
            if "EAST" in name:
                self.add_to_move_string("1")
            else:
                self.add_to_move_string("-1")

        move = Move.from_string(self.move_string)
        print(self.move_string)
        print(move)
        self.abalone.board.update_board(move)
        self.apply_board()
        self.reset_completed()
        self.root.nametowidget('player1_history').insert(END, f"{move}\n")
        self.root.nametowidget('player1_score').config(text=self.abalone.board.blue_score)
        self.root.nametowidget('player2_score').config(text=self.abalone.board.red_score)
        self.root.update()

        heuristic1 = Heuristic()
        heuristic2 = Heuristic2()

        t1 = threading.Thread(target=self.ai_search, args=["White", heuristic1])
        t1.start()

        # while True:
        #     search2 = Search()
        #     seconds = time.time()
        #     ai_move2 = search2.ab_search(self.abalone.board, "Black", heuristic1)
        #     seconds = abs(seconds - time.time())
        #     self.abalone.board.update_board(ai_move2)
        #     self.root.nametowidget('player1_history').insert(END, f"{ai_move2}\t{seconds:.4f}\n")
        #     self.root.nametowidget('player1_score').config(text=self.abalone.board.blue_score)
        #     self.root.nametowidget('player2_score').config(text=self.abalone.board.red_score)
        #     self.apply_board()
        #     self.root.update()
        #
        #     search = Search()
        #     seconds = time.time()
        #     ai_move = search.ab_search(self.abalone.board, "White", heuristic2)
        #     seconds = abs(seconds - time.time())
        #     self.abalone.board.update_board(ai_move)
        #     self.root.nametowidget('player2_history').insert(END, f"{ai_move}\t{seconds:.4f}\n")
        #     self.root.nametowidget('player1_score').config(text=self.abalone.board.blue_score)
        #     self.root.nametowidget('player2_score').config(text=self.abalone.board.red_score)
        #     self.apply_board()
        #     self.root.update()

    def ai_search(self, color: StringVar, heuristic):
        search = Search()
        seconds = time.time()
        ai_move = search.ab_search(self.abalone.board, color, heuristic)
        seconds = abs(seconds - time.time())
        print("AI should be making move here!!!")
        self.abalone.board.update_board(ai_move)
        self.root.nametowidget('player2_history').insert(END, f"{ai_move}\t{seconds:.4f}\n")
        self.root.nametowidget('player1_score').config(text=self.abalone.board.blue_score)
        self.root.nametowidget('player2_score').config(text=self.abalone.board.red_score)
        self.apply_board()
        # note to self: chance for race condition; board could update, but then thread loses control such that
        # keep_looping bool is still True, causing countdown timer to keep looping.
        self.root.update()
        # reset timer
        self.keep_looping = False

    def apply_board(self):
        board = self.abalone.board.board

        for key, value in board.items():
            if value == BoardTile.BLUE:
                button = self.dict.get(key)
                button.config(bg="blue")
            elif value == BoardTile.RED:
                button = self.dict.get(key)
                button.config(bg="red")
            elif value == BoardTile.EMPTY:
                button = self.dict.get(key)
                button.config(bg="grey")

    def start_timer(self):
        self.countdown(self.time_limit)

    def gui(self):
        self.root.geometry("1600x800")
        self.root.configure(background="darkgrey")

        self.timer_frame = Label(self.root, text="TimerFrame", height=5, width=20)
        self.timer_frame.place(x=600, y=30)

        start_game_button = Button(self.root, text="Start Game - starts timer", padx=2,
                                   command=self.start_timer)
        start_game_button.place(x=600, y=400)

        buttonI5 = Button(self.root, text="I5", height=2, width=5)
        buttonI5.place(x=125, y=25)

        buttonI6 = Button(self.root, text="I6", height=2, width=5)
        buttonI6.place(x=175, y=25)

        buttonI7 = Button(self.root, text="I7", height=2, width=5)
        buttonI7.place(x=225, y=25)

        buttonI8 = Button(self.root, text="I8", height=2, width=5)
        buttonI8.place(x=275, y=25)

        buttonI9 = Button(self.root, text="I9", height=2, width=5)
        buttonI9.place(x=325, y=25)

        buttonH4 = Button(self.root, text="H4", height=2, width=5)
        buttonH4.place(x=100, y=70)

        buttonH5 = Button(self.root, text="H5", height=2, width=5)
        buttonH5.place(x=150, y=70)

        buttonH6 = Button(self.root, text="H6", height=2, width=5)
        buttonH6.place(x=200, y=70)

        buttonH7 = Button(self.root, text="H7", height=2, width=5)
        buttonH7.place(x=250, y=70)

        buttonH8 = Button(self.root, text="H8", height=2, width=5)
        buttonH8.place(x=300, y=70)

        buttonH9 = Button(self.root, text="H9", height=2, width=5)
        buttonH9.place(x=350, y=70)

        buttonG3 = Button(self.root, text="G3", height=2, width=5)
        buttonG3.place(x=75, y=115)

        buttonG4 = Button(self.root, text="G4", height=2, width=5)
        buttonG4.place(x=125, y=115)

        buttonG5 = Button(self.root, text="G5", height=2, width=5, bg="blue")
        buttonG5.place(x=175, y=115)

        buttonG6 = Button(self.root, text="G6", height=2, width=5)
        buttonG6.place(x=225, y=115)

        buttonG7 = Button(self.root, text="G7", height=2, width=5)
        buttonG7.place(x=275, y=115)

        buttonG8 = Button(self.root, text="G8", height=2, width=5)
        buttonG8.place(x=325, y=115)

        buttonG9 = Button(self.root, text="G9", height=2, width=5)
        buttonG9.place(x=375, y=115)

        buttonF2 = Button(self.root, text="F2", height=2, width=5)
        buttonF2.place(x=50, y=160)

        buttonF3 = Button(self.root, text="F3", height=2, width=5)
        buttonF3.place(x=100, y=160)

        buttonF4 = Button(self.root, text="F4", height=2, width=5)
        buttonF4.place(x=150, y=160)

        buttonF5 = Button(self.root, text="F5", height=2, width=5)
        buttonF5.place(x=200, y=160)

        buttonF6 = Button(self.root, text="F6", height=2, width=5)
        buttonF6.place(x=250, y=160)

        buttonF7 = Button(self.root, text="F7", height=2, width=5)
        buttonF7.place(x=300, y=160)

        buttonF8 = Button(self.root, text="F8", height=2, width=5)
        buttonF8.place(x=350, y=160)

        buttonF9 = Button(self.root, text="F9", height=2, width=5)
        buttonF9.place(x=400, y=160)

        buttonE1 = Button(self.root, text="E1", height=2, width=5)
        buttonE1.place(x=25, y=205)

        buttonE2 = Button(self.root, text="E2", height=2, width=5)
        buttonE2.place(x=75, y=205)

        buttonE3 = Button(self.root, text="E3", height=2, width=5)
        buttonE3.place(x=125, y=205)

        buttonE4 = Button(self.root, text="E4", height=2, width=5)
        buttonE4.place(x=175, y=205)

        buttonE5 = Button(self.root, text="E5", height=2, width=5)
        buttonE5.place(x=225, y=205)

        buttonE6 = Button(self.root, text="E6", height=2, width=5)
        buttonE6.place(x=275, y=205)

        buttonE7 = Button(self.root, text="E7", height=2, width=5)
        buttonE7.place(x=325, y=205)

        buttonE8 = Button(self.root, text="E8", height=2, width=5)
        buttonE8.place(x=375, y=205)

        buttonE9 = Button(self.root, text="E9", height=2, width=5)
        buttonE9.place(x=425, y=205)

        buttonA1 = Button(self.root, text="A1", height=2, width=5)
        buttonA1.place(x=125, y=385)

        buttonA2 = Button(self.root, text="A2", height=2, width=5)
        buttonA2.place(x=175, y=385)

        buttonA3 = Button(self.root, text="A3", height=2, width=5)
        buttonA3.place(x=225, y=385)

        buttonA4 = Button(self.root, text="A4", height=2, width=5)
        buttonA4.place(x=275, y=385)

        buttonA5 = Button(self.root, text="A5", height=2, width=5)
        buttonA5.place(x=325, y=385)

        buttonB1 = Button(self.root, text="B1", height=2, width=5)
        buttonB1.place(x=100, y=340)

        buttonB2 = Button(self.root, text="B2", height=2, width=5)
        buttonB2.place(x=150, y=340)

        buttonB3 = Button(self.root, text="B3", height=2, width=5)
        buttonB3.place(x=200, y=340)

        buttonB4 = Button(self.root, text="B4", height=2, width=5)
        buttonB4.place(x=250, y=340)

        buttonB5 = Button(self.root, text="B5", height=2, width=5)
        buttonB5.place(x=300, y=340)

        buttonB6 = Button(self.root, text="B6", height=2, width=5)
        buttonB6.place(x=350, y=340)

        buttonC1 = Button(self.root, text="C1", height=2, width=5)
        buttonC1.place(x=75, y=295)

        buttonC2 = Button(self.root, text="C2", height=2, width=5)
        buttonC2.place(x=125, y=295)

        buttonC3 = Button(self.root, text="C3", height=2, width=5)
        buttonC3.place(x=175, y=295)

        buttonC4 = Button(self.root, text="C4", height=2, width=5)
        buttonC4.place(x=225, y=295)

        buttonC5 = Button(self.root, text="C5", height=2, width=5)
        buttonC5.place(x=275, y=295)

        buttonC6 = Button(self.root, text="C6", height=2, width=5)
        buttonC6.place(x=325, y=295)

        buttonC7 = Button(self.root, text="C7", height=2, width=5)
        buttonC7.place(x=375, y=295)

        buttonD1 = Button(self.root, text="D1", height=2, width=5)
        buttonD1.place(x=50, y=250)

        buttonD2 = Button(self.root, text="D2", height=2, width=5)
        buttonD2.place(x=100, y=250)

        buttonD3 = Button(self.root, text="D3", height=2, width=5)
        buttonD3.place(x=150, y=250)

        buttonD4 = Button(self.root, text="D4", height=2, width=5)
        buttonD4.place(x=200, y=250)

        buttonD5 = Button(self.root, text="D5", height=2, width=5)
        buttonD5.place(x=250, y=250)

        buttonD6 = Button(self.root, text="D6", height=2, width=5)
        buttonD6.place(x=300, y=250)

        buttonD7 = Button(self.root, text="D7", height=2, width=5)
        buttonD7.place(x=350, y=250)

        buttonD8 = Button(self.root, text="D8", height=2, width=5)
        buttonD8.place(x=400, y=250)

        self.dict = {
            ("A", 1): buttonA1, ("A", 2): buttonA2, ("A", 3): buttonA3, ("A", 4): buttonA4, ("A", 5): buttonA5,
            ("B", 1): buttonB1, ("B", 2): buttonB2, ("B", 3): buttonB3, ("B", 4): buttonB4, ("B", 5): buttonB5,
            ("B", 6): buttonB6, ("C", 1): buttonC1, ("C", 2): buttonC2, ("C", 3): buttonC3, ("C", 4): buttonC4,
            ("C", 5): buttonC5, ("C", 6): buttonC6, ("C", 7): buttonC7, ("D", 1): buttonD1, ("D", 2): buttonD2,
            ("D", 3): buttonD3, ("D", 4): buttonD4, ("D", 5): buttonD5, ("D", 6): buttonD6, ("D", 7): buttonD7,
            ("D", 8): buttonD8, ("E", 1): buttonE1, ("E", 2): buttonE2, ("E", 3): buttonE3, ("E", 4): buttonE4,
            ("E", 5): buttonE5, ("E", 6): buttonE6, ("E", 7): buttonE7, ("E", 8): buttonE8, ("E", 9): buttonE9,
            ("F", 2): buttonF2, ("F", 3): buttonF3, ("F", 4): buttonF4, ("F", 5): buttonF5, ("F", 6): buttonF6,
            ("F", 7): buttonF7, ("F", 8): buttonF8, ("F", 9): buttonF9, ("G", 3): buttonG3, ("G", 4): buttonG4,
            ("G", 5): buttonG5, ("G", 6): buttonG6, ("G", 7): buttonG7, ("G", 8): buttonG8, ("G", 9): buttonG9,
            ("H", 4): buttonH4, ("H", 5): buttonH5, ("H", 6): buttonH6, ("H", 7): buttonH7, ("H", 8): buttonH8,
            ("H", 9): buttonH9, ("I", 5): buttonI5, ("I", 6): buttonI6, ("I", 7): buttonI7, ("I", 8): buttonI8,
            ("I", 9): buttonI9,
        }

        self.apply_board()

        buttonNE = Button(self.root, text="NORTH-EAST", height=5, width=10)
        buttonNE.place(x=175, y=450)
        buttonNE.bind("<Button-1>", self.add_direction)

        buttonNW = Button(self.root, text="NORTH-WEST", height=5, width=10)
        buttonNW.place(x=75, y=450)
        buttonNW.bind("<Button-1>", self.add_direction)

        buttonE = Button(self.root, text="EAST", height=5, width=10)
        buttonE.place(x=225, y=550)
        buttonE.bind("<Button-1>", self.add_direction)

        buttonSE = Button(self.root, text="SOUTH-EAST", height=5, width=10)
        buttonSE.place(x=175, y=650)
        buttonSE.bind("<Button-1>", self.add_direction)

        buttonSW = Button(self.root, text="SOUTH-WEST", height=5, width=10)
        buttonSW.place(x=75, y=650)
        buttonSW.bind("<Button-1>", self.add_direction)

        buttonW = Button(self.root, text="WEST", height=5, width=10)
        buttonW.place(x=25, y=550)
        buttonW.bind("<Button-1>", self.add_direction)

        buttonReset = Button(self.root, text="RESET", height=5, width=10)
        buttonReset.place(x=125, y=550)
        buttonReset.bind("<Button-1>", self.reset_move)

        for key, value in self.dict.items():
            value.bind("<Button-1>", self.add_to_group)

        player1_label = Label(self.root, text="Player 1")
        player1_label.place(x=850, y=30)
        player1_history = tkinter.Text(self.root, width=40, height=20, name='player1_history')
        player1_history.place(x=850, y=50)

        player2_label = Label(self.root, text="Player 2")
        player2_label.place(x=1200, y=30)
        player2_history = tkinter.Text(self.root, width=48, height=20, name='player2_history')
        player2_history.place(x=1200, y=50)

        white_score = Label(self.root, text="0", font=("Courier", 40), fg="red", name="player2_score")
        white_score.place(x=600, y=200)

        hyphen_score = Label(self.root, text="-", font=("Courier", 40), bg="darkgrey")
        hyphen_score.place(x=650, y=200)

        black_score = Label(self.root, text="0", font=("Courier", 40), fg="blue", name="player1_score")
        black_score.place(x=700, y=200)

        early_access = Label(self.root, text="SUPER EARLY ACCESS TO THIS AMAZING ABALONE GUI")
        early_access.place(x=1290, y=770)

        self.root.mainloop()


if __name__ == "__main__":
    gui = GUI()
    gui.gui()
