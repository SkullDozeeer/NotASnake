import sys
import os
import datetime

# ─── BABYSITTER DEBUG LOG ──────────────────────────────────
def _setup_debug_log():
    if getattr(sys, 'frozen', False):
        base_dir = os.path.dirname(sys.executable)
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))

    log_dir = os.path.join(base_dir, "nasassets")
    os.makedirs(log_dir, exist_ok=True)

    MAX_LOGS = 5
    try:
        existing = sorted(
            [f for f in os.listdir(log_dir) if f.startswith("babysitter_notes_") and f.endswith(".log")]
        )
        while len(existing) >= MAX_LOGS:
            oldest = os.path.join(log_dir, existing.pop(0))
            os.remove(oldest)
    except Exception:
        pass

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    log_path = os.path.join(log_dir, f"babysitter_notes_{timestamp}.log")

    log_file = open(log_path, "w", encoding="utf-8", buffering=1)

    sys.stdout = log_file
    sys.stderr = log_file

    print(f"=== Baby sitting since: {datetime.datetime.now()} ===")
    print(f"Where we at: {os.getcwd()}")
    print(f"More Where we at:   {base_dir}")
    print(f"Babysitting note №:     {log_path}")
    print("=" * 47)

_setup_debug_log()
# ────────────────────────────────────────────────────────────

import pygame # type: ignore
import random
import math


DIFFICULTY = 10 

DIFFICULTY_LEVELS = {
    "Story game":   6,
    "The Classic": 10,
    "Faster!":   16,
    "Whoosh!!!": 24,
}

def _get_highscore_path():
    if getattr(sys, 'frozen', False):
        base_dir = os.path.dirname(sys.executable)
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_dir, "nasassets", "highscore.txt")

def load_high_score():
    path = _get_highscore_path()
    try:
        with open(path, "r") as f:
            val = int(f.read().strip())
            return max(0, val)
    except Exception:
        return 0

def save_high_score(score):
    path = _get_highscore_path()
    try:
        score = max(0, int(score))
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            f.write(str(score))
        print(f"You da real high score! You got: {score}")
    except Exception as e:
        print(f"Hey bro! What the fuck did you do? Look: {e}")

SCREEN_WIDTH = 1366
SCREEN_HEIGHT = 768
CELL_SIZE = 20
PIXEL_EFFECT_SPEED = 150
COLORS = {
    "black": pygame.Color(0, 0, 0),
    "white": pygame.Color(255, 255, 255),
    "red": pygame.Color(255, 0, 0),
    "green": pygame.Color(0, 255, 0),
    "blue": pygame.Color(0, 0, 255),
    "yellow": pygame.Color(255, 255, 0),
    "cyan": pygame.Color(0, 255, 255),
    "magenta": pygame.Color(255, 0, 255),
    "orange": pygame.Color(255, 165, 0),
    "head": pygame.Color(247, 33, 33),
    "head2": pygame.Color(33, 33, 247),
    "yummers": pygame.Color(255, 200, 0)
}

pygame.init()
pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("NotASnake v3.0 | Thanks for playing!")

try:
    icon_paths = [
        "NASiconNEW.ico",
        "nasassets/NASiconNEW.ico",
        "NASicon2.ico",
        "nasassets/NASicon2.ico",
        os.path.join(os.path.dirname(__file__), "nasassets", "NASicon2.ico"),
        os.path.join(os.path.dirname(__file__), "NASiconNEW.ico")
    ]

    for icon_path in icon_paths:
        if os.path.exists(icon_path):
            icon = pygame.image.load(icon_path)
            pygame.display.set_icon(icon)
            print(f"Your beatiful icon here: {icon_path}")
            break
    else:
        print("Where my icon at?")
except Exception as e:
    print(f"The fuck did you do man? Look: {e}")

clock = pygame.time.Clock()

class MusicManager:
    def __init__(self):
        self.current_music = None
        self.music_enabled = True
        self.music_paths = {
            'menu': self._find_music_file(['Menu.wav', 'Menu.mp3', 'Menu.wav']),
            'gameover': self._find_music_file(['TryAgain.wav', 'TryAgain.mp3', 'TryAgain.wav']),
            'effect': self._find_music_file(['SlowDeath.wav', 'SlowDeath.mp3', 'SlowDeath.wav']),
            'ingame': self._find_music_file(['Worm-Rock.mp3', 'Worm-Rock.m4a', 'Worm-Rock.wav'])
        }

        for key, path in self.music_paths.items():
            if path:
                print(f"Hey, {key}. We go here today: {path}")
            else:
                print(f"Where my fucking {key} at bitch????")

    def _find_music_file(self, filenames):

        if getattr(sys, 'frozen', False):
            base_dir = os.path.dirname(sys.executable)
        else:
            base_dir = os.path.dirname(os.path.abspath(__file__))

        search_paths = [
            "music/",
            "nasassets/music/",
            "nasassets/",
            os.path.join(os.path.dirname(__file__), "music"),
            os.path.join(os.path.dirname(__file__), "nasassets", "music")
        ]

        for path in search_paths:
            for filename in filenames:
                full_path = os.path.join(path, filename)
                if os.path.exists(full_path):
                    return full_path

        return None

    def play_music(self, music_type, loop=True, volume=0.7):

        if not self.music_enabled:
            return

        try:
            music_file = self.music_paths.get(music_type)
            if music_file and os.path.exists(music_file):
                if self.current_music != music_file:
                    pygame.mixer.music.stop()
                    pygame.mixer.music.load(music_file)
                    pygame.mixer.music.set_volume(volume)

                    if loop and music_type != 'effect':
                        pygame.mixer.music.play(-1)
                    else:
                        pygame.mixer.music.play(0)

                    self.current_music = music_file
                    print(f"This slaps! {music_type} music is FIRE!: {os.path.basename(music_file)}")
            elif music_type == 'effect':
                self._play_effect_sound()
        except Exception as e:
            print(f"The fuck did you do? My party said that {e}")

    def _play_effect_sound(self):
        try:
            sample_rate = 22050
            duration = 0.5
            frequency = 440

            n_samples = int(round(duration * sample_rate))
            buf = bytearray(n_samples * 2)

            for i in range(n_samples):
                sample = int(32767.0 * 0.5 * (1.0 + math.sin(2 * math.pi * frequency * i / sample_rate)))
                buf[2 * i] = sample & 0xff
                buf[2 * i + 1] = (sample >> 8) & 0xff

            sound = pygame.mixer.Sound(buffer=bytes(buf))
            sound.set_volume(0.3)
            sound.play()
        except:
            pass

    def stop_music(self):
        pygame.mixer.music.stop()
        self.current_music = None

    def fadeout_music(self, duration=1000):
        pygame.mixer.music.fadeout(duration)
        self.current_music = None


