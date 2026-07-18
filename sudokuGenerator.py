import argparse
import tkinter as tk
from random import randint, shuffle
from PIL import ImageGrab
from os import getcwd, makedirs
from os.path import join
from time import sleep


def connect_lists(lists):
    final_list = []
    for l in lists:
        final_list += l
    return final_list


def parse_args():
    parser = argparse.ArgumentParser(description="Generate and solve Sudoku puzzles.")
    parser.add_argument(
        "--n",
        type=int,
        default=3,
        help="Subgrid size. Use 3 for a 9x9 puzzle, 4 for 16x16, 5 for 25x25.",
    )
    args = parser.parse_args()
    if args.n < 2:
        parser.error("--n must be at least 2")
    return args


class Sudoku:
    def __init__(self, diff):
        # diff = number of given cells
        self.size = n ** 2

        # generate full solved grid
        self.map = self.create_sudoku()

        # choose which positions will be visible (givens)
        self.chosen = self.choose_numbers(diff)

        # precompute a "trail" for the solving animation
        self.trail = self.build_trail()

    # ---- FAST SUDOKU GENERATOR ----
    def create_sudoku(self):
        """
        Generate a full valid n^2 x n^2 Sudoku using a base pattern and shuffling.
        Works very fast even for n = 5 (25x25).
        """
        size = self.size
        base_nums = list(range(1, size + 1))

        def pattern(r, c):
            # standard generalized sudoku pattern
            return (n * (r % n) + r // n + c) % size

        def shuffled(seq):
            seq = list(seq)
            shuffle(seq)
            return seq

        r_base = range(n)
        rows = [g * n + r for g in shuffled(r_base) for r in shuffled(r_base)]
        cols = [g * n + c for g in shuffled(r_base) for c in shuffled(r_base)]
        nums = shuffled(base_nums)

        grid = [[nums[pattern(r, c)] for c in cols] for r in rows]
        return grid

    # ---- PUZZLE MASKING ----
    def choose_numbers(self, nums):
        """
        Pick 'nums' distinct coordinates to keep as givens.
        """
        numbers = []
        while len(numbers) < nums:
            num = [randint(0, n ** 2 - 1), randint(0, n ** 2 - 1)]
            if num not in numbers:
                numbers.append(num)
        return numbers

    # ---- "SOLVER" TRAIL (ANIMATION) ----
    def build_trail(self):
        """
        Build the list of steps for animation when pressing SOLVE.
        We already know the full solution (self.map), so we just
        reveal all non-given cells one by one.
        Format: [i, j, num]
        """
        trail = []
        for i in range(self.size):
            for j in range(self.size):
                if [i, j] not in self.chosen:
                    trail.append([i, j, self.map[i][j]])
        return trail


class Window:
    def __init__(self):
        self.widgets = [
            tk.Label(window, text="SUDOKU GENERATOR", font=("Calibri", 25)),
            tk.Label(window, text="CHOOSE A DIFFICULTY:", font=("Calibri", 18)),
            tk.Button(window, text="Easy", font=("Calibri", 15), command=self.choose_easy),
            tk.Button(window, text="Medium", font=("Calibri", 15), command=self.choose_medium),
            tk.Button(window, text="Hard", font=("Calibri", 15), command=self.choose_hard),
        ]

        self.widgets[0].place(relx=0.5, rely=0.21, anchor="center")
        self.widgets[1].place(relx=0.5, rely=0.32, anchor="center")
        self.widgets[2].place(width=s / 9, relx=0.5, rely=0.5, anchor="center")
        self.widgets[3].place(width=s / 9, relx=0.5, rely=0.58, anchor="center")
        self.widgets[4].place(width=s / 9, relx=0.5, rely=0.66, anchor="center")

        self.tile = s * (7 / 9) / (n ** 2)
        self.space_x = s * 1 / 9
        self.space_y = s * 1 / 18
        self.font_size = self.tile * 3 / 5

        self.shown = False

    def choose_easy(self):
        self.show_sudoku("easy", int(n ** 4 / 1.6))

    def choose_medium(self):
        self.show_sudoku("medium", int(n ** 4 / 2))

    def choose_hard(self):
        self.show_sudoku("hard", int(n ** 4 / 2.5))

    def show_sudoku(self, diff, num):
        for widget in self.widgets:
            widget.destroy()

        tk.Label(window, text="Difficulty: " + diff, font=("Calibri", 14)).place(
            relx=0.16, rely=0.95, anchor="center"
        )
        self.butt = tk.Button(window, text="SHOW ANSWERS", font=("Calibri", 15), command=self.show_answers)
        self.butt.place(relx=0.5, rely=0.95, anchor="center")

        tk.Button(window, text="SAVE", font=("Calibri", 15), command=self.save).place(
            width=s / 9, relx=0.9, rely=0.95, anchor="center"
        )

        self.savbutt = tk.Button(window, text="SOLVE", font=("Calibri", 15), command=self.start_solving)
        self.savbutt.place(width=s / 9, relx=0.75, rely=0.95, anchor="center")

        self.c = tk.Canvas(window, width=s, height=s * 8 / 9, bg="white")
        self.c.place(relx=0.5, rely=0, anchor="n")

        # create Sudoku (now fast even for n = 5)
        self.sudoku = Sudoku(num)

        self.draw_sudoku()

    def show_answers(self):
        if not self.shown:
            for i in range(n ** 2):
                for j in range(n ** 2):
                    if [i, j] not in self.sudoku.chosen:
                        self.draw_number(i, j, self.sudoku.map[i][j], "red")
            self.shown = True
            self.butt["text"] = "HIDE ANSWERS"
        else:
            self.c.create_rectangle(5, 5, s - 5, s * 8 / 9 - 5, fill="white", outline="white")
            self.draw_sudoku()
            self.shown = False
            self.butt["text"] = "SHOW ANSWERS"

    def save(self):
        name = self.get_name()
        if name:
            window.update_idletasks()
            window.update()
            sleep(0.1)

            x = self.c.winfo_rootx() + self.c.winfo_x() + 5
            y = self.c.winfo_rooty() + self.c.winfo_y()
            x1 = x + self.c.winfo_width() - 5
            y1 = y + self.c.winfo_height()
            save_dir = join(getcwd(), "Saved Sudokus")
            makedirs(save_dir, exist_ok=True)
            ImageGrab.grab().crop((x, y, x1, y1)).save(join(save_dir, name + ".png"))

    def start_solving(self):
        if self.shown:
            self.show_answers()
        self.butt.destroy()

        # replay precomputed trail
        for move in self.sudoku.trail:
            i, j, num = move
            self.c.create_rectangle(
                self.space_x + j * self.tile + 3,
                self.space_y + i * self.tile + 3,
                self.space_x + (j + 1) * self.tile - 3,
                self.space_y + (i + 1) * self.tile - 3,
                outline="white",
                fill="white",
            )

            # here num is always an int (we reveal final numbers)
            self.draw_number(i, j, num, "red")

            sleep(0.05)
            window.update()

        self.savbutt.destroy()

    def draw_sudoku(self):
        for i in range(n ** 2 + 1):
            w = 5 if i % n == 0 else 2
            self.c.create_line(
                self.space_x + i * self.tile,
                self.space_y,
                self.space_x + i * self.tile,
                s * 8 / 9 - self.space_y,
                width=w,
            )
        for j in range(n ** 2 + 1):
            w = 5 if j % n == 0 else 2
            self.c.create_line(
                self.space_x,
                self.space_y + j * self.tile,
                s - self.space_x,
                self.space_y + j * self.tile,
                width=w,
            )

        numbers = self.sudoku.chosen

        for i in range(n ** 2):
            for j in range(n ** 2):
                if [i, j] in numbers:
                    self.draw_number(i, j, self.sudoku.map[i][j], "black")

    def draw_number(self, i, j, number, color):
        self.c.create_text(
            self.space_x + j * self.tile + self.tile / 2,
            self.space_y + i * self.tile + self.tile / 2,
            text=number,
            font=("Calibri", int(self.font_size)),
            fill=color,
        )

    def get_name(self):
        self.w = tk.Toplevel(window)
        self.w.title("")
        self.w.resizable(0, 0)
        self.w.geometry("250x150+450+450")
        self.w.transient(window)
        self.w.grab_set()
        self.w.protocol("WM_DELETE_WINDOW", self.cancel_name)

        self.filename = None

        tk.Label(self.w, text="CHOOSE FILENAME:", font=15).place(
            relx=0.5, rely=0.2, anchor="center"
        )
        tk.Button(self.w, text="SAVE", command=self.choose).place(
            relx=0.5, rely=0.8, width=40, height=30, anchor="center"
        )

        self.entry = tk.Entry(self.w, textvariable=tk.StringVar(), font=8)
        self.entry.place(relx=0.5, rely=0.5, width=110, height=30, anchor="center")
        self.entry.focus_set()
        self.entry.bind("<Return>", lambda _: self.choose())

        window.wait_window(self.w)

        return self.filename

    def choose(self):
        filename = self.entry.get().strip()
        if filename:
            self.filename = filename
            self.w.destroy()

    def cancel_name(self):
        self.filename = None
        self.w.destroy()


if __name__ == "__main__":
    args = parse_args()
    s = 700
    n = args.n

    window = tk.Tk()
    window.title(f"Sudoku Generator {n ** 2}x{n ** 2}")
    window.geometry(str(s) + "x" + str(s))
    window.resizable(False, False)

    window.update()

    Window()

    window.mainloop()
