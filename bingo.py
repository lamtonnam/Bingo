import pygame
import random
import sys
import math

# --- Pygame Setup ---
pygame.init()
pygame.font.init()

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Bingo Rogue")

# --- Colors ---
COLOR_BG = (18, 22, 30)
COLOR_CARD = (38, 45, 58)
COLOR_TEXT = (240, 240, 240)
COLOR_ACCENT = (255, 198, 0)
COLOR_MARKED = (46, 204, 113)
COLOR_BALL = (231, 76, 60)
COLOR_BUTTON = (52, 152, 219)
COLOR_RED = (231, 76, 60)
COLOR_GREEN = (46, 204, 113)

COLOR_MOD_RED = (180, 50, 50)
COLOR_MOD_BLUE = (40, 110, 180)
COLOR_MOD_YELLOW = (200, 160, 30)

# --- Fonts ---
FONT_MAIN = pygame.font.SysFont("Arial", 22, bold=True)
FONT_LARGE = pygame.font.SysFont("Arial", 36, bold=True)
FONT_TITLE = pygame.font.SysFont("Arial", 60, bold=True)
FONT_SMALL = pygame.font.SysFont("Arial", 16)
FONT_POPUP = pygame.font.SysFont("Arial", 26, bold=True)
FONT_BADGE = pygame.font.SysFont("Arial", 11, bold=True)


class FloatingText:
    def __init__(self, text, x, y, color=COLOR_ACCENT):
        self.text = text
        self.x = x
        self.y = y
        self.color = color
        self.alpha = 255
        self.lifetime = 65
        self.speed_y = -1.5

    def update(self):
        self.y += self.speed_y
        self.alpha -= 255 / self.lifetime
        if self.alpha < 0:
            self.alpha = 0

    def draw(self, surface):
        if self.alpha > 0:
            txt_surf = FONT_POPUP.render(self.text, True, self.color)
            txt_surf.set_alpha(int(self.alpha))
            txt_rect = txt_surf.get_rect(center=(self.x, self.y))
            surface.blit(txt_surf, txt_rect)


class Tile:
    def __init__(self, x, y, size, number, r, c, is_free=False):
        self.rect = pygame.Rect(x, y, size, size)
        self.number = number
        self.row_idx = r
        self.col_idx = c
        self.is_marked = is_free
        self.is_free = is_free
        self.is_in_bingo = False
        self.mod = None

    def draw(self, surface):
        if self.is_in_bingo:
            ticks = pygame.time.get_ticks()
            pulse = (math.sin(ticks * 0.008) + 1) / 2
            r_c = int(46 + (255 - 46) * pulse)
            g_c = int(204 + (198 - 204) * pulse)
            b_c = int(113 + (0 - 113) * pulse)
            color = (r_c, g_c, b_c)
            border_color = (255, 255, 255)
            border_width = 3
        elif self.is_marked:
            color = COLOR_MARKED
            border_color = (70, 80, 95)
            border_width = 2
        else:
            if self.mod == "RED":
                color = COLOR_MOD_RED
                border_color = (255, 120, 120)
                border_width = 3
            elif self.mod == "BLUE":
                color = COLOR_MOD_BLUE
                border_color = (120, 200, 255)
                border_width = 3
            elif self.mod == "YELLOW":
                color = COLOR_MOD_YELLOW
                border_color = (255, 235, 120)
                border_width = 3
            else:
                color = COLOR_CARD
                border_color = (70, 80, 95)
                border_width = 2

        pygame.draw.rect(surface, color, self.rect, border_radius=8)
        pygame.draw.rect(surface, border_color, self.rect, width=border_width, border_radius=8)

        if self.mod and not self.is_marked and not self.is_free:
            badge_text = ""
            if self.mod == "RED":
                badge_text = "+5 MULT"
            elif self.mod == "BLUE":
                badge_text = "2X SCORE"
            elif self.mod == "YELLOW":
                badge_text = "+$2 MON"

            badge_surf = FONT_BADGE.render(badge_text, True, (255, 255, 255))
            badge_rect = badge_surf.get_rect(center=(self.rect.centerx, self.rect.top + 12))
            surface.blit(badge_surf, badge_rect)

        txt = "FREE" if self.is_free else str(self.number)
        txt_surf = FONT_MAIN.render(txt, True, COLOR_TEXT)
        offset_y = 6 if (self.mod and not self.is_marked and not self.is_free) else 0
        txt_rect = txt_surf.get_rect(center=(self.rect.centerx, self.rect.centery + offset_y))
        surface.blit(txt_surf, txt_rect)


