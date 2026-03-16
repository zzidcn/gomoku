"""
五子棋 Gomoku v2.0.0
功能：双人对战 / AI对战 / 音效 / 多主题换肤 / 悔棋
"""
import tkinter as tk
from tkinter import messagebox
import threading
import math
import random

# ── 尝试导入音频 ──────────────────────────────────────
try:
    import pygame
    pygame.mixer.init(frequency=44100, size=-16, channels=1, buffer=512)
    AUDIO_BACKEND = "pygame"
except Exception:
    try:
        import winsound
        AUDIO_BACKEND = "winsound"
    except Exception:
        AUDIO_BACKEND = "none"

# ══════════════════════════════════════════════════════
#  常量
# ══════════════════════════════════════════════════════
BOARD_SIZE  = 15
CELL        = 40
MARGIN      = 40
CANVAS_SIZE = MARGIN * 2 + CELL * (BOARD_SIZE - 1)

PLAYER_BLACK = 1
PLAYER_WHITE = 2
PLAYER_NAME  = {PLAYER_BLACK: "黑棋", PLAYER_WHITE: "白棋"}

# ── 主题定义 ──────────────────────────────────────────
THEMES = {
    "经典木纹": {
        "bg":        "#DEB887",
        "line":      "#8B6914",
        "frame":     "#5C3D1E",
        "btn_bg":    "#8B6914",
        "btn_fg":    "#FFF8DC",
        "btn_act":   "#A0522D",
        "status_fg": "#FFF8DC",
        "star":      "#8B6914",
        "black":     "#1a1a1a",
        "black_hi":  "#555",
        "white":     "#F5F5F5",
        "white_hi":  "#DDD",
        "last_mark": "#FF4444",
        "hover_b":   "#1a1a1a",
        "hover_w":   "#F5F5F5",
    },
    "翠竹青": {
        "bg":        "#C8E6C9",
        "line":      "#2E7D32",
        "frame":     "#1B5E20",
        "btn_bg":    "#388E3C",
        "btn_fg":    "#F1F8E9",
        "btn_act":   "#2E7D32",
        "status_fg": "#F1F8E9",
        "star":      "#1B5E20",
        "black":     "#1a1a1a",
        "black_hi":  "#555",
        "white":     "#F5F5F5",
        "white_hi":  "#DDD",
        "last_mark": "#FF5722",
        "hover_b":   "#1a1a1a",
        "hover_w":   "#F5F5F5",
    },
    "深夜蓝": {
        "bg":        "#1A237E",
        "line":      "#5C6BC0",
        "frame":     "#0D1257",
        "btn_bg":    "#3949AB",
        "btn_fg":    "#E8EAF6",
        "btn_act":   "#283593",
        "status_fg": "#E8EAF6",
        "star":      "#7986CB",
        "black":     "#212121",
        "black_hi":  "#616161",
        "white":     "#ECEFF1",
        "white_hi":  "#B0BEC5",
        "last_mark": "#FF4081",
        "hover_b":   "#212121",
        "hover_w":   "#ECEFF1",
    },
    "樱花粉": {
        "bg":        "#FCE4EC",
        "line":      "#C2185B",
        "frame":     "#880E4F",
        "btn_bg":    "#E91E63",
        "btn_fg":    "#FCE4EC",
        "btn_act":   "#C2185B",
        "status_fg": "#FCE4EC",
        "star":      "#880E4F",
        "black":     "#1a1a1a",
        "black_hi":  "#555",
        "white":     "#F5F5F5",
        "white_hi":  "#DDD",
        "last_mark": "#FF6F00",
        "hover_b":   "#1a1a1a",
        "hover_w":   "#F5F5F5",
    },
    "墨金": {
        "bg":        "#212121",
        "line":      "#FFD700",
        "frame":     "#111111",
        "btn_bg":    "#B8860B",
        "btn_fg":    "#FFFDE7",
        "btn_act":   "#DAA520",
        "status_fg": "#FFD700",
        "star":      "#FFD700",
        "black":     "#424242",
        "black_hi":  "#757575",
        "white":     "#FFFDE7",
        "white_hi":  "#FFF9C4",
        "last_mark": "#FF1744",
        "hover_b":   "#424242",
        "hover_w":   "#FFFDE7",
    },
}
THEME_NAMES = list(THEMES.keys())