music_manager = MusicManager()

debug_overlay_visible = False

def draw_debug_overlay(tick_accum=None, tick_accum1=None, tick_accum2=None,
                       is_multiplayer=False):
    """Render an in-game debug panel in the top-left corner (toggle with F5)."""
    font = pygame.font.SysFont("consolas", 16)
    diff_label = next((k for k, v in DIFFICULTY_LEVELS.items() if v == DIFFICULTY), "Custom")

    lines = [
        f"______________________",
        f"[DEBUG] F5 to hide",
        f"Difficulty: {diff_label} ({DIFFICULTY})",
        f"Food pos:   {food_pos}",
        f"Are you cool?:  sure...",
    ]

    if not is_multiplayer:
        lines += [
            f"Snake len:  {len(snake_body)}",
            f"Direction:  {direction}",
            f"Tick accum: {tick_accum:.3f}" if tick_accum is not None else "Tick accum: n/a",
            f"Burst:      {'ACTIVE' if burst1['active'] else 'off'}",
            f"Burst end:  {burst1['end_ms']}ms",
            f"Leftover:   {leftover}",
            f"if you see this, write to: skulldozer@dontmailme.ru ",
        ]
    else:
        lines += [
            f"P1 len:     {len(snake1_body)}  dir: {direction1}",
            f"P1 accum:   {tick_accum1:.3f}" if tick_accum1 is not None else "P1 accum: n/a",
            f"P1 burst:   {'ACTIVE' if burst1['active'] else 'off'}",
            f"P2 len:     {len(snake2_body)}  dir: {direction2}",
            f"P2 accum:   {tick_accum2:.3f}" if tick_accum2 is not None else "P2 accum: n/a",
            f"P2 burst:   {'ACTIVE' if burst2['active'] else 'off'}",
            f"Leftover:   {leftover}",
            f"if you see this, write to:   skulldozer@dontmailme.ru ",
        ]

    panel_w = 280
    line_h  = 18
    panel_h = len(lines) * line_h + 8
    panel   = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
    panel.fill((0, 0, 0, 180))
    screen.blit(panel, (0, 0))

    for i, line in enumerate(lines):
        color = (0, 255, 0) if i == 0 else (200, 200, 200)
        surf  = font.render(line, True, color)
        screen.blit(surf, (4, 4 + i * line_h))

snake_pos = [0, 0]
snake_body = []
food_pos = [0, 0]
food_spawn = True
direction = "RIGHT"
change_to = direction
score = 0

snake1_pos = [0, 0]
snake1_body = []
snake2_pos = [0, 0]
snake2_body = []
direction1 = "RIGHT"
change_to1 = direction1
direction2 = "LEFT"
change_to2 = direction2
score1 = 0
score2 = 0

LEFTOVER_LINGER_MS  = 10000   
BURST_DURATION_MS   = 5000   
BURST_MULTIPLIER    = 2.5    

leftover = None

burst1 = {"active": False, "end_ms": 0}
burst2 = {"active": False, "end_ms": 0}

