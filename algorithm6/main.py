import tkinter as tk
from tkinter import messagebox
from collections import defaultdict
import random


class Coords:
    def __init__(self, i, j):
        self.i = i
        self.j = j
    def add(self, other):
        return Coords(self.i + other.i, self.j + other.j)
    def is_on_board(self):
        return 0 <= self.i < 5 and 0 <= self.j < 5
    def __eq__(self, other):
        return self.i == other.i and self.j == other.j
    def __hash__(self):
        return hash((self.i, self.j))

class NeutreekoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Neutreeko")
        self.reset_game()

    def reset_game(self):
        self.board = [[0] * 5 for _ in range(5)]
        self.pawns = self.generate_random_positions()
        self.current_player = 1
        self.directions = [Coords(i, j) for i in range(-1, 2) for j in range(-1, 2) if i != 0 or j != 0]
        self.position_history = defaultdict(int)

        self.canvas = tk.Canvas(self.root, width=500, height=500, bg="white")
        self.canvas.grid(row=0, column=0, columnspan=2)

        self.reset_button = tk.Button(self.root, text="Reset the game", command=self.reset_game)
        self.reset_button.grid(row=1, column=0)

        self.game_mode = tk.StringVar(value="Player vs Player")
        self.mode_menu = tk.OptionMenu(self.root, self.game_mode, "Player vs Player", "Player vs AI")
        self.mode_menu.grid(row=1, column=1)

        self.canvas.bind("<Button-1>", self.handle_click)
        self.draw_board()

    def generate_random_positions(self):
        all_positions = [Coords(i, j) for i in range(5) for j in range(5)]
        random.shuffle(all_positions)
        return {
            1: all_positions[:3],
            2: all_positions[3:6],
        }

    def draw_board(self):
        self.canvas.delete("all")
        for i in range(6):
            self.canvas.create_line(0, i * 100, 500, i * 100, fill="black")
            self.canvas.create_line(i * 100, 0, i * 100, 500, fill="black")

        for player, pawns in self.pawns.items():
            for pawn in pawns:
                color = "black" if player == 1 else "white"
                x0, y0 = pawn.j * 100 + 10, pawn.i * 100 + 10
                x1, y1 = pawn.j * 100 + 90, pawn.i * 100 + 90
                self.canvas.create_oval(x0, y0, x1, y1, fill=color)

    def handle_click(self, event):
        col, row = event.x // 100, event.y // 100
        for index, pawn in enumerate(self.pawns[self.current_player]):
            if pawn.i == row and pawn.j == col:
                self.highlight_moves(index)
                break

    def highlight_moves(self, pawn_index):
        pawn = self.pawns[self.current_player][pawn_index]
        valid_moves = []
        for direction in self.directions:
            new_pos = pawn.add(direction)
            while new_pos.is_on_board() and self.is_cell_empty(new_pos):
                valid_moves.append(new_pos)
                new_pos = new_pos.add(direction)

        for move in valid_moves:
            x0, y0 = move.j * 100 + 20, move.i * 100 + 20
            x1, y1 = move.j * 100 + 80, move.i * 100 + 80
            self.canvas.create_rectangle(x0, y0, x1, y1, fill="yellow", outline="")

        self.canvas.bind("<Button-1>", lambda event: self.make_move(pawn_index, event, valid_moves))

    def make_move(self, pawn_index, event, valid_moves):
        col, row = event.x // 100, event.y // 100
        target = Coords(row, col)

        if target in valid_moves:
            old_pawn = self.pawns[self.current_player][pawn_index]
            self.animate_move(old_pawn, target)

            def after_animation():
                self.board[old_pawn.i][old_pawn.j] = 0
                self.pawns[self.current_player][pawn_index] = target
                self.board[target.i][target.j] = self.current_player
                self.draw_board()

                if self.has_won(self.current_player):
                    winner = "Black" if self.current_player == 1 else "White"
                    messagebox.showinfo("Game over", f"{winner} won!")
                    self.reset_game()
                    return

                if self.record_position():
                    messagebox.showinfo("Game over", "Draw: the position was repeated three times!")
                    self.reset_game()
                    return

                self.current_player = 3 - self.current_player
                self.canvas.bind("<Button-1>", self.handle_click)

                if self.current_player == 2 and self.game_mode.get() == "Player vs AI":
                    self.ai_move()

            self.root.after(500, after_animation)

    def ai_move(self):
        for index, pawn in enumerate(self.pawns[2]):
            for direction in self.directions:
                new_pos = pawn.add(direction)
                while new_pos.is_on_board() and self.is_cell_empty(new_pos):
                    self.pawns[2][index] = new_pos
                    self.draw_board()

                    if self.has_won(2):
                        messagebox.showinfo("Game over", "The reds won!")
                        self.reset_game()
                        return

                    self.current_player = 1
                    return
                new_pos = new_pos.add(direction)

    def has_won(self, player):
        for pawn in self.pawns[player]:
            for direction in self.directions:
                p2 = pawn.add(direction)
                p3 = p2.add(direction)
                if (
                        p2.is_on_board() and p3.is_on_board() and
                        p2 in self.pawns[player] and
                        p3 in self.pawns[player]
                ):
                    return True
        return False

    def animate_move(self, pawn, target, steps=10):
        start_x, start_y = pawn.j * 100 + 50, pawn.i * 100 + 50
        end_x, end_y = target.j * 100 + 50, target.i * 100 + 50
        delta_x = (end_x - start_x) / steps
        delta_y = (end_y - start_y) / steps

        def step_animation(step=0):
            if step < steps:
                x = start_x + delta_x * step
                y = start_y + delta_y * step
                self.canvas.delete("animation")
                self.canvas.create_oval(x - 40, y - 40, x + 40, y + 40, fill="blue", tags="animation")
                self.root.after(50, step_animation, step + 1)
            else:
                self.canvas.delete("animation")
                self.pawns[self.current_player][self.pawns[self.current_player].index(pawn)] = target
                self.draw_board()

        step_animation()

    def record_position(self):
        position_signature = tuple(tuple(row) for row in self.board)
        self.position_history[position_signature] += 1
        return self.position_history[position_signature] >= 3

    def is_cell_empty(self, pos):
        return self.board[pos.i][pos.j] == 0


if __name__ == "__main__":
    root = tk.Tk()
    app = NeutreekoApp(root)
    root.mainloop()