class Board:
    def __init__(self, start_x, start_y, existing_mods, size=5, tile_size=75, gap=8):
        self.size = size
        self.grid = []
        
        col_ranges = [(1, 15), (16, 30), (31, 45), (46, 60), (61, 75)]
        board_numbers = []
        for r in col_ranges:
            nums = random.sample(range(r[0], r[1] + 1), 5)
            board_numbers.append(nums)

        for row in range(size):
            row_tiles = []
            for col in range(size):
                x = start_x + col * (tile_size + gap)
                y = start_y + row * (tile_size + gap)
                
                is_free = (row == 2 and col == 2)
                num = 0 if is_free else board_numbers[col][row]
                
                tile = Tile(x, y, tile_size, num, row, col, is_free=is_free)
                if (row, col) in existing_mods:
                    tile.mod = existing_mods[(row, col)]

                row_tiles.append(tile)
            self.grid.append(row_tiles)

    def draw(self, surface):
        for row in self.grid:
            for tile in row:
                tile.draw(surface)

    def get_board_numbers(self):
        numbers = []
        for row in self.grid:
            for tile in row:
                if not tile.is_free:
                    numbers.append(tile.number)
        return numbers

    def mark_number(self, number):
        for row in self.grid:
            for tile in row:
                if tile.number == number and not tile.is_marked:
                    tile.is_marked = True
                    return tile
        return None

    def check_bingo_lines(self):
        lines = 0
        bingo_tiles = set()

        for r in range(self.size):
            if all(self.grid[r][c].is_marked for c in range(self.size)):
                lines += 1
                for c in range(self.size):
                    bingo_tiles.add(self.grid[r][c])

        for c in range(self.size):
            if all(self.grid[r][c].is_marked for r in range(self.size)):
                lines += 1
                for r in range(self.size):
                    bingo_tiles.add(self.grid[r][c])

        if all(self.grid[i][i].is_marked for i in range(self.size)):
            lines += 1
            for i in range(self.size):
                bingo_tiles.add(self.grid[i][i])

        if all(self.grid[i][self.size - 1 - i].is_marked for i in range(self.size)):
            lines += 1
            for i in range(self.size):
                bingo_tiles.add(self.grid[i][self.size - 1 - i])

        for tile in bingo_tiles:
            tile.is_in_bingo = True

        return lines


class BallBag:
    def __init__(self, guaranteed_numbers, filler_count=16):
        self.guaranteed_numbers = guaranteed_numbers
        self.filler_count = filler_count
        self.reset()

    def reset(self):
        pool = list(self.guaranteed_numbers)
        other_numbers = [n for n in range(1, 76) if n not in pool]
        
        count = min(len(other_numbers), max(0, self.filler_count))
        filler_numbers = random.sample(other_numbers, count)
        
        pool.extend(filler_numbers)
        random.shuffle(pool)
        
        self.balls = pool
        self.current_drawn = []

    def draw_balls(self, count=5):
        self.current_drawn = []
        for _ in range(count):
            if self.balls:
                self.current_drawn.append(self.balls.pop())

    def remove_ball(self, ball):
        if ball in self.current_drawn:
            self.current_drawn.remove(ball)


class ShopItem:
    def __init__(self, name, description, cost, item_type, data=None):
        self.name = name
        self.description = description
        self.cost = cost
        self.item_type = item_type
        self.data = data


