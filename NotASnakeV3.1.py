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

    MAX_LOGS = 7
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
    "ourple": pygame.Color(160, 32, 240),
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
            'gameover': self._find_music_file(['GameOver.wav', 'GameOver.mp3', 'GameOver.wav']),
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

        if not self.music_enabled or settings.get("music_muted", False):
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

# ─── SETTINGS ─────────────────────────────────────────────────
settings = {
    "music_muted":      False,
    "wrap_around":      False,
    "light_mode":       False,          # False = dark (default), True = light
    "grid_opacity":     0,              # 0, 127, or 255
    "control_scheme":   "wasd_arrows",  # "wasd_arrows", "ijkl", "arrows_only", "spacebar"
    "show_timer":       False,
    "fps_limit":        60,             # 30, 60, 120, 0=unlimited
    "hardcore":         False,
}

# Spacebar wildcard: cycles RIGHT -> DOWN -> LEFT -> UP
_SPACEBAR_CYCLE = ["RIGHT", "DOWN", "LEFT", "UP"]
_spacebar_idx   = 0   # current step in cycle

def get_key_directions():
    """Return key→direction dict for single-player based on current control scheme."""
    scheme = settings["control_scheme"]
    if scheme == "wasd_arrows":
        return {
            ord("w"): "UP",    ord("s"): "DOWN",
            ord("a"): "LEFT",  ord("d"): "RIGHT",
            pygame.K_UP: "UP", pygame.K_DOWN: "DOWN",
            pygame.K_LEFT: "LEFT", pygame.K_RIGHT: "RIGHT",
        }
    elif scheme == "ijkl":
        return {
            ord("i"): "UP",  ord("k"): "DOWN",
            ord("j"): "LEFT", ord("l"): "RIGHT",
        }
    elif scheme == "arrows_only":
        return {
            pygame.K_UP: "UP", pygame.K_DOWN: "DOWN",
            pygame.K_LEFT: "LEFT", pygame.K_RIGHT: "RIGHT",
        }
    else:  # spacebar — handled separately in the game loop
        return {}

# ─── BACKGROUND FILLER ────────────────────────────────────────
# To use a custom background image, set BACKGROUND_IMAGE_PATH to the
# file path of your image (e.g. "nasassets/bg.png").
# Leave as None for the default black screen.
BACKGROUND_IMAGE_PATH = None   # <-- put your image path here

_background_surface = None

def _load_background():
    global _background_surface
    if BACKGROUND_IMAGE_PATH is None:
        _background_surface = None
        return
    try:
        img = pygame.image.load(BACKGROUND_IMAGE_PATH).convert()
        _background_surface = pygame.transform.scale(img, (SCREEN_WIDTH, SCREEN_HEIGHT))
        print(f"Background loaded: {BACKGROUND_IMAGE_PATH}")
    except Exception as e:
        print(f"Background load failed: {e}")
        _background_surface = None

_load_background()

def get_bg_color():
    """Return the background fill colour based on light/dark mode."""
    return pygame.Color(255, 255, 255) if settings["light_mode"] else COLORS["black"]

def draw_background():
    """Call instead of screen.fill(black) to draw the custom background (or plain black)."""
    if _background_surface is not None and not settings["light_mode"]:
        screen.blit(_background_surface, (0, 0))
    else:
        screen.fill(get_bg_color())

    # ── Grid lines ──────────────────────────────────────────────
    grid_alpha = settings["grid_opacity"]   # 0, 127, or 255
    if grid_alpha > 0:
        if settings["light_mode"]:
            grid_rgb = (180, 180, 180)
        else:
            grid_rgb = (60, 60, 60)
        if grid_alpha == 255:
            # Draw directly (no surface needed, avoids per-frame allocation cost)
            for x in range(0, SCREEN_WIDTH, CELL_SIZE):
                pygame.draw.line(screen, grid_rgb, (x, 0), (x, SCREEN_HEIGHT))
            for y in range(0, SCREEN_HEIGHT, CELL_SIZE):
                pygame.draw.line(screen, grid_rgb, (0, y), (SCREEN_WIDTH, y))
        else:
            grid_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            for x in range(0, SCREEN_WIDTH, CELL_SIZE):
                pygame.draw.line(grid_surf, (*grid_rgb, grid_alpha), (x, 0), (x, SCREEN_HEIGHT))
            for y in range(0, SCREEN_HEIGHT, CELL_SIZE):
                pygame.draw.line(grid_surf, (*grid_rgb, grid_alpha), (0, y), (SCREEN_WIDTH, y))
            screen.blit(grid_surf, (0, 0))
    # ────────────────────────────────────────────────────────────