def reset_single_game():
    global snake_pos, snake_body, food_pos, food_spawn, direction, change_to, score
    global leftover, burst1
    start_x = (SCREEN_WIDTH // (2 * CELL_SIZE)) * CELL_SIZE
    start_y = (SCREEN_HEIGHT // (2 * CELL_SIZE)) * CELL_SIZE
    snake_pos = [start_x, start_y]
    snake_body = [
        [start_x, start_y],
        [start_x - CELL_SIZE, start_y],
        [start_x - (2 * CELL_SIZE), start_y]
    ]
    direction = "RIGHT"
    change_to = direction
    score = 0
    food_pos = spawn_food(snake_body)
    food_spawn = True
    leftover = None
    burst1["active"] = False
    burst1["end_ms"] = 0

def reset_multiplayer_game():
    global snake1_pos, snake1_body, snake2_pos, snake2_body, food_pos, food_spawn
    global direction1, change_to1, direction2, change_to2, score1, score2
    global leftover, burst1, burst2

    start_x1 = (SCREEN_WIDTH // (4 * CELL_SIZE)) * CELL_SIZE
    start_y = (SCREEN_HEIGHT // (2 * CELL_SIZE)) * CELL_SIZE
    snake1_pos = [start_x1, start_y]
    snake1_body = [
        [start_x1, start_y],
        [start_x1 - CELL_SIZE, start_y],
        [start_x1 - (2 * CELL_SIZE), start_y]
    ]
    direction1 = "RIGHT"
    change_to1 = direction1
    score1 = 0

    start_x2 = (3 * SCREEN_WIDTH // (4 * CELL_SIZE)) * CELL_SIZE
    snake2_pos = [start_x2, start_y]
    snake2_body = [
        [start_x2, start_y],
        [start_x2 + CELL_SIZE, start_y],
        [start_x2 + (2 * CELL_SIZE), start_y]
    ]
    direction2 = "LEFT"
    change_to2 = direction2
    score2 = 0

    all_snake_positions = snake1_body + snake2_body
    food_pos = spawn_food(all_snake_positions)
    food_spawn = True
    leftover = None
    burst1["active"] = False;  burst1["end_ms"] = 0
    burst2["active"] = False;  burst2["end_ms"] = 0

def spawn_food(snake_bodies):
    occupied = set(map(tuple, snake_bodies))
    cols = (SCREEN_WIDTH  // CELL_SIZE) - 1
    rows = (SCREEN_HEIGHT // CELL_SIZE) - 1
    total_cells = cols * rows

    if len(occupied) >= total_cells:
        print("WARNING: Bro i`m full af! Where do I put my food???")
        return list(snake_bodies[0]) if snake_bodies else [CELL_SIZE, CELL_SIZE]

    for _attempt in range(total_cells * 2):
        new_pos = [
            random.randrange(1, (SCREEN_WIDTH  // CELL_SIZE)) * CELL_SIZE,
            random.randrange(1, (SCREEN_HEIGHT // CELL_SIZE)) * CELL_SIZE
        ]
        if tuple(new_pos) not in occupied:
            return new_pos

    print("WARNING: Uhhhh, yeah IDK where to put KFC boxes anymore, let me look..")
    for col in range(1, SCREEN_WIDTH  // CELL_SIZE):
        for row in range(1, SCREEN_HEIGHT // CELL_SIZE):
            candidate = [col * CELL_SIZE, row * CELL_SIZE]
            if tuple(candidate) not in occupied:
                return candidate

def draw_leftover(lv, now_ms):
    if lv is None:
        return
    age  = now_ms - lv["born"]
    frac = 1.0 - (age / LEFTOVER_LINGER_MS)  
    pulse = 0.5 + 0.5 * math.sin(now_ms / 100.0)
    r = int((180 + 75 * pulse) * frac)
    g = int(80 * frac)
    b = int(20 * frac)
    alpha = int(frac * 210)

    size   = max(4, int(CELL_SIZE * 0.6 * (0.8 + 0.2 * pulse)))
    offset = (CELL_SIZE - size) // 2
    x, y   = lv["pos"]

    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    surf.fill((r, g, b, alpha))
    screen.blit(surf, (x + offset, y + offset))

def show_score(choice, color, font, size, score1=None, score2=None):
    score_font = pygame.font.SysFont(font, size)
    if choice == 1:
        if score2 is None:
            score_text = f"Score: {score1}"
            score_surface = score_font.render(score_text, True, color)
            screen.blit(score_surface, (10, 10))
        else:
            score1_text = f"P1: {score1}"
            score1_surface = score_font.render(score1_text, True, COLORS["head"])
            screen.blit(score1_surface, (10, 10))

            score2_text = f"P2: {score2}"
            score2_surface = score_font.render(score2_text, True, COLORS["head2"])
            screen.blit(score2_surface, (10, 40))

        diff_label = next((k for k, v in DIFFICULTY_LEVELS.items() if v == DIFFICULTY), "Custom")
        info_text = "NotASnake v3.0"
        info_surface = score_font.render(info_text, True, color)
        info_rect = info_surface.get_rect(topright=(SCREEN_WIDTH - 10, 10))
        screen.blit(info_surface, info_rect)
    else:
        if score2 is None:
            score_text = f"NotASnake v3.0 | End Score: {score1}"
            score_surface = score_font.render(score_text, True, color)
            screen.blit(score_surface, (SCREEN_WIDTH//2 - 250, SCREEN_HEIGHT * 4 // 5))
        else:
            score_text = f"NotASnake v3.0 | How cool! Two guys playing! | P1: {score1} | P2: {score2}"
            score_surface = score_font.render(score_text, True, color)
            screen.blit(score_surface, (SCREEN_WIDTH//2 - 300, SCREEN_HEIGHT * 4 // 5))

def pixel_fill_effect():
    music_manager.play_music('effect', loop=False, volume=0.5)

    pixels = []
    pixel_size = 10

    for x in range(0, SCREEN_WIDTH, pixel_size):
        for y in range(0, SCREEN_HEIGHT, pixel_size):
            pixels.append((x, y))

    random.shuffle(pixels)

    drawn_pixels = 0
    font = pygame.font.SysFont("times new roman", 50)
    game_over_text = font.render("GAME OVER", True, COLORS["red"])
    game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))

    while drawn_pixels < len(pixels):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        batch_size = min(PIXEL_EFFECT_SPEED, len(pixels) - drawn_pixels)
        for i in range(batch_size):
            x, y = pixels[drawn_pixels + i]
            color = (random.randint(100, 255), random.randint(0, 100), random.randint(0, 100))
            pygame.draw.rect(screen, color, (x, y, pixel_size, pixel_size))

        drawn_pixels += batch_size

        if drawn_pixels > len(pixels) * 0.7:
            text_alpha = min(255, int((drawn_pixels / len(pixels)) * 255 * 2))
            text_surface = font.render("GAME OVER", True, COLORS["red"])
            text_surface.set_alpha(text_alpha)
            screen.blit(text_surface, game_over_rect)

        pygame.display.flip()
        clock.tick(60)

    pygame.time.delay(300)
    music_manager.stop_music()

def pause_menu(is_multiplayer=False):
    menu_font = pygame.font.SysFont("times new roman", 72)
    while True:
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        screen.blit(overlay, (0, 0))

        mouse_pos = pygame.mouse.get_pos()

        title_surface = menu_font.render("Paused", True, COLORS["white"])
        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100))
        screen.blit(title_surface, title_rect)

        resume_text = menu_font.render("Resume", True, COLORS["white"])
        resume_rect = resume_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        quit_text = menu_font.render("Quit to Menu", True, COLORS["white"])
        quit_rect = quit_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100))

        if resume_rect.collidepoint(mouse_pos):
            resume_text = menu_font.render("Resume", True, COLORS["green"])
        if quit_rect.collidepoint(mouse_pos):
            quit_text = menu_font.render("Quit to Menu", True, COLORS["red"])

        screen.blit(resume_text, resume_rect)
        screen.blit(quit_text, quit_rect)

        mode_text = "Multiplayer" if is_multiplayer else "Single Player"
        info_font = pygame.font.SysFont("consolas", 20)
        info_text = f"Mode: {mode_text}, if you see this, write to skulldozer@dontmailme.ru"
        info_surface = info_font.render(info_text, True, COLORS["white"])
        info_rect = info_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))
        screen.blit(info_surface, info_rect)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if resume_rect.collidepoint(event.pos):
                    return False
                elif quit_rect.collidepoint(event.pos):
                    return True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_RETURN:
                    return False  # resume

        pygame.display.update()

def game_over_menu(is_multiplayer=False, score1=0, score2=0, high_score=0, winner=None):
    music_manager.play_music('gameover', volume=0.6)

    menu_font = pygame.font.SysFont("times new roman", 72)

    while True:
        screen.fill(COLORS["black"])
        mouse_pos = pygame.mouse.get_pos()

        title_surface = pygame.font.SysFont("times new roman", 100).render("Game Over", True, COLORS["red"])
        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 180))
        screen.blit(title_surface, title_rect)

        if is_multiplayer:
            winner_font = pygame.font.SysFont("times new roman", 60)
            if winner == "player1":
                winner_text = "Player 1 Wins!"
                color = COLORS["head"]
            elif winner == "player2":
                winner_text = "Player 2 Wins!"
                color = COLORS["head2"]
            else:
                winner_text = "T-T-Tie!"
                color = COLORS["white"]

            winner_surface = winner_font.render(winner_text, True, color)
            winner_rect = winner_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 80))
            screen.blit(winner_surface, winner_rect)

        score_font = pygame.font.SysFont("times", 30)
        if is_multiplayer:
            score_text = f"P1: {score1} | P2: {score2}"
            score_color = COLORS["white"]
        else:
            score_text = f"End Score: {score1}"
            score_color = COLORS["yellow"] if score1 >= high_score and score1 > 0 else COLORS["white"]

        score_surface = score_font.render(score_text, True, score_color)
        score_rect = score_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        screen.blit(score_surface, score_rect)

        if not is_multiplayer:
            hs_font = pygame.font.SysFont("times", 24)
            if score1 >= high_score and score1 > 0:
                hs_text = "WOAH! NEW HIGH SCORE!!!"
                hs_color = COLORS["yellow"]
            else:
                hs_text = f"Your highest score: {high_score}"
                hs_color = COLORS["white"]
            hs_surface = hs_font.render(hs_text, True, hs_color)
            hs_rect = hs_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 40))
            screen.blit(hs_surface, hs_rect)

        play_again_text = menu_font.render("Play Again", True, COLORS["white"])
        play_again_rect = play_again_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 80))
        exit_menu_text = menu_font.render("Main Menu", True, COLORS["white"])
        exit_menu_rect = exit_menu_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 160))
        exit_desktop_text = menu_font.render("Exit Game", True, COLORS["white"])
        exit_desktop_rect = exit_desktop_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 240))

        if play_again_rect.collidepoint(mouse_pos):
            play_again_text = menu_font.render("Play Again", True, COLORS["green"])
        if exit_menu_rect.collidepoint(mouse_pos):
            exit_menu_text = menu_font.render("Main Menu", True, COLORS["yellow"])
        if exit_desktop_rect.collidepoint(mouse_pos):
            exit_desktop_text = menu_font.render("Exit Game", True, COLORS["red"])

        screen.blit(play_again_text, play_again_rect)
        screen.blit(exit_menu_text, exit_menu_rect)
        screen.blit(exit_desktop_text, exit_desktop_rect)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if play_again_rect.collidepoint(event.pos):
                    music_manager.stop_music()
                    return "play_again"
                elif exit_menu_rect.collidepoint(event.pos):
                    music_manager.stop_music()
                    return "main_menu"
                elif exit_desktop_rect.collidepoint(event.pos):
                    pygame.quit()
                    sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1 or event.key == pygame.K_RETURN:
                    music_manager.stop_music()
                    return "play_again"
                elif event.key == pygame.K_2 or event.key == pygame.K_m:
                    music_manager.stop_music()
                    return "main_menu"
                elif event.key == pygame.K_3 or event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

        pygame.display.update()

