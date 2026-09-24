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

SA_TARGETS = [15, 30, 50]

def _get_save_path():
    if getattr(sys, 'frozen', False):
        base_dir = os.path.dirname(sys.executable)
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_dir, "nasassets", "save.txt")

def _get_highscore_path():
    if getattr(sys, 'frozen', False):
        base_dir = os.path.dirname(sys.executable)
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_dir, "nasassets", "highscore.txt")

_SETTINGS_BOOL_KEYS  = ["music_muted", "wrap_around", "light_mode", "show_timer", "hardcore", "double_food"]
_SETTINGS_INT_KEYS   = ["grid_opacity", "fps_limit"]
_SETTINGS_STR_KEYS   = ["control_scheme"]

def load_save():
    path = _get_save_path()
    data = {
        "score": 0, "seed": "", "double_food": True,
        "apples": set(), "sa_best_15": 0, "sa_best_30": 0, "sa_best_50": 0,
        "music_muted": False, "wrap_around": False, "light_mode": False,
        "show_timer": False, "hardcore": False, "grid_opacity": 0,
        "fps_limit": 60, "control_scheme": "wasd_arrows",
    }
    try:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or "=" not in line:
                    continue
                key, _, val = line.partition("=")
                val = val.strip()
                if key == "score":
                    try: data["score"] = max(0, int(val))
                    except ValueError: pass
                elif key == "seed":
                    data["seed"] = val
                elif key == "apples":
                    if val:
                        data["apples"] = set(int(x) for x in val.split(",") if x.strip().isdigit())
                elif key.startswith("sa_best_"):
                    try:
                        t = int(key[8:])
                        data[f"sa_best_{t}"] = int(val) if val else 0
                    except ValueError:
                        pass
                elif key in _SETTINGS_BOOL_KEYS:
                    data[key] = val == "1"
                elif key in _SETTINGS_INT_KEYS:
                    try: data[key] = int(val)
                    except ValueError: pass
                elif key in _SETTINGS_STR_KEYS:
                    data[key] = val
    except FileNotFoundError:
        legacy = _get_highscore_path()
        try:
            with open(legacy, "r") as f:
                data["score"] = max(0, int(f.read().strip()))
            print(f"Migrated legacy highscore.txt (score={data['score']})")
            os.makedirs(os.path.dirname(path), exist_ok=True)
            save_save(data)
            try:
                os.remove(legacy)
                print("Deleted highscore.txt after migration")
            except Exception:
                pass
        except Exception:
            pass
    except Exception as e:
        print(f"load_save borked: {e}")
    return data

def save_save(data):
    path = _get_save_path()
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(f"score={max(0, int(data.get('score', 0)))}\n")
            f.write(f"seed={data.get('seed', '')}\n")
            apples_str = ",".join(str(t) for t in sorted(data.get("apples", set())))
            f.write(f"apples={apples_str}\n")
            for t in SA_TARGETS:
                f.write(f"sa_best_{t}={data.get(f'sa_best_{t}', 0)}\n")
            for k in _SETTINGS_BOOL_KEYS:
                f.write(f"{k}={'1' if data.get(k, False) else '0'}\n")
            for k in _SETTINGS_INT_KEYS:
                f.write(f"{k}={data.get(k, 0)}\n")
            for k in _SETTINGS_STR_KEYS:
                f.write(f"{k}={data.get(k, '')}\n")
        print(f"Save written: score={data.get('score')} seed={data.get('seed')} apples={data.get('apples')}")
    except Exception as e:
        print(f"save_save borked: {e}")

def load_high_score():
    return load_save()["score"]

def save_high_score(new_score):
    data = load_save()
    if new_score > data["score"]:
        data["score"] = new_score
        save_save(data)
        print(f"New high score: {new_score}")

# ── Active seed (None = pure random, str = seeded mode) ──────────
ACTIVE_SEED = ""      # loaded from save.txt at startup (see below)
_food_call_counter = 0  # incremented each spawn_food call for per-food determinism

def _seed_int():
    if not ACTIVE_SEED:
        return None
    return hash(ACTIVE_SEED) & 0xFFFFFFFF

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
pygame.display.set_caption("NotASnake v3.4 | Thanks for playing!")

try:
    icon_paths = [
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "nasassets", "NASiconNEW.ico"),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "NASiconNEW.ico"),
        "nasassets/NASiconNEW.ico",
        "NASiconNEW.ico",
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "nasassets", "NASicon2.ico"),
        "nasassets/NASicon2.ico",
        "NASicon2.ico",
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

# ── Load everything from save at startup ─────────────────────────
_boot_data    = load_save()
ACTIVE_SEED   = _boot_data["seed"]
_earned_apples = _boot_data.get("apples", set())
_sa_bests     = {t: _boot_data.get(f"sa_best_{t}", 0) for t in SA_TARGETS}
if ACTIVE_SEED:
    print(f" Seeding active: '{ACTIVE_SEED}' (int={_seed_int()}) ===")
else:
    print("No seed active — random bullshit GO! ")
print(f"Apples earned: {sorted(_earned_apples)} | SA bests: {_sa_bests} ")

settings = {
    "music_muted":    _boot_data.get("music_muted",    False),
    "wrap_around":    _boot_data.get("wrap_around",    False),
    "light_mode":     _boot_data.get("light_mode",     False),
    "grid_opacity":   _boot_data.get("grid_opacity",   0),
    "control_scheme": _boot_data.get("control_scheme", "wasd_arrows"),
    "show_timer":     _boot_data.get("show_timer",     False),
    "fps_limit":      _boot_data.get("fps_limit",      60),
    "hardcore":       _boot_data.get("hardcore",       False),
    "double_food":    _boot_data.get("double_food",    True),
}
pygame.joystick.init()

_joysticks = {}

def _refresh_joysticks():
    global _joysticks
    _joysticks = {}
    for i in range(pygame.joystick.get_count()):
        j = pygame.joystick.Joystick(i)
        j.init()
        _joysticks[i] = j
        print(f"Joystick {i}: {j.get_name()}")

_refresh_joysticks()

def _joy_direction(joy_id):
    j = _joysticks.get(joy_id)
    if j is None:
        return None
    DEAD = 0.55

    if j.get_numhats() > 0:
        hx, hy = j.get_hat(0)
        if hx == 1:  return "RIGHT"
        if hx == -1: return "LEFT"
        if hy == 1:  return "UP"
        if hy == -1: return "DOWN"

    n = j.get_numbuttons()
    for up_b, down_b, left_b, right_b in [(11, 12, 13, 14), (12, 13, 14, 15)]:
        if right_b < n and j.get_button(right_b): return "RIGHT"
        if left_b  < n and j.get_button(left_b):  return "LEFT"
        if up_b    < n and j.get_button(up_b):    return "UP"
        if down_b  < n and j.get_button(down_b):  return "DOWN"

    ax = j.get_axis(0) if j.get_numaxes() > 0 else 0.0
    ay = j.get_axis(1) if j.get_numaxes() > 1 else 0.0
    if abs(ax) > DEAD or abs(ay) > DEAD:
        if abs(ax) >= abs(ay):
            return "RIGHT" if ax > 0 else "LEFT"
        else:
            return "DOWN" if ay > 0 else "UP"

    return None

def _joy_x_pressed(event, joy_id):
    if event.type != pygame.JOYBUTTONDOWN:
        return False
    if event.joy != joy_id:
        return False
    return event.button in (0, 2)

def _joy_is_debug_btn(event):
    return event.type == pygame.JOYBUTTONDOWN and event.button == 3

def _joy_is_panel_btn(event):
    return event.type == pygame.JOYBUTTONDOWN and event.button in (4, 8)

def _joy_is_pause_btn(event):
    return event.type == pygame.JOYBUTTONDOWN and event.button in (6, 7, 9)


_SPACEBAR_CYCLE = ["RIGHT", "DOWN", "LEFT", "UP"]
_spacebar_idx   = 0   # current step in cycle

def get_key_directions():
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
        print(f"Background load fucked: {e}")
        _background_surface = None

_load_background()

def get_bg_color():
    return pygame.Color(255, 255, 255) if settings["light_mode"] else COLORS["black"]

def draw_background():
    if _background_surface is not None and not settings["light_mode"]:
        screen.blit(_background_surface, (0, 0))
    else:
        screen.fill(get_bg_color())

    grid_alpha = settings["grid_opacity"]   # 0, 127, or 255
    if grid_alpha > 0:
        if settings["light_mode"]:
            grid_rgb = (180, 180, 180)
        else:
            grid_rgb = (60, 60, 60)
        if grid_alpha == 255:
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

debug_overlay_visible = False