debug_overlay_visible = False

def draw_debug_overlay(tick_accum=None, tick_accum1=None, tick_accum2=None,
                       is_multiplayer=False):
    """Render an in-game debug panel in the top-left corner (toggle with F5)."""
    font = pygame.font.SysFont("consolas", 16)
    diff_label = next((k for k, v in DIFFICULTY_LEVELS.items() if v == DIFFICULTY), "Custom")

    lines = [
        f"",
        f"",
        f"[DEBUG] F5 to hide",
        f"Difficulty: {diff_label} ({DIFFICULTY})",
        f"Food pos:   {food_pos}",
        f"Wrap-around: {'ON' if settings['wrap_around'] else 'off'}",
        f"Music muted: {'YES' if settings['music_muted'] else 'no'}",
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

LEFTOVER_LINGER_MS  = 8000   
BURST_DURATION_MS   = 4000   
BURST_MULTIPLIER    = 2.0    

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

def show_score(choice, color, font, size, score1=None, score2=None, game_start_ms=None):
    # In light mode, use a dark colour for readability
    txt_color = (30, 30, 30) if settings["light_mode"] else color
    score_font = pygame.font.SysFont(font, size)
    if choice == 1:
        if score2 is None:
            score_text = f"Score: {score1}"
            score_surface = score_font.render(score_text, True, txt_color)
            screen.blit(score_surface, (10, 10))
        else:
            score1_surface = score_font.render(f"P1: {score1}", True, COLORS["head"])
            screen.blit(score1_surface, (10, 10))
            score2_surface = score_font.render(f"P2: {score2}", True, COLORS["head2"])
            screen.blit(score2_surface, (10, 40))

        info_surface = score_font.render("NotASnake v3.0", True, txt_color)
        info_rect = info_surface.get_rect(topright=(SCREEN_WIDTH - 10, 10))
        screen.blit(info_surface, info_rect)

        # ── Timer ────────────────────────────────────────────────
        if (settings["show_timer"] or settings["hardcore"]) and game_start_ms is not None:
            elapsed_s = (pygame.time.get_ticks() - game_start_ms) / 1000.0
            mins  = int(elapsed_s) // 60
            secs  = int(elapsed_s) % 60
            ms    = int((elapsed_s - int(elapsed_s)) * 100)
            timer_str = f"[T] {mins:02d}:{secs:02d}.{ms:02d}"
            t_color = (255, 60, 60) if settings["hardcore"] else txt_color
            t_surf = score_font.render(timer_str, True, t_color)
            t_rect = t_surf.get_rect(topright=(SCREEN_WIDTH - 10, 35))
            screen.blit(t_surf, t_rect)
    else:
        if score2 is None:
            score_text = f"NotASnake v3.0 | End Score: {score1}"
            score_surface = score_font.render(score_text, True, txt_color)
            screen.blit(score_surface, (SCREEN_WIDTH//2 - 250, SCREEN_HEIGHT * 4 // 5))
        else:
            score_text = f"NotASnake v3.0 | How cool! Two guys playing! | P1: {score1} | P2: {score2}"
            score_surface = score_font.render(score_text, True, txt_color)
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
    game_over_text = font.render("my head..", True, COLORS["red"])
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
            score_color = COLORS["ourple"] if score1 >= high_score and score1 > 0 else COLORS["white"]

        score_surface = score_font.render(score_text, True, score_color)
        score_rect = score_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        screen.blit(score_surface, score_rect)

        if not is_multiplayer:
            hs_font = pygame.font.SysFont("times", 24)
            if score1 >= high_score and score1 > 0:
                hs_text = "NEW HIGH SCORE!"
                hs_color = COLORS["ourple"]
            else:
                hs_text = f"Your highest ever score: {high_score}"
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
            exit_menu_text = menu_font.render("Main Menu", True, COLORS["ourple"])
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

    menu_font     = pygame.font.SysFont("times new roman", 72)
    diff_font     = pygame.font.SysFont("consolas", 28)
    controls_font = pygame.font.SysFont("consolas", 18)
    panel_font    = pygame.font.SysFont("consolas", 24)

    diff_names = list(DIFFICULTY_LEVELS.keys())
    current_diff_idx = 1
    for i, name in enumerate(diff_names):
        if DIFFICULTY_LEVELS[name] == DIFFICULTY:
            current_diff_idx = i
            break

    high_score = load_high_score()

    # Settings panel state
    PANEL_W       = 360
    panel_open    = False
    panel_x       = SCREEN_WIDTH          # starts off-screen right
    panel_target  = SCREEN_WIDTH          # target x for animation
    PANEL_SPEED   = 40                    # px per frame slide speed
    MENU_SHIFT    = PANEL_W // 2          # how far left buttons shift when panel opens

    def toggle_panel():
        nonlocal panel_open, panel_target
        panel_open   = not panel_open
        panel_target = SCREEN_WIDTH - PANEL_W if panel_open else SCREEN_WIDTH

    while True:
        # Animate panel slide
        if panel_x < panel_target:
            panel_x = min(panel_x + PANEL_SPEED, panel_target)
        elif panel_x > panel_target:
            panel_x = max(panel_x - PANEL_SPEED, panel_target)

        # Button horizontal offset — shifts left when panel is open
        slide_ratio  = 1.0 - (panel_x - (SCREEN_WIDTH - PANEL_W)) / PANEL_W
        slide_ratio  = max(0.0, min(1.0, slide_ratio))
        btn_cx       = SCREEN_WIDTH // 2 - int(MENU_SHIFT * slide_ratio)

        draw_background()
        mouse_pos = pygame.mouse.get_pos()

        # In light mode flip "white" text to near-black so it's readable
        lm = settings["light_mode"]
        txt   = (20, 20, 20)      if lm else COLORS["white"]
        dim   = (80, 80, 80)      if lm else (140, 140, 140)

        # ── Title & high score ──
        title_surface = pygame.font.SysFont("times new roman", 100).render("NotASnake v3.0", True, COLORS["green"])
        title_rect = title_surface.get_rect(center=(btn_cx, SCREEN_HEIGHT // 2 - 210))
        screen.blit(title_surface, title_rect)

        hs_surface = diff_font.render(f"High Score: {high_score}", True, COLORS["ourple"])
        hs_rect = hs_surface.get_rect(center=(btn_cx, SCREEN_HEIGHT // 2 - 130))
        screen.blit(hs_surface, hs_rect)

        # ── Difficulty picker ──
        diff_label = diff_font.render("Difficulty:", True, txt)
        screen.blit(diff_label, diff_label.get_rect(center=(btn_cx, SCREEN_HEIGHT // 2 - 45)))

        arrow_left  = diff_font.render("<", True, txt)
        arrow_right = diff_font.render(">", True, txt)
        diff_name_str = diff_names[current_diff_idx]
        diff_colors = {"Story game": txt, "The Classic": COLORS["green"],
                       "Faster!": COLORS["ourple"], "Whoosh!!!": COLORS["red"]}
        diff_val_surface = diff_font.render(diff_name_str, True, diff_colors[diff_name_str])

        arrow_left_rect  = arrow_left.get_rect(center=(btn_cx - 100, SCREEN_HEIGHT // 2))
        diff_val_rect    = diff_val_surface.get_rect(center=(btn_cx, SCREEN_HEIGHT // 2))
        arrow_right_rect = arrow_right.get_rect(center=(btn_cx + 100, SCREEN_HEIGHT // 2))

        if arrow_left_rect.collidepoint(mouse_pos):
            arrow_left = diff_font.render("<", True, COLORS["ourple"])
        if arrow_right_rect.collidepoint(mouse_pos):
            arrow_right = diff_font.render(">", True, COLORS["ourple"])

        screen.blit(arrow_left,      arrow_left_rect)
        screen.blit(diff_val_surface, diff_val_rect)
        screen.blit(arrow_right,     arrow_right_rect)

        # ── Main buttons ──
        single_text = menu_font.render("Single Player", True, txt)
        single_rect = single_text.get_rect(center=(btn_cx, SCREEN_HEIGHT // 2 + 60))
        multi_text  = menu_font.render("Local Multiplayer", True, txt)
        multi_rect  = multi_text.get_rect(center=(btn_cx, SCREEN_HEIGHT // 2 + 150))
        exit_text   = menu_font.render("Exit", True, txt)
        exit_rect   = exit_text.get_rect(center=(btn_cx, SCREEN_HEIGHT // 2 + 240))

        if single_rect.collidepoint(mouse_pos):
            single_text = menu_font.render("Single Player", True, COLORS["green"])
        if multi_rect.collidepoint(mouse_pos):
            multi_text  = menu_font.render("Local Multiplayer", True, COLORS["cyan"])
        if exit_rect.collidepoint(mouse_pos):
            exit_text   = menu_font.render("Exit", True, COLORS["red"])

        screen.blit(single_text, single_rect)
        screen.blit(multi_text,  multi_rect)
        screen.blit(exit_text,   exit_rect)

        # ── Settings button (gear icon, top-right) ──
        gear_font = pygame.font.SysFont("consolas", 28)
        gear_label = "[ Settings ]" if not panel_open else "[ Close ]"
        gear_color = COLORS["ourple"] if panel_open else txt
        gear_surf  = gear_font.render(gear_label, True, gear_color)
        gear_rect  = gear_surf.get_rect(topright=(SCREEN_WIDTH - 16, 16))
        if gear_rect.collidepoint(mouse_pos):
            gear_surf = gear_font.render(gear_label, True, COLORS["ourple"])
        screen.blit(gear_surf, gear_rect)

        setting_rects = {}   # reset each frame; filled during panel draw

        # ── Settings panel ──
        if panel_x < SCREEN_WIDTH:
            panel_surf = pygame.Surface((PANEL_W, SCREEN_HEIGHT), pygame.SRCALPHA)
            panel_surf.fill((15, 15, 30, 220))
            screen.blit(panel_surf, (panel_x, 0))

            px = panel_x + 24  # left edge of text inside panel

            # Panel title
            pt = panel_font.render("Settings", True, COLORS["green"])
            screen.blit(pt, (panel_x + PANEL_W // 2 - pt.get_width() // 2, 24))

            # Divider
            pygame.draw.line(screen, (60, 60, 80), (panel_x + 16, 60), (panel_x + PANEL_W - 16, 60), 1)

            def draw_setting(y, label, val_str, val_col, desc_lines):
                """Draw one settings row; returns (value_rect, new_y_after_divider)."""
                lbl  = panel_font.render(label, True, COLORS["white"])
                screen.blit(lbl, (px, y))
                vs   = panel_font.render(val_str, True, val_col if not vs_hover(y, val_str) else COLORS["ourple"])
                vr   = vs.get_rect(topright=(panel_x + PANEL_W - 16, y))
                if vr.collidepoint(mouse_pos):
                    vs = panel_font.render(val_str, True, COLORS["ourple"])
                screen.blit(vs, vr)
                for di, dl in enumerate(desc_lines):
                    ds = controls_font.render(dl, True, (140, 140, 160))
                    screen.blit(ds, (px, y + 30 + di * 18))
                row_h = 30 + len(desc_lines) * 18 + 14
                div_y = y + row_h
                pygame.draw.line(screen, (40, 40, 60),
                                 (panel_x + 16, div_y), (panel_x + PANEL_W - 16, div_y), 1)
                return vr, div_y + 14

            def vs_hover(y, val_str):
                """Check if the value button for a row at y is hovered."""
                vs_tmp = panel_font.render(val_str, True, COLORS["white"])
                vr_tmp = vs_tmp.get_rect(topright=(panel_x + PANEL_W - 16, y))
                return vr_tmp.collidepoint(mouse_pos)

            cur_y = 80

            # ── 1: Music ──────────────────────────────────────────
            mute_val = "[ MUTED ]" if settings["music_muted"] else "[ ON ]"
            mute_col = COLORS["red"] if settings["music_muted"] else COLORS["green"]
            mute_rect, cur_y = draw_setting(cur_y, "Music", mute_val, mute_col,
                                            ["Toggle music on/off"])
            setting_rects["music"] = mute_rect

            # ── 2: Wrap-Around ────────────────────────────────────
            wrap_val = "[ ON ]" if settings["wrap_around"] else "[ OFF ]"
            wrap_col = COLORS["green"] if settings["wrap_around"] else (160, 160, 160)
            wrap_rect, cur_y = draw_setting(cur_y, "Wrap-Around", wrap_val, wrap_col,
                                            ["Walls teleport you to", "the opposite side"])
            setting_rects["wrap"] = wrap_rect

            # ── 3: Light/Dark mode ────────────────────────────────
            lm_val = "[ LIGHT ]" if settings["light_mode"] else "[ DARK ]"
            lm_col = (255, 230, 80) if settings["light_mode"] else (160, 160, 220)
            lm_rect, cur_y = draw_setting(cur_y, "Theme", lm_val, lm_col,
                                          ["Dark = black/grey", "Light = white"])
            setting_rects["lightmode"] = lm_rect

            # ── 4: Grid lines ─────────────────────────────────────
            go = settings["grid_opacity"]
            grid_labels = {0: "[ OFF ]", 127: "[ 50% ]", 255: "[ 100% ]"}
            grid_val = grid_labels[go]
            grid_col = (160, 160, 160) if go == 0 else ((180, 255, 180) if go == 127 else COLORS["green"])
            grid_rect, cur_y = draw_setting(cur_y, "Grid Lines", grid_val, grid_col,
                                            ["Show grid: Off / 50% / 100%"])
            setting_rects["grid"] = grid_rect

            # ── 5: Controls (singleplayer) ────────────────────────
            scheme_labels = {
                "wasd_arrows": "[ WASD+Arrows ]",
                "ijkl":        "[ IJKL ]",
                "arrows_only": "[ Arrows only ]",
                "spacebar":    "[ SPACEBAR ]",
            }
            ctrl_val = scheme_labels[settings["control_scheme"]]
            ctrl_col = COLORS["cyan"]
            ctrl_rect, cur_y = draw_setting(cur_y, "SP Controls", ctrl_val, ctrl_col,
                                            ["Click to cycle scheme", "Space = cycle dirs"])
            setting_rects["controls"] = ctrl_rect

            # ── 6: Show Timer ─────────────────────────────────────
            tmr_val = "[ ON ]" if settings["show_timer"] else "[ OFF ]"
            tmr_col = COLORS["green"] if settings["show_timer"] else (160, 160, 160)
            tmr_rect, cur_y = draw_setting(cur_y, "Timer", tmr_val, tmr_col,
                                           ["Show elapsed time HUD"])
            setting_rects["timer"] = tmr_rect

            # ── 7: FPS limiter ────────────────────────────────────
            fps_labels = {30: "[ 30 FPS ]", 60: "[ 60 FPS ]", 120: "[ 120 FPS ]", 0: "[ Unlim. ]"}
            fps_val = fps_labels.get(settings["fps_limit"], "[ 60 FPS ]")
            fps_col = (180, 255, 180)
            fps_rect, cur_y = draw_setting(cur_y, "FPS Cap", fps_val, fps_col,
                                           ["30 / 60 / 120 / Unlim."])
            setting_rects["fps"] = fps_rect

            # ── 8: Hardcore ───────────────────────────────────────
            hc_val = "[ ON ]" if settings["hardcore"] else "[ OFF ]"
            hc_col = (255, 60, 60) if settings["hardcore"] else (160, 160, 160)
            hc_rect, cur_y = draw_setting(cur_y, "!! Hardcore", hc_val, hc_col,
                                          ["No pause, no burst,", "no wrap, timer forced"])
            setting_rects["hardcore"] = hc_rect

        # ── Controls hint (bottom) ──
        controls_text = [
            "Single Player: WASD or Arrow Keys",
            "Multiplayer: P1: WASD | P2: Arrow Keys",
            "Pause/Unpause: ESC | Return to Menu: M"
        ]
        for i, text in enumerate(controls_text):
            cs = controls_font.render(text, True, dim)
            cr = cs.get_rect(center=(btn_cx, SCREEN_HEIGHT - 68 + i * 22))
            screen.blit(cs, cr)

        # ── Events ──
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if gear_rect.collidepoint(event.pos):
                    toggle_panel()
                elif panel_x < SCREEN_WIDTH:
                    # Settings panel clicks
                    if setting_rects.get("music") and setting_rects["music"].collidepoint(event.pos):
                        settings["music_muted"] = not settings["music_muted"]
                        if settings["music_muted"]:
                            pygame.mixer.music.stop()
                            music_manager.current_music = None
                        else:
                            music_manager.play_music('menu', volume=0.5)
                    elif setting_rects.get("wrap") and setting_rects["wrap"].collidepoint(event.pos):
                        settings["wrap_around"] = not settings["wrap_around"]
                    elif setting_rects.get("lightmode") and setting_rects["lightmode"].collidepoint(event.pos):
                        settings["light_mode"] = not settings["light_mode"]
                    elif setting_rects.get("grid") and setting_rects["grid"].collidepoint(event.pos):
                        cycle = {0: 127, 127: 255, 255: 0}
                        settings["grid_opacity"] = cycle[settings["grid_opacity"]]
                    elif setting_rects.get("controls") and setting_rects["controls"].collidepoint(event.pos):
                        schemes = ["wasd_arrows", "ijkl", "arrows_only", "spacebar"]
                        idx = schemes.index(settings["control_scheme"])
                        settings["control_scheme"] = schemes[(idx + 1) % len(schemes)]
                    elif setting_rects.get("timer") and setting_rects["timer"].collidepoint(event.pos):
                        settings["show_timer"] = not settings["show_timer"]
                    elif setting_rects.get("fps") and setting_rects["fps"].collidepoint(event.pos):
                        fps_cycle = {30: 60, 60: 120, 120: 0, 0: 30}
                        settings["fps_limit"] = fps_cycle[settings["fps_limit"]]
                    elif setting_rects.get("hardcore") and setting_rects["hardcore"].collidepoint(event.pos):
                        settings["hardcore"] = not settings["hardcore"]
                        if settings["hardcore"]:
                            # Hardcore forces these off
                            settings["wrap_around"] = False
                    elif arrow_left_rect.collidepoint(event.pos):
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
                else:
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
        fps_cap = settings["fps_limit"]
        clock.tick(fps_cap if fps_cap > 0 else 0)

def draw_countdown():
    font_big  = pygame.font.SysFont("times new roman", 180)
    font_hint = pygame.font.SysFont("consolas", 24)
    bg_col    = get_bg_color()
    hint_col  = (30, 30, 30) if settings["light_mode"] else COLORS["white"]
    for count in (3, 2, 1):
        start = pygame.time.get_ticks()
        while pygame.time.get_ticks() - start < 800:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            elapsed = pygame.time.get_ticks() - start
            alpha   = max(0, 255 - int(elapsed / 800 * 255))
            screen.fill(bg_col)
            num_surf = font_big.render(str(count), True, COLORS["green"])
            num_surf.set_alpha(alpha)
            num_rect = num_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            screen.blit(num_surf, num_rect)
            hint_surf = font_hint.render("Get ready...", True, hint_col)
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
    global _spacebar_idx

    reset_single_game()
    _spacebar_idx = 0  # reset spacebar cycle
    draw_countdown()

    tick_accum  = 0.0
    game_start_ms = pygame.time.get_ticks()

    while True:
        now_ms = pygame.time.get_ticks()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                # ── Spacebar wildcard control scheme ──
                if settings["control_scheme"] == "spacebar":
                    if event.key == pygame.K_SPACE:
                        change_to = _SPACEBAR_CYCLE[_spacebar_idx % len(_SPACEBAR_CYCLE)]
                        _spacebar_idx += 1
                else:
                    key_directions = get_key_directions()
                    if event.key in key_directions:
                        change_to = key_directions[event.key]

                if event.key == pygame.K_F5:
                    debug_overlay_visible = not debug_overlay_visible
                    print(f"Debug overlay status: {'ON' if debug_overlay_visible else 'OFF'}")
                elif event.key == pygame.K_ESCAPE:
                    if not settings["hardcore"]:
                        if pause_menu(is_multiplayer=False):
                            return "menu"
                elif event.key == pygame.K_m:
                    if not settings["hardcore"]:
                        return "menu"
            elif event.type == pygame.ACTIVEEVENT:
                if event.state == pygame.APPINPUTFOCUS and not event.gain:
                    if not settings["hardcore"]:
                        if pause_menu(is_multiplayer=False):
                            return "menu"

        if burst1["active"] and now_ms >= burst1["end_ms"]:
            burst1["active"] = False
            print("Speedy end..")

        if leftover is not None and now_ms - leftover["born"] >= LEFTOVER_LINGER_MS:
            leftover = None
            print("Too slow! Burst pickup faded")

        # Hardcore: no speed boosts spawn (burst pickup immediately disappears)
        if settings["hardcore"] and leftover is not None:
            leftover = None

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

            # Wrap-around: disabled in hardcore mode
            if settings["wrap_around"] and not settings["hardcore"]:
                grid_w = (SCREEN_WIDTH  // CELL_SIZE) * CELL_SIZE
                grid_h = (SCREEN_HEIGHT // CELL_SIZE) * CELL_SIZE
                if snake_pos[0] < 0:           snake_pos[0] = grid_w - CELL_SIZE
                elif snake_pos[0] >= grid_w:   snake_pos[0] = 0
                if snake_pos[1] < 0:           snake_pos[1] = grid_h - CELL_SIZE
                elif snake_pos[1] >= grid_h:   snake_pos[1] = 0

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
                if not settings["hardcore"]:  # no burst in hardcore
                    burst1["active"] = True
                    burst1["end_ms"] = now_ms + BURST_DURATION_MS
                leftover = None
                print(f"Burst kidnapped!")

        draw_background()
        draw_leftover(leftover, now_ms)
        draw_snake(snake_pos, snake_body, direction, True, burst_active=burst1["active"])

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

        # Hardcore badge
        if settings["hardcore"]:
            hc_font = pygame.font.SysFont("consolas", 18)
            hc_surf = hc_font.render("!! HARDCORE !!", True, (255, 40, 40))
            screen.blit(hc_surf, (10, 35))

        game_over = (
            (not (settings["wrap_around"] and not settings["hardcore"]) and (
                snake_pos[0] < 0 or snake_pos[0] >= SCREEN_WIDTH or
                snake_pos[1] < 0 or snake_pos[1] >= SCREEN_HEIGHT
            )) or
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
                _spacebar_idx = 0
                music_manager.current_music = None
                music_manager.play_music('ingame', loop=True, volume=0.5)
                draw_countdown()
                tick_accum = 0.0
                game_start_ms = pygame.time.get_ticks()
                continue
            elif result == "main_menu":
                return "menu"
            else:
                pygame.quit()
                sys.exit()

        if debug_overlay_visible:
            draw_debug_overlay(tick_accum=tick_accum, is_multiplayer=False)

        show_score(1, COLORS["white"], "consolas", 20, score, None, game_start_ms=game_start_ms)
        pygame.display.update()

        # FPS limiter
        fps_cap = settings["fps_limit"]
        clock.tick(fps_cap if fps_cap > 0 else 0)

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
    game_start_ms = pygame.time.get_ticks()

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
            if settings["wrap_around"]:
                grid_w = (SCREEN_WIDTH  // CELL_SIZE) * CELL_SIZE
                grid_h = (SCREEN_HEIGHT // CELL_SIZE) * CELL_SIZE
                if snake1_pos[0] < 0:          snake1_pos[0] = grid_w - CELL_SIZE
                elif snake1_pos[0] >= grid_w:  snake1_pos[0] = 0
                if snake1_pos[1] < 0:          snake1_pos[1] = grid_h - CELL_SIZE
                elif snake1_pos[1] >= grid_h:  snake1_pos[1] = 0
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
            if settings["wrap_around"]:
                grid_w = (SCREEN_WIDTH  // CELL_SIZE) * CELL_SIZE
                grid_h = (SCREEN_HEIGHT // CELL_SIZE) * CELL_SIZE
                if snake2_pos[0] < 0:          snake2_pos[0] = grid_w - CELL_SIZE
                elif snake2_pos[0] >= grid_w:  snake2_pos[0] = 0
                if snake2_pos[1] < 0:          snake2_pos[1] = grid_h - CELL_SIZE
                elif snake2_pos[1] >= grid_h:  snake2_pos[1] = 0
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

        draw_background()

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

        wall_kill = not settings["wrap_around"]
        head_collision = (snake1_pos == snake2_pos)

        p1_game_over = (
            (wall_kill and (
                snake1_pos[0] < 0 or snake1_pos[0] >= SCREEN_WIDTH or
                snake1_pos[1] < 0 or snake1_pos[1] >= SCREEN_HEIGHT
            )) or
            any(segment == snake1_pos for segment in snake1_body[1:]) or
            any(segment == snake1_pos for segment in snake2_body[1:]) or
            head_collision
        )
        p2_game_over = (
            (wall_kill and (
                snake2_pos[0] < 0 or snake2_pos[0] >= SCREEN_WIDTH or
                snake2_pos[1] < 0 or snake2_pos[1] >= SCREEN_HEIGHT
            )) or
            any(segment == snake2_pos for segment in snake2_body[1:]) or
            any(segment == snake2_pos for segment in snake1_body[1:]) or
            head_collision
        )

        if p1_game_over or p2_game_over:
            if p1_game_over and p2_game_over:
                # Both died same frame — highest score wins, equal is a tie
                if score1 > score2:
                    winner = "player1"
                elif score2 > score1:
                    winner = "player2"
                else:
                    winner = "tie"
            elif p1_game_over and not p2_game_over:
                winner = "player2"
            elif p2_game_over and not p1_game_over:
                winner = "player1"
            else:
                winner = "tie"  # fallback, should never happen

            print(f"Game over! Our winner={winner}, score1={score1}, score2={score2}")
            pixel_fill_effect()
            result = game_over_menu(is_multiplayer=True, score1=score1, score2=score2, winner=winner)
            if result == "play_again":
                reset_multiplayer_game()
                music_manager.current_music = None  # force reload so play_music doesn't skip
                music_manager.play_music('ingame', loop=True, volume=0.5)
                draw_countdown()
                tick_accum1 = tick_accum2 = 0.0
                game_start_ms = pygame.time.get_ticks()
                continue
            elif result == "main_menu":
                return "menu"
            else:
                pygame.quit()
                sys.exit()

        if debug_overlay_visible:
            draw_debug_overlay(tick_accum1=tick_accum1, tick_accum2=tick_accum2, is_multiplayer=True)

        show_score(1, COLORS["white"], "consolas", 20, score1, score2, game_start_ms=game_start_ms)
        pygame.display.update()
        fps_cap = settings["fps_limit"]
        clock.tick(fps_cap if fps_cap > 0 else 0)

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