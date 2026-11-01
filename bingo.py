import pygame
import random
import sys

# --- ตั้งค่าสีและขนาด ---
SCREEN_WIDTH = 900
SCREEN_HEIGHT = 650
GRID_SIZE = 5
CELL_SIZE = 75
GRID_X = 50
GRID_Y = 180

# โทนสี UI หลัก
BG_COLOR = (245, 247, 250)
PANEL_BG = (255, 255, 255)
TEXT_COLOR = (40, 40, 40)
HEADER_COLOR = (44, 62, 80)
ACCENT_BLUE = (52, 152, 219)
ACCENT_RED = (231, 76, 60)
ACCENT_PURPLE = (142, 68, 173)
CELL_BG = (236, 240, 241)
CELL_TEXT = (40, 40, 40)
MARKED_TEXT = (255, 255, 255)

# 🎨 สีประจำคอลัมน์ B - I - N - G - O
BINGO_COLORS = [
    (220, 53, 69),   # B: สีแดง
    (235, 130, 0),   # I: สีส้ม
    (212, 143, 24),  # N: สีเหลืองอำพัน
    (40, 167, 69),   # G: สีเขียว
    (0, 123, 255)    # O: สีน้ำเงิน
]


class BingoCard:
    """จัดการข้อมูลตารางบิงโกและการตรวจผลชนะ"""
    def __init__(self):
        self.grid = [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.marked = [[False for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.reset_card()

    def reset_card(self):
        self.marked = [[False for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        ranges = [(1, 15), (16, 30), (31, 45), (46, 60), (61, 75)]
        for col in range(GRID_SIZE):
            low, high = ranges[col]
            nums = random.sample(range(low, high + 1), GRID_SIZE)
            for row in range(GRID_SIZE):
                self.grid[row][col] = nums[row]

        self.grid[2][2] = "FREE"
        self.marked[2][2] = True

    def mark_number(self, number):
        """กาตัวเลขโดยอัตโนมัติ"""
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                if self.grid[r][c] == number:
                    self.marked[r][c] = True

    def try_mark_cell(self, row, col, called_numbers):
        """ผู้เล่นกดกาเอง (กาได้เฉพาะเลขที่สุ่มออกแล้ว)"""
        number = self.grid[row][col]
        if number in called_numbers and not self.marked[row][col]:
            self.marked[row][col] = True
            return True
        return False

    def check_bingo(self):
        for r in range(GRID_SIZE):
            if all(self.marked[r][c] for c in range(GRID_SIZE)):
                return True
        for c in range(GRID_SIZE):
            if all(self.marked[r][c] for r in range(GRID_SIZE)):
                return True
        if all(self.marked[i][i] for i in range(GRID_SIZE)):
            return True
        if all(self.marked[i][GRID_SIZE - 1 - i] for i in range(GRID_SIZE)):
            return True
        return False


class BallCaller:
    """สุ่มและบันทึกประวัติลูกบอลตัวเลข"""
    def __init__(self):
        self.reset()

    def reset(self):
        self.pool = list(range(1, 76))
        random.shuffle(self.pool)
        self.called_numbers = []
        self.current_ball = None

    def draw_ball(self):
        if self.pool:
            self.current_ball = self.pool.pop()
            self.called_numbers.append(self.current_ball)
            return self.current_ball
        return None

    def get_ball_label(self, ball):
        if ball is None:
            return "-"
        if 1 <= ball <= 15:
            prefix = "B"
        elif 16 <= ball <= 30:
            prefix = "I"
        elif 31 <= ball <= 45:
            prefix = "N"
        elif 46 <= ball <= 60:
            prefix = "G"
        elif 61 <= ball <= 75:
            prefix = "O"
        else:
            prefix = ""
        return f"{prefix}{ball}"

    def get_ball_color(self, ball):
        if ball is None:
            return (180, 180, 180)
        if 1 <= ball <= 15:
            return BINGO_COLORS[0]
        elif 16 <= ball <= 30:
            return BINGO_COLORS[1]
        elif 31 <= ball <= 45:
            return BINGO_COLORS[2]
        elif 46 <= ball <= 60:
            return BINGO_COLORS[3]
        elif 61 <= ball <= 75:
            return BINGO_COLORS[4]
        return (180, 180, 180)


class Button:
    """ส่วนประกอบ UI ปุ่มกด"""
    def __init__(self, x, y, width, height, text, color, hover_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color

    def draw(self, surface, font):
        mouse_pos = pygame.mouse.get_pos()
        color = self.hover_color if self.rect.collidepoint(mouse_pos) else self.color
        
        pygame.draw.rect(surface, color, self.rect, border_radius=10)
        pygame.draw.rect(surface, HEADER_COLOR, self.rect, width=2, border_radius=10)
        
        text_surf = font.render(self.text, True, (255, 255, 255))
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def is_clicked(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self.rect.collidepoint(event.pos)
        return False


class BingoGame:
    """ควบคุม Game Loop และการวาด UI ทั้งหมด"""
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Bingo Game - Auto/Manual Mode Edition")
        self.clock = pygame.time.Clock()

        self.title_font = pygame.font.SysFont("arial", 38, bold=True)
        self.font = pygame.font.SysFont("arial", 20, bold=True)
        self.small_font = pygame.font.SysFont("arial", 18)

        self.card = BingoCard()
        self.caller = BallCaller()
        self.is_won = False
        self.auto_mode = False  # เริ่มต้นเป็นโหมดกดเอง (Manual)

        # จัดตำแหน่งปุ่มกด 3 ปุ่มด้านขวา
        self.btn_draw = Button(500, 180, 105, 45, "Draw", ACCENT_BLUE, (41, 128, 185))
        self.btn_mode = Button(612, 180, 115, 45, "Auto: OFF", ACCENT_PURPLE, (125, 60, 152))
        self.btn_reset = Button(734, 180, 105, 45, "New Game", ACCENT_RED, (192, 57, 43))

    def run(self):
        running = True
        while running:
            self.clock.tick(60)
            running = self.handle_events()
            self.draw()
        pygame.quit()
        sys.exit()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            # กดปุ่มสุ่มลูกบอล
            if self.btn_draw.is_clicked(event) and not self.is_won:
                ball = self.caller.draw_ball()
                # ถ้าเปิดโหมด Auto ให้กาให้อัตโนมัติทันที
                if ball and self.auto_mode:
                    self.card.mark_number(ball)
                    if self.card.check_bingo():
                        self.is_won = True

            # กดปุ่มสลับโหมด Auto / Manual
            if self.btn_mode.is_clicked(event):
                self.auto_mode = not self.auto_mode
                self.btn_mode.text = "Auto: ON" if self.auto_mode else "Auto: OFF"
                
                # หากสลับมาเป็น Auto ให้ช่วยกากบาทตัวเลขที่เคยสุ่มออกไปแล้วทั้งหมดทันที
                if self.auto_mode:
                    for b in self.caller.called_numbers:
                        self.card.mark_number(b)
                    if self.card.check_bingo():
                        self.is_won = True

            # กดปุ่มเริ่มเกมใหม่
            if self.btn_reset.is_clicked(event):
                self.card.reset_card()
                self.caller.reset()
                self.is_won = False

            # คลิกเลือกช่องบนตารางบิงโก (ทำงานในโหมด Manual)
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and not self.is_won:
                mouse_pos = event.pos
                for col in range(GRID_SIZE):
                    for row in range(GRID_SIZE):
                        x = GRID_X + col * CELL_SIZE
                        y = GRID_Y + row * CELL_SIZE
                        cell_rect = pygame.Rect(x, y, CELL_SIZE - 5, CELL_SIZE - 5)

                        if cell_rect.collidepoint(mouse_pos):
                            if self.card.try_mark_cell(row, col, self.caller.called_numbers):
                                if self.card.check_bingo():
                                    self.is_won = True

        return True

    def draw_card(self):
        headers = ['B', 'I', 'N', 'G', 'O']
        for col in range(GRID_SIZE):
            column_color = BINGO_COLORS[col]

            header_rect = pygame.Rect(GRID_X + col * CELL_SIZE, GRID_Y - 45, CELL_SIZE - 5, 40)
            pygame.draw.rect(self.screen, column_color, header_rect, border_radius=5)
            h_text = self.font.render(headers[col], True, (255, 255, 255))
            self.screen.blit(h_text, h_text.get_rect(center=header_rect.center))

            for row in range(GRID_SIZE):
                x = GRID_X + col * CELL_SIZE
                y = GRID_Y + row * CELL_SIZE
                rect = pygame.Rect(x, y, CELL_SIZE - 5, CELL_SIZE - 5)

                is_marked = self.card.marked[row][col]
                bg_color = column_color if is_marked else CELL_BG
                txt_color = MARKED_TEXT if is_marked else CELL_TEXT

                pygame.draw.rect(self.screen, bg_color, rect, border_radius=8)
                pygame.draw.rect(self.screen, HEADER_COLOR, rect, width=1, border_radius=8)

                val = str(self.card.grid[row][col])
                f = self.small_font if val == "FREE" else self.font
                val_text = f.render(val, True, txt_color)
                self.screen.blit(val_text, val_text.get_rect(center=rect.center))

    def draw_caller_panel(self):
        panel_rect = pygame.Rect(500, 250, 340, 325)
        pygame.draw.rect(self.screen, PANEL_BG, panel_rect, border_radius=12)
        pygame.draw.rect(self.screen, (200, 200, 200), panel_rect, width=2, border_radius=12)

        title = self.font.render("Current Ball", True, TEXT_COLOR)
        self.screen.blit(title, (panel_rect.x + 20, panel_rect.y + 15))

        ball_color = self.caller.get_ball_color(self.caller.current_ball)
        circle_center = (panel_rect.x + 170, panel_rect.y + 110)
        pygame.draw.circle(self.screen, ball_color, circle_center, 55)

        current_val = self.caller.get_ball_label(self.caller.current_ball)
        ball_text = self.title_font.render(current_val, True, (255, 255, 255))
        self.screen.blit(ball_text, ball_text.get_rect(center=circle_center))

        history_title = self.small_font.render("Recent Calls:", True, TEXT_COLOR)
        self.screen.blit(history_title, (panel_rect.x + 20, panel_rect.y + 185))

        history = [self.caller.get_ball_label(b) for b in self.caller.called_numbers[-5:][::-1]]
        hist_str = ", ".join(history) if history else "None"
        hist_text = self.small_font.render(hist_str, True, (100, 100, 100))
        self.screen.blit(hist_text, (panel_rect.x + 20, panel_rect.y + 215))

        if self.is_won:
            win_text = self.title_font.render("BINGO! YOU WIN!", True, BINGO_COLORS[3])
            self.screen.blit(win_text, win_text.get_rect(center=(panel_rect.x + 170, panel_rect.y + 270)))

    def draw(self):
        self.screen.fill(BG_COLOR)

        title = self.title_font.render("BINGO GAME", True, HEADER_COLOR)
        self.screen.blit(title, (GRID_X, 40))

        self.draw_card()
        self.draw_caller_panel()
        self.btn_draw.draw(self.screen, self.font)
        self.btn_mode.draw(self.screen, self.font)
        self.btn_reset.draw(self.screen, self.font)

        pygame.display.flip()

if __name__ == "__main__":
    game = BingoGame()
    game.run()  