"""
CLASSIC CASINO BINGO - HIGH FIDELITY EDITION
Styled directly based on mobile Bingo Card aesthetics:
- 5 Vibrant Column Colors (Red, Gold, Green, Blue, Magenta)
- White glossy tile styling
- Red glossy Dauber stamps when marked
- Gold 3D star Free Space
- Auto-mark / Manual mark toggle
- Complete draw & win validation engine
"""

import math
import random
import tkinter as tk
from typing import List, Optional, Tuple
import customtkinter as ctk

# ==========================================
# COLOR PALETTE BASED ON REFERENCE IMAGE
# ==========================================
THEME = {
    "bg_app": "#122543",            # สีพื้นหลังน้ำเงินเข้มไล่เฉด
    "card_bg": "#1C355E",           # กรอบการ์ดบิงโกสีน้ำเงินมันวาว
    "card_inner": "#224175",        # ขอบรองพื้นการ์ด
    "text_dark": "#1A1A1A",         # สีตัวเลขบนช่องปกติ (สีดำเข้มคมชัด)
    "tile_normal": "#FFFFFF",       # ช่องตัวเลขสีขาวสว่าง
    "tile_hover": "#E2E8F0",        # สีเวลาชี้เมาส์
    "tile_border": "#94A3B8",       # ขอบช่องมนๆ
    
    # สีหัวคอลัมน์ B-I-N-G-O ตามภาพเป๊ะๆ
    "col_B": "#D32F2F",             # สีแดงสด
    "col_I": "#F59E0B",             # สีส้มทอง
    "col_N": "#10B981",             # สีเขียวสด
    "col_G": "#38BDF8",             # สีฟ้าสว่าง
    "col_O": "#D946EF",             # สีชมพูอมม่วง
    
    # Dauber สแตมป์สีแดงเวลาถูกมาร์ก
    "dauber_red": "#DC2626",        # แดงเข้มทรงเหรียญ
    "dauber_border": "#991B1B",     # ขอบเหรียญแดง
    "free_star_bg": "#DC2626",      # พื้นหลังช่องฟรีสีแดง
}

COLUMN_SPECS = [
    ("B", (1, 15), THEME["col_B"]),
    ("I", (16, 30), THEME["col_I"]),
    ("N", (31, 45), THEME["col_N"]),
    ("G", (46, 60), THEME["col_G"]),
    ("O", (61, 75), THEME["col_O"]),
]


class BingoBoard:
    """ระบบจัดการตารางและสุ่มตัวเลข 5x5"""
    def __init__(self):
        self.grid: List[List[int]] = [[0 for _ in range(5)] for _ in range(5)]
        self.marked: List[List[bool]] = [[False for _ in range(5)] for _ in range(5)]
        self.generate()

    def generate(self):
        cols = []
        for _, (low, high), _ in COLUMN_SPECS:
            cols.append(random.sample(range(low, high + 1), 5))

        for r in range(5):
            for c in range(5):
                self.grid[r][c] = cols[c][r]
                self.marked[r][c] = False

        # ช่องกลาง FREE SPACE ถูกเลือกตั้งแต่เริ่ม
        self.grid[2][2] = 0
        self.marked[2][2] = True

    def mark(self, r: int, c: int) -> bool:
        if not self.marked[r][c]:
            self.marked[r][c] = True
            return True
        return False

    def check_bingo(self) -> Tuple[bool, str, List[Tuple[int, int]]]:
        # แนวนอน
        for r in range(5):
            if all(self.marked[r][c] for c in range(5)):
                return True, f"แนวนอน (แถว {r+1})", [(r, c) for c in range(5)]
        
        # แนวตั้ง
        letters = ["B", "I", "N", "G", "O"]
        for c in range(5):
            if all(self.marked[r][c] for r in range(5)):
                return True, f"แนวตั้ง (คอลัมน์ {letters[c]})", [(r, c) for r in range(5)]

        # เส้นทแยงมุม
        if all(self.marked[i][i] for i in range(5)):
            return True, "แนวทแยง (ซ้ายบน ↘ ขวาล่าง)", [(i, i) for i in range(5)]

        if all(self.marked[i][4 - i] for i in range(5)):
            return True, "แนวทแยง (ขวาบน ↙ ซ้ายล่าง)", [(i, 4 - i) for i in range(5)]

        return False, "", []


class BingoApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("BINGO - Classic Dauber Edition")
        self.geometry("980x820")
        self.minsize(920, 780)
        self.configure(fg_color=THEME["bg_app"])

        ctk.set_appearance_mode("dark")

        # Game State
        self.board = BingoBoard()
        self.number_pool = list(range(1, 76))
        random.shuffle(self.number_pool)
        self.called_numbers: List[int] = []
        self.called_set = set()
        self.auto_mark = False
        self.is_game_over = False
        self.is_animating = False

        self.tile_buttons: dict[Tuple[int, int], ctk.CTkButton] = {}

        self.build_ui()

    def build_ui(self):
        # 1. TOP HEADER (Dashboard Controls)
        header = ctk.CTkFrame(self, fg_color="#0F1D33", height=65, corner_radius=0)
        header.pack(fill="x", side="top")
        header.pack_propagate(False)

        logo = ctk.CTkLabel(
            header,
            text="⭐ BINGO LIVE",
            font=ctk.CTkFont(family="Arial Black", size=22, weight="bold"),
            text_color="#FACC15"
        )
        logo.pack(side="left", padx=25)

        ctrl_frame = ctk.CTkFrame(header, fg_color="transparent")
        ctrl_frame.pack(side="right", padx=20)

        self.auto_switch = ctk.CTkSwitch(
            ctrl_frame,
            text="ระบบ Auto-Mark (มาร์กให้อัตโนมัติ)",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#E2E8F0",
            progress_color="#10B981",
            command=self.toggle_auto_mark
        )
        self.auto_switch.pack(side="left", padx=15)

        new_game_btn = ctk.CTkButton(
            ctrl_frame,
            text="🔄 สุ่มการ์ดใหม่",
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#334155",
            hover_color="#475569",
            text_color="#FFFFFF",
            width=110,
            height=36,
            corner_radius=8,
            command=self.reset_game
        )
        new_game_btn.pack(side="left", padx=5)

        # 2. MAIN CONTAINER
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=25, pady=20)

        # ---------------------------------------------
        # ซ้าย: BINGO CARD กรอบแก้วตามสไตล์ภาพต้นฉบับ
        # ---------------------------------------------
        card_outer_border = ctk.CTkFrame(
            content,
            fg_color=THEME["card_bg"],
            corner_radius=28,
            border_width=3,
            border_color="#38BDF8"
        )
        card_outer_border.pack(side="left", fill="both", expand=True, padx=(0, 20))

        card_pad = ctk.CTkFrame(
            card_outer_border,
            fg_color=THEME["card_inner"],
            corner_radius=22,
            border_width=2,
            border_color="#1E293B"
        )
        card_pad.pack(fill="both", expand=True, padx=12, pady=12)

        # ตั้งค่า Grid 5 Columns
        for c in range(5):
            card_pad.grid_columnconfigure(c, weight=1)
        for r in range(6):
            card_pad.grid_rowconfigure(r, weight=1)

        # หัว B - I - N - G - O 5 สีสดใส
        for idx, (letter, _, col_color) in enumerate(COLUMN_SPECS):
            header_cell = ctk.CTkFrame(
                card_pad,
                fg_color=col_color,
                corner_radius=14,
                border_width=2,
                border_color="#FFFFFF",
                height=60
            )
            header_cell.grid(row=0, column=idx, padx=4, pady=(4, 8), sticky="nsew")
            header_cell.pack_propagate(False)

            ctk.CTkLabel(
                header_cell,
                text=letter,
                font=ctk.CTkFont(family="Arial Black", size=32, weight="bold"),
                text_color="#FFFFFF"
            ).pack(expand=True)

        # ช่องตารางตัวเลข 5x5
        for r in range(5):
            for c in range(5):
                val = self.board.grid[r][c]
                is_free = (r == 2 and c == 2)

                if is_free:
                    # ช่อง FREE SPACE: เหรียญสีแดง + ดาวสีทอง 3D
                    btn = ctk.CTkButton(
                        card_pad,
                        text="⭐",
                        font=ctk.CTkFont(size=38),
                        fg_color=THEME["free_star_bg"],
                        hover_color=THEME["free_star_bg"],
                        text_color="#FACC15",
                        border_width=3,
                        border_color="#FDE047",
                        corner_radius=20,
                        command=lambda: None
                    )
                else:
                    # ช่องปกติ: การ์ดสีขาวนูนสวยงาม
                    btn = ctk.CTkButton(
                        card_pad,
                        text=str(val),
                        font=ctk.CTkFont(family="Arial Black", size=26, weight="bold"),
                        fg_color=THEME["tile_normal"],
                        hover_color=THEME["tile_hover"],
                        text_color=THEME["text_dark"],
                        border_width=2,
                        border_color=THEME["tile_border"],
                        corner_radius=16,
                        command=lambda row=r, col=c: self.on_tile_clicked(row, col)
                    )

                btn.grid(row=r+1, column=c, padx=4, pady=4, sticky="nsew")
                self.tile_buttons[(r, c)] = btn

        # ---------------------------------------------
        # ขวา: แผงควบคุมการสุ่มเลข (CALL BALL SECTION)
        # ---------------------------------------------
        right_panel = ctk.CTkFrame(
            content,
            fg_color="#1E293B",
            width=310,
            corner_radius=20,
            border_width=2,
            border_color="#334155"
        )
        right_panel.pack(side="right", fill="y")
        right_panel.pack_propagate(False)

        ctk.CTkLabel(
            right_panel,
            text="LUCKY BALL",
            font=ctk.CTkFont(family="Arial Black", size=16, weight="bold"),
            text_color="#38BDF8"
        ).pack(pady=(20, 10))

        # บอลตัวเลขล่าสุดทรงกลมเงางาม
        ball_container = ctk.CTkFrame(
            right_panel,
            fg_color="#0F172A",
            corner_radius=16,
            width=240,
            height=160,
            border_width=2,
            border_color="#475569"
        )
        ball_container.pack(pady=5)
        ball_container.pack_propagate(False)

        self.ball_letter_lbl = ctk.CTkLabel(
            ball_container,
            text="READY",
            font=ctk.CTkFont(family="Arial Black", size=20, weight="bold"),
            text_color="#FACC15"
        )
        self.ball_letter_lbl.pack(pady=(20, 0))

        self.ball_number_lbl = ctk.CTkLabel(
            ball_container,
            text="--",
            font=ctk.CTkFont(family="Arial Black", size=60, weight="bold"),
            text_color="#FFFFFF"
        )
        self.ball_number_lbl.pack(pady=(0, 15))

        # ปุ่ม DRAW NUMBER สไตล์คาสิโน
        self.draw_button = ctk.CTkButton(
            right_panel,
            text="🎲 สุ่มตัวเลข (DRAW)",
            font=ctk.CTkFont(family="Arial Black", size=16, weight="bold"),
            fg_color="#D946EF",
            hover_color="#C026D3",
            text_color="#FFFFFF",
            height=48,
            corner_radius=12,
            command=self.draw_number
        )
        self.draw_button.pack(fill="x", padx=25, pady=(18, 5))

        self.pool_status_lbl = ctk.CTkLabel(
            right_panel,
            text="ออกแล้ว: 0 / 75",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#94A3B8"
        )
        self.pool_status_lbl.pack(pady=(0, 12))

        # ประวัติการออกเลข
        ctk.CTkLabel(
            right_panel,
            text="ประวัติตัวเลขก่อนหน้า",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#F1F5F9"
        ).pack(anchor="w", padx=25, pady=(8, 4))

        self.history_frame = ctk.CTkScrollableFrame(
            right_panel,
            fg_color="#0F172A",
            corner_radius=12,
            height=280
        )
        self.history_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

    # ==========================================
    # GAMEPLAY LOGIC
    # ==========================================
    def toggle_auto_mark(self):
        self.auto_mark = bool(self.auto_switch.get())
        if self.auto_mark and self.called_set:
            # หากเปิด Auto ให้กวาดมาร์กช่องที่ออกไปแล้วทันที
            for r in range(5):
                for c in range(5):
                    val = self.board.grid[r][c]
                    if val in self.called_set and not self.board.marked[r][c]:
                        self.apply_dauber_mark(r, c)

    def draw_number(self):
        if self.is_animating or self.is_game_over or not self.number_pool:
            return

        self.is_animating = True
        self.draw_button.configure(state="disabled", fg_color="#64748B")

        # Roll Animation สุ่มสลับตัวเลขแบบตื่นเต้น
        def roll(step):
            if step > 0:
                fake_n = random.randint(1, 75)
                self.ball_number_lbl.configure(text=str(fake_n))
                self.after(35, lambda: roll(step - 1))
            else:
                num = self.number_pool.pop()
                self.called_numbers.append(num)
                self.called_set.add(num)

                # หาคอลัมน์ของตัวเลข
                letter, col_color = "", "#FFFFFF"
                for l, (low, high), color in COLUMN_SPECS:
                    if low <= num <= high:
                        letter = l
                        col_color = color
                        break

                self.ball_letter_lbl.configure(text=f"COLUMN {letter}", text_color=col_color)
                self.ball_number_lbl.configure(text=str(num), text_color="#FFFFFF")
                self.pool_status_lbl.configure(text=f"ออกแล้ว: {len(self.called_numbers)} / 75")

                # เพิ่มรายการใน History
                self.add_history_entry(letter, num, col_color)

                # ตรวจสอบการทำเครื่องหมาย
                if self.auto_mark:
                    for r in range(5):
                        for c in range(5):
                            if self.board.grid[r][c] == num:
                                self.apply_dauber_mark(r, c)
                else:
                    # ช่วยกะพริบช่องสีเหลืองให้อ่อนๆ เพื่อให้ผู้เล่นหาเจอง่าย
                    for r in range(5):
                        for c in range(5):
                            if self.board.grid[r][c] == num and not self.board.marked[r][c]:
                                self.tile_buttons[(r, c)].configure(
                                    border_color="#FACC15",
                                    border_width=3
                                )

                self.is_animating = False
                if not self.is_game_over:
                    self.draw_button.configure(state="normal", fg_color="#D946EF")

        roll(9)

    def on_tile_clicked(self, r: int, c: int):
        if self.is_game_over or (r == 2 and c == 2):
            return

        val = self.board.grid[r][c]
        if val in self.called_set:
            self.apply_dauber_mark(r, c)
        else:
            # แจ้งเตือนสีกะพริบแดงหากเลขยังไม่ออก
            btn = self.tile_buttons[(r, c)]
            btn.configure(fg_color="#F87171")
            self.after(160, lambda: btn.configure(fg_color=THEME["tile_normal"]))

    def apply_dauber_mark(self, r: int, c: int):
        """เปลี่ยนช่องเป็นเหรียญ Dauber แดงสดตัวเลขขาวตามภาพ"""
        if self.board.mark(r, c):
            btn = self.tile_buttons[(r, c)]
            btn.configure(
                fg_color=THEME["dauber_red"],
                hover_color=THEME["dauber_red"],
                text_color="#FFFFFF",
                border_color="#FFFFFF",
                border_width=3,
                corner_radius=22  # ทำเป็นทรงกลม/เหรียญ
            )

            # ตรวจสอบบิงโก
            won, pattern, winning_cells = self.board.check_bingo()
            if won:
                self.is_game_over = True
                self.draw_button.configure(state="disabled", fg_color="#64748B")

                # ไฮไลต์แนวที่ชนะด้วยสีทองอร่าม
                for wr, wc in winning_cells:
                    if not (wr == 2 and wc == 2):
                        self.tile_buttons[(wr, wc)].configure(
                            fg_color="#F59E0B",
                            border_color="#FDE047"
                        )
                self.show_win_modal(pattern)

    def add_history_entry(self, letter: str, num: int, color: str):
        item = ctk.CTkFrame(self.history_frame, fg_color="#1E293B", height=36, corner_radius=8)
        item.pack(fill="x", pady=3, padx=4)

        tag = ctk.CTkLabel(
            item,
            text=f"{letter} - {num:02d}",
            font=ctk.CTkFont(family="Arial Black", size=13, weight="bold"),
            text_color=color
        )
        tag.pack(side="left", padx=12)

        idx_lbl = ctk.CTkLabel(
            item,
            text=f"#{len(self.called_numbers)}",
            font=ctk.CTkFont(size=11),
            text_color="#64748B"
        )
        idx_lbl.pack(side="right", padx=12)

    def show_win_modal(self, pattern: str):
        modal = ctk.CTkToplevel(self)
        modal.title("🎉 BINGO!")
        modal.geometry("420x350")
        modal.configure(fg_color="#0F172A")
        modal.transient(self)
        modal.grab_set()

        box = ctk.CTkFrame(
            modal,
            fg_color="#1E293B",
            corner_radius=20,
            border_width=2,
            border_color="#FACC15"
        )
        box.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(box, text="🏆", font=ctk.CTkFont(size=55)).pack(pady=(20, 0))
        ctk.CTkLabel(
            box,
            text="B I N G O !",
            font=ctk.CTkFont(family="Arial Black", size=32, weight="bold"),
            text_color="#FACC15"
        ).pack(pady=(0, 5))

        ctk.CTkLabel(
            box,
            text=f"รูปแบบที่ชนะ: {pattern}\nจำนวนตัวเลขที่สุ่ม: {len(self.called_numbers)} / 75",
            font=ctk.CTkFont(size=14),
            text_color="#E2E8F0",
            justify="center"
        ).pack(pady=(0, 20))

        ctk.CTkButton(
            box,
            text="เล่นใหม่อีกครั้ง",
            font=ctk.CTkFont(family="Arial Black", size=14, weight="bold"),
            fg_color="#D946EF",
            hover_color="#C026D3",
            height=42,
            corner_radius=10,
            command=lambda: [modal.destroy(), self.reset_game()]
        ).pack(fill="x", padx=40, pady=5)

    def reset_game(self):
        self.board = BingoBoard()
        self.number_pool = list(range(1, 76))
        random.shuffle(self.number_pool)
        self.called_numbers.clear()
        self.called_set.clear()
        self.is_game_over = False
        self.is_animating = False

        self.ball_letter_lbl.configure(text="READY", text_color="#FACC15")
        self.ball_number_lbl.configure(text="--", text_color="#FFFFFF")
        self.pool_status_lbl.configure(text="ออกแล้ว: 0 / 75")
        self.draw_button.configure(state="normal", fg_color="#D946EF")

        for w in self.history_frame.winfo_children():
            w.destroy()

        for r in range(5):
            for c in range(5):
                val = self.board.grid[r][c]
                is_free = (r == 2 and c == 2)
                btn = self.tile_buttons[(r, c)]
                if is_free:
                    btn.configure(
                        text="⭐",
                        fg_color=THEME["free_star_bg"],
                        hover_color=THEME["free_star_bg"],
                        text_color="#FACC15",
                        border_color="#FDE047",
                        border_width=3,
                        corner_radius=20
                    )
                else:
                    btn.configure(
                        text=str(val),
                        fg_color=THEME["tile_normal"],
                        hover_color=THEME["tile_hover"],
                        text_color=THEME["text_dark"],
                        border_color=THEME["tile_border"],
                        border_width=2,
                        corner_radius=16
                    )


if __name__ == "__main__":
    app = BingoApp()
    app.mainloop()