def main_menu():
    global DIFFICULTY
    music_manager.play_music('menu', volume=0.5)

    menu_font = pygame.font.SysFont("times new roman", 72)
    diff_font = pygame.font.SysFont("consolas", 28)
    info_font  = pygame.font.SysFont("consolas", 28)
    controls_font = pygame.font.SysFont("consolas", 18)

    diff_names = list(DIFFICULTY_LEVELS.keys())
    current_diff_idx = 1
    for i, name in enumerate(diff_names):
        if DIFFICULTY_LEVELS[name] == DIFFICULTY:
            current_diff_idx = i
            break

    high_score = load_high_score()

    while True:
        screen.fill(COLORS["black"])
        mouse_pos = pygame.mouse.get_pos()

        title_surface = pygame.font.SysFont("times new roman", 100).render("NotASnake v3.0", True, COLORS["green"])
        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 210))
        screen.blit(title_surface, title_rect)

        hs_color = COLORS["yellow"]
        hs_surface = diff_font.render(f"High Score: {high_score}", True, hs_color)
        hs_rect = hs_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 130))
        screen.blit(hs_surface, hs_rect)

        diff_label = diff_font.render("Difficulty:", True, COLORS["white"])
        diff_label_rect = diff_label.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 45))
        screen.blit(diff_label, diff_label_rect)

        arrow_left  = diff_font.render("<", True, COLORS["white"])
        arrow_right = diff_font.render(">", True, COLORS["white"])
        diff_name_str = diff_names[current_diff_idx]

        diff_colors = {"Story game": COLORS["white"], "The Classic": COLORS["green"],
                       "Faster!": COLORS["yellow"], "Whoosh!!!": COLORS["red"]}
        diff_val_surface = diff_font.render(diff_name_str, True, diff_colors[diff_name_str])

        arrow_left_rect  = arrow_left.get_rect(center=(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2))
        diff_val_rect    = diff_val_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        arrow_right_rect = arrow_right.get_rect(center=(SCREEN_WIDTH // 2 + 100, SCREEN_HEIGHT // 2))

        if arrow_left_rect.collidepoint(mouse_pos):
            arrow_left = diff_font.render("<", True, COLORS["yellow"])
        if arrow_right_rect.collidepoint(mouse_pos):
            arrow_right = diff_font.render(">", True, COLORS["yellow"])

        screen.blit(arrow_left,      arrow_left_rect)
        screen.blit(diff_val_surface, diff_val_rect)
        screen.blit(arrow_right,     arrow_right_rect)

        single_text = menu_font.render("Single Player", True, COLORS["white"])
        single_rect = single_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 90))
        multi_text  = menu_font.render("Local Multiplayer", True, COLORS["white"])
        multi_rect  = multi_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 180))
        exit_text   = menu_font.render("Exit", True, COLORS["white"])
        exit_rect   = exit_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 270))

        if single_rect.collidepoint(mouse_pos):
            single_text = menu_font.render("Single Player", True, COLORS["green"])
        if multi_rect.collidepoint(mouse_pos):
            multi_text = menu_font.render("Local Multiplayer", True, COLORS["cyan"])
        if exit_rect.collidepoint(mouse_pos):
            exit_text = menu_font.render("Exit", True, COLORS["red"])

        screen.blit(single_text, single_rect)
        screen.blit(multi_text,  multi_rect)
        screen.blit(exit_text,   exit_rect)

        controls_text = [
            "Single Player: WASD or Arrow Keys",
            "Multiplayer: P1: WASD | P2: Arrow Keys",
            "Pause/Unpause: ESC | Return to Menu: M"
        ]
        for i, text in enumerate(controls_text):
            cs = controls_font.render(text, True, COLORS["white"])
            cr = cs.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 80 + i * 25))
            screen.blit(cs, cr)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if arrow_left_rect.collidepoint(event.pos):
                    current_diff_idx = (current_diff_idx - 1) % len(diff_names)
                    DIFFICULTY = DIFFICULTY_LEVELS[diff_names[current_diff_idx]]
                elif arrow_right_rect.collidepoint(event.pos):
                    current_diff_idx = (current_diff_idx + 1) % len(diff_names)
                    DIFFICULTY = DIFFICULTY_LEVELS[diff_names[current_diff_idx]]
                elif single_rect.collidepoint(event.pos):
                    music_manager.stop_music()
                    return "single"
                elif multi_rect.collidepoint(event.pos):
                    music_manager.stop_music()
                    return "multi"
                elif exit_rect.collidepoint(event.pos):
                    pygame.quit()
                    sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    current_diff_idx = (current_diff_idx - 1) % len(diff_names)
                    DIFFICULTY = DIFFICULTY_LEVELS[diff_names[current_diff_idx]]
                elif event.key == pygame.K_RIGHT:
                    current_diff_idx = (current_diff_idx + 1) % len(diff_names)
                    DIFFICULTY = DIFFICULTY_LEVELS[diff_names[current_diff_idx]]
                elif event.key == pygame.K_1 or event.key == pygame.K_RETURN:
                    music_manager.stop_music()
                    return "single"
                elif event.key == pygame.K_2 or event.key == pygame.K_m:
                    music_manager.stop_music()
                    return "multi"
                elif event.key == pygame.K_3 or event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

        pygame.display.update()