class DivisibleSevenCap:
    def __init__(self):
        self.id = "DIV_7_CAP"
        self.name = "Lucky Div 7 Cap"
        self.description = "+25 Score if marked ball is divisible by 7"
        self.cost = 6
        self.count = 1
        self.color = (231, 76, 60)

    def apply_effect(self, state, ball):
        if ball % 7 == 0:
            state["chips"] += 25 * self.count


class CrosshairCap:
    def __init__(self):
        self.id = "CROSSHAIR_CAP"
        self.name = "Crosshair Cap"
        self.description = "+50 Score on every Marked Tile"
        self.cost = 6
        self.count = 1
        self.color = (52, 152, 219)

    def apply_effect(self, state, ball):
        state["chips"] += 50 * self.count


def draw_bottle_cap_icon(surface, center_x, center_y, radius, color):
    """วาดฝาขวดเหล็กขอบหยัก"""
    num_teeth = 16
    points = []
    for i in range(num_teeth * 2):
        angle = i * (2 * math.pi / (num_teeth * 2))
        r = radius if i % 2 == 0 else radius - int(radius * 0.12)
        x = center_x + math.cos(angle) * r
        y = center_y + math.sin(angle) * r
        points.append((x, y))

    pygame.draw.polygon(surface, (200, 200, 200), points)
    pygame.draw.circle(surface, color, (center_x, center_y), radius - int(radius * 0.15))
    pygame.draw.circle(surface, (255, 255, 255), (center_x, center_y), radius - int(radius * 0.28), width=2)