# ══════════════════════════════════════════════════════
#  音效生成（用 pygame 合成，无需音频文件）
# ══════════════════════════════════════════════════════
def _gen_sound(freq, duration_ms, volume=0.6, wave="sine"):
    """生成合成音效，返回 pygame.mixer.Sound 或 None"""
    if AUDIO_BACKEND != "pygame":
        return None
    try:
        import array, math
        sample_rate = 44100
        n = int(sample_rate * duration_ms / 1000)
        buf = array.array("h")
        for i in range(n):
            t = i / sample_rate
            fade = min(1.0, (n - i) / (n * 0.3))   # 淡出
            if wave == "sine":
                v = math.sin(2 * math.pi * freq * t)
            elif wave == "square":
                v = 1.0 if math.sin(2 * math.pi * freq * t) > 0 else -1.0
            else:
                v = math.sin(2 * math.pi * freq * t)
            buf.append(int(v * fade * volume * 32767))
        sound = pygame.sndarray.make_sound(
            __import__("numpy").array(buf, dtype="int16").reshape(-1, 1)
            if False else buf
        )
        return sound
    except Exception:
        return None


class SoundManager:
    def __init__(self):
        self.enabled = True
        self._sounds = {}
        self._init_sounds()

    def _init_sounds(self):
        if AUDIO_BACKEND != "pygame":
            return
        try:
            import numpy as np
            sr = 44100

            def make(freq, dur, vol=0.5, decay=0.8):
                n = int(sr * dur)
                t = np.linspace(0, dur, n, False)
                wave = np.sin(2 * np.pi * freq * t)
                env  = np.exp(-decay * t / dur * 10)
                data = (wave * env * vol * 32767).astype(np.int16)
                data = np.column_stack([data, data])
                return pygame.sndarray.make_sound(data)

            self._sounds["place_black"] = make(440, 0.12, 0.6, 1.2)
            self._sounds["place_white"] = make(660, 0.12, 0.6, 1.2)
            self._sounds["win"]         = make(523, 0.5,  0.7, 0.3)
            self._sounds["undo"]        = make(330, 0.08, 0.4, 2.0)
            self._sounds["start"]       = make(392, 0.15, 0.5, 0.8)
        except Exception:
            pass

    def play(self, name):
        if not self.enabled:
            return
        if AUDIO_BACKEND == "pygame" and name in self._sounds:
            try:
                self._sounds[name].play()
            except Exception:
                pass
        elif AUDIO_BACKEND == "winsound":
            import winsound
            freq_map = {"place_black": 800, "place_white": 1000,
                        "win": 1200, "undo": 500, "start": 600}
            freq = freq_map.get(name, 800)
            threading.Thread(
                target=lambda: winsound.Beep(freq, 80), daemon=True
            ).start()

    def toggle(self):
        self.enabled = not self.enabled
        return self.enabled


# ══════════════════════════════════════════════════════
#  AI（Minimax + Alpha-Beta，深度3）
# ══════════════════════════════════════════════════════
SCORE_TABLE = {
    (5, True):  1_000_000,
    (5, False): 1_000_000,
    (4, True):  100_000,
    (4, False): 10_000,
    (3, True):  5_000,
    (3, False): 500,
    (2, True):  200,
    (2, False): 50,
    (1, True):  10,
    (1, False): 2,
}

DIRECTIONS = [(0,1),(1,0),(1,1),(1,-1)]


def _count_line(board, row, col, dr, dc, player):
    """统计某方向连子数及两端是否开放"""
    count = 1
    open_ends = 0
    for sign in (1, -1):
        r, c = row + dr*sign, col + dc*sign
        while 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE and board[r][c] == player:
            count += 1
            r += dr*sign
            c += dc*sign
        if 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE and board[r][c] == 0:
            open_ends += 1
    return count, open_ends