def draw_countdown():
    font_big  = pygame.font.SysFont("times new roman", 180)
    font_hint = pygame.font.SysFont("consolas", 24)
    for count in (3, 2, 1):
        start = pygame.time.get_ticks()
        while pygame.time.get_ticks() - start < 800:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            elapsed = pygame.time.get_ticks() - start
            alpha   = max(0, 255 - int(elapsed / 800 * 255))
            screen.fill(COLORS["black"])
            num_surf = font_big.render(str(count), True, COLORS["green"])
            num_surf.set_alpha(alpha)
            num_rect = num_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            screen.blit(num_surf, num_rect)
            hint_surf = font_hint.render("Get ready...", True, COLORS["white"])
            hint_rect = hint_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 110))
            screen.blit(hint_surf, hint_rect)
            pygame.display.flip()
            clock.tick(60)

def draw_snake(pos, body, direction, is_head1=True, burst_active=False):
    if burst_active:
        pulse = 0.5 + 0.5 * math.sin(pygame.time.get_ticks() / 60.0)
        head_color = (255, int(140 * pulse), 0)  
    else:
        head_color = COLORS["head"] if is_head1 else COLORS["head2"]

    for idx, pos in enumerate(body):
        if idx == 0:  
            pygame.draw.rect(screen, head_color, pygame.Rect(
                pos[0], pos[1], CELL_SIZE, CELL_SIZE
            ))
            eye_size = CELL_SIZE // 5
            eye_color = COLORS["white"]

            if direction == "RIGHT":
                pygame.draw.rect(screen, eye_color, pygame.Rect(
                    pos[0] + CELL_SIZE - eye_size*2, pos[1] + eye_size,
                    eye_size, eye_size
                ))
                pygame.draw.rect(screen, eye_color, pygame.Rect(
                    pos[0] + CELL_SIZE - eye_size*2, pos[1] + CELL_SIZE - eye_size*2,
                    eye_size, eye_size
                ))
            elif direction == "LEFT":
                pygame.draw.rect(screen, eye_color, pygame.Rect(
                    pos[0] + eye_size, pos[1] + eye_size,
                    eye_size, eye_size
                ))
                pygame.draw.rect(screen, eye_color, pygame.Rect(
                    pos[0] + eye_size, pos[1] + CELL_SIZE - eye_size*2,
                    eye_size, eye_size
                ))
            elif direction == "UP":
                pygame.draw.rect(screen, eye_color, pygame.Rect(
                    pos[0] + eye_size, pos[1] + eye_size,
                    eye_size, eye_size
                ))
                pygame.draw.rect(screen, eye_color, pygame.Rect(
                    pos[0] + CELL_SIZE - eye_size*2, pos[1] + eye_size,
                    eye_size, eye_size
                ))
            elif direction == "DOWN":
                pygame.draw.rect(screen, eye_color, pygame.Rect(
                    pos[0] + eye_size, pos[1] + CELL_SIZE - eye_size*2,
                    eye_size, eye_size
                ))
                pygame.draw.rect(screen, eye_color, pygame.Rect(
                    pos[0] + CELL_SIZE - eye_size*2, pos[1] + CELL_SIZE - eye_size*2,
                    eye_size, eye_size
                ))
        else:  
            snake_len = max(len(body) - 1, 1)
            t = idx / snake_len  
            color_intensity = int(255 - t * 155)  
            if is_head1:
                body_color = (0, color_intensity, 0)  
            else:
                body_color = (0, 0, color_intensity)  

            pygame.draw.rect(screen, body_color, pygame.Rect(
                pos[0], pos[1], CELL_SIZE, CELL_SIZE
            ))
            border_color = (0, 200, 0) if is_head1 else (0, 0, 200)
            pygame.draw.rect(screen, border_color, pygame.Rect(
                pos[0], pos[1], CELL_SIZE, CELL_SIZE
            ), 1)