class GameManager:
    def __init__(self):
        self.game_state = "LOBBY"
        self.ante = 1
        self.money = 15
        self.bottle_caps = [DivisibleSevenCap()]
        self.bag_filler_count = 16
        self.board_mods = {}
        self.shop_items = []
        self.floating_texts = []
        
        self.grid_offset_x = 0
        self.grid_offset_y = 0

        self.shake_timer = 0
        self.shake_intensity = 0
        self.render_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))

    def start_new_game(self):
        self.ante = 1
        self.money = 15
        self.bottle_caps = [DivisibleSevenCap()]
        self.bag_filler_count = 16
        self.board_mods = {}
        self.game_state = "PLAYING"
        self.reset_round()

    def reset_round(self):
        self.board = Board(start_x=80, start_y=160, existing_mods=self.board_mods)
        board_nums = self.board.get_board_numbers()
        self.bag = BallBag(board_nums, filler_count=self.bag_filler_count)
        
        self.score = 0
        self.target_score = int(1000 * (1.5 ** (self.ante - 1)))
        self.hands_left = 6
        self.last_bingo_count = 0
        self.draw_button = pygame.Rect(540, 520, 380, 50)
        self.drawn_ball_rects = []
        self.floating_texts.clear()
        self.refresh_shop()
        self.roll_balls()

    def refresh_shop(self):
        pool = [
            ShopItem("Crosshair Cap", "+50 Score on every mark", 6, "CAP", CrosshairCap()),
            ShopItem("Lucky Div 7 Cap", "+25 Score on div by 7", 6, "CAP", DivisibleSevenCap()),
            ShopItem("Trim Bag (-4 Balls)", "Reduce bag size (Guaranteed Board)", 5, "BAG_TRIM"),
            ShopItem("Red Tile Mod", "Change 1 random tile to Red (+5 Mult)", 4, "TILE_MOD", "RED"),
            ShopItem("Blue Tile Mod", "Change 1 random tile to Blue (2x Score)", 4, "TILE_MOD", "BLUE"),
            ShopItem("Yellow Tile Mod", "Change 1 random tile to Yellow (+$2 Money)", 4, "TILE_MOD", "YELLOW"),
        ]
        random.shuffle(pool)
        self.shop_items = pool[:2]

    def trigger_shake(self, duration=15, intensity=8):
        self.shake_timer = duration
        self.shake_intensity = intensity

    def roll_balls(self):
        if self.hands_left > 0:
            self.bag.draw_balls(5)
            self.hands_left -= 1
            self.update_ball_ui()
            self.check_game_over()

    def update_ball_ui(self):
        self.drawn_ball_rects = []
        start_x = 540
        start_y = 420
        size = 60
        gap = 15
        for i, ball in enumerate(self.bag.current_drawn):
            rect = pygame.Rect(start_x + i * (size + gap), start_y, size, size)
            self.drawn_ball_rects.append((rect, ball))

    def handle_click(self, pos):
        if self.game_state == "LOBBY":
            start_btn = pygame.Rect(350, 480, 300, 70)
            if start_btn.collidepoint(pos):
                self.start_new_game()

        elif self.game_state == "PLAYING":
            if self.draw_button.collidepoint(pos):
                self.roll_balls()
                return

            for rect, ball in self.drawn_ball_rects:
                if rect.collidepoint(pos):
                    marked_tile = self.board.mark_number(ball)
                    if marked_tile:
                        self.bag.remove_ball(ball)
                        self.update_ball_ui()
                        self.score_marked_tile(ball, marked_tile)
                        self.check_game_over()
                    break

        elif self.game_state == "SHOP":
            btn1 = pygame.Rect(180, 240, 300, 140)
            if btn1.collidepoint(pos) and len(self.shop_items) > 0:
                self.buy_item(0)

            btn2 = pygame.Rect(520, 240, 300, 140)
            if btn2.collidepoint(pos) and len(self.shop_items) > 1:
                self.buy_item(1)

            next_btn = pygame.Rect(350, 480, 300, 60)
            if next_btn.collidepoint(pos):
                self.ante += 1
                if self.ante > 5:
                    self.game_state = "RUN_WIN"
                else:
                    self.game_state = "PLAYING"
                    self.reset_round()

        elif self.game_state in ["GAME_OVER", "RUN_WIN"]:
            retry_btn = pygame.Rect(190, 400, 280, 60)
            if retry_btn.collidepoint(pos):
                self.start_new_game()

            menu_btn = pygame.Rect(530, 400, 280, 60)
            if menu_btn.collidepoint(pos):
                self.game_state = "LOBBY"

    def buy_item(self, index):
        item = self.shop_items[index]
        if self.money >= item.cost:
            self.money -= item.cost
            
            if item.item_type == "CAP":
                new_cap = item.data
                existing = next((c for c in self.bottle_caps if c.id == new_cap.id), None)
                if existing:
                    existing.count += 1
                else:
                    self.bottle_caps.append(new_cap)
                    
            elif item.item_type == "BAG_TRIM":
                self.bag_filler_count = max(0, self.bag_filler_count - 4)
            elif item.item_type == "TILE_MOD":
                available_coords = []
                for r in range(5):
                    for c in range(5):
                        if (r, c) != (2, 2) and (r, c) not in self.board_mods:
                            available_coords.append((r, c))

                if available_coords:
                    chosen_coord = random.choice(available_coords)
                    self.board_mods[chosen_coord] = item.data
                    self.board.grid[chosen_coord[0]][chosen_coord[1]].mod = item.data

            self.shop_items.pop(index)

    def score_marked_tile(self, ball, tile):
        base_chips = 50
        current_bingos = self.board.check_bingo_lines()
        
        if current_bingos > self.last_bingo_count:
            new_lines = current_bingos - self.last_bingo_count
            self.trigger_shake(duration=15 + (new_lines * 5), intensity=6 + (new_lines * 3))
            self.last_bingo_count = current_bingos

        mult = 1 + current_bingos

        if tile.mod == "RED":
            mult += 5
        elif tile.mod == "BLUE":
            base_chips *= 2
        elif tile.mod == "YELLOW":
            self.money += 2

        state = {"chips": base_chips, "mult": mult}
        for cap in self.bottle_caps:
            cap.apply_effect(state, ball)

        scored = state["chips"] * state["mult"]
        self.score += scored

        color = COLOR_ACCENT if (current_bingos > 0 or tile.mod) else COLOR_GREEN
        popup_str = f"+{scored} ({state['chips']} x {state['mult']})"
        popup = FloatingText(popup_str, tile.rect.centerx, tile.rect.centery, color=color)
        self.floating_texts.append(popup)

    def check_game_over(self):
        if self.score >= self.target_score:
            reward = 4 + self.hands_left
            self.money += reward
            self.game_state = "SHOP"
            return

        board_numbers = [tile.number for row in self.board.grid for tile in row if not tile.is_marked]
        has_valid_move = any(ball in board_numbers for ball in self.bag.current_drawn)

        if self.hands_left <= 0 and not has_valid_move and self.score < self.target_score:
            self.game_state = "GAME_OVER"

    def draw(self, target_screen):
        self.render_surface.fill(COLOR_BG)

        if self.game_state == "LOBBY":
            self.draw_lobby_screen(self.render_surface)
        elif self.game_state == "PLAYING":
            self.draw_playing_screen(self.render_surface)
        elif self.game_state == "SHOP":
            self.draw_shop_screen(self.render_surface)
        elif self.game_state == "GAME_OVER":
            self.draw_game_over_screen(self.render_surface)
        elif self.game_state == "RUN_WIN":
            self.draw_run_win_screen(self.render_surface)

        for popup in self.floating_texts[:]:
            popup.update()
            popup.draw(self.render_surface)
            if popup.alpha <= 0:
                self.floating_texts.remove(popup)

        offset_x, offset_y = 0, 0
        if self.shake_timer > 0:
            self.shake_timer -= 1
            offset_x = random.randint(-self.shake_intensity, self.shake_intensity)
            offset_y = random.randint(-self.shake_intensity, self.shake_intensity)

        target_screen.fill((0, 0, 0))
        target_screen.blit(self.render_surface, (offset_x, offset_y))

    def draw_lobby_screen(self, surface):
        grid_size = 50
        self.grid_offset_x = (self.grid_offset_x + 0.6) % grid_size
        self.grid_offset_y = (self.grid_offset_y + 0.6) % grid_size

        surface.fill((20, 24, 34))
        grid_line_color = (36, 44, 62)

        start_x = int(self.grid_offset_x) - grid_size
        for x in range(start_x, SCREEN_WIDTH + grid_size, grid_size):
            pygame.draw.line(surface, grid_line_color, (x, 0), (x, SCREEN_HEIGHT), width=2)

        start_y = int(self.grid_offset_y) - grid_size
        for y in range(start_y, SCREEN_HEIGHT + grid_size, grid_size):
            pygame.draw.line(surface, grid_line_color, (0, y), (SCREEN_WIDTH, y), width=2)

        ticks = pygame.time.get_ticks() * 0.0015
        cap_size = 220
        cap_surf = pygame.Surface((cap_size, cap_size), pygame.SRCALPHA)
        center_c = cap_size // 2
        radius = 85

        draw_bottle_cap_icon(cap_surf, center_c, center_c, radius, (231, 76, 60))

        star_points = []
        for i in range(5 * 2):
            ang = i * (math.pi / 5) - math.pi / 2
            r_val = 32 if i % 2 == 0 else 14
            star_points.append((center_c + math.cos(ang) * r_val, center_c + math.sin(ang) * r_val))
        pygame.draw.polygon(cap_surf, COLOR_ACCENT, star_points)

        tilt_angle = math.sin(ticks * 2) * 12
        float_y = math.sin(ticks * 2.5) * 10

        rotated_cap = pygame.transform.rotate(cap_surf, tilt_angle)
        cap_rect = rotated_cap.get_rect(center=(SCREEN_WIDTH // 2, 180 + float_y))
        surface.blit(rotated_cap, cap_rect)

        title_shadow = FONT_TITLE.render("BINGO ROGUE", True, (0, 0, 0))
        title_txt = FONT_TITLE.render("BINGO ROGUE", True, COLOR_ACCENT)

        surface.blit(title_shadow, title_shadow.get_rect(center=(SCREEN_WIDTH // 2 + 4, 344)))
        surface.blit(title_txt, title_txt.get_rect(center=(SCREEN_WIDTH // 2, 340)))

        start_btn = pygame.Rect(350, 480, 300, 70)
        mouse_pos = pygame.mouse.get_pos()
        btn_color = (41, 128, 185) if start_btn.collidepoint(mouse_pos) else COLOR_BUTTON

        pygame.draw.rect(surface, (0, 0, 0), (start_btn.x + 4, start_btn.y + 4, start_btn.width, start_btn.height), border_radius=12)
        pygame.draw.rect(surface, btn_color, start_btn, border_radius=12)
        pygame.draw.rect(surface, (255, 255, 255), start_btn, width=2, border_radius=12)

        btn_txt = FONT_LARGE.render("START GAME", True, COLOR_TEXT)
        surface.blit(btn_txt, btn_txt.get_rect(center=start_btn.center))

    def draw_playing_screen(self, surface):
        self.board.draw(surface)

        score_txt = FONT_LARGE.render(f"Score: {self.score} / {self.target_score}", True, COLOR_ACCENT)
        surface.blit(score_txt, (80, 40))

        bag_count = 24 + self.bag_filler_count
        info_txt = FONT_MAIN.render(f"Ante: {self.ante}/5  |  Draws Left: {self.hands_left}  |  Money: ${self.money}  |  Bag: {bag_count} Balls", True, COLOR_TEXT)
        surface.blit(info_txt, (80, 95))

        label_balls = FONT_MAIN.render("Drawn Balls (Click to Mark):", True, COLOR_TEXT)
        surface.blit(label_balls, (540, 380))

        for rect, ball in self.drawn_ball_rects:
            pygame.draw.ellipse(surface, COLOR_BALL, rect)
            pygame.draw.ellipse(surface, (255, 255, 255), rect, width=2)
            txt = FONT_MAIN.render(str(ball), True, COLOR_TEXT)
            txt_rect = txt.get_rect(center=rect.center)
            surface.blit(txt, txt_rect)

        btn_color = COLOR_BUTTON if self.hands_left > 0 else (100, 100, 100)
        pygame.draw.rect(surface, btn_color, self.draw_button, border_radius=10)
        btn_txt = FONT_MAIN.render("REROLL / NEXT HAND", True, COLOR_TEXT)
        btn_rect = btn_txt.get_rect(center=self.draw_button.center)
        surface.blit(btn_txt, btn_rect)

        cap_title = FONT_MAIN.render("Active Bottle Caps:", True, COLOR_ACCENT)
        surface.blit(cap_title, (540, 160))
        for i, cap in enumerate(self.bottle_caps):
            c_rect = pygame.Rect(540, 200 + i * 70, 380, 60)
            pygame.draw.rect(surface, COLOR_CARD, c_rect, border_radius=8)
            
            draw_bottle_cap_icon(surface, c_rect.x + 30, c_rect.centery, 18, cap.color)

            count_str = f" (x{cap.count})" if cap.count > 1 else ""
            name_txt = FONT_MAIN.render(f"{cap.name}{count_str}", True, COLOR_ACCENT)
            desc_txt = FONT_SMALL.render(cap.description, True, COLOR_TEXT)
            surface.blit(name_txt, (c_rect.x + 60, c_rect.y + 8))
            surface.blit(desc_txt, (c_rect.x + 60, c_rect.y + 32))

    def draw_shop_screen(self, surface):
        title = FONT_TITLE.render("STAGE CLEAR - SHOP", True, COLOR_GREEN)
        surface.blit(title, (200, 60))

        money_txt = FONT_LARGE.render(f"Current Money: ${self.money}", True, COLOR_ACCENT)
        surface.blit(money_txt, (360, 140))

        if len(self.shop_items) > 0:
            item = self.shop_items[0]
            btn1 = pygame.Rect(180, 240, 300, 140)
            btn_color = COLOR_CARD if self.money >= item.cost else (80, 50, 50)
            pygame.draw.rect(surface, btn_color, btn1, border_radius=10)
            pygame.draw.rect(surface, COLOR_ACCENT, btn1, width=2, border_radius=10)
            
            name_txt = FONT_MAIN.render(f"{item.name} (${item.cost})", True, COLOR_ACCENT)
            desc_txt = FONT_SMALL.render(item.description, True, COLOR_TEXT)
            surface.blit(name_txt, (btn1.x + 15, btn1.y + 20))
            surface.blit(desc_txt, (btn1.x + 15, btn1.y + 60))

        if len(self.shop_items) > 1:
            item = self.shop_items[1]
            btn2 = pygame.Rect(520, 240, 300, 140)
            btn_color = COLOR_CARD if self.money >= item.cost else (80, 50, 50)
            pygame.draw.rect(surface, btn_color, btn2, border_radius=10)
            pygame.draw.rect(surface, COLOR_ACCENT, btn2, width=2, border_radius=10)
            
            name_txt = FONT_MAIN.render(f"{item.name} (${item.cost})", True, COLOR_ACCENT)
            desc_txt = FONT_SMALL.render(item.description, True, COLOR_TEXT)
            surface.blit(name_txt, (btn2.x + 15, btn2.y + 20))
            surface.blit(desc_txt, (btn2.x + 15, btn2.y + 60))

        next_btn = pygame.Rect(350, 480, 300, 60)
        pygame.draw.rect(surface, COLOR_BUTTON, next_btn, border_radius=10)
        next_txt = FONT_MAIN.render("NEXT ANTE", True, COLOR_TEXT)
        surface.blit(next_txt, (next_btn.x + 95, next_btn.y + 18))

    def draw_game_over_screen(self, surface):
        title = FONT_TITLE.render("GAME OVER", True, COLOR_RED)
        surface.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, 200)))

        score_txt = FONT_LARGE.render(f"Final Score: {self.score} / {self.target_score}", True, COLOR_TEXT)
        surface.blit(score_txt, score_txt.get_rect(center=(SCREEN_WIDTH // 2, 290)))

        retry_btn = pygame.Rect(190, 400, 280, 60)
        pygame.draw.rect(surface, COLOR_GREEN, retry_btn, border_radius=10)
        btn1_txt = FONT_MAIN.render("RETRY", True, COLOR_TEXT)
        surface.blit(btn1_txt, btn1_txt.get_rect(center=retry_btn.center))

        menu_btn = pygame.Rect(530, 400, 280, 60)
        pygame.draw.rect(surface, COLOR_BUTTON, menu_btn, border_radius=10)
        btn2_txt = FONT_MAIN.render("MAIN MENU", True, COLOR_TEXT)
        surface.blit(btn2_txt, btn2_txt.get_rect(center=menu_btn.center))

    def draw_run_win_screen(self, surface):
        title = FONT_TITLE.render("VICTORY! RUN COMPLETE!", True, COLOR_ACCENT)
        surface.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, 200)))

        money_txt = FONT_LARGE.render(f"Final Money: ${self.money}", True, COLOR_TEXT)
        surface.blit(money_txt, money_txt.get_rect(center=(SCREEN_WIDTH // 2, 290)))

        retry_btn = pygame.Rect(190, 400, 280, 60)
        pygame.draw.rect(surface, COLOR_GREEN, retry_btn, border_radius=10)
        btn1_txt = FONT_MAIN.render("PLAY AGAIN", True, COLOR_TEXT)
        surface.blit(btn1_txt, btn1_txt.get_rect(center=retry_btn.center))

        menu_btn = pygame.Rect(530, 400, 280, 60)
        pygame.draw.rect(surface, COLOR_BUTTON, menu_btn, border_radius=10)
        btn2_txt = FONT_MAIN.render("MAIN MENU", True, COLOR_TEXT)
        surface.blit(btn2_txt, btn2_txt.get_rect(center=menu_btn.center))


def main():
    clock = pygame.time.Clock()
    game = GameManager()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                game.handle_click(event.pos)

        game.draw(screen)
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()