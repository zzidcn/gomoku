import tkinter as tk
from tkinter import messagebox
import sys

# ── 常量 ──────────────────────────────────────────────
BOARD_SIZE   = 15          # 棋盘路数
CELL         = 40          # 格子像素
MARGIN       = 40          # 边距
CANVAS_SIZE  = MARGIN * 2 + CELL * (BOARD_SIZE - 1)

COLOR_BG     = "#DEB887"   # 棋盘底色
COLOR_LINE   = "#8B6914"   # 线条
COLOR_BLACK  = "#1a1a1a"
COLOR_WHITE  = "#F5F5F5"
COLOR_HINT   = "#FF4444"   # 最后落子标记
COLOR_BTN_BG = "#8B6914"
COLOR_BTN_FG = "#FFF8DC"

PLAYER_BLACK = 1
PLAYER_WHITE = 2
PLAYER_NAME  = {PLAYER_BLACK: "黑棋", PLAYER_WHITE: "白棋"}


# ── 游戏逻辑 ──────────────────────────────────────────
class GomokuGame:
    def __init__(self):
        self.reset()

    def reset(self):
        self.board      = [[0] * BOARD_SIZE for _ in range(BOARD_SIZE)]
        self.current    = PLAYER_BLACK
        self.winner     = None
        self.last_move  = None
        self.history    = []          # [(row, col, player), ...]

    def place(self, row, col):
        """落子，返回 True 表示成功"""
        if self.winner or self.board[row][col] != 0:
            return False
        self.board[row][col] = self.current
        self.last_move = (row, col)
        self.history.append((row, col, self.current))
        if self._check_win(row, col):
            self.winner = self.current
        else:
            self.current = PLAYER_WHITE if self.current == PLAYER_BLACK else PLAYER_BLACK
        return True

    def undo(self):
        """悔棋"""
        if not self.history or self.winner:
            return False
        row, col, player = self.history.pop()
        self.board[row][col] = 0
        self.current = player
        self.last_move = (self.history[-1][0], self.history[-1][1]) if self.history else None
        return True

    def _check_win(self, row, col):
        directions = [(0,1),(1,0),(1,1),(1,-1)]
        p = self.board[row][col]
        for dr, dc in directions:
            count = 1
            for sign in (1, -1):
                r, c = row + dr*sign, col + dc*sign
                while 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE and self.board[r][c] == p:
                    count += 1
                    r += dr*sign
                    c += dc*sign
            if count >= 5:
                return True
        return False