def single_player_game():
    music_manager.play_music('ingame', loop=True, volume=0.5)
    global snake_pos, snake_body, food_pos, food_spawn, direction, change_to, score
    global leftover, burst1
    global debug_overlay_visible

    reset_single_game()
    draw_countdown()

    tick_accum = 0.0

    while True:
        now_ms = pygame.time.get_ticks()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                key_directions = {
                    pygame.K_UP: "UP", ord("w"): "UP",
                    pygame.K_DOWN: "DOWN", ord("s"): "DOWN",
                    pygame.K_LEFT: "LEFT", ord("a"): "LEFT",
                    pygame.K_RIGHT: "RIGHT", ord("d"): "RIGHT"
                }
                if event.key in key_directions:
                    change_to = key_directions[event.key]
                elif event.key == pygame.K_F5:
                    debug_overlay_visible = not debug_overlay_visible
                    print(f"Debug overlay status: {'ON' if debug_overlay_visible else 'OFF'}")
                elif event.key == pygame.K_ESCAPE:
                    if pause_menu(is_multiplayer=False):
                        return "menu"
                elif event.key == pygame.K_m:
                    return "menu"
            elif event.type == pygame.ACTIVEEVENT:
                if event.state == pygame.APPINPUTFOCUS and not event.gain:
                    if pause_menu(is_multiplayer=False):
                        return "menu"

        if burst1["active"] and now_ms >= burst1["end_ms"]:
            burst1["active"] = False
            print("Speedy end..")

        if leftover is not None and now_ms - leftover["born"] >= LEFTOVER_LINGER_MS:
            leftover = None
            print("Too slow! Burst pickup faded")

        effective_difficulty = DIFFICULTY * (BURST_MULTIPLIER if burst1["active"] else 1.0)

        tick_accum += effective_difficulty / 60.0
        do_step = tick_accum >= 1.0
        if do_step:
            tick_accum -= 1.0

            opposites = {"UP": "DOWN", "DOWN": "UP", "LEFT": "RIGHT", "RIGHT": "LEFT"}
            if change_to != opposites[direction]:
                direction = change_to

            movement = {
                "UP": (0, -CELL_SIZE),
                "DOWN": (0, CELL_SIZE),
                "LEFT": (-CELL_SIZE, 0),
                "RIGHT": (CELL_SIZE, 0)
            }
            snake_pos[0] += movement[direction][0]
            snake_pos[1] += movement[direction][1]

            snake_body.insert(0, list(snake_pos))

            if snake_pos == food_pos:
                score += 1
                food_spawn = False
                pickup_pos = spawn_food(snake_body)  
                leftover = {"pos": pickup_pos, "born": now_ms}
                print(f"Yummies! Burst now at {pickup_pos}. Score: {score}")
            else:
                snake_body.pop()

            if not food_spawn:
                food_pos = spawn_food(snake_body)
                food_spawn = True

            if leftover is not None and snake_pos == leftover["pos"]:
                burst1["active"] = True
                burst1["end_ms"] = now_ms + BURST_DURATION_MS
                leftover = None
                print(f"Burst kidnapped!")

        screen.fill(COLORS["black"])

        draw_leftover(leftover, now_ms)

        draw_snake(snake_pos, snake_body, direction, True,
                   burst_active=burst1["active"])

        pygame.draw.rect(screen, COLORS["yummers"], pygame.Rect(
            food_pos[0], food_pos[1], CELL_SIZE, CELL_SIZE
        ))
        pygame.draw.rect(screen, (255, 255, 200), pygame.Rect(
            food_pos[0] + CELL_SIZE//4, food_pos[1] + CELL_SIZE//4,
            CELL_SIZE//4, CELL_SIZE//4
        ))

        if burst1["active"]:
            remaining = max(0, burst1["end_ms"] - now_ms)
            pulse = 0.5 + 0.5 * math.sin(now_ms / 80.0)
            r = int(255 * pulse)
            burst_font = pygame.font.SysFont("consolas", 22)
            burst_surf = burst_font.render(f"SPEED BURST ACTIVE FOR {remaining/1000:.1f}s", True, (r, 200, 0))
            screen.blit(burst_surf, (10, 35))

        game_over = (
            snake_pos[0] < 0 or snake_pos[0] >= SCREEN_WIDTH or
            snake_pos[1] < 0 or snake_pos[1] >= SCREEN_HEIGHT or
            any(segment == snake_pos for segment in snake_body[1:])
        )

        if game_over:
            hs = load_high_score()
            if score > hs:
                save_high_score(score)
            pixel_fill_effect()
            result = game_over_menu(is_multiplayer=False, score1=score, high_score=load_high_score())
            if result == "play_again":
                reset_single_game()
                draw_countdown()
                tick_accum = 0.0
                continue
            elif result == "main_menu":
                return "menu"
            else:
                pygame.quit()
                sys.exit()

        if debug_overlay_visible:
            draw_debug_overlay(tick_accum=tick_accum, is_multiplayer=False)

        show_score(1, COLORS["white"], "consolas", 20, score, None)
        pygame.display.update()
        clock.tick(60)