_debug_font = None
def draw_debug_overlay(tick_accum=None, tick_accum1=None, tick_accum2=None,
                       is_multiplayer=False):
    global _debug_font
    if _debug_font is None:
        _debug_font = pygame.font.SysFont("consolas", 16)
    font = _debug_font
    diff_label = next((k for k, v in DIFFICULTY_LEVELS.items() if v == DIFFICULTY), "Unknown?")

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
            f"if you see this, write to:",
            f"skulldozer@dontmailme.ru",
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
            f"if you see this, write to: ",
            f"skulldozer@dontmailme.ru",
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
food2_pos = [0, 0]
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
    global snake_pos, snake_body, food_pos, food_spawn, food2_pos, direction, change_to, score
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
    food2_pos = spawn_food(snake_body + [food_pos]) if settings.get("double_food", True) else food_pos
    food_spawn = True
    leftover = None
    burst1["active"] = False
    burst1["end_ms"] = 0
    global _food_call_counter
    _food_call_counter = 0
    df_tag = "double food ON" if settings.get("double_food", True) else "double food off"
    if ACTIVE_SEED:
        print(f"=== Game Started  seed='{ACTIVE_SEED}' | {df_tag} | counter reset ===")
    else:
        print(f"=== Game Start | no seed | {df_tag} ===")

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
    global _food_call_counter
    _food_call_counter = 0
    if ACTIVE_SEED:
        print(f"MP game started | seed='{ACTIVE_SEED}' int={_seed_int()} | food counter reset ===")
    else:
        print("=== MP game started | no seed — random bullshit go! ===")