# ── 界面 ──────────────────────────────────────────────
class GomokuApp:
    def __init__(self, root):
        self.root  = root
        self.game  = GomokuGame()
        self._build_ui()
        self._draw_board()
        self._update_status()

    # ── 构建 UI ──
    def _build_ui(self):
        self.root.title("五子棋 Gomoku")
        self.root.resizable(False, False)
        self.root.configure(bg="#5C3D1E")

        # 顶部状态栏
        top = tk.Frame(self.root, bg="#5C3D1E", pady=6)
        top.pack(fill=tk.X)
        self.lbl_status = tk.Label(
            top, text="", font=("微软雅黑", 14, "bold"),
            bg="#5C3D1E", fg="#FFF8DC", width=20
        )
        self.lbl_status.pack()

        # 棋盘画布
        self.canvas = tk.Canvas(
            self.root,
            width=CANVAS_SIZE, height=CANVAS_SIZE,
            bg=COLOR_BG, highlightthickness=3,
            highlightbackground="#5C3D1E"
        )
        self.canvas.pack(padx=16, pady=(0, 8))
        self.canvas.bind("<Button-1>", self._on_click)
        self.canvas.bind("<Motion>",   self._on_hover)
        self._hover_pos = None

        # 按钮栏
        btn_frame = tk.Frame(self.root, bg="#5C3D1E", pady=8)
        btn_frame.pack()
        for text, cmd in [("重新开始", self._restart), ("悔棋", self._undo), ("退出", self.root.quit)]:
            tk.Button(
                btn_frame, text=text, command=cmd,
                font=("微软雅黑", 11), bg=COLOR_BTN_BG, fg=COLOR_BTN_FG,
                activebackground="#A0522D", activeforeground="#FFF8DC",
                relief=tk.FLAT, padx=18, pady=6, cursor="hand2"
            ).pack(side=tk.LEFT, padx=8)

    # ── 绘制棋盘 ──
    def _draw_board(self):
        self.canvas.delete("all")
        # 背景纹理感（浅色格子）
        for i in range(BOARD_SIZE):
            x = MARGIN + i * CELL
            y = MARGIN + i * CELL
            self.canvas.create_line(x, MARGIN, x, MARGIN + (BOARD_SIZE-1)*CELL,
                                    fill=COLOR_LINE, width=1)
            self.canvas.create_line(MARGIN, y, MARGIN + (BOARD_SIZE-1)*CELL, y,
                                    fill=COLOR_LINE, width=1)

        # 天元和星位
        stars = [(3,3),(3,11),(7,7),(11,3),(11,11)]
        for r, c in stars:
            cx = MARGIN + c * CELL
            cy = MARGIN + r * CELL
            self.canvas.create_oval(cx-4, cy-4, cx+4, cy+4, fill=COLOR_LINE, outline="")

        # 棋子
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                if self.game.board[r][c]:
                    self._draw_stone(r, c, self.game.board[r][c])

        # 最后落子标记
        if self.game.last_move:
            r, c = self.game.last_move
            cx = MARGIN + c * CELL
            cy = MARGIN + r * CELL
            s = 6
            self.canvas.create_oval(cx-s, cy-s, cx+s, cy+s,
                                    outline=COLOR_HINT, width=2)

        # 悬停预览
        if self._hover_pos and not self.game.winner:
            r, c = self._hover_pos
            if self.game.board[r][c] == 0:
                cx = MARGIN + c * CELL
                cy = MARGIN + r * CELL
                rad = CELL // 2 - 3
                color = COLOR_BLACK if self.game.current == PLAYER_BLACK else COLOR_WHITE
                self.canvas.create_oval(cx-rad, cy-rad, cx+rad, cy+rad,
                                        fill=color, outline="", stipple="gray50")

    def _draw_stone(self, row, col, player):
        cx  = MARGIN + col * CELL
        cy  = MARGIN + row * CELL
        rad = CELL // 2 - 3
        if player == PLAYER_BLACK:
            # 黑棋渐变感
            self.canvas.create_oval(cx-rad, cy-rad, cx+rad, cy+rad,
                                    fill=COLOR_BLACK, outline="#555", width=1)
            self.canvas.create_oval(cx-rad+4, cy-rad+4, cx-rad+10, cy-rad+10,
                                    fill="#555", outline="")
        else:
            self.canvas.create_oval(cx-rad, cy-rad, cx+rad, cy+rad,
                                    fill=COLOR_WHITE, outline="#999", width=1)
            self.canvas.create_oval(cx-rad+4, cy-rad+4, cx-rad+10, cy-rad+10,
                                    fill="#DDD", outline="")

    # ── 事件 ──
    def _on_click(self, event):
        if self.game.winner:
            return
        col = round((event.x - MARGIN) / CELL)
        row = round((event.y - MARGIN) / CELL)
        if not (0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE):
            return
        if self.game.place(row, col):
            self._draw_board()
            self._update_status()
            if self.game.winner:
                self._show_winner()

    def _on_hover(self, event):
        col = round((event.x - MARGIN) / CELL)
        row = round((event.y - MARGIN) / CELL)
        pos = (row, col) if (0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE) else None
        if pos != self._hover_pos:
            self._hover_pos = pos
            self._draw_board()

    def _restart(self):
        self.game.reset()
        self._hover_pos = None
        self._draw_board()
        self._update_status()

    def _undo(self):
        if self.game.undo():
            self._draw_board()
            self._update_status()

    def _update_status(self):
        if self.game.winner:
            text = f"🏆 {PLAYER_NAME[self.game.winner]} 获胜！"
        else:
            icon = "⚫" if self.game.current == PLAYER_BLACK else "⚪"
            text = f"{icon} {PLAYER_NAME[self.game.current]} 落子"
        self.lbl_status.config(text=text)

    def _show_winner(self):
        name = PLAYER_NAME[self.game.winner]
        if messagebox.askyesno("游戏结束", f"🎉 {name} 获胜！\n\n是否重新开始？"):
            self._restart()


# ── 入口 ──────────────────────────────────────────────
def main():
    root = tk.Tk()
    app  = GomokuApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