def multiplayer_game():
    music_manager.play_music('ingame', loop=True, volume=0.5)
    global snake1_pos, snake1_body, snake2_pos, snake2_body, food_pos, food_spawn
    global direction1, change_to1, direction2, change_to2, score1, score2
    global leftover, burst1, burst2
    global debug_overlay_visible

    reset_multiplayer_game()
    draw_countdown()

    tick_accum1 = 0.0
    tick_accum2 = 0.0

    while True:
        now_ms = pygame.time.get_ticks()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                p1_key_directions = {
                    ord("w"): "UP", ord("s"): "DOWN",
                    ord("a"): "LEFT", ord("d"): "RIGHT"
                }
                p2_key_directions = {
                    pygame.K_UP: "UP", pygame.K_DOWN: "DOWN",
                    pygame.K_LEFT: "LEFT", pygame.K_RIGHT: "RIGHT"
                }
                if event.key in p1_key_directions:
                    change_to1 = p1_key_directions[event.key]
                elif event.key in p2_key_directions:
                    change_to2 = p2_key_directions[event.key]
                elif event.key == pygame.K_F5:
                    debug_overlay_visible = not debug_overlay_visible
                    print(f"Debug overlay status: {'ON' if debug_overlay_visible else 'OFF'}")
                elif event.key == pygame.K_ESCAPE:
                    if pause_menu(is_multiplayer=True):
                        return "menu"
                elif event.key == pygame.K_m:
                    return "menu"
            elif event.type == pygame.ACTIVEEVENT:
                if event.state == pygame.APPINPUTFOCUS and not event.gain:
                    if pause_menu(is_multiplayer=True):
                        return "menu"

        if burst1["active"] and now_ms >= burst1["end_ms"]:
            burst1["active"] = False
        if burst2["active"] and now_ms >= burst2["end_ms"]:
            burst2["active"] = False

        if leftover is not None and now_ms - leftover["born"] >= LEFTOVER_LINGER_MS:
            leftover = None

        opposites = {"UP": "DOWN", "DOWN": "UP", "LEFT": "RIGHT", "RIGHT": "LEFT"}
        movement = {
            "UP": (0, -CELL_SIZE), "DOWN": (0, CELL_SIZE),
            "LEFT": (-CELL_SIZE, 0), "RIGHT": (CELL_SIZE, 0)
        }

        eff1 = DIFFICULTY * (BURST_MULTIPLIER if burst1["active"] else 1.0)
        tick_accum1 += eff1 / 60.0
        if tick_accum1 >= 1.0:
            tick_accum1 -= 1.0
            if change_to1 != opposites[direction1]:
                direction1 = change_to1
            snake1_pos[0] += movement[direction1][0]
            snake1_pos[1] += movement[direction1][1]
            snake1_body.insert(0, list(snake1_pos))

            if snake1_pos == food_pos:
                score1 += 1
                food_spawn = False
                pickup_pos = spawn_food(snake1_body + snake2_body)
                leftover = {"pos": pickup_pos, "born": now_ms}
            else:
                snake1_body.pop()

            if leftover is not None and snake1_pos == leftover["pos"]:
                burst1["active"] = True
                burst1["end_ms"] = now_ms + BURST_DURATION_MS
                leftover = None

        eff2 = DIFFICULTY * (BURST_MULTIPLIER if burst2["active"] else 1.0)
        tick_accum2 += eff2 / 60.0
        if tick_accum2 >= 1.0:
            tick_accum2 -= 1.0
            if change_to2 != opposites[direction2]:
                direction2 = change_to2
            snake2_pos[0] += movement[direction2][0]
            snake2_pos[1] += movement[direction2][1]
            snake2_body.insert(0, list(snake2_pos))

            if snake2_pos == food_pos:
                score2 += 1
                food_spawn = False
                pickup_pos = spawn_food(snake1_body + snake2_body)
                leftover = {"pos": pickup_pos, "born": now_ms}
            else:
                snake2_body.pop()

            if leftover is not None and snake2_pos == leftover["pos"]:
                burst2["active"] = True
                burst2["end_ms"] = now_ms + BURST_DURATION_MS
                leftover = None

        if not food_spawn:
            all_snake_positions = snake1_body + snake2_body
            food_pos = spawn_food(all_snake_positions)
            food_spawn = True

        screen.fill(COLORS["black"])

        draw_leftover(leftover, now_ms)
        draw_snake(snake1_pos, snake1_body, direction1, True,  burst_active=burst1["active"])
        draw_snake(snake2_pos, snake2_body, direction2, False, burst_active=burst2["active"])

        pygame.draw.rect(screen, COLORS["yummers"], pygame.Rect(
            food_pos[0], food_pos[1], CELL_SIZE, CELL_SIZE
        ))
        pygame.draw.rect(screen, (255, 255, 200), pygame.Rect(
            food_pos[0] + CELL_SIZE//4, food_pos[1] + CELL_SIZE//4,
            CELL_SIZE//4, CELL_SIZE//4
        ))

        hud_font = pygame.font.SysFont("consolas", 20)
        if burst1["active"]:
            remaining = max(0, burst1["end_ms"] - now_ms)
            pulse = 0.5 + 0.5 * math.sin(now_ms / 80.0)
            surf = hud_font.render(f"!! P1 BURST active for {remaining/1000:.1f}s", True, (255, int(200*pulse), 0))
            screen.blit(surf, (10, 60))
        if burst2["active"]:
            remaining = max(0, burst2["end_ms"] - now_ms)
            pulse = 0.5 + 0.5 * math.sin(now_ms / 80.0)
            surf = hud_font.render(f"!! P2 BURST active for {remaining/1000:.1f}s", True, (0, int(200*pulse), 255))
            screen.blit(surf, (10, 85))

        head_collision = (snake1_pos == snake2_pos)

        p1_game_over = (
            snake1_pos[0] < 0 or snake1_pos[0] >= SCREEN_WIDTH or
            snake1_pos[1] < 0 or snake1_pos[1] >= SCREEN_HEIGHT or
            any(segment == snake1_pos for segment in snake1_body[1:]) or
            any(segment == snake1_pos for segment in snake2_body[1:]) or
            head_collision
        )
        p2_game_over = (
            snake2_pos[0] < 0 or snake2_pos[0] >= SCREEN_WIDTH or
            snake2_pos[1] < 0 or snake2_pos[1] >= SCREEN_HEIGHT or
            any(segment == snake2_pos for segment in snake2_body[1:]) or
            any(segment == snake2_pos for segment in snake1_body[1:]) or
            head_collision
        )

        if p1_game_over or p2_game_over:
            if p1_game_over and p2_game_over:
                winner = "player1" if score1 > score2 else ("player2" if score2 > score1 else "tie")
            elif p1_game_over:
                winner = "player2"
            else:
                winner = "player1"

            print(f"Game over! Our winner={winner}, score1={score1}, score2={score2}")
            pixel_fill_effect()
            result = game_over_menu(is_multiplayer=True, score1=score1, score2=score2, winner=winner)
            if result == "play_again":
                reset_multiplayer_game()
                draw_countdown()
                tick_accum1 = tick_accum2 = 0.0
                continue
            elif result == "main_menu":
                return "menu"
            else:
                pygame.quit()
                sys.exit()

        if debug_overlay_visible:
            draw_debug_overlay(tick_accum1=tick_accum1, tick_accum2=tick_accum2, is_multiplayer=True)

        show_score(1, COLORS["white"], "consolas", 20, score1, score2)
        pygame.display.update()
        clock.tick(60)

if __name__ == "__main__":
    while True:
        game_mode = main_menu()

        if game_mode == "single":
            result = single_player_game()
            if result == "menu":
                continue
        elif game_mode == "multi":
            result = multiplayer_game()
            if result == "menu":
                continue
        else:
            pygame.quit()
            sys.exit()