def spawn_food(snake_bodies):
    global _food_call_counter
    occupied = set(map(tuple, snake_bodies))
    cols = (SCREEN_WIDTH  // CELL_SIZE) - 1
    rows = (SCREEN_HEIGHT // CELL_SIZE) - 1
    total_cells = cols * rows

    if len(occupied) >= total_cells:
        print("WARNING: Bro i`m full af! Where do I put my food???")
        return list(snake_bodies[0]) if snake_bodies else [CELL_SIZE, CELL_SIZE]

    # Seed-aware RNG: local Random so we don't pollute global state
    if ACTIVE_SEED:
        rng = random.Random((_seed_int() ^ (_food_call_counter * 2654435761)) & 0xFFFFFFFF)
    else:
        rng = random

    _food_call_counter += 1

    for _attempt in range(total_cells * 2):
        new_pos = [
            rng.randrange(1, (SCREEN_WIDTH  // CELL_SIZE)) * CELL_SIZE,
            rng.randrange(1, (SCREEN_HEIGHT // CELL_SIZE)) * CELL_SIZE
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
    speed = 50 + 250 * (1.0 - frac)
    pulse = 0.5 + 0.5 * math.sin(now_ms / speed)
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

        version_str = "NotASnake v3.4"
        if ACTIVE_SEED:
            version_str += f"  [S:{ACTIVE_SEED[:8]}]"
        info_surface = score_font.render(version_str, True, txt_color if not ACTIVE_SEED else COLORS["ourple"])
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
            score_text = f"NotASnake v3.4 | End Score: {score1}"
            score_surface = score_font.render(score_text, True, txt_color)
            screen.blit(score_surface, (SCREEN_WIDTH//2 - 250, SCREEN_HEIGHT * 4 // 5))
        else:
            score_text = f"NotASnake v3.4 | How cool! Two guys playing! | P1: {score1} | P2: {score2}"
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

def pause_menu(is_multiplayer=False, mode_label=None):
    menu_font = pygame.font.SysFont("times new roman", 72)
    if mode_label is None:
        mode_label = "Multiplayer" if is_multiplayer else "Single Player"
    sel = 0
    _joy_axis_last = {}
    resume_rect = pygame.Rect(0, 0, 0, 0)
    quit_rect   = pygame.Rect(0, 0, 0, 0)
    while True:
        lm  = settings["light_mode"]
        txt = (20, 20, 20) if lm else COLORS["white"]
        dim = (80, 80, 80) if lm else (160, 160, 160)
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((255, 255, 255, 100) if lm else (0, 0, 0, 128))
        screen.blit(overlay, (0, 0))
        mouse_pos = pygame.mouse.get_pos()

        title_s = menu_font.render("Paused", True, txt)
        screen.blit(title_s, title_s.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100)))

        r_hover = resume_rect.collidepoint(mouse_pos)
        q_hover = quit_rect.collidepoint(mouse_pos)
        r_s = menu_font.render("Resume",       True, COLORS["green"] if sel == 0 or r_hover else txt)
        q_s = menu_font.render("Quit to Menu", True, COLORS["red"]   if sel == 1 or q_hover else txt)
        resume_rect = r_s.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        quit_rect   = q_s.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100))
        screen.blit(r_s, resume_rect)
        screen.blit(q_s, quit_rect)

        info_s = pygame.font.SysFont("consolas", 16).render(
            f"Mode: {mode_label}. Uhh, it`s 5 o`clock somewhere, am i right? ", True, dim)
        screen.blit(info_s, info_s.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50)))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if resume_rect.collidepoint(event.pos): return False
                elif quit_rect.collidepoint(event.pos): return True
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_RETURN): return False
                elif event.key in (pygame.K_UP, pygame.K_w):   sel = 0
                elif event.key in (pygame.K_DOWN, pygame.K_s): sel = 1
                elif event.key == pygame.K_SPACE:
                    return sel == 1
            if event.type == pygame.JOYBUTTONDOWN:
                if event.button in (0, 2): return sel == 1
                if event.button == 1:      return False
            if event.type == pygame.JOYHATMOTION:
                if event.value[1] > 0:  sel = 0
                elif event.value[1] < 0: sel = 1
            if event.type == pygame.JOYAXISMOTION:
                prev = _joy_axis_last.get(event.axis, 0.0)
                cur  = event.value
                _joy_axis_last[event.axis] = cur
                if event.axis == 1:
                    if cur < -0.55 and prev >= -0.55:  sel = 0
                    elif cur > 0.55 and prev <= 0.55:  sel = 1

        pygame.display.update()


def confirm_quit_to_menu():
    font    = pygame.font.SysFont("times new roman", 62)
    sm_font = pygame.font.SysFont("consolas", 20)
    while True:
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        screen.blit(overlay, (0, 0))
        bw, bh = 480, 210
        bx = (SCREEN_WIDTH  - bw) // 2
        by = (SCREEN_HEIGHT - bh) // 2
        pygame.draw.rect(screen, (18, 18, 35), (bx, by, bw, bh))
        pygame.draw.rect(screen, COLORS["ourple"], (bx, by, bw, bh), 2)
        q_s = font.render("Return to menu?", True, COLORS["white"])
        screen.blit(q_s, q_s.get_rect(center=(SCREEN_WIDTH // 2, by + 55)))
        hint = sm_font.render("ENTER for Yes // ESC for No", True, (140, 140, 160))
        screen.blit(hint, hint.get_rect(center=(SCREEN_WIDTH // 2, by + 105)))
        mouse_pos = pygame.mouse.get_pos()
        yes_s  = font.render("Yes", True,  COLORS["red"]   if pygame.Rect(bx, by + 130, bw // 2, 60).collidepoint(mouse_pos) else COLORS["white"])
        no_s   = font.render("No",  True,  COLORS["green"] if pygame.Rect(bx + bw // 2, by + 130, bw // 2, 60).collidepoint(mouse_pos) else COLORS["white"])
        yes_r  = yes_s.get_rect(center=(SCREEN_WIDTH // 2 - 90, by + 165))
        no_r   = no_s.get_rect( center=(SCREEN_WIDTH // 2 + 90, by + 165))
        screen.blit(yes_s, yes_r); screen.blit(no_s, no_r)
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if yes_r.collidepoint(event.pos): return True
                elif no_r.collidepoint(event.pos): return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN: return True
                elif event.key == pygame.K_ESCAPE: return False

def game_over_menu(is_multiplayer=False, score1=0, score2=0, high_score=0, winner=None):
    music_manager.play_music('gameover', volume=0.6)
    menu_font = pygame.font.SysFont("times new roman", 72)
    sel = 0
    _joy_axis_last = {}
    play_again_rect = pygame.Rect(0,0,0,0)
    exit_menu_rect  = pygame.Rect(0,0,0,0)
    exit_desk_rect  = pygame.Rect(0,0,0,0)

    while True:
        screen.fill(get_bg_color())
        mouse_pos = pygame.mouse.get_pos()
        lm  = settings["light_mode"]
        txt = (20, 20, 20) if lm else COLORS["white"]

        title_surface = pygame.font.SysFont("times new roman", 100).render("Game Over", True, COLORS["red"])
        screen.blit(title_surface, title_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 180)))

        if is_multiplayer:
            if winner == "player1":   wt, wc = "Player 1 Wins!", COLORS["head"]
            elif winner == "player2": wt, wc = "Player 2 Wins!", COLORS["head2"]
            else:                     wt, wc = "T-T-Tie!", COLORS["ourple"]
            ws = pygame.font.SysFont("times new roman", 60).render(wt, True, wc)
            screen.blit(ws, ws.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 80)))

        score_font = pygame.font.SysFont("times", 30)
        if is_multiplayer:
            sc_t = f"P1: {score1} | P2: {score2}"; sc_c = txt
        else:
            sc_t = f"End Score: {score1}"
            sc_c = COLORS["ourple"] if score1 >= high_score and score1 > 0 else txt
        ss = score_font.render(sc_t, True, sc_c)
        screen.blit(ss, ss.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)))

        if not is_multiplayer:
            hs_font = pygame.font.SysFont("times", 24)
            if score1 >= high_score and score1 > 0:
                hs_t, hs_c = "NEW HIGH SCORE!", COLORS["ourple"]
            else:
                hs_t, hs_c = f"Your highest ever score: {high_score}", txt
            hs_s = hs_font.render(hs_t, True, hs_c)
            screen.blit(hs_s, hs_s.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 40)))

        def btn_col(idx):
            cols = [COLORS["green"], COLORS["ourple"], COLORS["red"]]
            return cols[idx] if sel == idx or [play_again_rect, exit_menu_rect, exit_desk_rect][idx].collidepoint(mouse_pos) else txt

        pa_s  = menu_font.render("Play Again", True, btn_col(0))
        em_s  = menu_font.render("Main Menu",  True, btn_col(1))
        ed_s  = menu_font.render("Exit Game",  True, btn_col(2))
        play_again_rect = pa_s.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 80))
        exit_menu_rect  = em_s.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 160))
        exit_desk_rect  = ed_s.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 240))
        screen.blit(pa_s, play_again_rect)
        screen.blit(em_s, exit_menu_rect)
        screen.blit(ed_s, exit_desk_rect)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if play_again_rect.collidepoint(event.pos):
                    music_manager.stop_music(); return "play_again"
                elif exit_menu_rect.collidepoint(event.pos):
                    music_manager.stop_music(); return "main_menu"
                elif exit_desk_rect.collidepoint(event.pos):
                    pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_UP, pygame.K_w):     sel = (sel - 1) % 3
                elif event.key in (pygame.K_DOWN, pygame.K_s): sel = (sel + 1) % 3
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    music_manager.stop_music()
                    if sel == 0: return "play_again"
                    elif sel == 1: return "main_menu"
                    else: pygame.quit(); sys.exit()
                elif event.key == pygame.K_1: music_manager.stop_music(); return "play_again"
                elif event.key in (pygame.K_2, pygame.K_m): music_manager.stop_music(); return "main_menu"
                elif event.key in (pygame.K_3, pygame.K_ESCAPE): pygame.quit(); sys.exit()
            if event.type == pygame.JOYBUTTONDOWN:
                if event.button in (0, 2):
                    music_manager.stop_music()
                    if sel == 0: return "play_again"
                    elif sel == 1: return "main_menu"
                    else: pygame.quit(); sys.exit()
                elif event.button == 1: music_manager.stop_music(); return "main_menu"
            if event.type == pygame.JOYHATMOTION:
                if event.value[1] > 0:   sel = (sel - 1) % 3
                elif event.value[1] < 0: sel = (sel + 1) % 3
            if event.type == pygame.JOYAXISMOTION:
                prev = _joy_axis_last.get(event.axis, 0.0)
                cur  = event.value
                _joy_axis_last[event.axis] = cur
                if event.axis == 1:
                    if cur < -0.55 and prev >= -0.55:  sel = (sel - 1) % 3
                    elif cur > 0.55 and prev <= 0.55:  sel = (sel + 1) % 3

        pygame.display.update()


def seed_input_overlay():
    global ACTIVE_SEED
    font_big  = pygame.font.SysFont("consolas", 36)
    font_med  = pygame.font.SysFont("consolas", 22)
    font_sm   = pygame.font.SysFont("consolas", 17)
    MAX_LEN   = 20
    buf       = list(ACTIVE_SEED)

    while True:
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        screen.blit(overlay, (0, 0))

        bw, bh = 500, 220
        bx = (SCREEN_WIDTH  - bw) // 2
        by = (SCREEN_HEIGHT - bh) // 2
        pygame.draw.rect(screen, (20, 20, 40),  (bx, by, bw, bh))
        pygame.draw.rect(screen, COLORS["ourple"], (bx, by, bw, bh), 2)

        title = font_big.render("[ DEBUG ] Set Seed", True, COLORS["ourple"])
        screen.blit(title, (bx + bw//2 - title.get_width()//2, by + 18))

        hint = font_sm.render("No symbols |  Max 20 chars | ENTER to confirm  ESC to cancel", True, (140,140,160))
        screen.blit(hint, (bx + bw//2 - hint.get_width()//2, by + 66))

        # Input field
        field_rect = pygame.Rect(bx + 30, by + 102, bw - 60, 44)
        pygame.draw.rect(screen, (10, 10, 25), field_rect)
        pygame.draw.rect(screen, COLORS["cyan"], field_rect, 1)
        text_str  = "".join(buf)
        cursor    = "|" if (pygame.time.get_ticks() // 500) % 2 == 0 else " "
        rendered  = font_big.render(text_str + cursor, True, COLORS["white"])
        screen.blit(rendered, (field_rect.x + 8, field_rect.y + 6))

        # Buttons
        now_ms = pygame.time.get_ticks()
        mouse_pos = pygame.mouse.get_pos()

        confirm_surf = font_med.render("[ confirm ]", True, COLORS["green"])
        clear_surf   = font_med.render("[ clear ]",   True, COLORS["red"])
        cancel_surf  = font_med.render("[ cancel ]",  True, (160,160,160))

        confirm_rect = confirm_surf.get_rect(center=(bx + bw//4,       by + bh - 30))
        clear_rect   = clear_surf.get_rect(  center=(bx + bw//2,       by + bh - 30))
        cancel_rect  = cancel_surf.get_rect( center=(bx + 3*bw//4,     by + bh - 30))

        for surf, rect in [(confirm_surf, confirm_rect), (clear_surf, clear_rect), (cancel_surf, cancel_rect)]:
            screen.blit(surf, rect)

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                    result = "".join(buf).strip()
                    ACTIVE_SEED = result
                    _d = load_save(); _d["seed"] = ACTIVE_SEED; save_save(_d)
                    if ACTIVE_SEED:
                        print(f"Seed set: '{ACTIVE_SEED}' (int={_seed_int()})")
                    else:
                        print("Seed cleared (ENTER with empty field)")
                    return ACTIVE_SEED
                elif event.key == pygame.K_ESCAPE:
                    print("Seed overlay cancelled — no change")
                    return ACTIVE_SEED
                elif event.key == pygame.K_BACKSPACE:
                    if buf:
                        buf.pop()
                else:
                    ch = event.unicode
                    if ch.isalnum() and len(buf) < MAX_LEN:
                        buf.append(ch)
            if event.type == pygame.MOUSEBUTTONDOWN:
                if confirm_rect.collidepoint(event.pos):
                    result = "".join(buf).strip()
                    ACTIVE_SEED = result
                    _d = load_save(); _d["seed"] = ACTIVE_SEED; save_save(_d)
                    if ACTIVE_SEED:
                        print(f"Seed set: '{ACTIVE_SEED}' (int={_seed_int()})")
                    else:
                        print("Seed confirmed as empty (cleared)")
                    return ACTIVE_SEED
                elif clear_rect.collidepoint(event.pos):
                    buf = []
                    ACTIVE_SEED = ""
                    _d = load_save(); _d["seed"] = ""; save_save(_d)
                    print("Seed cleared")
                    return ""
                elif cancel_rect.collidepoint(event.pos):
                    print("Seed overlay cancelled — no change")
                    return ACTIVE_SEED


def draw_apple(cx, cy, size, filled):
    if filled:
        pygame.draw.circle(screen, (200, 45, 45), (cx, cy + size // 10), size // 2)
        pygame.draw.rect(screen, (110, 75, 35), (cx - 1, cy - size // 2, 3, size // 4))
        leaf_pts = [(cx + 1, cy - size // 2 + 2), (cx + size // 3, cy - size // 3), (cx + 2, cy - size // 5)]
        pygame.draw.polygon(screen, (55, 175, 55), leaf_pts)
        pygame.draw.circle(screen, (255, 155, 155), (cx - size // 5, cy - size // 10), max(2, size // 5))
    else:
        pygame.draw.circle(screen, (70, 70, 70), (cx, cy + size // 10), size // 2, 2)
        pygame.draw.rect(screen, (55, 55, 55), (cx - 1, cy - size // 2, 3, size // 4))


def sa_success_screen(target, elapsed_ms, is_new_best, is_new_apple):
    music_manager.stop_music()
    music_manager.play_music("effect", loop=False, volume=0.7)
    font_huge = pygame.font.SysFont("times new roman", 110)
    font_big  = pygame.font.SysFont("times new roman", 58)
    font_med  = pygame.font.SysFont("consolas", 28)
    font_sm   = pygame.font.SysFont("consolas", 20)
    btn_font  = pygame.font.SysFont("times new roman", 54)
    secs = elapsed_ms / 1000.0
    time_str = f"{int(secs // 60):02d}:{secs % 60:05.2f}"
    while True:
        screen.fill(get_bg_color())
        mouse_pos = pygame.mouse.get_pos()
        now_ms = pygame.time.get_ticks()
        lm  = settings["light_mode"]
        txt = (20, 20, 20) if lm else COLORS["white"]
        pulse = 0.5 + 0.5 * math.sin(now_ms / 300.0)
        comp_col = (int(80 + 175 * pulse), int(200 + 55 * pulse), 80)
        title_s = font_huge.render("GREAT JOB!", True, comp_col)
        screen.blit(title_s, title_s.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 210)))
        tgt_s = font_big.render(f"Score Attack  —  Target: {target}", True, txt)
        screen.blit(tgt_s, tgt_s.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 120)))
        time_col = COLORS["ourple"] if is_new_best else txt
        time_s = font_med.render(f"Time:  {time_str}", True, time_col)
        screen.blit(time_s, time_s.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 60)))
        if is_new_best:
            nb_s = font_sm.render("New Best!", True, COLORS["yummers"])
            screen.blit(nb_s, nb_s.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20)))
        apple_y = SCREEN_HEIGHT // 2 + 30
        if is_new_apple:
            draw_apple(SCREEN_WIDTH // 2, apple_y, 36, True)
            ap_s = font_sm.render("Apple Earned!", True, (220, 80, 80))
            screen.blit(ap_s, ap_s.get_rect(center=(SCREEN_WIDTH // 2, apple_y + 40)))
        pa_s   = btn_font.render("Play Again",     True, txt)
        ch_s   = btn_font.render("Back to SP Mode",  True, txt)
        mn_s   = btn_font.render("Main Menu",      True, txt)
        pa_r   = pa_s.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 110))
        ch_r   = ch_s.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 175))
        mn_r   = mn_s.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 240))
        if pa_r.collidepoint(mouse_pos): pa_s = btn_font.render("Play Again",    True, COLORS["green"])
        if ch_r.collidepoint(mouse_pos): ch_s = btn_font.render("Back to SP Mode", True, COLORS["cyan"])
        if mn_r.collidepoint(mouse_pos): mn_s = btn_font.render("Main Menu",     True, COLORS["red"])
        screen.blit(pa_s, pa_r); screen.blit(ch_s, ch_r); screen.blit(mn_s, mn_r)
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if pa_r.collidepoint(event.pos): return "play_again"
                elif ch_r.collidepoint(event.pos): return "modes"
                elif mn_r.collidepoint(event.pos): return "menu"
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_RETURN, pygame.K_SPACE): return "play_again"
                elif event.key == pygame.K_ESCAPE: return "modes"
            if event.type == pygame.JOYBUTTONDOWN:
                if event.button in (0, 2): return "play_again"
                elif event.button == 1:    return "modes"


def sp_mode_select():
    global _earned_apples, _sa_bests
    font_title = pygame.font.SysFont("times new roman", 78)
    font_mode  = pygame.font.SysFont("times new roman", 58)
    font_desc  = pygame.font.SysFont("consolas", 22)
    font_sm    = pygame.font.SysFont("consolas", 18)
    font_btn   = pygame.font.SysFont("times new roman", 50)
    font_back  = pygame.font.SysFont("consolas", 26)
    mx = SCREEN_WIDTH // 2
    sel = 0          # 0=Endless, 1/2/3 = SA_TARGETS index
    _joy_axis_last = {}
    while True:
        draw_background()
        mouse_pos = pygame.mouse.get_pos()
        lm  = settings["light_mode"]
        txt = (20, 20, 20) if lm else COLORS["white"]
        dim = (80, 80, 80) if lm else (140, 140, 140)
        title_s = font_title.render("Single Player", True, COLORS["green"])
        screen.blit(title_s, title_s.get_rect(center=(SCREEN_WIDTH // 2, 58)))
        back_col = COLORS["ourple"] if pygame.Rect(0, 0, 160, 46).collidepoint(mouse_pos) else dim
        back_s = font_back.render("< Back", True, back_col)
        back_r = back_s.get_rect(topleft=(22, 14))
        screen.blit(back_s, back_r)
        back_hit = pygame.Rect(0, 0, back_r.right + 10, 50)
        pygame.draw.line(screen, (60, 60, 80), (mx, 105), (mx, SCREEN_HEIGHT - 30), 2)

        left_cx = mx // 2
        endless_joy_sel = sel == 0
        endless_hover = endless_joy_sel or (mouse_pos[0] < mx - 6 and mouse_pos[1] > 105)
        if endless_hover:
            hs = pygame.Surface((mx, SCREEN_HEIGHT - 105), pygame.SRCALPHA)
            hs.fill((255, 255, 255, 10) if not lm else (0, 0, 0, 10))
            screen.blit(hs, (0, 105))
        if endless_joy_sel:
            pygame.draw.rect(screen, COLORS["green"], (4, 108, mx - 14, SCREEN_HEIGHT - 120), 2)
        endless_hit = pygame.Rect(0, 105, mx - 6, SCREEN_HEIGHT - 105)
        en_s = font_mode.render("Endless", True, COLORS["green"])
        screen.blit(en_s, en_s.get_rect(center=(left_cx, 175)))
        for i, line in enumerate(["Survive as long as possible.", "High score tracking.", "All settings apply."]):
            ds = font_desc.render(line, True, txt)
            screen.blit(ds, ds.get_rect(center=(left_cx, 270 + i * 34)))
        hi = load_high_score()
        hs_s = font_sm.render(f"High Score: {hi}", True, COLORS["ourple"])
        screen.blit(hs_s, hs_s.get_rect(center=(left_cx, 400)))
        play_col = COLORS["green"] if endless_hover else txt
        play_s = font_btn.render("[ Play ]", True, play_col)
        screen.blit(play_s, play_s.get_rect(center=(left_cx, SCREEN_HEIGHT // 2 + 110)))

        right_cx = mx + (SCREEN_WIDTH - mx) // 2
        sa_s = font_mode.render("Score Attack", True, COLORS["yummers"])
        screen.blit(sa_s, sa_s.get_rect(center=(right_cx, 175)))
        for i, line in enumerate(["Race to a target score!", "Timer is always on.", "Earn an apple on first clear."]):
            ds = font_desc.render(line, True, txt)
            screen.blit(ds, ds.get_rect(center=(right_cx, 270 + i * 34)))
        card_w, card_h = 158, 128
        gap = 28
        total_w = 3 * card_w + 2 * gap
        cx0 = right_cx - total_w // 2
        card_y = 415
        sa_rects = {}
        for i, t in enumerate(SA_TARGETS):
            cx = cx0 + i * (card_w + gap)
            cr = pygame.Rect(cx, card_y, card_w, card_h)
            sa_rects[t] = cr
            joy_card_sel = sel == i + 1
            hover = joy_card_sel or cr.collidepoint(mouse_pos)
            if lm:
                bg_c = (255, 250, 215) if hover else (238, 238, 238)
                bd_c = (180, 140, 0)   if hover else (180, 180, 180)
            else:
                bg_c = (38, 38, 20)    if hover else (20, 20, 38)
                bd_c = (230, 200, 0)   if joy_card_sel else ((230, 200, 0) if hover else (60, 60, 80))
            pygame.draw.rect(screen, bg_c, cr, border_radius=8)
            pygame.draw.rect(screen, bd_c, cr, 3 if joy_card_sel else 2, border_radius=8)
            num_col = COLORS["yummers"] if hover else txt
            num_s = pygame.font.SysFont("consolas", 42, bold=True).render(str(t), True, num_col)
            screen.blit(num_s, num_s.get_rect(center=(cx + card_w // 2, card_y + 28)))
            draw_apple(cx + card_w // 2, card_y + 67, 22, t in _earned_apples)
            best_ms = _sa_bests.get(t, 0)
            if best_ms > 0:
                bs = best_ms / 1000.0
                best_str = f"{int(bs // 60):02d}:{bs % 60:05.2f}"
            else:
                best_str = "—"
            best_col = COLORS["ourple"] if t in _earned_apples else dim
            bs_s = font_sm.render(best_str, True, best_col)
            screen.blit(bs_s, bs_s.get_rect(center=(cx + card_w // 2, card_y + 108)))

        pygame.display.update()
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type in (pygame.JOYDEVICEADDED, pygame.JOYDEVICEREMOVED):
                _refresh_joysticks()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: return "back"
                elif event.key == pygame.K_LEFT:
                    sel = (sel - 1) % 4
                elif event.key == pygame.K_RIGHT:
                    sel = (sel + 1) % 4
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    music_manager.stop_music()
                    if sel == 0: return ("endless",)
                    else: return ("sa", SA_TARGETS[sel - 1])
            if event.type == pygame.JOYBUTTONDOWN:
                if event.button in (0, 2):
                    music_manager.stop_music()
                    if sel == 0: return ("endless",)
                    else: return ("sa", SA_TARGETS[sel - 1])
                elif event.button == 1:
                    return "back"
            if event.type == pygame.JOYHATMOTION:
                if event.value[0] == -1:  sel = (sel - 1) % 4
                elif event.value[0] == 1: sel = (sel + 1) % 4
            if event.type == pygame.JOYAXISMOTION:
                prev = _joy_axis_last.get(event.axis, 0.0)
                cur  = event.value
                _joy_axis_last[event.axis] = cur
                if event.axis == 0:
                    if cur < -0.55 and prev >= -0.55: sel = (sel - 1) % 4
                    elif cur > 0.55 and prev <= 0.55: sel = (sel + 1) % 4
            if event.type == pygame.MOUSEBUTTONDOWN:
                if back_hit.collidepoint(event.pos): return "back"
                elif endless_hit.collidepoint(event.pos):
                    music_manager.stop_music(); return ("endless",)
                else:
                    for t, r in sa_rects.items():
                        if r.collidepoint(event.pos):
                            music_manager.stop_music(); return ("sa", t)


def score_attack_game(target):
    global snake_pos, snake_body, food_pos, food_spawn, food2_pos, direction, change_to, score
    global leftover, burst1, debug_overlay_visible, _spacebar_idx
    global _earned_apples, _sa_bests
    music_manager.play_music("ingame", loop=True, volume=0.5)
    reset_single_game()
    _spacebar_idx = 0
    draw_countdown()
    tick_accum    = 0.0
    game_start_ms = pygame.time.get_ticks()
    while True:
        now_ms = pygame.time.get_ticks()
        if score >= target:
            elapsed_ms = now_ms - game_start_ms
            data       = load_save()
            old_best   = data.get(f"sa_best_{target}", 0)
            is_new_best  = (old_best == 0 or elapsed_ms < old_best)
            is_new_apple = target not in data.get("apples", set())
            if is_new_best:
                data[f"sa_best_{target}"] = elapsed_ms
                _sa_bests[target] = elapsed_ms
            data.setdefault("apples", set()).add(target)
            _earned_apples.add(target)
            save_save(data)
            print(f"SA done! target was {target}, it took {elapsed_ms}ms, Now, its ={is_new_best} and ={is_new_apple}")
            result = sa_success_screen(target, elapsed_ms, is_new_best, is_new_apple)
            if result == "play_again":
                reset_single_game()
                music_manager.current_music = None
                music_manager.play_music("ingame", loop=True, volume=0.5)
                draw_countdown()
                tick_accum = 0.0; game_start_ms = pygame.time.get_ticks()
                continue
            elif result == "modes":
                return "modes"
            return "menu"
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            elif event.type in (pygame.JOYDEVICEADDED, pygame.JOYDEVICEREMOVED):
                _refresh_joysticks()
            elif event.type == pygame.JOYBUTTONDOWN and event.joy == 0:
                if _joy_is_debug_btn(event):
                    debug_overlay_visible = not debug_overlay_visible
                elif _joy_is_pause_btn(event):
                    if not settings["hardcore"]:
                        if pause_menu(is_multiplayer=False, mode_label=f"SP Score Attack ({target})"): return "menu"
                elif settings["control_scheme"] == "spacebar" or not _joysticks:
                    if _joy_x_pressed(event, 0):
                        change_to = _SPACEBAR_CYCLE[_spacebar_idx % len(_SPACEBAR_CYCLE)]
                        _spacebar_idx += 1
            elif event.type == pygame.KEYDOWN:
                if settings["control_scheme"] == "spacebar":
                    if event.key == pygame.K_SPACE:
                        change_to = _SPACEBAR_CYCLE[_spacebar_idx % len(_SPACEBAR_CYCLE)]
                        _spacebar_idx += 1
                else:
                    kd = get_key_directions()
                    if event.key in kd: change_to = kd[event.key]
                if event.key == pygame.K_F5:
                    debug_overlay_visible = not debug_overlay_visible
                elif event.key == pygame.K_ESCAPE:
                    if not settings["hardcore"]:
                        if pause_menu(is_multiplayer=False, mode_label=f"SP Score Attack ({target})"): return "menu"
                elif event.key == pygame.K_m:
                    if not settings["hardcore"]:
                        if confirm_quit_to_menu(): return "menu"
            elif event.type == pygame.ACTIVEEVENT:
                if event.state == pygame.APPINPUTFOCUS and not event.gain:
                    if not settings["hardcore"]:
                        if pause_menu(is_multiplayer=False, mode_label=f"SP Score Attack ({target})"): return "menu"
        if burst1["active"] and now_ms >= burst1["end_ms"]:
            burst1["active"] = False
        if leftover is not None and now_ms - leftover["born"] >= LEFTOVER_LINGER_MS:
            leftover = None
        if settings["hardcore"] and leftover is not None:
            leftover = None
        eff = DIFFICULTY * (BURST_MULTIPLIER if burst1["active"] else 1.0)
        tick_accum += eff / 60.0
        if tick_accum >= 1.0:
            tick_accum -= 1.0
            opposites = {"UP": "DOWN", "DOWN": "UP", "LEFT": "RIGHT", "RIGHT": "LEFT"}
            pressed = pygame.key.get_pressed()
            kd = get_key_directions()
            for k, d in kd.items():
                if pressed[k] and d != opposites[direction]:
                    change_to = d
                    break
            joy_dir = _joy_direction(0)
            if joy_dir and joy_dir != opposites[direction]:
                change_to = joy_dir
            if change_to != opposites[direction]: direction = change_to
            mv = {"UP": (0, -CELL_SIZE), "DOWN": (0, CELL_SIZE), "LEFT": (-CELL_SIZE, 0), "RIGHT": (CELL_SIZE, 0)}
            snake_pos[0] += mv[direction][0]; snake_pos[1] += mv[direction][1]
            if settings["wrap_around"] and not settings["hardcore"]:
                gw = (SCREEN_WIDTH  // CELL_SIZE) * CELL_SIZE
                gh = (SCREEN_HEIGHT // CELL_SIZE) * CELL_SIZE
                if snake_pos[0] < 0:      snake_pos[0] = gw - CELL_SIZE
                elif snake_pos[0] >= gw:  snake_pos[0] = 0
                if snake_pos[1] < 0:      snake_pos[1] = gh - CELL_SIZE
                elif snake_pos[1] >= gh:  snake_pos[1] = 0
            snake_body.insert(0, list(snake_pos))
            ate = False
            if snake_pos == food_pos:
                score += 1; ate = True
                if leftover is None and not settings["hardcore"]:
                    leftover = {"pos": spawn_food(snake_body), "born": now_ms}
                food_pos = spawn_food(snake_body)
            elif settings["double_food"] and snake_pos == food2_pos:
                score += 1; ate = True
                if leftover is None and not settings["hardcore"]:
                    leftover = {"pos": spawn_food(snake_body), "born": now_ms}
                food2_pos = spawn_food(snake_body)
            if not ate: snake_body.pop()
            if leftover is not None and snake_pos == leftover["pos"]:
                if not settings["hardcore"]:
                    burst1["active"] = True; burst1["end_ms"] = now_ms + BURST_DURATION_MS
                leftover = None
        wall_kill = not settings["wrap_around"]
        game_over = (
            (wall_kill and (snake_pos[0] < 0 or snake_pos[0] >= SCREEN_WIDTH or
                            snake_pos[1] < 0 or snake_pos[1] >= SCREEN_HEIGHT)) or
            any(seg == snake_pos for seg in snake_body[1:])
        )
        if game_over:
            print(f"SA died. target={target} score={score}/{target}")
            pixel_fill_effect()
            result = game_over_menu(is_multiplayer=False, score1=score, high_score=0)
            if result == "play_again":
                reset_single_game()
                music_manager.current_music = None
                music_manager.play_music("ingame", loop=True, volume=0.5)
                draw_countdown()
                tick_accum = 0.0; game_start_ms = pygame.time.get_ticks()
                continue
            elif result == "main_menu":
                return "menu"
            else:
                pygame.quit(); sys.exit()
        draw_background()
        draw_leftover(leftover, now_ms)
        draw_snake(snake_pos, snake_body, direction, True, burst_active=burst1["active"])
        pygame.draw.rect(screen, COLORS["yummers"], pygame.Rect(food_pos[0], food_pos[1], CELL_SIZE, CELL_SIZE))
        pygame.draw.rect(screen, (255, 255, 200), pygame.Rect(food_pos[0] + CELL_SIZE//4, food_pos[1] + CELL_SIZE//4, CELL_SIZE//4, CELL_SIZE//4))
        if settings["double_food"]:
            pygame.draw.rect(screen, COLORS["yummers"], pygame.Rect(food2_pos[0], food2_pos[1], CELL_SIZE, CELL_SIZE))
            pygame.draw.rect(screen, (255, 200, 80), pygame.Rect(food2_pos[0] + CELL_SIZE//4, food2_pos[1] + CELL_SIZE//4, CELL_SIZE//4, CELL_SIZE//4))
        if burst1["active"]:
            remaining = max(0, burst1["end_ms"] - now_ms)
            pulse = 0.5 + 0.5 * math.sin(now_ms / 80.0)
            bf = pygame.font.SysFont("consolas", 22)
            bs = bf.render(f"Burst active for {remaining/1000:.1f}s", True, (int(255*pulse), 200, 0))
            screen.blit(bs, (10, 60))
        if settings["hardcore"]:
            hf = pygame.font.SysFont("consolas", 18)
            screen.blit(hf.render("HARDCORE MODE", True, (255, 40, 40)), (10, 35))
        elapsed_s = (now_ms - game_start_ms) / 1000.0
        m2 = int(elapsed_s) // 60; s2 = int(elapsed_s) % 60; cs = int((elapsed_s - int(elapsed_s)) * 100)
        sa_hud = pygame.font.SysFont("consolas", 24)
        hud_str = f"TARGET:  {score} / {target}   |   {m2:02d}:{s2:02d}.{cs:02d}"
        hud_s = sa_hud.render(hud_str, True, COLORS["yummers"])
        screen.blit(hud_s, hud_s.get_rect(center=(SCREEN_WIDTH // 2, 18)))
        if debug_overlay_visible:
            draw_debug_overlay(tick_accum)
        version_str = "NotASnake v3.4"
        if ACTIVE_SEED: version_str += f"  [S:{ACTIVE_SEED[:8]}]"
        vs = pygame.font.SysFont("consolas", 20).render(version_str, True, COLORS["ourple"] if ACTIVE_SEED else (140,140,140))
        screen.blit(vs, vs.get_rect(topright=(SCREEN_WIDTH - 10, 10)))
        pygame.display.update()
        fps_cap = settings["fps_limit"]
        clock.tick(fps_cap if fps_cap > 0 else 0)

def _save_settings():
    d = load_save()
    for k in _SETTINGS_BOOL_KEYS + _SETTINGS_INT_KEYS + _SETTINGS_STR_KEYS:
        d[k] = settings.get(k)
    save_save(d)

_PANEL_ROW_KEYS = [
    "music", "wrap", "lightmode", "grid", "controls",
    "timer", "fps", "hardcore", "double_food", "seed"
]

def _toggle_setting(key):
    if key == "music":
        settings["music_muted"] = not settings["music_muted"]
        if settings["music_muted"]:
            pygame.mixer.music.stop(); music_manager.current_music = None
        else:
            music_manager.play_music('menu', volume=0.5)
        _save_settings()
    elif key == "wrap":
        settings["wrap_around"] = not settings["wrap_around"]; _save_settings()
    elif key == "lightmode":
        settings["light_mode"] = not settings["light_mode"]; _save_settings()
    elif key == "grid":
        settings["grid_opacity"] = {0: 127, 127: 255, 255: 0}[settings["grid_opacity"]]; _save_settings()
    elif key == "controls":
        schemes = ["wasd_arrows", "ijkl", "arrows_only", "spacebar"]
        settings["control_scheme"] = schemes[(schemes.index(settings["control_scheme"]) + 1) % len(schemes)]
        _save_settings()
    elif key == "timer":
        settings["show_timer"] = not settings["show_timer"]; _save_settings()
    elif key == "fps":
        settings["fps_limit"] = {30: 60, 60: 120, 120: 0, 0: 30}[settings["fps_limit"]]; _save_settings()
    elif key == "hardcore":
        settings["hardcore"] = not settings["hardcore"]
        if settings["hardcore"]: settings["wrap_around"] = False
        _save_settings()
    elif key == "double_food":
        settings["double_food"] = not settings["double_food"]; _save_settings()
    elif key == "seed":
        seed_input_overlay()

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

    menu_sel = 0
    _joy_axis_last = {}

    PANEL_W       = 360
    panel_open    = False
    panel_x       = SCREEN_WIDTH
    panel_target  = SCREEN_WIDTH
    PANEL_SPEED   = 40
    MENU_SHIFT    = PANEL_W // 2
    panel_sel     = 0
    PANEL_ROWS    = 10

    single_rect = pygame.Rect(0, 0, 0, 0)
    multi_rect  = pygame.Rect(0, 0, 0, 0)
    exit_rect   = pygame.Rect(0, 0, 0, 0)

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

        high_score = load_high_score()

        # ── Title & high score ──
        title_surface = pygame.font.SysFont("times new roman", 100).render("NotASnake v3.4", True, COLORS["green"])
        title_rect = title_surface.get_rect(center=(btn_cx, SCREEN_HEIGHT // 2 - 210))
        screen.blit(title_surface, title_rect)

        hs_surface = diff_font.render(f"High Score: {high_score}", True, COLORS["ourple"])
        hs_rect = hs_surface.get_rect(center=(btn_cx, SCREEN_HEIGHT // 2 - 140))
        screen.blit(hs_surface, hs_rect)
        apple_size = 18
        apple_gap  = 44
        apple_y    = SCREEN_HEIGHT // 2 - 96
        for _ai, _at in enumerate(SA_TARGETS):
            draw_apple(btn_cx + (_ai - 1) * apple_gap, apple_y, apple_size, _at in _earned_apples)

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
        single_text = menu_font.render("Single Player",    True, COLORS["green"] if menu_sel == 0 or single_rect.collidepoint(mouse_pos) else txt)
        single_rect = single_text.get_rect(center=(btn_cx, SCREEN_HEIGHT // 2 + 60))
        multi_text  = menu_font.render("Local Multiplayer", True, COLORS["cyan"]  if menu_sel == 1 or multi_rect.collidepoint(mouse_pos)  else txt)
        multi_rect  = multi_text.get_rect(center=(btn_cx, SCREEN_HEIGHT // 2 + 150))
        exit_text   = menu_font.render("Exit",             True, COLORS["red"]   if menu_sel == 2 or exit_rect.collidepoint(mouse_pos)   else txt)
        exit_rect   = exit_text.get_rect(center=(btn_cx, SCREEN_HEIGHT // 2 + 240))

        screen.blit(single_text, single_rect)
        screen.blit(multi_text,  multi_rect)
        screen.blit(exit_text,   exit_rect)

        # ── Settings button (gear icon, top-right) ──
        gear_font = pygame.font.SysFont("consolas", 28)
        joy_count = pygame.joystick.get_count()
        if panel_open:
            gear_label = "[ Close ]"
        elif joy_count > 0:
            gear_label = "[ Settings  Share/Select ]"
        else:
            gear_label = "[ Settings ]"
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

            row_idx = [0]

            def draw_setting(y, label, val_str, val_col, desc_lines):
                idx = row_idx[0]
                row_idx[0] += 1
                is_sel = panel_open and idx == panel_sel
                if is_sel:
                    hi = pygame.Surface((PANEL_W - 8, 48), pygame.SRCALPHA)
                    hi.fill((80, 80, 180, 60))
                    screen.blit(hi, (panel_x + 4, y - 2))
                    pygame.draw.rect(screen, COLORS["ourple"], (panel_x + 4, y - 2, PANEL_W - 8, 48), 1)
                lbl  = panel_font.render(label, True, COLORS["white"])
                screen.blit(lbl, (px, y))
                val_highlight = is_sel or vs_hover(y, val_str)
                vs   = panel_font.render(val_str, True, COLORS["ourple"] if val_highlight else val_col)
                vr   = vs.get_rect(topright=(panel_x + PANEL_W - 16, y))
                screen.blit(vs, vr)
                if desc_lines:
                    ds = controls_font.render(desc_lines[0], True, (140, 140, 160))
                    screen.blit(ds, (px, y + 26))
                row_h = 50
                div_y = y + row_h
                pygame.draw.line(screen, (40, 40, 60),
                                 (panel_x + 16, div_y), (panel_x + PANEL_W - 16, div_y), 1)
                return vr, div_y + 6

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
                                            ["Walls wrap to opposite side"])
            setting_rects["wrap"] = wrap_rect

            # ── 3: Light/Dark mode ────────────────────────────────
            lm_val = "[ LIGHT ]" if settings["light_mode"] else "[ DARK ]"
            lm_col = (255, 230, 80) if settings["light_mode"] else (160, 160, 220)
            lm_rect, cur_y = draw_setting(cur_y, "Theme", lm_val, lm_col,
                                          ["Toggle Dark / Light theme"])
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
                "spacebar":    "[ Wildcard ]",
            }
            ctrl_val = scheme_labels[settings["control_scheme"]]
            ctrl_col = COLORS["cyan"]
            ctrl_rect, cur_y = draw_setting(cur_y, "SP Controls", ctrl_val, ctrl_col,
                                            ["Cycle: WASD / IJKL / Arrows / Wildcard"])
            setting_rects["controls"] = ctrl_rect

            # ── 6: Show Timer ─────────────────────────────────────
            tmr_val = "[ ON ]" if settings["show_timer"] else "[ OFF ]"
            tmr_col = COLORS["green"] if settings["show_timer"] else (160, 160, 160)
            tmr_rect, cur_y = draw_setting(cur_y, "Timer", tmr_val, tmr_col,
                                           ["Show elapsed time on HUD"])
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
                                          ["No pause, no burst, no wrap."])
            setting_rects["hardcore"] = hc_rect

            # ── 9: Double Food ────────────────────────────────────
            df_val = "[ ON ]" if settings["double_food"] else "[ OFF ]"
            df_col = COLORS["cyan"] if settings["double_food"] else (160, 160, 160)
            df_rect, cur_y = draw_setting(cur_y, "Double Food", df_val, df_col,
                                          ["Two food items always active"])
            setting_rects["double_food"] = df_rect

            # ── 10: Seed (debug) ──────────────────────────────────
            seed_display = f"[ {ACTIVE_SEED[:12]}.. ]" if len(ACTIVE_SEED) > 12 else (f"[ {ACTIVE_SEED} ]" if ACTIVE_SEED else "[ none ]")
            seed_col = COLORS["ourple"] if ACTIVE_SEED else (160, 160, 160)
            seed_rect, cur_y = draw_setting(cur_y, "Seed [debug]", seed_display, seed_col,
                                            ["Set for reproducible food RNG"])
            setting_rects["seed"] = seed_rect

        # ── Controls hint (bottom) ──
        joy_count = pygame.joystick.get_count()
        joy_hint = f"Controllers: {joy_count} connected" if joy_count > 0 else "No controllers detected"
        joy_col  = COLORS["green"] if joy_count > 0 else dim
        controls_text = [
            "Single Player: WASD / Arrows / Controller",
            "Multiplayer: P1 WASD or Ctrl1  |  P2 Arrows or Ctrl2",
            f"Pause: ESC  |  Menu: M  |  {joy_hint}",
        ]
        for i, text in enumerate(controls_text):
            c = joy_col if i == 2 and joy_count > 0 else dim
            cs = controls_font.render(text, True, c)
            cr = cs.get_rect(center=(btn_cx, SCREEN_HEIGHT - 68 + i * 22))
            screen.blit(cs, cr)

        # ── Events ──
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type in (pygame.JOYDEVICEADDED, pygame.JOYDEVICEREMOVED):
                _refresh_joysticks()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if gear_rect.collidepoint(event.pos):
                    toggle_panel()
                elif panel_x < SCREEN_WIDTH:
                    if setting_rects.get("music") and setting_rects["music"].collidepoint(event.pos):
                        settings["music_muted"] = not settings["music_muted"]
                        if settings["music_muted"]:
                            pygame.mixer.music.stop()
                            music_manager.current_music = None
                        else:
                            music_manager.play_music('menu', volume=0.5)
                        _save_settings()
                    elif setting_rects.get("wrap") and setting_rects["wrap"].collidepoint(event.pos):
                        settings["wrap_around"] = not settings["wrap_around"]
                        _save_settings()
                    elif setting_rects.get("lightmode") and setting_rects["lightmode"].collidepoint(event.pos):
                        settings["light_mode"] = not settings["light_mode"]
                        _save_settings()
                    elif setting_rects.get("grid") and setting_rects["grid"].collidepoint(event.pos):
                        cycle = {0: 127, 127: 255, 255: 0}
                        settings["grid_opacity"] = cycle[settings["grid_opacity"]]
                        _save_settings()
                    elif setting_rects.get("controls") and setting_rects["controls"].collidepoint(event.pos):
                        schemes = ["wasd_arrows", "ijkl", "arrows_only", "spacebar"]
                        idx = schemes.index(settings["control_scheme"])
                        settings["control_scheme"] = schemes[(idx + 1) % len(schemes)]
                        _save_settings()
                    elif setting_rects.get("timer") and setting_rects["timer"].collidepoint(event.pos):
                        settings["show_timer"] = not settings["show_timer"]
                        _save_settings()
                    elif setting_rects.get("fps") and setting_rects["fps"].collidepoint(event.pos):
                        fps_cycle = {30: 60, 60: 120, 120: 0, 0: 30}
                        settings["fps_limit"] = fps_cycle[settings["fps_limit"]]
                        _save_settings()
                    elif setting_rects.get("hardcore") and setting_rects["hardcore"].collidepoint(event.pos):
                        settings["hardcore"] = not settings["hardcore"]
                        if settings["hardcore"]:
                            settings["wrap_around"] = False
                        _save_settings()
                    elif setting_rects.get("double_food") and setting_rects["double_food"].collidepoint(event.pos):
                        settings["double_food"] = not settings["double_food"]
                        _save_settings()
                    elif setting_rects.get("seed") and setting_rects["seed"].collidepoint(event.pos):
                        seed_input_overlay()
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
                elif event.key == pygame.K_UP:
                    menu_sel = (menu_sel - 1) % 3
                elif event.key == pygame.K_DOWN:
                    menu_sel = (menu_sel + 1) % 3
                elif event.key == pygame.K_1 or event.key == pygame.K_RETURN:
                    music_manager.stop_music()
                    return "single"
                elif event.key == pygame.K_2:
                    music_manager.stop_music()
                    return "multi"
                elif event.key == pygame.K_3 or event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
            if event.type == pygame.JOYBUTTONDOWN:
                if _joy_is_debug_btn(event):
                    debug_overlay_visible = not debug_overlay_visible
                    print(f"Debug overlay status: {'ON' if debug_overlay_visible else 'OFF'}")
                elif _joy_is_panel_btn(event):
                    toggle_panel()
                elif panel_open:
                    if event.button in (0, 2):
                        _toggle_setting(_PANEL_ROW_KEYS[panel_sel])
                    elif event.button == 1:
                        toggle_panel()
                else:
                    if event.button in (0, 2):
                        music_manager.stop_music()
                        if menu_sel == 0: return "single"
                        elif menu_sel == 1: return "multi"
                        else: pygame.quit(); sys.exit()
                    elif event.button == 4:
                        current_diff_idx = (current_diff_idx - 1) % len(diff_names)
                        DIFFICULTY = DIFFICULTY_LEVELS[diff_names[current_diff_idx]]
                    elif event.button == 5:
                        current_diff_idx = (current_diff_idx + 1) % len(diff_names)
                        DIFFICULTY = DIFFICULTY_LEVELS[diff_names[current_diff_idx]]
            if event.type == pygame.JOYHATMOTION:
                if panel_open:
                    if event.value[1] > 0:   panel_sel = (panel_sel - 1) % PANEL_ROWS
                    elif event.value[1] < 0: panel_sel = (panel_sel + 1) % PANEL_ROWS
                else:
                    if event.value[1] > 0:    menu_sel = (menu_sel - 1) % 3
                    elif event.value[1] < 0:  menu_sel = (menu_sel + 1) % 3
                    elif event.value[0] == -1:
                        current_diff_idx = (current_diff_idx - 1) % len(diff_names)
                        DIFFICULTY = DIFFICULTY_LEVELS[diff_names[current_diff_idx]]
                    elif event.value[0] == 1:
                        current_diff_idx = (current_diff_idx + 1) % len(diff_names)
                        DIFFICULTY = DIFFICULTY_LEVELS[diff_names[current_diff_idx]]
            if event.type == pygame.JOYAXISMOTION:
                prev = _joy_axis_last.get(event.axis, 0.0)
                cur  = event.value
                _joy_axis_last[event.axis] = cur
                if event.axis == 1:
                    if cur < -0.55 and prev >= -0.55:
                        if panel_open: panel_sel = (panel_sel - 1) % PANEL_ROWS
                        else:          menu_sel   = (menu_sel - 1) % 3
                    elif cur > 0.55 and prev <= 0.55:
                        if panel_open: panel_sel = (panel_sel + 1) % PANEL_ROWS
                        else:          menu_sel   = (menu_sel + 1) % 3
                elif event.axis == 0 and not panel_open:
                    if cur < -0.55 and prev >= -0.55:
                        current_diff_idx = (current_diff_idx - 1) % len(diff_names)
                        DIFFICULTY = DIFFICULTY_LEVELS[diff_names[current_diff_idx]]
                    elif cur > 0.55 and prev <= 0.55:
                        current_diff_idx = (current_diff_idx + 1) % len(diff_names)
                        DIFFICULTY = DIFFICULTY_LEVELS[diff_names[current_diff_idx]]

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
            eye_color = (30, 30, 30) if settings["light_mode"] else COLORS["white"]

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
    global snake_pos, snake_body, food_pos, food_spawn, food2_pos, direction, change_to, score
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
            elif event.type in (pygame.JOYDEVICEADDED, pygame.JOYDEVICEREMOVED):
                _refresh_joysticks()
            elif event.type == pygame.JOYBUTTONDOWN and event.joy == 0:
                if _joy_is_debug_btn(event):
                    debug_overlay_visible = not debug_overlay_visible
                    print(f"Debug overlay status: {'ON' if debug_overlay_visible else 'OFF'}")
                elif _joy_is_pause_btn(event):
                    if not settings["hardcore"]:
                        if pause_menu(is_multiplayer=False, mode_label="SP Endless"):
                            return "menu"
                elif settings["control_scheme"] == "spacebar" or not _joysticks:
                    if _joy_x_pressed(event, 0):
                        change_to = _SPACEBAR_CYCLE[_spacebar_idx % len(_SPACEBAR_CYCLE)]
                        _spacebar_idx += 1
            elif event.type == pygame.KEYDOWN:
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
                        if pause_menu(is_multiplayer=False, mode_label="SP Endless"):
                            return "menu"
                elif event.key == pygame.K_m:
                    if not settings["hardcore"]:
                        if confirm_quit_to_menu():
                            return "menu"
            elif event.type == pygame.ACTIVEEVENT:
                if event.state == pygame.APPINPUTFOCUS and not event.gain:
                    if not settings["hardcore"]:
                        if pause_menu(is_multiplayer=False, mode_label="SP Endless"):
                            return "menu"

        if burst1["active"] and now_ms >= burst1["end_ms"]:
            burst1["active"] = False
            print("Speedy end..")

        if leftover is not None and now_ms - leftover["born"] >= LEFTOVER_LINGER_MS:
            leftover = None
            print("Too slow! Burst pickup faded")

        if settings["hardcore"] and leftover is not None:
            leftover = None

        effective_difficulty = DIFFICULTY * (BURST_MULTIPLIER if burst1["active"] else 1.0)

        tick_accum += effective_difficulty / 60.0
        do_step = tick_accum >= 1.0
        if do_step:
            tick_accum -= 1.0

            opposites = {"UP": "DOWN", "DOWN": "UP", "LEFT": "RIGHT", "RIGHT": "LEFT"}
            joy_dir = _joy_direction(0)
            if joy_dir and joy_dir != opposites[direction]:
                change_to = joy_dir
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

            if settings["wrap_around"] and not settings["hardcore"]:
                grid_w = (SCREEN_WIDTH  // CELL_SIZE) * CELL_SIZE
                grid_h = (SCREEN_HEIGHT // CELL_SIZE) * CELL_SIZE
                if snake_pos[0] < 0:           snake_pos[0] = grid_w - CELL_SIZE
                elif snake_pos[0] >= grid_w:   snake_pos[0] = 0
                if snake_pos[1] < 0:           snake_pos[1] = grid_h - CELL_SIZE
                elif snake_pos[1] >= grid_h:   snake_pos[1] = 0

            snake_body.insert(0, list(snake_pos))

            ate = False
            if snake_pos == food_pos:
                score += 1; ate = True
                if leftover is None and not settings["hardcore"]:
                    leftover = {"pos": spawn_food(snake_body), "born": now_ms}
                food_pos = spawn_food(snake_body)
                print(f"Yummies food1! Score: {score}")
            elif settings["double_food"] and snake_pos == food2_pos:
                score += 1; ate = True
                if leftover is None and not settings["hardcore"]:
                    leftover = {"pos": spawn_food(snake_body), "born": now_ms}
                food2_pos = spawn_food(snake_body)
                print(f"Yummies food2! Score: {score}")
            if not ate:
                snake_body.pop()

            if leftover is not None and snake_pos == leftover["pos"]:
                if not settings["hardcore"]:  # no burst in hardcore
                    burst1["active"] = True
                    burst1["end_ms"] = now_ms + BURST_DURATION_MS
                leftover = None
                print(f"Burst is a goner!")

        draw_background()
        draw_leftover(leftover, now_ms)
        draw_snake(snake_pos, snake_body, direction, True, burst_active=burst1["active"])

        pygame.draw.rect(screen, COLORS["yummers"], pygame.Rect(food_pos[0], food_pos[1], CELL_SIZE, CELL_SIZE))
        pygame.draw.rect(screen, (255, 255, 200), pygame.Rect(food_pos[0] + CELL_SIZE//4, food_pos[1] + CELL_SIZE//4, CELL_SIZE//4, CELL_SIZE//4))
        if settings["double_food"]:
            pygame.draw.rect(screen, COLORS["yummers"], pygame.Rect(food2_pos[0], food2_pos[1], CELL_SIZE, CELL_SIZE))
            pygame.draw.rect(screen, (255, 200, 80), pygame.Rect(food2_pos[0] + CELL_SIZE//4, food2_pos[1] + CELL_SIZE//4, CELL_SIZE//4, CELL_SIZE//4))

        if burst1["active"]:
            remaining = max(0, burst1["end_ms"] - now_ms)
            pulse = 0.5 + 0.5 * math.sin(now_ms / 80.0)
            r = int(255 * pulse)
            burst_font = pygame.font.SysFont("consolas", 22)
            burst_surf = burst_font.render(f"Burst active for {remaining/1000:.1f}s", True, (r, 200, 0))
            screen.blit(burst_surf, (10, 35))

        # Hardcore badge
        if settings["hardcore"]:
            hc_font = pygame.font.SysFont("consolas", 18)
            hc_surf = hc_font.render("HARDCORE MODE", True, (255, 40, 40))
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

def _mp_controller_warning():
    font_big = pygame.font.SysFont("times new roman", 58)
    font_med = pygame.font.SysFont("consolas", 24)
    font_sm  = pygame.font.SysFont("consolas", 19)
    pygame.event.clear()
    open_time = pygame.time.get_ticks()
    while True:
        draw_background()
        lm  = settings["light_mode"]
        txt = (20, 20, 20) if lm else COLORS["white"]
        dim = (100, 100, 100) if lm else (160, 160, 160)
        now_ms = pygame.time.get_ticks()
        ready  = now_ms - open_time > 400

        title_s = font_big.render("Only 1 controller connected", True, COLORS["yummers"])
        screen.blit(title_s, title_s.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 120)))
        lines = [
            "P1 uses Controller 1",
            "P2 uses Arrow Keys on keyboard",
            "",
            "Press any button or key to continue." if ready else "...",
            "Connect a second controller and press R to refresh.",
        ]
        for i, line in enumerate(lines):
            c = dim if not line else txt
            s = font_med.render(line, True, c)
            screen.blit(s, s.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 30 + i * 36)))
        hint_s = font_sm.render("ESC = back to menu", True, dim)
        screen.blit(hint_s, hint_s.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 200)))
        pygame.display.update()
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type in (pygame.JOYDEVICEADDED, pygame.JOYDEVICEREMOVED):
                _refresh_joysticks()
            if not ready:
                continue
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                if event.key in (ord("r"), ord("R")):
                    _refresh_joysticks()
                    if len(_joysticks) >= 2:
                        return True
                else:
                    return True
            if event.type == pygame.JOYBUTTONDOWN:
                return True

def multiplayer_game():
    music_manager.play_music('ingame', loop=True, volume=0.5)
    global snake1_pos, snake1_body, snake2_pos, snake2_body, food_pos, food_spawn
    global direction1, change_to1, direction2, change_to2, score1, score2
    global leftover, burst1, burst2
    global debug_overlay_visible

    _refresh_joysticks()
    p1_on_joy   = len(_joysticks) >= 1
    p2_on_joy   = len(_joysticks) >= 2
    joy_warning = p1_on_joy and not p2_on_joy

    if joy_warning:
        if not _mp_controller_warning():
            return "menu"
        p2_on_joy = len(_joysticks) >= 2

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
            elif event.type in (pygame.JOYDEVICEADDED, pygame.JOYDEVICEREMOVED):
                _refresh_joysticks()
                p1_on_joy = len(_joysticks) >= 1
                p2_on_joy = len(_joysticks) >= 2
            elif event.type == pygame.JOYBUTTONDOWN:
                if _joy_is_debug_btn(event):
                    debug_overlay_visible = not debug_overlay_visible
                    print(f"Debug overlay status: {'ON' if debug_overlay_visible else 'OFF'}")
                elif _joy_is_pause_btn(event):
                    if pause_menu(is_multiplayer=True, mode_label="Multiplayer"):
                        return "menu"
                elif event.joy == 0 and _joy_x_pressed(event, 0) and settings["control_scheme"] == "spacebar":
                    change_to1 = _SPACEBAR_CYCLE[0]
            elif event.type == pygame.KEYDOWN:
                p1_key_directions = {
                    ord("w"): "UP", ord("s"): "DOWN",
                    ord("a"): "LEFT", ord("d"): "RIGHT"
                }
                p2_key_directions = {
                    pygame.K_UP: "UP", pygame.K_DOWN: "DOWN",
                    pygame.K_LEFT: "LEFT", pygame.K_RIGHT: "RIGHT"
                }
                if not p1_on_joy and event.key in p1_key_directions:
                    change_to1 = p1_key_directions[event.key]
                if (not p2_on_joy) and event.key in p2_key_directions:
                    change_to2 = p2_key_directions[event.key]
                if event.key == pygame.K_F5:
                    debug_overlay_visible = not debug_overlay_visible
                    print(f"Debug overlay status: {'ON' if debug_overlay_visible else 'OFF'}")
                elif event.key == pygame.K_ESCAPE:
                    if pause_menu(is_multiplayer=True, mode_label="Multiplayer"):
                        return "menu"
                elif event.key == pygame.K_m:
                    if confirm_quit_to_menu():
                        return "menu"
            elif event.type == pygame.ACTIVEEVENT:
                if event.state == pygame.APPINPUTFOCUS and not event.gain:
                    if pause_menu(is_multiplayer=True, mode_label="Multiplayer"):
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
            if p1_on_joy:
                joy_dir1 = _joy_direction(0)
                if joy_dir1 and joy_dir1 != opposites[direction1]:
                    change_to1 = joy_dir1
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
            if p2_on_joy:
                joy_dir2 = _joy_direction(1)
                if joy_dir2 and joy_dir2 != opposites[direction2]:
                    change_to2 = joy_dir2
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
            surf = hud_font.render(f"P1 BURST active for {remaining/1000:.1f}s", True, (255, int(200*pulse), 0))
            screen.blit(surf, (10, 60))
        if burst2["active"]:
            remaining = max(0, burst2["end_ms"] - now_ms)
            pulse = 0.5 + 0.5 * math.sin(now_ms / 80.0)
            surf = hud_font.render(f"P2 BURST active for {remaining/1000:.1f}s", True, (0, int(200*pulse), 255))
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
                winner = "tie" 

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
            while True:
                choice = sp_mode_select()
                if choice == "back":
                    break
                elif isinstance(choice, tuple) and choice[0] == "endless":
                    result = single_player_game()
                    if result == "menu":
                        break
                elif isinstance(choice, tuple) and choice[0] == "sa":
                    result = score_attack_game(choice[1])
                    if result == "menu":
                        break
        elif game_mode == "multi":
            result = multiplayer_game()
            if result == "menu":
                continue
        else:
            pygame.quit()
            sys.exit()