def _eval_board(board, player):
    opp   = PLAYER_WHITE if player == PLAYER_BLACK else PLAYER_BLACK
    score = 0
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            for dr, dc in DIRECTIONS:
                if board[r][c] == player:
                    cnt, opens = _count_line(board, r, c, dr, dc, player)
                    score += SCORE_TABLE.get((min(cnt,5), opens==2), 0)
                elif board[r][c] == opp:
                    cnt, opens = _count_line(board, r, c, dr, dc, opp)
                    score -= SCORE_TABLE.get((min(cnt,5), opens==2), 0) * 1.1
    return score


def _get_candidates(board):
    """只考虑已有棋子周围2格内的空位"""
    cands = set()
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            if board[r][c] != 0:
                for dr in range(-2, 3):
                    for dc in range(-2, 3):
                        nr, nc = r+dr, c+dc
                        if 0 <= nr < BOARD_SIZE and 0 <= nc < BOARD_SIZE and board[nr][nc] == 0:
                            cands.add((nr, nc))
    if not cands:
        cands.add((BOARD_SIZE//2, BOARD_SIZE//2))
    return list(cands)


def _check_five(board, row, col, player):
    for dr, dc in DIRECTIONS:
        cnt, _ = _count_line(board, row, col, dr, dc, player)
        if cnt >= 5:
            return True
    return False


def _minimax(board, depth, alpha, beta, maximizing, ai_player, opp_player):
    cands = _get_candidates(board)

    # 终止条件
    if depth == 0 or not cands:
        return _eval_board(board, ai_player), None

    best_move = None
    if maximizing:
        best = -math.inf
        for r, c in cands:
            board[r][c] = ai_player
            if _check_five(board, r, c, ai_player):
                board[r][c] = 0
                return 1_000_000 + depth, (r, c)
            val, _ = _minimax(board, depth-1, alpha, beta, False, ai_player, opp_player)
            board[r][c] = 0
            if val > best:
                best, best_move = val, (r, c)
            alpha = max(alpha, best)
            if beta <= alpha:
                break
        return best, best_move
    else:
        best = math.inf
        for r, c in cands:
            board[r][c] = opp_player
            if _check_five(board, r, c, opp_player):
                board[r][c] = 0
                return -1_000_000 - depth, (r, c)
            val, _ = _minimax(board, depth-1, alpha, beta, True, ai_player, opp_player)
            board[r][c] = 0
            if val < best:
                best, best_move = val, (r, c)
            beta = min(beta, best)
            if beta <= alpha:
                break
        return best, best_move


class AIPlayer:
    def __init__(self, player, depth=3):
        self.player = player
        self.opp    = PLAYER_WHITE if player == PLAYER_BLACK else PLAYER_BLACK
        self.depth  = depth

    def get_move(self, board):
        # 第一手下天元
        empty = sum(1 for r in range(BOARD_SIZE) for c in range(BOARD_SIZE) if board[r][c] == 0)
        if empty == BOARD_SIZE * BOARD_SIZE:
            return BOARD_SIZE//2, BOARD_SIZE//2

        _, move = _minimax(
            [row[:] for row in board],
            self.depth, -math.inf, math.inf,
            True, self.player, self.opp
        )
        if move is None:
            cands = _get_candidates(board)
            move  = random.choice(cands) if cands else (BOARD_SIZE//2, BOARD_SIZE//2)
        return move


# ══════════════════════════════════════════════════════
#  游戏逻辑
# ══════════════════════════════════════════════════════
class GomokuGame:
    def __init__(self):
        self.reset()

    def reset(self):
        self.board     = [[0]*BOARD_SIZE for _ in range(BOARD_SIZE)]
        self.current   = PLAYER_BLACK
        self.winner    = None
        self.last_move = None
        self.history   = []

    def place(self, row, col):
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

    def undo(self, steps=1):
        for _ in range(steps):
            if not self.history or self.winner:
                return False
            row, col, player = self.history.pop()
            self.board[row][col] = 0
            self.current   = player
            self.last_move = (self.history[-1][0], self.history[-1][1]) if self.history else None
        return True

    def _check_win(self, row, col):
        return _check_five(self.board, row, col, self.board[row][col])


# ══════════════════════════════════════════════════════
#  界面
# ══════════════════════════════════════════════════════
class GomokuApp:
    def __init__(self, root):
        self.root        = root
        self.game        = GomokuGame()
        self.sound       = SoundManager()
        self.theme_idx   = 0
        self.theme       = THEMES[THEME_NAMES[self.theme_idx]]
        self.mode        = "pvp"      # "pvp" | "pva_b" | "pva_w"
        self.ai          = None
        self._hover_pos  = None
        self._ai_thinking = False

        self._build_ui()
        self._draw_board()
        self._update_status()

    # ── 构建 UI ──────────────────────────────────────
    def _build_ui(self):
        self.root.title("五子棋 Gomoku v2.0")
        self.root.resizable(False, False)
        self._apply_theme_root()

        # ── 顶部工具栏 ──
        top = tk.Frame(self.root, bg=self.theme["frame"], pady=4)
        top.pack(fill=tk.X)

        # 模式选择
        tk.Label(top, text="模式:", bg=self.theme["frame"],
                 fg=self.theme["status_fg"], font=("微软雅黑", 10)).pack(side=tk.LEFT, padx=(10,2))
        self.mode_var = tk.StringVar(value="pvp")
        modes = [("双人对战", "pvp"), ("AI执白", "pva_w"), ("AI执黑", "pva_b")]
        for text, val in modes:
            tk.Radiobutton(
                top, text=text, variable=self.mode_var, value=val,
                command=self._on_mode_change,
                bg=self.theme["frame"], fg=self.theme["status_fg"],
                selectcolor=self.theme["btn_bg"],
                activebackground=self.theme["frame"],
                activeforeground=self.theme["status_fg"],
                font=("微软雅黑", 10)
            ).pack(side=tk.LEFT, padx=4)

        # 主题选择
        tk.Label(top, text="  主题:", bg=self.theme["frame"],
                 fg=self.theme["status_fg"], font=("微软雅黑", 10)).pack(side=tk.LEFT, padx=(10,2))
        self.theme_var = tk.StringVar(value=THEME_NAMES[0])
        self.theme_menu = tk.OptionMenu(top, self.theme_var, *THEME_NAMES,
                                        command=self._on_theme_change)
        self.theme_menu.config(
            bg=self.theme["btn_bg"], fg=self.theme["btn_fg"],
            activebackground=self.theme["btn_act"],
            font=("微软雅黑", 10), relief=tk.FLAT, bd=0
        )
        self.theme_menu.pack(side=tk.LEFT, padx=4)

        # 音效开关
        self.sound_btn = tk.Button(
            top, text="🔊", command=self._toggle_sound,
            bg=self.theme["btn_bg"], fg=self.theme["btn_fg"],
            font=("微软雅黑", 11), relief=tk.FLAT, padx=6, cursor="hand2"
        )
        self.sound_btn.pack(side=tk.RIGHT, padx=8)

        # ── 状态栏 ──
        mid = tk.Frame(self.root, bg=self.theme["frame"], pady=4)
        mid.pack(fill=tk.X)
        self.lbl_status = tk.Label(
            mid, text="", font=("微软雅黑", 14, "bold"),
            bg=self.theme["frame"], fg=self.theme["status_fg"]
        )
        self.lbl_status.pack()

        # ── 棋盘 ──
        self.canvas = tk.Canvas(
            self.root,
            width=CANVAS_SIZE, height=CANVAS_SIZE,
            bg=self.theme["bg"],
            highlightthickness=3,
            highlightbackground=self.theme["frame"]
        )
        self.canvas.pack(padx=16, pady=(0, 6))
        self.canvas.bind("<Button-1>", self._on_click)
        self.canvas.bind("<Motion>",   self._on_hover)

        # ── 按钮栏 ──
        btn_frame = tk.Frame(self.root, bg=self.theme["frame"], pady=8)
        btn_frame.pack()
        self.btns = []
        for text, cmd in [("重新开始", self._restart), ("悔棋", self._undo)]:
            b = tk.Button(
                btn_frame, text=text, command=cmd,
                font=("微软雅黑", 11),
                bg=self.theme["btn_bg"], fg=self.theme["btn_fg"],
                activebackground=self.theme["btn_act"],
                activeforeground=self.theme["btn_fg"],
                relief=tk.FLAT, padx=18, pady=6, cursor="hand2"
            )
            b.pack(side=tk.LEFT, padx=8)
            self.btns.append(b)

    def _apply_theme_root(self):
        self.root.configure(bg=self.theme["frame"])

    # ── 主题切换 ──────────────────────────────────────
    def _on_theme_change(self, name):
        self.theme = THEMES[name]
        self._rebuild_ui()

    def _rebuild_ui(self):
        for w in self.root.winfo_children():
            w.destroy()
        self._apply_theme_root()
        self._build_ui()
        self.mode_var.set(self.mode)
        self.theme_var.set(THEME_NAMES[list(THEMES.keys()).index(self.theme)])
        self._draw_board()
        self._update_status()

    # ── 模式切换 ──────────────────────────────────────
    def _on_mode_change(self):
        self.mode = self.mode_var.get()
        if self.mode == "pva_w":
            self.ai = AIPlayer(PLAYER_WHITE, depth=3)
        elif self.mode == "pva_b":
            self.ai = AIPlayer(PLAYER_BLACK, depth=3)
        else:
            self.ai = None
        self._restart()

    # ── 音效 ──────────────────────────────────────────
    def _toggle_sound(self):
        on = self.sound.toggle()
        self.sound_btn.config(text="🔊" if on else "🔇")

    # ── 绘制棋盘 ──────────────────────────────────────
    def _draw_board(self):
        t = self.theme
        self.canvas.config(bg=t["bg"])
        self.canvas.delete("all")

        # 网格线
        for i in range(BOARD_SIZE):
            x = MARGIN + i * CELL
            y = MARGIN + i * CELL
            self.canvas.create_line(x, MARGIN, x, MARGIN+(BOARD_SIZE-1)*CELL,
                                    fill=t["line"], width=1)
            self.canvas.create_line(MARGIN, y, MARGIN+(BOARD_SIZE-1)*CELL, y,
                                    fill=t["line"], width=1)

        # 星位
        for r, c in [(3,3),(3,11),(7,7),(11,3),(11,11)]:
            cx = MARGIN + c * CELL
            cy = MARGIN + r * CELL
            self.canvas.create_oval(cx-4, cy-4, cx+4, cy+4,
                                    fill=t["star"], outline="")

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
            self.canvas.create_oval(cx-6, cy-6, cx+6, cy+6,
                                    outline=t["last_mark"], width=2)

        # 悬停预览
        if self._hover_pos and not self.game.winner and not self._ai_thinking:
            r, c = self._hover_pos
            if self.game.board[r][c] == 0:
                cx  = MARGIN + c * CELL
                cy  = MARGIN + r * CELL
                rad = CELL // 2 - 3
                col = t["hover_b"] if self.game.current == PLAYER_BLACK else t["hover_w"]
                self.canvas.create_oval(cx-rad, cy-rad, cx+rad, cy+rad,
                                        fill=col, outline="", stipple="gray50")

        # AI 思考中提示
        if self._ai_thinking:
            self.canvas.create_text(
                CANVAS_SIZE//2, CANVAS_SIZE//2,
                text="AI 思考中...", font=("微软雅黑", 18, "bold"),
                fill=self.theme["last_mark"]
            )

    def _draw_stone(self, row, col, player):
        t   = self.theme
        cx  = MARGIN + col * CELL
        cy  = MARGIN + row * CELL
        rad = CELL // 2 - 3
        if player == PLAYER_BLACK:
            self.canvas.create_oval(cx-rad, cy-rad, cx+rad, cy+rad,
                                    fill=t["black"], outline=t["black_hi"], width=1)
            self.canvas.create_oval(cx-rad+3, cy-rad+3, cx-rad+9, cy-rad+9,
                                    fill=t["black_hi"], outline="")
        else:
            self.canvas.create_oval(cx-rad, cy-rad, cx+rad, cy+rad,
                                    fill=t["white"], outline=t["white_hi"], width=1)
            self.canvas.create_oval(cx-rad+3, cy-rad+3, cx-rad+9, cy-rad+9,
                                    fill=t["white_hi"], outline="")

    # ── 事件处理 ──────────────────────────────────────
    def _on_click(self, event):
        if self.game.winner or self._ai_thinking:
            return
        # AI 模式下，轮到 AI 时不响应点击
        if self.ai and self.game.current == self.ai.player:
            return
        col = round((event.x - MARGIN) / CELL)
        row = round((event.y - MARGIN) / CELL)
        if not (0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE):
            return
        self._do_place(row, col)

    def _do_place(self, row, col):
        player = self.game.current
        if self.game.place(row, col):
            snd = "place_black" if player == PLAYER_BLACK else "place_white"
            self.sound.play(snd)
            self._draw_board()
            self._update_status()
            if self.game.winner:
                self.sound.play("win")
                self.root.after(300, self._show_winner)
            elif self.ai and self.game.current == self.ai.player:
                self._ai_move_async()

    def _on_hover(self, event):
        col = round((event.x - MARGIN) / CELL)
        row = round((event.y - MARGIN) / CELL)
        pos = (row, col) if (0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE) else None
        if pos != self._hover_pos:
            self._hover_pos = pos
            self._draw_board()

    # ── AI 异步落子 ────────────────────────────────────
    def _ai_move_async(self):
        self._ai_thinking = True
        self._draw_board()
        self._update_status()

        def run():
            board_copy = [row[:] for row in self.game.board]
            r, c = self.ai.get_move(board_copy)
            self.root.after(0, lambda: self._ai_move_done(r, c))

        threading.Thread(target=run, daemon=True).start()

    def _ai_move_done(self, row, col):
        self._ai_thinking = False
        self._do_place(row, col)

    # ── 控制 ──────────────────────────────────────────
    def _restart(self):
        self.game.reset()
        self._hover_pos   = None
        self._ai_thinking = False
        self._draw_board()
        self._update_status()
        self.sound.play("start")
        # AI 执黑时先手
        if self.ai and self.game.current == self.ai.player:
            self._ai_move_async()

    def _undo(self):
        if self._ai_thinking:
            return
        steps = 2 if self.ai and len(self.game.history) >= 2 else 1
        if self.game.undo(steps):
            self.sound.play("undo")
            self._draw_board()
            self._update_status()

    def _update_status(self):
        if self._ai_thinking:
            text = "🤖 AI 思考中..."
        elif self.game.winner:
            text = f"🏆 {PLAYER_NAME[self.game.winner]} 获胜！"
        else:
            icon = "⚫" if self.game.current == PLAYER_BLACK else "⚪"
            is_ai = self.ai and self.game.current == self.ai.player
            suffix = "（AI）" if is_ai else ""
            text = f"{icon} {PLAYER_NAME[self.game.current]}{suffix} 落子"
        self.lbl_status.config(text=text)

    def _show_winner(self):
        name = PLAYER_NAME[self.game.winner]
        if messagebox.askyesno("游戏结束", f"🎉 {name} 获胜！\n\n是否重新开始？"):
            self._restart()


# ══════════════════════════════════════════════════════
#  入口
# ══════════════════════════════════════════════════════
def main():
    root = tk.Tk()
    app  = GomokuApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
