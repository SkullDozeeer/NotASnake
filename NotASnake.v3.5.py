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

def _get_screenshots_dir():
    if getattr(sys, 'frozen', False):
        base_dir = os.path.dirname(sys.executable)
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))
    d = os.path.join(base_dir, "nasassets", "screenshots")
    os.makedirs(d, exist_ok=True)
    return d

_SETTINGS_BOOL_KEYS  = ["music_muted", "wrap_around", "light_mode", "show_timer", "hardcore", "double_food", "fog_of_war", "snake_pattern"]
_SETTINGS_INT_KEYS   = ["grid_opacity", "fps_limit", "start_length"]
_SETTINGS_STR_KEYS   = ["control_scheme", "bg_style"]
_STATS_INT_KEYS      = [
    "total_apples", "games_played", "games_cheated", "games_mp",
    "mp_p1_wins", "mp_p2_wins", "mp_ties", "longest_game_ms", "shortest_game_ms",
]

def load_save(path=None):
    if path is None:
        path = _get_save_path()
    data = {
        "score": 0, "seed": "", "double_food": True,
        "apples": set(), "sa_best_15": 0, "sa_best_30": 0, "sa_best_50": 0,
        "shrink_best": 0, "dm_best_ms": 0,
        "pacifist_best": 0, "trust_best": 0, "chaos_best": 0, "rewind_best": 0,
        "music_muted": False, "wrap_around": False, "light_mode": False,
        "show_timer": False, "hardcore": False, "grid_opacity": 0,
        "fps_limit": 60, "control_scheme": "wasd_arrows",
        "fog_of_war": False, "start_length": 3, "snake_pattern": True,
        "bg_style": "plain", "seen_tips": set(),
    }
    for k in _STATS_INT_KEYS:
        data[k] = 0
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
                elif key == "seen_tips":
                    if val:
                        data["seen_tips"] = set(x for x in val.split(",") if x.strip())
                elif key.startswith("sa_best_"):
                    try:
                        t = int(key[8:])
                        data[f"sa_best_{t}"] = int(val) if val else 0
                    except ValueError:
                        pass
                elif key == "shrink_best":
                    try: data["shrink_best"] = int(val)
                    except ValueError: pass
                elif key == "dm_best_ms":
                    try: data["dm_best_ms"] = int(val)
                    except ValueError: pass
                elif key in ("pacifist_best", "trust_best", "chaos_best", "rewind_best"):
                    try: data[key] = int(val)
                    except ValueError: pass
                elif key in _SETTINGS_BOOL_KEYS:
                    data[key] = val == "1"
                elif key in _SETTINGS_INT_KEYS:
                    try: data[key] = int(val)
                    except ValueError: pass
                elif key in _SETTINGS_STR_KEYS:
                    data[key] = val
                elif key in _STATS_INT_KEYS:
                    try: data[key] = int(val)
                    except ValueError: pass
    except FileNotFoundError:
        if path != _get_save_path():
            return data
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
            tips_str = ",".join(sorted(data.get("seen_tips", set())))
            f.write(f"seen_tips={tips_str}\n")
            for t in SA_TARGETS:
                f.write(f"sa_best_{t}={data.get(f'sa_best_{t}', 0)}\n")
            f.write(f"shrink_best={data.get('shrink_best', 0)}\n")
            f.write(f"dm_best_ms={data.get('dm_best_ms', 0)}\n")
            f.write(f"pacifist_best={data.get('pacifist_best', 0)}\n")
            f.write(f"trust_best={data.get('trust_best', 0)}\n")
            f.write(f"chaos_best={data.get('chaos_best', 0)}\n")
            f.write(f"rewind_best={data.get('rewind_best', 0)}\n")
            for k in _SETTINGS_BOOL_KEYS:
                f.write(f"{k}={'1' if data.get(k, False) else '0'}\n")
            for k in _SETTINGS_INT_KEYS:
                f.write(f"{k}={data.get(k, 0)}\n")
            for k in _SETTINGS_STR_KEYS:
                f.write(f"{k}={data.get(k, '')}\n")
            for k in _STATS_INT_KEYS:
                f.write(f"{k}={data.get(k, 0)}\n")
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

def record_game_stats(duration_ms, apples, cheated=False, is_mp=False, winner=None):
    data = load_save()
    data["games_played"] = data.get("games_played", 0) + 1
    data["total_apples"] = data.get("total_apples", 0) + max(0, apples)
    if cheated:
        data["games_cheated"] = data.get("games_cheated", 0) + 1
    if duration_ms > 0:
        if duration_ms > data.get("longest_game_ms", 0):
            data["longest_game_ms"] = duration_ms
        shortest = data.get("shortest_game_ms", 0)
        if shortest == 0 or duration_ms < shortest:
            data["shortest_game_ms"] = duration_ms
    if is_mp:
        data["games_mp"] = data.get("games_mp", 0) + 1
        if winner == "player1":
            data["mp_p1_wins"] = data.get("mp_p1_wins", 0) + 1
        elif winner == "player2":
            data["mp_p2_wins"] = data.get("mp_p2_wins", 0) + 1
        else:
            data["mp_ties"] = data.get("mp_ties", 0) + 1
    save_save(data)
    print(f"Stats recorded: dur={duration_ms}ms apples={apples} cheated={cheated} mp={is_mp} winner={winner}")
    return data

def _fmt_time_ms(ms):
    s = ms / 1000.0
    return f"{int(s // 60):02d}:{s % 60:05.2f}"

def _better_time(va, vb):
    if va == 0: return vb
    if vb == 0: return va
    return min(va, vb)

def fuse_save_data(a, b):
    result = dict(a)
    result["score"] = max(a.get("score", 0), b.get("score", 0))
    result["apples"] = set(a.get("apples", set())) | set(b.get("apples", set()))
    for t in SA_TARGETS:
        key = f"sa_best_{t}"
        result[key] = _better_time(a.get(key, 0), b.get(key, 0))
    result["shrink_best"] = max(a.get("shrink_best", 0), b.get("shrink_best", 0))
    result["dm_best_ms"]  = max(a.get("dm_best_ms", 0), b.get("dm_best_ms", 0))
    result["pacifist_best"] = max(a.get("pacifist_best", 0), b.get("pacifist_best", 0))
    result["trust_best"]    = max(a.get("trust_best", 0), b.get("trust_best", 0))
    result["chaos_best"]    = max(a.get("chaos_best", 0), b.get("chaos_best", 0))
    result["rewind_best"]   = max(a.get("rewind_best", 0), b.get("rewind_best", 0))
    for k in ["total_apples", "games_played", "games_cheated", "games_mp",
              "mp_p1_wins", "mp_p2_wins", "mp_ties", "longest_game_ms"]:
        result[k] = max(a.get(k, 0), b.get(k, 0))
    result["shortest_game_ms"] = _better_time(a.get("shortest_game_ms", 0), b.get("shortest_game_ms", 0))
    return result

ACTIVE_SEED = ""      # loaded from save.txt at startup (see below)
_food_call_counter = 0  # incremented each spawn_food call for per-food determinism

def _seed_int():
    if not ACTIVE_SEED:
        return None
    return hash(ACTIVE_SEED) & 0xFFFFFFFF

def _seed_display(max_len=8):
    if not ACTIVE_SEED:
        return ""
    if len(ACTIVE_SEED) <= max_len:
        return ACTIVE_SEED
    return ACTIVE_SEED[:max_len] + ".."

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
    "purpleguy": pygame.Color(160, 32, 240),
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
pygame.display.set_caption("NotASnake v3.5 | Thanks for playing!")

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

_FONT_FILES = {
    "title":    ["PressStart2P-Regular.ttf"],
    "menu":     ["PixelifySans-Regular.ttf", "PixelifySans-VariableFont_wght.ttf"],
    "ui":       ["JetBrainsMono-Regular.ttf"],
    "ui_bold":  ["JetBrainsMono-Bold.ttf", "JetBrainsMono-Regular.ttf"],
}
_SYSFONT_FALLBACK = {
    "title": "times new roman",
    "menu": "times new roman",
    "ui": "consolas",
    "ui_bold": "consolas",
}
_FONT_KEY_ALIAS = {"consolas": "ui", "times new roman": "title", "times": "title"}

_font_paths = {}
_font_cache = {}

def _find_font_file(filenames):
    if getattr(sys, 'frozen', False):
        base_dir = os.path.dirname(sys.executable)
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))
    search_paths = [
        "fonts/", "nasassets/fonts/",
        os.path.join(base_dir, "fonts"),
        os.path.join(base_dir, "nasassets", "fonts"),
    ]
    for path in search_paths:
        for filename in filenames:
            full_path = os.path.join(path, filename)
            if os.path.exists(full_path):
                return full_path
    return None

def _load_fonts():
    for key, names in _FONT_FILES.items():
        found = _find_font_file(names)
        _font_paths[key] = found
        if found:
            print(f"Font McGee is here: {key} -> {found}")
        else:
            print(f"Font missing for '{key}', we are back to '{_SYSFONT_FALLBACK[key]}')")

_load_fonts()

def get_font(key, size, bold=False):
    key = _FONT_KEY_ALIAS.get(key, key)
    cache_key = (key, size, bold)
    if cache_key in _font_cache:
        return _font_cache[cache_key]
    path = _font_paths.get(key)
    if path:
        f = pygame.font.Font(path, size)
        if bold:
            f.set_bold(True)
    else:
        f = pygame.font.SysFont(_SYSFONT_FALLBACK.get(key, "consolas"), size, bold=bold)
    _font_cache[cache_key] = f
    return f

def render_fit(key, text, color, max_width, start_size, min_size=10, bold=False):
    size = start_size
    while size > min_size:
        f = get_font(key, size, bold=bold)
        surf = f.render(text, True, color)
        if surf.get_width() <= max_width:
            return surf
        size -= 2
    f = get_font(key, min_size, bold=bold)
    surf = f.render(text, True, color)
    if surf.get_width() <= max_width:
        return surf
    trimmed = text
    while len(trimmed) > 1:
        trimmed = trimmed[:-1]
        surf = f.render(trimmed + "...", True, color)
        if surf.get_width() <= max_width:
            return surf
    return surf

MUSIC_LOOP_HANDOFF_EVENT = pygame.USEREVENT + 1

class MusicManager:
    def __init__(self):
        self.current_music = None
        self.music_enabled = True
        self.pending_loop_file = None
        self.music_paths = {
            'menu': self._find_music_file(['Menu.wav', 'Menu.mp3', 'Menu.wav']),
            'gameover': self._find_music_file(['GameOver.wav', 'GameOver.mp3', 'GameOver.wav']),
            'effect': self._find_music_file(['SlowDeath.wav', 'SlowDeath.mp3', 'SlowDeath.wav']),
            'ingame': self._find_music_file(['Worm-Rock.mp3', 'Worm-Rock.m4a', 'Worm-Rock.wav']),
            'heroic_intro': self._find_music_file(['Heroic_intro.wav', 'Heroic_intro.mp3', 'Heroic_intro.m4a']),
            'heroic_loop': self._find_music_file(['Heroic_loop.wav', 'Heroic_loop.mp3', 'Heroic_loop.m4a']),
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
            print(f"  (was trying to load '{music_type}' -> {self.music_paths.get(music_type)})")

    def play_heroic(self, volume=0.5):
        """Plays the countdown-synced intro once, then hands off to the seamless loop body.
        Avoids replaying the intro every loop the way a plain play(-1) would.
        Falls back to the regular ingame track (Worm-Rock) if the loop file is missing."""
        if not self.music_enabled or settings.get("music_muted", False):
            return
        intro_file    = self.music_paths.get('heroic_intro')
        loop_file     = self.music_paths.get('heroic_loop')
        fallback_file = self.music_paths.get('ingame')
        has_loop      = loop_file and os.path.exists(loop_file)
        try:
            if intro_file and os.path.exists(intro_file):
                pygame.mixer.music.stop()
                pygame.mixer.music.load(intro_file)
                pygame.mixer.music.set_volume(volume)
                pygame.mixer.music.set_endevent(MUSIC_LOOP_HANDOFF_EVENT)
                pygame.mixer.music.play(0)
                self.current_music = intro_file
                if has_loop:
                    self.pending_loop_file = loop_file
                elif fallback_file and os.path.exists(fallback_file):
                    self.pending_loop_file = fallback_file
                    print("heroic_loop missing, play plain old shit after intro")
                else:
                    self.pending_loop_file = None
                print(f"This slaps! heroic_intro music is FIRE!: {os.path.basename(intro_file)}")
            elif has_loop:
                pygame.mixer.music.stop()
                pygame.mixer.music.set_endevent()
                pygame.mixer.music.load(loop_file)
                pygame.mixer.music.set_volume(volume)
                pygame.mixer.music.play(-1)
                self.current_music = loop_file
                self.pending_loop_file = None
            else:
                print("No heroic intro or loop found, bruh, rolling back to regular program...")
                self.pending_loop_file = None
                self.play_music('ingame', loop=True, volume=volume)
        except Exception as e:
            print(f"The fuck did you do? My party said that {e}")
            print(f"  (was trying to load heroic_intro/heroic_loop)")

    def handle_event(self, event):
        """Call this from a game loop's event handling. Completes the heroic
        intro -> loop handoff once the intro naturally finishes playing."""
        if event.type == MUSIC_LOOP_HANDOFF_EVENT and self.pending_loop_file:
            loop_file = self.pending_loop_file
            is_fallback = loop_file == self.music_paths.get('ingame')
            self.pending_loop_file = None
            try:
                pygame.mixer.music.set_endevent()
                pygame.mixer.music.load(loop_file)
                pygame.mixer.music.play(-1)
                self.current_music = loop_file
                label = "ingame (fallback)" if is_fallback else "heroic_loop"
                print(f"This slaps! {label} music is FIRE!: {os.path.basename(loop_file)}")
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
        pygame.mixer.music.set_endevent()
        self.pending_loop_file = None
        pygame.mixer.music.stop()
        self.current_music = None

    def fadeout_music(self, duration=1000):
        pygame.mixer.music.set_endevent()
        self.pending_loop_file = None
        pygame.mixer.music.fadeout(duration)
        self.current_music = None


music_manager = MusicManager()

_boot_data    = load_save()
ACTIVE_SEED   = _boot_data["seed"]
_earned_apples = _boot_data.get("apples", set())
_sa_bests     = {t: _boot_data.get(f"sa_best_{t}", 0) for t in SA_TARGETS}
_shrink_best  = _boot_data.get("shrink_best", 0)
_dm_best_ms   = _boot_data.get("dm_best_ms", 0)
_pacifist_best = _boot_data.get("pacifist_best", 0)
_trust_best    = _boot_data.get("trust_best", 0)
_chaos_best    = _boot_data.get("chaos_best", 0)
_rewind_best   = _boot_data.get("rewind_best", 0)
_seen_tips     = _boot_data.get("seen_tips", set())
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
    "fog_of_war":     _boot_data.get("fog_of_war",      False),
    "start_length":   _boot_data.get("start_length",    3),
    "snake_pattern":  _boot_data.get("snake_pattern",   True),
    "bg_style":       _boot_data.get("bg_style",        "plain"),
}

def _reload_state_from_save():
    global ACTIVE_SEED, _earned_apples, _sa_bests, _shrink_best, _dm_best_ms
    global _pacifist_best, _trust_best, _chaos_best, _rewind_best
    data = load_save()
    ACTIVE_SEED    = data["seed"]
    _earned_apples = data.get("apples", set())
    _sa_bests      = {t: data.get(f"sa_best_{t}", 0) for t in SA_TARGETS}
    _shrink_best   = data.get("shrink_best", 0)
    _dm_best_ms    = data.get("dm_best_ms", 0)
    _pacifist_best = data.get("pacifist_best", 0)
    _trust_best    = data.get("trust_best", 0)
    _chaos_best    = data.get("chaos_best", 0)
    _rewind_best   = data.get("rewind_best", 0)
    settings["music_muted"]    = data.get("music_muted", False)
    settings["wrap_around"]    = data.get("wrap_around", False)
    settings["light_mode"]     = data.get("light_mode", False)
    settings["grid_opacity"]   = data.get("grid_opacity", 0)
    settings["control_scheme"] = data.get("control_scheme", "wasd_arrows")
    settings["show_timer"]     = data.get("show_timer", False)
    settings["fps_limit"]      = data.get("fps_limit", 60)
    settings["hardcore"]       = data.get("hardcore", False)
    settings["double_food"]    = data.get("double_food", True)
    return data

def _pick_file(mode="open"):
    import tkinter as tk
    from tkinter import filedialog
    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    try:
        if mode == "open":
            path = filedialog.askopenfilename(
                title="Select your NotASnake save.txt",
                filetypes=[("TXT saves", "*.txt"), ("All files", "*.*")],
            )
        else:
            path = filedialog.asksaveasfilename(
                title="Export your NotASnake save",
                defaultextension=".txt",
                filetypes=[("Save file", "*.txt")],
            )
    finally:
        root.destroy()
    return path or None

def import_save_file():
    try:
        path = _pick_file("open")
    except Exception as e:
        print(f"Import dialog failed: {e}")
        return None
    if not path:
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        save_path = _get_save_path()
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        with open(save_path, "w", encoding="utf-8") as f:
            f.write(content)
        _reload_state_from_save()
        print(f"Save imported from {path}, a regular i see!")
        return True
    except Exception as e:
        print(f"Import failed: {e}")
        return False

def export_save_file():
    try:
        path = _pick_file("save")
    except Exception as e:
        print(f"Export dialog failed: {e}")
        return None
    if not path:
        return None
    try:
        import shutil
        shutil.copyfile(_get_save_path(), path)
        print(f"Save exported to {path}, see you soon!")
        return True
    except Exception as e:
        print(f"Export failed: {e}")
        return False

def fuse_save_files(path_a, path_b):
    try:
        data_a = load_save(path_a)
        data_b = load_save(path_b)
        fused  = fuse_save_data(data_a, data_b)
        save_save(fused)
        _reload_state_from_save()
        print(f"Fused '{path_a}' + '{path_b}' into current save")
        return True
    except Exception as e:
        print(f"Fuse failed: {e}")
        return False

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


def _cheat_key_open(event):
    if event.type != pygame.KEYDOWN:
        return False
    return event.key == pygame.K_BACKQUOTE or event.unicode in ('`', 'ё', 'Ё')


class CheatConsole:
    def __init__(self):
        self.open    = False
        self.buf     = []
        self.message = ""
        self.msg_until_ms = 0

    def toggle(self):
        self.open = not self.open
        if self.open:
            self.buf = []
            self.message = ""

    def feed_event(self, event, dispatch):
        if not self.open:
            return None
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.open = False
                return None
            elif event.key == pygame.K_RETURN:
                code = "".join(self.buf).strip()
                self.buf = []
                if code in dispatch:
                    result = dispatch[code]()
                    self.message = result if isinstance(result, str) else "Cheat activated."
                elif code:
                    self.message = f"Uhh, {code}' is not a cheat code"
                self.msg_until_ms = pygame.time.get_ticks() + 2500
                return code
            elif event.key == pygame.K_BACKSPACE:
                if self.buf:
                    self.buf.pop()
            elif event.key == pygame.K_BACKQUOTE or event.unicode in ('`', 'ё', 'Ё'):
                self.open = False
            else:
                ch = event.unicode
                if ch and ch.isprintable() and ch not in ('`', 'ё', 'Ё') and len(self.buf) < 40:
                    self.buf.append(ch)
        return None

    def draw(self, screen_w, screen_h):
        if not self.open:
            return
        font_hint = get_font("ui", 16)
        bw, bh = 560, 90
        bx = (screen_w - bw) // 2
        by = screen_h - 160
        overlay = pygame.Surface((bw, bh), pygame.SRCALPHA)
        overlay.fill((10, 10, 20, 230))
        screen.blit(overlay, (bx, by))
        pygame.draw.rect(screen, COLORS["purpleguy"], (bx, by, bw, bh), 2)
        cursor = "|" if (pygame.time.get_ticks() // 400) % 2 == 0 else " "
        txt_s = render_fit("ui", "> " + "".join(self.buf) + cursor, COLORS["green"],
                            bw - 24, 26, min_size=14)
        screen.blit(txt_s, (bx + 12, by + 14))
        hint_s = font_hint.render("ENTER to submit  //  ESC or ` to close", True, (140, 140, 160))
        screen.blit(hint_s, (bx + 12, by + bh - 24))
        now_ms = pygame.time.get_ticks()
        if self.message and now_ms < self.msg_until_ms:
            msg_s = font_hint.render(self.message, True, COLORS["yummers"])
            screen.blit(msg_s, msg_s.get_rect(center=(screen_w // 2, by - 18)))


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
        print(f"Background is here: {BACKGROUND_IMAGE_PATH}")
    except Exception as e:
        print(f"Background load fucked: {e}")
        _background_surface = None

_load_background()

def get_bg_color():
    return pygame.Color(255, 255, 255) if settings["light_mode"] else COLORS["black"]

_grid_surface_cache = {"key": None, "surf": None}

def _get_grid_surface(grid_alpha, light_mode):
    key = (grid_alpha, light_mode)
    if _grid_surface_cache["key"] == key:
        return _grid_surface_cache["surf"]
    grid_rgb = (180, 180, 180) if light_mode else (60, 60, 60)
    surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    for x in range(0, SCREEN_WIDTH, CELL_SIZE):
        pygame.draw.line(surf, (*grid_rgb, grid_alpha), (x, 0), (x, SCREEN_HEIGHT))
    for y in range(0, SCREEN_HEIGHT, CELL_SIZE):
        pygame.draw.line(surf, (*grid_rgb, grid_alpha), (0, y), (SCREEN_WIDTH, y))
    _grid_surface_cache["key"]  = key
    _grid_surface_cache["surf"] = surf
    return surf

_bg_style_surface_cache = {"key": None, "surf": None}

def _build_vignette_surface(base_color, light_mode):
    surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    surf.fill(base_color)
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    cx, cy = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
    max_r = math.hypot(cx, cy)
    steps = 28
    max_alpha = 90
    accent = (0, 0, 0) if light_mode else (255, 255, 255)
    for i in range(steps, -1, -1):
        r = max_r * (i / steps)
        frac = i / steps
        alpha = int(max_alpha * frac) if light_mode else int(max_alpha * (1 - frac))
        pygame.draw.circle(overlay, (*accent, alpha), (cx, cy), int(r))
    surf.blit(overlay, (0, 0))
    return surf

def _build_diagonal_surface(base_color, light_mode):
    surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    surf.fill(base_color)
    shade = tuple((c + 16) if c < 128 else (c - 16) for c in base_color)
    band_w = 46
    period = 170
    x = -SCREEN_HEIGHT
    while x < SCREEN_WIDTH + SCREEN_HEIGHT:
        pts = [
            (x, SCREEN_HEIGHT), (x + SCREEN_HEIGHT, 0),
            (x + SCREEN_HEIGHT + band_w, 0), (x + band_w, SCREEN_HEIGHT),
        ]
        pygame.draw.polygon(surf, shade, pts)
        x += period
    return surf

def _get_bg_style_surface(style, base_color, light_mode):
    key = (style, base_color, light_mode)
    if _bg_style_surface_cache["key"] == key:
        return _bg_style_surface_cache["surf"]
    if style == "vignette":
        surf = _build_vignette_surface(base_color, light_mode)
    elif style == "diagonal":
        surf = _build_diagonal_surface(base_color, light_mode)
    else:
        surf = None
    _bg_style_surface_cache["key"]  = key
    _bg_style_surface_cache["surf"] = surf
    return surf

def draw_background():
    bg_style = settings.get("bg_style", "plain")
    if _background_surface is not None and not settings["light_mode"]:
        screen.blit(_background_surface, (0, 0))
    elif bg_style != "plain":
        styled = _get_bg_style_surface(bg_style, tuple(get_bg_color())[:3], settings["light_mode"])
        if styled is not None:
            screen.blit(styled, (0, 0))
        else:
            screen.fill(get_bg_color())
    else:
        screen.fill(get_bg_color())

    grid_alpha = settings["grid_opacity"]   # 0, 127, or 255
    if grid_alpha > 0:
        screen.blit(_get_grid_surface(grid_alpha, settings["light_mode"]), (0, 0))

debug_overlay_visible = False

_debug_font = None
def draw_debug_overlay(tick_accum=None, tick_accum1=None, tick_accum2=None,
                       is_multiplayer=False):
    global _debug_font
    if _debug_font is None:
        _debug_font = get_font("ui", 16)
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
            f"Leftover:   {leftover['pos'] if leftover else None}",
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
            f"Leftover:   {leftover['pos'] if leftover else None}",
            f"if you see this, write to: ",
            f"skulldozer@dontmailme.ru",
        ]

    panel_w = 320
    line_h  = 18
    panel_h = len(lines) * line_h + 8
    panel   = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
    panel.fill((0, 0, 0, 180))
    screen.blit(panel, (0, 0))

    for i, line in enumerate(lines):
        color = (0, 255, 0) if i == 0 else (200, 200, 200)
        surf  = font.render(line, True, color)
        if surf.get_width() > panel_w - 8:
            surf = font.render(line[:40] + "...", True, color)
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
    start_len = max(1, settings.get("start_length", 3))
    snake_body = [[start_x - i * CELL_SIZE, start_y] for i in range(start_len)]
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
    global snake1_pos, snake1_body, snake2_pos, snake2_body, food_pos, food2_pos, food_spawn
    global direction1, change_to1, direction2, change_to2, score1, score2
    global leftover, burst1, burst2

    start_x1 = (SCREEN_WIDTH // (4 * CELL_SIZE)) * CELL_SIZE
    start_y = (SCREEN_HEIGHT // (2 * CELL_SIZE)) * CELL_SIZE
    snake1_pos = [start_x1, start_y]
    start_len = max(1, settings.get("start_length", 3))
    snake1_body = [[start_x1 - i * CELL_SIZE, start_y] for i in range(start_len)]
    direction1 = "RIGHT"
    change_to1 = direction1
    score1 = 0

    start_x2 = (3 * SCREEN_WIDTH // (4 * CELL_SIZE)) * CELL_SIZE
    snake2_pos = [start_x2, start_y]
    snake2_body = [[start_x2 + i * CELL_SIZE, start_y] for i in range(start_len)]
    direction2 = "LEFT"
    change_to2 = direction2
    score2 = 0

    all_snake_positions = snake1_body + snake2_body
    food_pos = spawn_food(all_snake_positions)
    food2_pos = spawn_food(all_snake_positions + [food_pos]) if settings.get("double_food", True) else food_pos
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
    txt_color = (30, 30, 30) if settings["light_mode"] else color
    score_font = get_font(font, size)
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

        version_str = "NotASnake v3.5"
        if ACTIVE_SEED:
            version_str += f"  [S:{_seed_display()}]"
        info_surface = score_font.render(version_str, True, txt_color if not ACTIVE_SEED else COLORS["purpleguy"])
        info_rect = info_surface.get_rect(topright=(SCREEN_WIDTH - 10, 10))
        screen.blit(info_surface, info_rect)

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
            score_text = f"NotASnake v3.5 | End Score: {score1}"
            score_surface = score_font.render(score_text, True, txt_color)
            screen.blit(score_surface, (SCREEN_WIDTH//2 - 250, SCREEN_HEIGHT * 4 // 5))
        else:
            score_text = f"NotASnake v3.5 | How cool! Two guys playing! | P1: {score1} | P2: {score2}"
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
    font = get_font("title", 50)
    game_over_text = font.render("GAME OVER", True, COLORS["red"])
    game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))

    fill_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    fill_surf.fill(get_bg_color())

    while drawn_pixels < len(pixels):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        batch_size = min(PIXEL_EFFECT_SPEED, len(pixels) - drawn_pixels)
        for i in range(batch_size):
            x, y = pixels[drawn_pixels + i]
            color = (random.randint(100, 255), random.randint(0, 100), random.randint(0, 100))
            pygame.draw.rect(fill_surf, color, (x, y, pixel_size, pixel_size))

        drawn_pixels += batch_size

        screen.blit(fill_surf, (0, 0))

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
    title_font = get_font("title", 72)
    if mode_label is None:
        mode_label = "Multiplayer" if is_multiplayer else "Single Player"
    sel = 0
    nav_active = False
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

        title_s = title_font.render("Paused", True, txt)
        screen.blit(title_s, title_s.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100)))

        r_hover = resume_rect.collidepoint(mouse_pos)
        q_hover = quit_rect.collidepoint(mouse_pos)
        r_s = render_fit("menu", "Resume", COLORS["green"] if (nav_active and sel == 0) or r_hover else txt, SCREEN_WIDTH - 80, 72, min_size=30)
        q_s = render_fit("menu", "Quit to Menu", COLORS["red"] if (nav_active and sel == 1) or q_hover else txt, SCREEN_WIDTH - 80, 72, min_size=30)
        resume_rect = r_s.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        quit_rect   = q_s.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100))
        screen.blit(r_s, resume_rect)
        screen.blit(q_s, quit_rect)

        info_s = get_font("ui", 16).render(
            f"Mode: {mode_label}. Wow, hello over there!", True, dim)
        screen.blit(info_s, info_s.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50)))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if resume_rect.collidepoint(event.pos): return False
                elif quit_rect.collidepoint(event.pos): return True
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_RETURN): return False
                elif event.key in (pygame.K_UP, pygame.K_w):   sel = 0; nav_active = True
                elif event.key in (pygame.K_DOWN, pygame.K_s): sel = 1; nav_active = True
                elif event.key == pygame.K_SPACE:
                    return sel == 1
            if event.type == pygame.JOYBUTTONDOWN:
                if event.button in (0, 2): return sel == 1
                if event.button == 1:      return False
            if event.type == pygame.JOYHATMOTION:
                if event.value[1] > 0:  sel = 0; nav_active = True
                elif event.value[1] < 0: sel = 1; nav_active = True
            if event.type == pygame.JOYAXISMOTION:
                prev = _joy_axis_last.get(event.axis, 0.0)
                cur  = event.value
                _joy_axis_last[event.axis] = cur
                if event.axis == 1:
                    if cur < -0.55 and prev >= -0.55:  sel = 0; nav_active = True
                    elif cur > 0.55 and prev <= 0.55:  sel = 1; nav_active = True

        pygame.display.update()


def confirm_quit_to_menu():
    sm_font = get_font("ui", 20)
    while True:
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        screen.blit(overlay, (0, 0))
        bw, bh = 480, 210
        bx = (SCREEN_WIDTH  - bw) // 2
        by = (SCREEN_HEIGHT - bh) // 2
        pygame.draw.rect(screen, (18, 18, 35), (bx, by, bw, bh))
        pygame.draw.rect(screen, COLORS["purpleguy"], (bx, by, bw, bh), 2)
        q_s = render_fit("menu", "Return to menu?", COLORS["white"], bw - 40, 62, min_size=24)
        screen.blit(q_s, q_s.get_rect(center=(SCREEN_WIDTH // 2, by + 55)))
        hint = sm_font.render("ENTER for Yes // ESC for No", True, (140, 140, 160))
        screen.blit(hint, hint.get_rect(center=(SCREEN_WIDTH // 2, by + 105)))
        mouse_pos = pygame.mouse.get_pos()
        yes_s  = render_fit("menu", "Yes", COLORS["red"]   if pygame.Rect(bx, by + 130, bw // 2, 60).collidepoint(mouse_pos) else COLORS["white"], bw // 2 - 30, 62, min_size=24)
        no_s   = render_fit("menu", "No",  COLORS["green"] if pygame.Rect(bx + bw // 2, by + 130, bw // 2, 60).collidepoint(mouse_pos) else COLORS["white"], bw // 2 - 30, 62, min_size=24)
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

def save_score_screenshot(score, tag="game"):
    try:
        d = _get_screenshots_dir()
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        path = os.path.join(d, f"{tag}_{max(0, int(score))}pts_{timestamp}.png")
        pygame.image.save(screen, path)
        print(f"Screenshot saved: {path}")
    except Exception as e:
        print(f"Screenshot failed: {e}")

def game_over_menu(is_multiplayer=False, score1=0, score2=0, high_score=0, winner=None,
                    score_display=None, best_display=None, is_new_best=None):
    music_manager.play_music('gameover', volume=0.6)
    sel = 0
    nav_active = False
    _joy_axis_last = {}
    shot_taken = False
    play_again_rect = pygame.Rect(0,0,0,0)
    exit_menu_rect  = pygame.Rect(0,0,0,0)
    exit_desk_rect  = pygame.Rect(0,0,0,0)

    while True:
        draw_background()
        mouse_pos = pygame.mouse.get_pos()
        lm  = settings["light_mode"]
        txt = (20, 20, 20) if lm else COLORS["white"]

        title_surface = get_font("title", 100).render("Game Over", True, COLORS["red"])
        screen.blit(title_surface, title_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 180)))

        if is_multiplayer:
            if winner == "player1":   wt, wc = "Player 1 Wins!", COLORS["head"]
            elif winner == "player2": wt, wc = "Player 2 Wins!", COLORS["head2"]
            else:                     wt, wc = "T-T-Tie!", COLORS["purpleguy"]
            ws = get_font("title", 60).render(wt, True, wc)
            screen.blit(ws, ws.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 80)))

        score_font = get_font("ui", 26)
        if is_multiplayer:
            sc_t = f"P1: {score1} | P2: {score2}"; sc_c = txt
        elif score_display is not None:
            sc_t = score_display
            sc_c = COLORS["purpleguy"] if is_new_best else txt
        else:
            sc_t = f"End Score: {score1}"
            sc_c = COLORS["purpleguy"] if score1 >= high_score and score1 > 0 else txt
        ss = score_font.render(sc_t, True, sc_c)
        score_rect = ss.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        screen.blit(ss, score_rect)

        cursor_y = score_rect.bottom + 30
        if not is_multiplayer:
            hs_font = get_font("ui", 22)
            if score_display is not None:
                new_best = bool(is_new_best)
                hs_t = "NEW HIGH SCORE!" if new_best else (best_display or "")
                hs_c = COLORS["purpleguy"] if new_best else txt
            elif score1 >= high_score and score1 > 0:
                hs_t, hs_c = "NEW HIGH SCORE!", COLORS["purpleguy"]
            else:
                hs_t, hs_c = f"Your highest ever score: {high_score}", txt
            hs_s = hs_font.render(hs_t, True, hs_c)
            hs_rect = hs_s.get_rect(center=(SCREEN_WIDTH // 2, cursor_y))
            screen.blit(hs_s, hs_rect)
            cursor_y = hs_rect.bottom + 34

        def btn_col(idx):
            cols = [COLORS["green"], COLORS["purpleguy"], COLORS["red"]]
            hover = [play_again_rect, exit_menu_rect, exit_desk_rect][idx].collidepoint(mouse_pos)
            return cols[idx] if (nav_active and sel == idx) or hover else txt

        pa_s  = render_fit("menu", "Play Again", btn_col(0), SCREEN_WIDTH - 80, 72, min_size=30)
        em_s  = render_fit("menu", "Main Menu",  btn_col(1), SCREEN_WIDTH - 80, 72, min_size=30)
        ed_s  = render_fit("menu", "Exit Game",  btn_col(2), SCREEN_WIDTH - 80, 72, min_size=30)
        play_again_rect = pa_s.get_rect(center=(SCREEN_WIDTH // 2, cursor_y + 40))
        exit_menu_rect  = em_s.get_rect(center=(SCREEN_WIDTH // 2, cursor_y + 120))
        exit_desk_rect  = ed_s.get_rect(center=(SCREEN_WIDTH // 2, cursor_y + 200))
        screen.blit(pa_s, play_again_rect)
        screen.blit(em_s, exit_menu_rect)
        screen.blit(ed_s, exit_desk_rect)

        if not shot_taken:
            shot_taken = True
            total_score = (score1 + score2) if is_multiplayer else score1
            save_score_screenshot(total_score, "mp" if is_multiplayer else "sp")

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
                if event.key in (pygame.K_UP, pygame.K_w):     sel = (sel - 1) % 3; nav_active = True
                elif event.key in (pygame.K_DOWN, pygame.K_s): sel = (sel + 1) % 3; nav_active = True
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    music_manager.stop_music()
                    if sel == 0: return "play_again"
                    elif sel == 1: return "main_menu"
                    else: pygame.quit(); sys.exit()
                elif event.key == pygame.K_1: music_manager.stop_music(); return "play_again"
                elif event.key in (pygame.K_2, pygame.K_m): music_manager.stop_music(); return "main_menu"
                elif event.key == pygame.K_3: pygame.quit(); sys.exit()
            if event.type == pygame.JOYBUTTONDOWN:
                if event.button in (0, 2):
                    music_manager.stop_music()
                    if sel == 0: return "play_again"
                    elif sel == 1: return "main_menu"
                    else: pygame.quit(); sys.exit()
                elif event.button == 1: music_manager.stop_music(); return "main_menu"
            if event.type == pygame.JOYHATMOTION:
                if event.value[1] > 0:   sel = (sel - 1) % 3; nav_active = True
                elif event.value[1] < 0: sel = (sel + 1) % 3; nav_active = True
            if event.type == pygame.JOYAXISMOTION:
                prev = _joy_axis_last.get(event.axis, 0.0)
                cur  = event.value
                _joy_axis_last[event.axis] = cur
                if event.axis == 1:
                    if cur < -0.55 and prev >= -0.55:  sel = (sel - 1) % 3; nav_active = True
                    elif cur > 0.55 and prev <= 0.55:  sel = (sel + 1) % 3; nav_active = True

        pygame.display.update()


def seed_input_overlay():
    global ACTIVE_SEED
    font_big  = get_font("ui", 36)
    font_med  = get_font("ui", 22)
    font_sm   = get_font("ui", 17)
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
        pygame.draw.rect(screen, COLORS["purpleguy"], (bx, by, bw, bh), 2)

        title = font_big.render("[ DEBUG ] Set Seed", True, COLORS["purpleguy"])
        screen.blit(title, (bx + bw//2 - title.get_width()//2, by + 18))

        hint = font_sm.render("No symbols |  Max 20 chars | ENTER to confirm  ESC to cancel", True, (140,140,160))
        screen.blit(hint, (bx + bw//2 - hint.get_width()//2, by + 66))

        field_rect = pygame.Rect(bx + 30, by + 102, bw - 60, 44)
        pygame.draw.rect(screen, (10, 10, 25), field_rect)
        pygame.draw.rect(screen, COLORS["cyan"], field_rect, 1)
        text_str  = "".join(buf)
        cursor    = "|" if (pygame.time.get_ticks() // 500) % 2 == 0 else " "
        rendered  = render_fit("ui", text_str + cursor, COLORS["white"], field_rect.w - 16, 36, min_size=16)
        screen.blit(rendered, (field_rect.x + 8, field_rect.y + (field_rect.h - rendered.get_height()) // 2))

        now_ms = pygame.time.get_ticks()
        mouse_pos = pygame.mouse.get_pos()

        confirm_surf = font_med.render("[ confirm ]", True, COLORS["green"])
        clear_surf   = font_med.render("[ clear ]",   True, COLORS["red"])
        cancel_surf  = font_med.render("[ cancel ]",  True, (160,160,160))
        confirm_rect = confirm_surf.get_rect(center=(bx + bw//4,       by + bh - 30))
        clear_rect   = clear_surf.get_rect(  center=(bx + bw//2,       by + bh - 30))
        cancel_rect  = cancel_surf.get_rect( center=(bx + 3*bw//4,     by + bh - 30))

        if confirm_rect.collidepoint(mouse_pos):
            confirm_surf = font_med.render("[ confirm ]", True, COLORS["yummers"])
        if clear_rect.collidepoint(mouse_pos):
            clear_surf = font_med.render("[ clear ]", True, COLORS["yummers"])
        if cancel_rect.collidepoint(mouse_pos):
            cancel_surf = font_med.render("[ cancel ]", True, COLORS["yummers"])

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

def draw_apple_shrink(cx, cy, size, filled):
    r = size // 2
    pts = []
    for i in range(4):
        angle = math.pi / 4 + i * math.pi / 2
        pts.append((cx + int(r * math.cos(angle)), cy + int(r * math.sin(angle))))
    if filled:
        pygame.draw.polygon(screen, (255, 140, 0), pts)
        pygame.draw.polygon(screen, (255, 200, 80), pts, 2)
        pygame.draw.circle(screen, (255, 220, 120), (cx - size // 6, cy - size // 6), max(2, size // 6))
    else:
        pygame.draw.polygon(screen, (90, 60, 10), pts, 2)

def draw_apple_dm(cx, cy, size, filled):
    r = size // 2
    pts = []
    for i in range(6):
        angle = -math.pi / 2 + i * math.pi / 3
        pts.append((cx + int(r * math.cos(angle)), cy + int(r * math.sin(angle))))
    if filled:
        pygame.draw.polygon(screen, (0, 200, 200), pts)
        pygame.draw.polygon(screen, (120, 255, 255), pts, 2)
        pygame.draw.circle(screen, (180, 255, 255), (cx - size // 6, cy - size // 6), max(2, size // 6))
    else:
        pygame.draw.polygon(screen, (20, 80, 80), pts, 2)

def draw_food_pickup(pos, shape_fn=draw_apple, size_scale=1.0):
    cx = pos[0] + CELL_SIZE // 2
    cy = pos[1] + CELL_SIZE // 2
    size = max(4, int(CELL_SIZE * size_scale))
    shape_fn(cx, cy, size, True)


def sa_success_screen(target, elapsed_ms, is_new_best, is_new_apple):
    music_manager.stop_music()
    music_manager.play_music("effect", loop=False, volume=0.7)
    font_huge = get_font("title", 110)
    font_med  = get_font("ui", 28)
    font_sm   = get_font("ui", 20)
    secs = elapsed_ms / 1000.0
    time_str = f"{int(secs // 60):02d}:{secs % 60:05.2f}"
    while True:
        draw_background()
        mouse_pos = pygame.mouse.get_pos()
        now_ms = pygame.time.get_ticks()
        lm  = settings["light_mode"]
        txt = (20, 20, 20) if lm else COLORS["white"]
        pulse = 0.5 + 0.5 * math.sin(now_ms / 300.0)
        comp_col = (int(80 + 175 * pulse), int(200 + 55 * pulse), 80)
        title_s = font_huge.render("You did it!", True, comp_col)
        screen.blit(title_s, title_s.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 210)))
        tgt_s = render_fit("title", f"Score Attack  —  Target: {target}", txt, SCREEN_WIDTH - 60, 58, min_size=24)
        screen.blit(tgt_s, tgt_s.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 120)))
        time_col = COLORS["purpleguy"] if is_new_best else txt
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
        pa_s   = render_fit("menu", "Play Again", txt, SCREEN_WIDTH - 80, 54, min_size=24)
        ch_s   = render_fit("menu", "Back to SP Mode", txt, SCREEN_WIDTH - 80, 54, min_size=24)
        mn_s   = render_fit("menu", "Main Menu", txt, SCREEN_WIDTH - 80, 54, min_size=24)
        pa_r   = pa_s.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 110))
        ch_r   = ch_s.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 175))
        mn_r   = mn_s.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 240))
        if pa_r.collidepoint(mouse_pos): pa_s = render_fit("menu", "Play Again", COLORS["green"], SCREEN_WIDTH - 80, 54, min_size=24)
        if ch_r.collidepoint(mouse_pos): ch_s = render_fit("menu", "Back to SP Mode", COLORS["cyan"], SCREEN_WIDTH - 80, 54, min_size=24)
        if mn_r.collidepoint(mouse_pos): mn_s = render_fit("menu", "Main Menu", COLORS["red"], SCREEN_WIDTH - 80, 54, min_size=24)
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
    global _earned_apples, _sa_bests, _shrink_best, _dm_best_ms
    global _pacifist_best, _trust_best, _chaos_best
    font_title = get_font("title", 60)
    font_mode  = get_font("title", 28)
    font_desc  = get_font("ui", 16)
    font_sm    = get_font("ui", 15)
    font_back  = get_font("ui", 26)
    sel = 0
    sa_sel = 0
    nav_active = False
    _joy_axis_last = {}
    NUM_COLS = 4
    col_w = SCREEN_WIDTH // NUM_COLS
    row_h = (SCREEN_HEIGHT - 100) // 2
    PAD   = 10
    HEADER_Y = 100

    def _mode_col(color):
        if not lm:
            return color
        luma = 0.299 * color[0] + 0.587 * color[1] + 0.114 * color[2]
        if luma < 170:
            return color
        return tuple(max(0, int(c * 0.55)) for c in color)

    MODES = [
        {"key": "endless",  "label": "Endless",      "color": COLORS["green"],
         "desc": ["Survive as long", "as possible."]},
        {"key": "sa",       "label": "Score Attack",  "color": COLORS["yummers"],
         "desc": ["Race to a", "target score!"]},
        {"key": "shrink",   "label": "Shrink",        "color": (255, 140, 0),
         "desc": ["Snake shrinks every 3s.", "Eat to survive."]},
        {"key": "deathmatch","label": "Deathmatch",   "color": COLORS["cyan"],
         "desc": ["Walls close in.", "Last as long as you can."]},
        {"key": "pacifist", "label": "Pacifist %",    "color": (255, 120, 120),
         "desc": ["+1 score every 3s.", "Touching food kills you."]},
        {"key": "trust",    "label": "Trust Issues",  "color": (120, 200, 255),
         "desc": ["Mash a direction", "to turn. 4 apples."]},
        {"key": "chaos",    "label": "Chaos Mode",    "color": (220, 100, 240),
         "desc": ["Certain settings", "shuffle every 10 seconds."]},
        {"key": "rewind",   "label": "Rewind",        "color": (150, 210, 255),
         "desc": ["Time travel 10s back.", "10 charges per life."]},
    ]

    while True:
        draw_background()
        mouse_pos = pygame.mouse.get_pos()
        lm  = settings["light_mode"]
        txt = (20, 20, 20) if lm else COLORS["white"]
        dim = (80, 80, 80) if lm else (140, 140, 140)

        title_s = font_title.render("Single Player", True, COLORS["green"])
        screen.blit(title_s, title_s.get_rect(center=(SCREEN_WIDTH // 2, 45)))

        back_col = COLORS["purpleguy"] if pygame.Rect(0, 0, 160, 46).collidepoint(mouse_pos) else dim
        back_s = font_back.render("< Back", True, back_col)
        back_r = back_s.get_rect(topleft=(22, 14))
        screen.blit(back_s, back_r)
        back_hit = pygame.Rect(0, 0, back_r.right + 10, 50)

        for c in range(1, NUM_COLS):
            pygame.draw.line(screen, (60, 60, 80), (c * col_w, HEADER_Y), (c * col_w, SCREEN_HEIGHT - 10), 1)
        pygame.draw.line(screen, (60, 60, 80), (0, HEADER_Y + row_h), (SCREEN_WIDTH, HEADER_Y + row_h), 1)

        cell_rects  = []
        sa_card_rects = {}
        for i, mode in enumerate(MODES):
            col = i % NUM_COLS
            row = i // NUM_COLS
            cx  = col * col_w + col_w // 2
            top = HEADER_Y + row * row_h
            cell_rect = pygame.Rect(col * col_w, top, col_w, row_h)
            cell_rects.append(cell_rect)

            disabled = mode.get("disabled", False)
            joy_sel  = (not disabled) and nav_active and sel == i
            hovering = (not disabled) and (joy_sel or cell_rect.collidepoint(mouse_pos))

            if hovering:
                hs = pygame.Surface((col_w, row_h), pygame.SRCALPHA)
                hs.fill((255, 255, 255, 10) if not lm else (0, 0, 0, 12))
                screen.blit(hs, (col * col_w, top))
            if joy_sel:
                pygame.draw.rect(screen, _mode_col(mode["color"]), (col * col_w + 3, top + 3, col_w - 6, row_h - 6), 2)

            label_s = render_fit("title", mode["label"], _mode_col(mode["color"]), col_w - 16, 28, min_size=15)
            screen.blit(label_s, label_s.get_rect(center=(cx, top + 40)))

            for di, dline in enumerate(mode["desc"]):
                ds = render_fit("ui", dline, txt if not disabled else dim, col_w - 16, 16, min_size=11)
                screen.blit(ds, ds.get_rect(center=(cx, top + 82 + di * 22)))

            if disabled:
                continue

            if mode["key"] == "endless":
                play_col = _mode_col(mode["color"]) if hovering else dim
                play_s = render_fit("menu", "[ Play ]", play_col, col_w - 16, 30, min_size=14)
                play_r = play_s.get_rect(midbottom=(cx, top + row_h - PAD))
                screen.blit(play_s, play_r)
                hi = load_high_score()
                hs_s = render_fit("ui", f"High Score: {hi}", COLORS["purpleguy"], col_w - 16, 15, min_size=11)
                screen.blit(hs_s, hs_s.get_rect(midbottom=(cx, play_r.top - 4)))

            elif mode["key"] == "sa":
                card_w, card_h = 88, 70
                gap = 8
                total_w = 3 * card_w + 2 * gap
                cx0 = cx - total_w // 2
                card_y = top + row_h - card_h - 10
                for ci, t in enumerate(SA_TARGETS):
                    ccx = cx0 + ci * (card_w + gap)
                    cr  = pygame.Rect(ccx, card_y, card_w, card_h)
                    sa_card_rects[t] = cr
                    card_hover = (joy_sel and ci == sa_sel) or cr.collidepoint(mouse_pos)
                    bg_c = (38, 38, 20) if not card_hover else (55, 50, 15)
                    if lm: bg_c = (238, 238, 238) if not card_hover else (255, 250, 215)
                    pygame.draw.rect(screen, bg_c, cr, border_radius=6)
                    pygame.draw.rect(screen, (230, 200, 0) if card_hover else (60, 60, 80), cr, 2, border_radius=6)
                    ns = get_font("ui_bold", 22, bold=True).render(str(t), True, COLORS["yummers"] if card_hover else txt)
                    screen.blit(ns, ns.get_rect(center=(ccx + card_w // 2, card_y + 18)))
                    draw_apple(ccx + card_w // 2, card_y + 42, 14, t in _earned_apples)
                    best_ms = _sa_bests.get(t, 0)
                    if best_ms > 0:
                        bs = best_ms / 1000.0
                        bstr = f"{int(bs // 60):02d}:{bs % 60:05.2f}"
                    else:
                        bstr = "—"
                    bs_s = render_fit("ui", bstr, COLORS["purpleguy"] if t in _earned_apples else dim, card_w - 6, 15, min_size=10)
                    screen.blit(bs_s, bs_s.get_rect(midbottom=(ccx + card_w // 2, card_y + card_h - 4)))

            elif mode["key"] == "shrink":
                play_col = _mode_col(mode["color"]) if hovering else dim
                play_s = render_fit("menu", "[ Play ]", play_col, col_w - 16, 30, min_size=14)
                play_r = play_s.get_rect(midbottom=(cx, top + row_h - PAD))
                screen.blit(play_s, play_r)
                sb_s = render_fit("ui", f"Best: {_shrink_best}" if _shrink_best > 0 else "No record yet",
                                   (255, 140, 0) if _shrink_best > 0 else dim, col_w - 16, 15, min_size=11)
                sb_r = sb_s.get_rect(midbottom=(cx, play_r.top - 4))
                screen.blit(sb_s, sb_r)
                draw_apple_shrink(cx, sb_r.top - 20, 22, _shrink_best > 0)

            elif mode["key"] == "deathmatch":
                play_col = _mode_col(mode["color"]) if hovering else dim
                play_s = render_fit("menu", "[ Play ]", play_col, col_w - 16, 30, min_size=14)
                play_r = play_s.get_rect(midbottom=(cx, top + row_h - PAD))
                screen.blit(play_s, play_r)
                if _dm_best_ms > 0:
                    ds2 = _dm_best_ms / 1000.0
                    dm_str = f"Best: {int(ds2 // 60):02d}:{ds2 % 60:05.2f}"
                else:
                    dm_str = "No record yet"
                db_s = render_fit("ui", dm_str, COLORS["cyan"] if _dm_best_ms > 0 else dim, col_w - 16, 15, min_size=11)
                db_r = db_s.get_rect(midbottom=(cx, play_r.top - 4))
                screen.blit(db_s, db_r)
                draw_apple_dm(cx, db_r.top - 20, 22, _dm_best_ms > 0)

            elif mode["key"] == "pacifist":
                play_col = _mode_col(mode["color"]) if hovering else dim
                play_s = render_fit("menu", "[ Play ]", play_col, col_w - 16, 30, min_size=14)
                play_r = play_s.get_rect(midbottom=(cx, top + row_h - PAD))
                screen.blit(play_s, play_r)
                pb_s = render_fit("ui", f"Best: {_pacifist_best}" if _pacifist_best > 0 else "No record yet",
                                   (255, 120, 120) if _pacifist_best > 0 else dim, col_w - 16, 15, min_size=11)
                screen.blit(pb_s, pb_s.get_rect(midbottom=(cx, play_r.top - 4)))

            elif mode["key"] == "trust":
                play_col = _mode_col(mode["color"]) if hovering else dim
                play_s = render_fit("menu", "[ Play ]", play_col, col_w - 16, 30, min_size=14)
                play_r = play_s.get_rect(midbottom=(cx, top + row_h - PAD))
                screen.blit(play_s, play_r)
                tb_s = render_fit("ui", f"Best: {_trust_best}" if _trust_best > 0 else "No record yet",
                                   (120, 200, 255) if _trust_best > 0 else dim, col_w - 16, 15, min_size=11)
                screen.blit(tb_s, tb_s.get_rect(midbottom=(cx, play_r.top - 4)))

            elif mode["key"] == "chaos":
                play_col = _mode_col(mode["color"]) if hovering else dim
                play_s = render_fit("menu", "[ Play ]", play_col, col_w - 16, 30, min_size=14)
                play_r = play_s.get_rect(midbottom=(cx, top + row_h - PAD))
                screen.blit(play_s, play_r)
                cb_s = render_fit("ui", f"Best: {_chaos_best}" if _chaos_best > 0 else "No record yet",
                                   (220, 100, 240) if _chaos_best > 0 else dim, col_w - 16, 15, min_size=11)
                screen.blit(cb_s, cb_s.get_rect(midbottom=(cx, play_r.top - 4)))

            elif mode["key"] == "rewind":
                play_col = _mode_col(mode["color"]) if hovering else dim
                play_s = render_fit("menu", "[ Play ]", play_col, col_w - 16, 30, min_size=14)
                play_r = play_s.get_rect(midbottom=(cx, top + row_h - PAD))
                screen.blit(play_s, play_r)
                rb_s = render_fit("ui", f"Best: {_rewind_best}" if _rewind_best > 0 else "No record yet",
                                   (150, 210, 255) if _rewind_best > 0 else dim, col_w - 16, 15, min_size=11)
                screen.blit(rb_s, rb_s.get_rect(midbottom=(cx, play_r.top - 4)))

        pygame.display.update()
        clock.tick(60)

        def _dispatch(k):
            music_manager.stop_music()
            if k == "endless":      return ("endless",)
            elif k == "sa":         return ("sa", SA_TARGETS[sa_sel])
            elif k == "shrink":     return ("shrink",)
            elif k == "deathmatch": return ("deathmatch",)
            elif k == "pacifist":   return ("pacifist",)
            elif k == "trust":      return ("trust",)
            elif k == "chaos":      return ("chaos",)
            elif k == "rewind":     return ("rewind",)
            return None

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type in (pygame.JOYDEVICEADDED, pygame.JOYDEVICEREMOVED):
                _refresh_joysticks()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "back"
                elif event.key == pygame.K_LEFT:
                    if nav_active and sel == 1: sa_sel = (sa_sel - 1) % 3
                    else: sel = (sel - 1) % len(MODES); nav_active = True
                elif event.key == pygame.K_RIGHT:
                    if nav_active and sel == 1: sa_sel = (sa_sel + 1) % 3
                    else: sel = (sel + 1) % len(MODES); nav_active = True
                elif event.key == pygame.K_UP:
                    sel = (sel - NUM_COLS) % len(MODES); nav_active = True
                elif event.key == pygame.K_DOWN:
                    sel = (sel + NUM_COLS) % len(MODES); nav_active = True
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    if not MODES[sel].get("disabled"):
                        result = _dispatch(MODES[sel]["key"])
                        if result: return result
            if event.type == pygame.JOYBUTTONDOWN:
                if event.button in (0, 2):
                    if not MODES[sel].get("disabled"):
                        result = _dispatch(MODES[sel]["key"])
                        if result: return result
                elif event.button == 1:
                    return "back"
            if event.type == pygame.JOYHATMOTION:
                if event.value[0] == -1:
                    if nav_active and sel == 1: sa_sel = (sa_sel - 1) % 3
                    else: sel = (sel - 1) % len(MODES); nav_active = True
                elif event.value[0] == 1:
                    if nav_active and sel == 1: sa_sel = (sa_sel + 1) % 3
                    else: sel = (sel + 1) % len(MODES); nav_active = True
                elif event.value[1] == 1:  sel = (sel - NUM_COLS) % len(MODES); nav_active = True
                elif event.value[1] == -1: sel = (sel + NUM_COLS) % len(MODES); nav_active = True
            if event.type == pygame.JOYAXISMOTION:
                prev = _joy_axis_last.get(event.axis, 0.0)
                cur  = event.value
                _joy_axis_last[event.axis] = cur
                if event.axis == 0:
                    if cur < -0.55 and prev >= -0.55:
                        if nav_active and sel == 1: sa_sel = (sa_sel - 1) % 3
                        else: sel = (sel - 1) % len(MODES); nav_active = True
                    elif cur > 0.55 and prev <= 0.55:
                        if nav_active and sel == 1: sa_sel = (sa_sel + 1) % 3
                        else: sel = (sel + 1) % len(MODES); nav_active = True
                elif event.axis == 1:
                    if cur < -0.55 and prev >= -0.55: sel = (sel - NUM_COLS) % len(MODES); nav_active = True
                    elif cur > 0.55 and prev <= 0.55: sel = (sel + NUM_COLS) % len(MODES); nav_active = True
            if event.type == pygame.MOUSEBUTTONDOWN:
                if back_hit.collidepoint(event.pos):
                    return "back"
                for i, cr in enumerate(cell_rects):
                    if cr.collidepoint(event.pos) and not MODES[i].get("disabled"):
                        k = MODES[i]["key"]
                        if k == "sa":
                            for t, tcr in sa_card_rects.items():
                                if tcr.collidepoint(event.pos):
                                    music_manager.stop_music()
                                    return ("sa", t)
                            music_manager.stop_music()
                            return ("sa", SA_TARGETS[0])
                        result = _dispatch(k)
                        if result: return result


def score_attack_game(target):
    global snake_pos, snake_body, food_pos, food_spawn, food2_pos, direction, change_to, score
    global leftover, burst1, debug_overlay_visible, _spacebar_idx
    global _earned_apples, _sa_bests
    music_manager.play_music("ingame", loop=True, volume=0.5)
    reset_single_game()
    _spacebar_idx = 0
    draw_countdown()
    tick_accum    = 0.0
    dt_ms = 1000.0 / 60.0
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
            record_game_stats(elapsed_ms, score)
            print(f"SA done! target was {target}, it took {elapsed_ms}ms, Now, its ={is_new_best} and ={is_new_apple}")
            result = sa_success_screen(target, elapsed_ms, is_new_best, is_new_apple)
            if result == "play_again":
                reset_single_game()
                music_manager.current_music = None
                music_manager.play_music("ingame", loop=True, volume=0.5)
                draw_countdown()
                tick_accum = 0.0; game_start_ms = pygame.time.get_ticks()
                dt_ms = 1000.0 / 60.0
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
                    pygame.mixer.music.pause()
                    quit_to_menu = False
                    if not settings["hardcore"]:
                        quit_to_menu = pause_menu(is_multiplayer=False, mode_label=f"SP Score Attack ({target})")
                    pygame.mixer.music.unpause()
                    if quit_to_menu: return "menu"
            elif event.type == pygame.WINDOWFOCUSLOST:
                pygame.mixer.music.pause()
                quit_to_menu = False
                if not settings["hardcore"]:
                    quit_to_menu = pause_menu(is_multiplayer=False, mode_label=f"SP Score Attack ({target})")
                pygame.mixer.music.unpause()
                if quit_to_menu: return "menu"
        if burst1["active"] and now_ms >= burst1["end_ms"]:
            burst1["active"] = False
        if leftover is not None and now_ms - leftover["born"] >= LEFTOVER_LINGER_MS:
            leftover = None
        if settings["hardcore"] and leftover is not None:
            leftover = None
        eff = DIFFICULTY * (BURST_MULTIPLIER if burst1["active"] else 1.0)
        tick_accum += eff * (dt_ms / 1000.0)
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
                food_pos = spawn_food(snake_body + ([food2_pos] if settings['double_food'] else []))
            elif settings["double_food"] and snake_pos == food2_pos:
                score += 1; ate = True
                if leftover is None and not settings["hardcore"]:
                    leftover = {"pos": spawn_food(snake_body), "born": now_ms}
                food2_pos = spawn_food(snake_body + [food_pos])
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
            record_game_stats(now_ms - game_start_ms, score)
            pixel_fill_effect()
            result = game_over_menu(is_multiplayer=False, score1=score, high_score=0)
            if result == "play_again":
                reset_single_game()
                music_manager.current_music = None
                music_manager.play_music("ingame", loop=True, volume=0.5)
                draw_countdown()
                tick_accum = 0.0; game_start_ms = pygame.time.get_ticks()
                dt_ms = 1000.0 / 60.0
                continue
            elif result == "main_menu":
                return "menu"
            else:
                pygame.quit(); sys.exit()
        draw_background()
        draw_leftover(leftover, now_ms)
        draw_snake(snake_pos, snake_body, direction, True, burst_active=burst1["active"])
        if settings["fog_of_war"]:
            draw_fog_of_war(snake_pos, direction)
        draw_food_pickup(food_pos, draw_apple, 0.95)
        if settings["double_food"]:
            draw_food_pickup(food2_pos, draw_apple, 0.75)
            pulse = 0.5 + 0.5 * math.sin(now_ms / 80.0)
            bf = get_font("ui", 22)
            bs = bf.render(f"Burst active for {remaining/1000:.1f}s", True, (int(255*pulse), 200, 0))
            screen.blit(bs, (10, 60))
        if settings["hardcore"]:
            hf = get_font("ui", 18)
            screen.blit(hf.render("HARDCORE MODE", True, (255, 40, 40)), (10, 35))
        elapsed_s = (now_ms - game_start_ms) / 1000.0
        m2 = int(elapsed_s) // 60; s2 = int(elapsed_s) % 60; cs = int((elapsed_s - int(elapsed_s)) * 100)
        hud_str = f"TARGET:  {score} / {target}   |   {m2:02d}:{s2:02d}.{cs:02d}"
        hud_s = render_fit("ui", hud_str, COLORS["yummers"], SCREEN_WIDTH - 40, 24, min_size=14)
        screen.blit(hud_s, hud_s.get_rect(center=(SCREEN_WIDTH // 2, 18)))
        if debug_overlay_visible:
            draw_debug_overlay(tick_accum)
        version_str = "NotASnake v3.5"
        if ACTIVE_SEED: version_str += f"  [S:{_seed_display()}]"
        vs = get_font("ui", 20).render(version_str, True, COLORS["purpleguy"] if ACTIVE_SEED else (140,140,140))
        screen.blit(vs, vs.get_rect(topright=(SCREEN_WIDTH - 10, 10)))
        pygame.display.update()
        fps_cap = settings["fps_limit"]
        dt_ms = min(clock.tick(fps_cap if fps_cap > 0 else 0), 100)

def shrink_game():
    global snake_pos, snake_body, food_pos, food_spawn, food2_pos, direction, change_to, score
    global leftover, burst1, debug_overlay_visible, _spacebar_idx
    global _shrink_best
    music_manager.play_heroic(volume=0.5)
    reset_single_game()
    _spacebar_idx = 0
    draw_countdown()

    SHRINK_INTERVAL_MS = 5000
    last_shrink_ms     = pygame.time.get_ticks()
    tick_accum         = 0.0
    dt_ms = 1000.0 / 60.0
    game_start_ms      = pygame.time.get_ticks()

    while True:
        now_ms = pygame.time.get_ticks()

        for event in pygame.event.get():
            music_manager.handle_event(event)
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            elif event.type in (pygame.JOYDEVICEADDED, pygame.JOYDEVICEREMOVED):
                _refresh_joysticks()
            elif event.type == pygame.JOYBUTTONDOWN and event.joy == 0:
                if _joy_is_debug_btn(event):
                    debug_overlay_visible = not debug_overlay_visible
                elif _joy_is_pause_btn(event):
                    if pause_menu(is_multiplayer=False, mode_label="Shrink"): return "menu"
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
                    if pause_menu(is_multiplayer=False, mode_label="Shrink"): return "menu"
                elif event.key == pygame.K_m:
                    if confirm_quit_to_menu(): return "menu"
            elif event.type == pygame.ACTIVEEVENT:
                if event.state == pygame.APPINPUTFOCUS and not event.gain:
                    pygame.mixer.music.pause()
                    quit_to_menu = pause_menu(is_multiplayer=False, mode_label="Shrink")
                    pygame.mixer.music.unpause()
                    if quit_to_menu: return "menu"
            elif event.type == pygame.WINDOWFOCUSLOST:
                pygame.mixer.music.pause()
                quit_to_menu = pause_menu(is_multiplayer=False, mode_label="Shrink")
                pygame.mixer.music.unpause()
                if quit_to_menu: return "menu"

        if now_ms - last_shrink_ms >= SHRINK_INTERVAL_MS:
            last_shrink_ms = now_ms
            if len(snake_body) > 1:
                snake_body.pop()
            else:
                data = load_save()
                if score > data.get("shrink_best", 0):
                    data["shrink_best"] = score
                    _shrink_best = score
                    save_save(data)
                record_game_stats(now_ms - game_start_ms, score)
                pixel_fill_effect()
                result = game_over_menu(is_multiplayer=False, score1=score, high_score=_shrink_best)
                if result == "play_again":
                    reset_single_game()
                    _spacebar_idx = 0
                    music_manager.play_heroic(volume=0.5)
                    draw_countdown()
                    tick_accum = 0.0
                    dt_ms = 1000.0 / 60.0
                    last_shrink_ms = pygame.time.get_ticks()
                    game_start_ms  = pygame.time.get_ticks()
                    continue
                elif result == "main_menu":
                    return "menu"
                else:
                    pygame.quit(); sys.exit()

        effective_difficulty = DIFFICULTY * (BURST_MULTIPLIER if burst1["active"] else 1.0)
        tick_accum += effective_difficulty * (dt_ms / 1000.0)
        if tick_accum >= 1.0:
            tick_accum -= 1.0
            opposites = {"UP": "DOWN", "DOWN": "UP", "LEFT": "RIGHT", "RIGHT": "LEFT"}
            joy_dir = _joy_direction(0)
            if joy_dir and joy_dir != opposites[direction]:
                change_to = joy_dir
            if change_to != opposites[direction]:
                direction = change_to
            mv = {"UP": (0, -CELL_SIZE), "DOWN": (0, CELL_SIZE), "LEFT": (-CELL_SIZE, 0), "RIGHT": (CELL_SIZE, 0)}
            snake_pos[0] += mv[direction][0]
            snake_pos[1] += mv[direction][1]
            snake_body.insert(0, list(snake_pos))

            ate = False
            if snake_pos == food_pos:
                score += 1; ate = True
                snake_body.append(snake_body[-1][:])
                food_pos = spawn_food(snake_body + ([food2_pos] if settings['double_food'] else []))
            elif settings["double_food"] and snake_pos == food2_pos:
                score += 1; ate = True
                snake_body.append(snake_body[-1][:])
                food2_pos = spawn_food(snake_body + [food_pos])
            if not ate:
                snake_body.pop()

        wall_kill = not settings["wrap_around"]
        game_over = (
            (wall_kill and (snake_pos[0] < 0 or snake_pos[0] >= SCREEN_WIDTH or
                            snake_pos[1] < 0 or snake_pos[1] >= SCREEN_HEIGHT)) or
            any(seg == snake_pos for seg in snake_body[1:])
        )
        if game_over:
            data = load_save()
            if score > data.get("shrink_best", 0):
                data["shrink_best"] = score
                _shrink_best = score
                save_save(data)
            record_game_stats(now_ms - game_start_ms, score)
            pixel_fill_effect()
            result = game_over_menu(is_multiplayer=False, score1=score, high_score=_shrink_best)
            if result == "play_again":
                reset_single_game()
                _spacebar_idx = 0
                music_manager.play_heroic(volume=0.5)
                draw_countdown()
                tick_accum = 0.0
                dt_ms = 1000.0 / 60.0
                last_shrink_ms = pygame.time.get_ticks()
                game_start_ms  = pygame.time.get_ticks()
                continue
            elif result == "main_menu":
                return "menu"
            else:
                pygame.quit(); sys.exit()

        draw_background()
        draw_snake(snake_pos, snake_body, direction, True, burst_active=False)
        if settings["fog_of_war"]:
            draw_fog_of_war(snake_pos, direction)
        draw_food_pickup(food_pos, draw_apple_shrink, 0.95)
        if settings["double_food"]:
            draw_food_pickup(food2_pos, draw_apple_shrink, 0.75)

        hf = get_font("ui", 22)
        time_to_shrink = max(0, SHRINK_INTERVAL_MS - (now_ms - last_shrink_ms))
        pulse = 0.5 + 0.5 * math.sin(now_ms / 120.0)
        shrink_col = (int(255 * pulse), int(140 * (1 - pulse)), 0) if time_to_shrink < 1000 else (255, 140, 0)
        hud_s = hf.render(f"Shrinks in: {time_to_shrink / 1000:.1f}s   |   Score: {score}   |   Length: {len(snake_body)}", True, shrink_col)
        screen.blit(hud_s, hud_s.get_rect(center=(SCREEN_WIDTH // 2, 18)))

        if debug_overlay_visible:
            draw_debug_overlay(tick_accum)
        show_score(1, COLORS["white"], "consolas", 20, score, None, game_start_ms=game_start_ms)
        pygame.display.update()
        fps_cap = settings["fps_limit"]
        dt_ms = min(clock.tick(fps_cap if fps_cap > 0 else 0), 100)


def deathmatch_game():
    global snake_pos, snake_body, food_pos, food_spawn, food2_pos, direction, change_to, score
    global leftover, burst1, debug_overlay_visible, _spacebar_idx
    global _dm_best_ms
    music_manager.play_heroic(volume=0.5)
    reset_single_game()
    _spacebar_idx = 0
    draw_countdown()

    SHRINK_INTERVAL_MS = 10000
    SHRINK_AMOUNT      = CELL_SIZE
    last_shrink_ms     = pygame.time.get_ticks()
    game_start_ms      = pygame.time.get_ticks()

    cols = SCREEN_WIDTH  // CELL_SIZE
    rows = SCREEN_HEIGHT // CELL_SIZE
    wall_left   = 0
    wall_top    = 0
    wall_right  = cols
    wall_bottom = rows

    tick_accum = 0.0
    dt_ms = 1000.0 / 60.0

    def _food_in_arena(occupied):
        for _ in range(500):
            fx = random.randrange(wall_left + 1, max(wall_left + 2, wall_right - 1)) * CELL_SIZE
            fy = random.randrange(wall_top  + 1, max(wall_top  + 2, wall_bottom - 1)) * CELL_SIZE
            if (fx, fy) not in occupied:
                return [fx, fy]
        return [wall_left * CELL_SIZE + CELL_SIZE, wall_top * CELL_SIZE + CELL_SIZE]

    while True:
        now_ms = pygame.time.get_ticks()

        for event in pygame.event.get():
            music_manager.handle_event(event)
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            elif event.type in (pygame.JOYDEVICEADDED, pygame.JOYDEVICEREMOVED):
                _refresh_joysticks()
            elif event.type == pygame.JOYBUTTONDOWN and event.joy == 0:
                if _joy_is_debug_btn(event):
                    debug_overlay_visible = not debug_overlay_visible
                elif _joy_is_pause_btn(event):
                    if pause_menu(is_multiplayer=False, mode_label="Deathmatch"): return "menu"
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
                    if pause_menu(is_multiplayer=False, mode_label="Deathmatch"): return "menu"
                elif event.key == pygame.K_m:
                    if confirm_quit_to_menu(): return "menu"
            elif event.type == pygame.ACTIVEEVENT:
                if event.state == pygame.APPINPUTFOCUS and not event.gain:
                    pygame.mixer.music.pause()
                    quit_to_menu = pause_menu(is_multiplayer=False, mode_label="Deathmatch")
                    pygame.mixer.music.unpause()
                    if quit_to_menu: return "menu"
            elif event.type == pygame.WINDOWFOCUSLOST:
                pygame.mixer.music.pause()
                quit_to_menu = pause_menu(is_multiplayer=False, mode_label="Deathmatch")
                pygame.mixer.music.unpause()
                if quit_to_menu: return "menu"

        if now_ms - last_shrink_ms >= SHRINK_INTERVAL_MS:
            last_shrink_ms = now_ms
            arena_w = wall_right  - wall_left
            arena_h = wall_bottom - wall_top
            if arena_w > 6 and arena_h > 6:
                wall_left   += 1
                wall_top    += 1
                wall_right  -= 1
                wall_bottom -= 1
                occupied = set(map(tuple, snake_body))
                food_pos  = _food_in_arena(occupied)
                if settings["double_food"]:
                    food2_pos = _food_in_arena(occupied | {tuple(food_pos)})

        effective_difficulty = DIFFICULTY * (BURST_MULTIPLIER if burst1["active"] else 1.0)
        tick_accum += effective_difficulty * (dt_ms / 1000.0)
        if tick_accum >= 1.0:
            tick_accum -= 1.0
            opposites = {"UP": "DOWN", "DOWN": "UP", "LEFT": "RIGHT", "RIGHT": "LEFT"}
            joy_dir = _joy_direction(0)
            if joy_dir and joy_dir != opposites[direction]:
                change_to = joy_dir
            if change_to != opposites[direction]:
                direction = change_to
            mv = {"UP": (0, -CELL_SIZE), "DOWN": (0, CELL_SIZE), "LEFT": (-CELL_SIZE, 0), "RIGHT": (CELL_SIZE, 0)}
            snake_pos[0] += mv[direction][0]
            snake_pos[1] += mv[direction][1]
            snake_body.insert(0, list(snake_pos))

            ate = False
            if snake_pos == food_pos:
                score += 1; ate = True
                occ = set(map(tuple, snake_body))
                if settings["double_food"]:
                    occ.add(tuple(food2_pos))
                food_pos = _food_in_arena(occ)
            elif settings["double_food"] and snake_pos == food2_pos:
                score += 1; ate = True
                food2_pos = _food_in_arena(set(map(tuple, snake_body)) | {tuple(food_pos)})
            if not ate:
                snake_body.pop()

        px_left   = wall_left   * CELL_SIZE
        px_top    = wall_top    * CELL_SIZE
        px_right  = wall_right  * CELL_SIZE
        px_bottom = wall_bottom * CELL_SIZE

        out_of_arena = (
            snake_pos[0] < px_left or snake_pos[0] >= px_right or
            snake_pos[1] < px_top  or snake_pos[1] >= px_bottom
        )
        game_over = out_of_arena or any(seg == snake_pos for seg in snake_body[1:])

        if game_over:
            elapsed_ms = now_ms - game_start_ms
            data = load_save()
            is_new_best = data.get("dm_best_ms", 0) == 0 or elapsed_ms > data.get("dm_best_ms", 0)
            if is_new_best:
                data["dm_best_ms"] = elapsed_ms
                _dm_best_ms = elapsed_ms
                save_save(data)
            record_game_stats(elapsed_ms, score)
            pixel_fill_effect()
            surv_s = elapsed_ms / 1000.0
            surv_str = f"{int(surv_s // 60):02d}:{surv_s % 60:05.2f}"
            if _dm_best_ms > 0:
                best_s = _dm_best_ms / 1000.0
                best_str = f"Best Survival: {int(best_s // 60):02d}:{best_s % 60:05.2f}"
            else:
                best_str = "Best Survival: —"
            result = game_over_menu(
                is_multiplayer=False, score1=score,
                score_display=f"Apples Eaten: {score}   |   Survived: {surv_str}",
                best_display=best_str, is_new_best=is_new_best,
            )
            if result == "play_again":
                reset_single_game()
                _spacebar_idx = 0
                music_manager.play_heroic(volume=0.5)
                draw_countdown()
                tick_accum = 0.0
                dt_ms = 1000.0 / 60.0
                last_shrink_ms = pygame.time.get_ticks()
                game_start_ms  = pygame.time.get_ticks()
                wall_left = 0; wall_top = 0
                wall_right = cols; wall_bottom = rows
                continue
            elif result == "main_menu":
                return "menu"
            else:
                pygame.quit(); sys.exit()

        draw_background()

        danger_pulse = 0.5 + 0.5 * math.sin(now_ms / 200.0)
        wall_col = (int(80 + 175 * danger_pulse), int(30 * danger_pulse), int(30 * danger_pulse))
        pygame.draw.rect(screen, wall_col, (px_left, px_top, px_right - px_left, CELL_SIZE), 0)
        pygame.draw.rect(screen, wall_col, (px_left, px_bottom - CELL_SIZE, px_right - px_left, CELL_SIZE), 0)
        pygame.draw.rect(screen, wall_col, (px_left, px_top, CELL_SIZE, px_bottom - px_top), 0)
        pygame.draw.rect(screen, wall_col, (px_right - CELL_SIZE, px_top, CELL_SIZE, px_bottom - px_top), 0)

        draw_snake(snake_pos, snake_body, direction, True, burst_active=False)
        if settings["fog_of_war"]:
            draw_fog_of_war(snake_pos, direction)

        draw_food_pickup(food_pos, draw_apple_dm, 0.95)
        if settings["double_food"]:
            draw_food_pickup(food2_pos, draw_apple_dm, 0.75)

        elapsed_s  = (now_ms - game_start_ms) / 1000.0
        m2 = int(elapsed_s) // 60; s2 = int(elapsed_s) % 60; cs = int((elapsed_s - int(elapsed_s)) * 100)
        time_to_shrink = max(0, SHRINK_INTERVAL_MS - (now_ms - last_shrink_ms))
        arena_w = wall_right - wall_left
        hf = get_font("ui", 22)
        shrink_col = (int(255 * danger_pulse), 60, 60) if time_to_shrink < 1500 else COLORS["cyan"]
        hud_text = f"DEATHMATCH  |  {m2:02d}:{s2:02d}.{cs:02d}  |  Score: {score}  |  Shrinks in: {time_to_shrink / 1000:.1f}s"
        hud_s = render_fit("ui", hud_text, shrink_col, SCREEN_WIDTH - 260, 22, min_size=14)
        screen.blit(hud_s, hud_s.get_rect(center=(SCREEN_WIDTH // 2, 18)))

        version_str = "NotASnake v3.5  [DEATHMATCH]"
        vs = get_font("ui", 18).render(version_str, True, COLORS["cyan"])
        screen.blit(vs, vs.get_rect(topright=(SCREEN_WIDTH - 10, 10)))

        if debug_overlay_visible:
            draw_debug_overlay(tick_accum)
        pygame.display.update()
        fps_cap = settings["fps_limit"]
        dt_ms = min(clock.tick(fps_cap if fps_cap > 0 else 0), 100)


def pacifist_percent_game():
    global snake_pos, snake_body, direction, change_to, score
    global debug_overlay_visible, _spacebar_idx, _pacifist_best
    music_manager.play_heroic(volume=0.5)
    reset_single_game()
    score = 0
    _spacebar_idx = 0
    draw_countdown()

    PACIFIST_TICK_MS        = 3000
    HAZARD_GROW_INTERVAL_MS = 12000
    MAX_HAZARDS             = 100

    hazards       = [spawn_food(snake_body)]
    last_tick_ms  = pygame.time.get_ticks()
    last_grow_ms  = pygame.time.get_ticks()
    tick_accum    = 0.0
    dt_ms = 1000.0 / 60.0
    game_start_ms = pygame.time.get_ticks()

    while True:
        now_ms = pygame.time.get_ticks()

        for event in pygame.event.get():
            music_manager.handle_event(event)
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            elif event.type in (pygame.JOYDEVICEADDED, pygame.JOYDEVICEREMOVED):
                _refresh_joysticks()
            elif event.type == pygame.JOYBUTTONDOWN and event.joy == 0:
                if _joy_is_debug_btn(event):
                    debug_overlay_visible = not debug_overlay_visible
                elif _joy_is_pause_btn(event):
                    if pause_menu(is_multiplayer=False, mode_label="Pacifist Percent"): return "menu"
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
                    if pause_menu(is_multiplayer=False, mode_label="Pacifist Percent"): return "menu"
                elif event.key == pygame.K_m:
                    if confirm_quit_to_menu(): return "menu"
            elif event.type == pygame.ACTIVEEVENT:
                if event.state == pygame.APPINPUTFOCUS and not event.gain:
                    pygame.mixer.music.pause()
                    quit_to_menu = pause_menu(is_multiplayer=False, mode_label="Pacifist Percent")
                    pygame.mixer.music.unpause()
                    if quit_to_menu: return "menu"
            elif event.type == pygame.WINDOWFOCUSLOST:
                pygame.mixer.music.pause()
                quit_to_menu = pause_menu(is_multiplayer=False, mode_label="Pacifist Percent")
                pygame.mixer.music.unpause()
                if quit_to_menu: return "menu"

        if now_ms - last_tick_ms >= PACIFIST_TICK_MS:
            last_tick_ms = now_ms
            score += 1

        if len(hazards) < MAX_HAZARDS and now_ms - last_grow_ms >= HAZARD_GROW_INTERVAL_MS:
            last_grow_ms = now_ms
            hazards.append(spawn_food(snake_body + hazards))

        tick_accum += DIFFICULTY * (dt_ms / 1000.0)
        if tick_accum >= 1.0:
            tick_accum -= 1.0
            opposites = {"UP": "DOWN", "DOWN": "UP", "LEFT": "RIGHT", "RIGHT": "LEFT"}
            joy_dir = _joy_direction(0)
            if joy_dir and joy_dir != opposites[direction]:
                change_to = joy_dir
            if change_to != opposites[direction]:
                direction = change_to
            mv = {"UP": (0, -CELL_SIZE), "DOWN": (0, CELL_SIZE), "LEFT": (-CELL_SIZE, 0), "RIGHT": (CELL_SIZE, 0)}
            snake_pos[0] += mv[direction][0]
            snake_pos[1] += mv[direction][1]
            if settings["wrap_around"]:
                gw = (SCREEN_WIDTH  // CELL_SIZE) * CELL_SIZE
                gh = (SCREEN_HEIGHT // CELL_SIZE) * CELL_SIZE
                if snake_pos[0] < 0:      snake_pos[0] = gw - CELL_SIZE
                elif snake_pos[0] >= gw:  snake_pos[0] = 0
                if snake_pos[1] < 0:      snake_pos[1] = gh - CELL_SIZE
                elif snake_pos[1] >= gh:  snake_pos[1] = 0
            snake_body.insert(0, list(snake_pos))
            snake_body.pop()

        wall_kill = not settings["wrap_around"]
        game_over = (
            (wall_kill and (snake_pos[0] < 0 or snake_pos[0] >= SCREEN_WIDTH or
                            snake_pos[1] < 0 or snake_pos[1] >= SCREEN_HEIGHT)) or
            any(seg == snake_pos for seg in snake_body[1:]) or
            any(tuple(snake_pos) == tuple(h) for h in hazards)
        )
        if game_over:
            data = load_save()
            if score > data.get("pacifist_best", 0):
                data["pacifist_best"] = score
                _pacifist_best = score
                save_save(data)
            record_game_stats(now_ms - game_start_ms, 0)
            pixel_fill_effect()
            result = game_over_menu(is_multiplayer=False, score1=score, high_score=_pacifist_best)
            if result == "play_again":
                reset_single_game()
                score = 0
                _spacebar_idx = 0
                music_manager.play_heroic(volume=0.5)
                draw_countdown()
                hazards       = [spawn_food(snake_body)]
                tick_accum    = 0.0
                dt_ms = 1000.0 / 60.0
                last_tick_ms  = pygame.time.get_ticks()
                last_grow_ms  = pygame.time.get_ticks()
                game_start_ms = pygame.time.get_ticks()
                continue
            elif result == "main_menu":
                return "menu"
            else:
                pygame.quit(); sys.exit()

        draw_background()
        draw_snake(snake_pos, snake_body, direction, True, burst_active=False)
        if settings["fog_of_war"]:
            draw_fog_of_war(snake_pos, direction)
        for hx, hy in hazards:
            pygame.draw.rect(screen, (200, 40, 40), pygame.Rect(hx, hy, CELL_SIZE, CELL_SIZE))
            pygame.draw.rect(screen, (255, 120, 120), pygame.Rect(hx, hy, CELL_SIZE, CELL_SIZE), 1)

        time_to_tick = max(0, PACIFIST_TICK_MS - (now_ms - last_tick_ms))
        hud_str = f"PACIFIST PERCENT  |  Score: {score}  |  Next point in {time_to_tick / 1000:.1f}s  |  Hazards: {len(hazards)}"
        hud_s = render_fit("ui", hud_str, (255, 120, 120), SCREEN_WIDTH - 260, 22, min_size=14)
        screen.blit(hud_s, hud_s.get_rect(center=(SCREEN_WIDTH // 2, 18)))

        if debug_overlay_visible:
            draw_debug_overlay(tick_accum)
        pygame.display.update()
        fps_cap = settings["fps_limit"]
        dt_ms = min(clock.tick(fps_cap if fps_cap > 0 else 0), 100)


def trust_issues_game():
    global snake_pos, snake_body, direction, change_to, score
    global debug_overlay_visible, _spacebar_idx, _trust_best
    music_manager.play_heroic(volume=0.5)
    reset_single_game()
    score = 0
    _spacebar_idx = 0
    draw_countdown()

    MASH_REQUIRED = 4
    MASH_DECAY_MS = 500
    FOOD_COUNT    = 4
    opposites = {"UP": "DOWN", "DOWN": "UP", "LEFT": "RIGHT", "RIGHT": "LEFT"}

    food_list = []
    for _ in range(FOOD_COUNT):
        food_list.append(spawn_food(snake_body + food_list))

    charge_dir     = [None]
    charge_count   = [0]
    charge_last_ms = [0]
    last_joy_dir   = [None]

    def _try_charge(pressed_dir, now_ms):
        global change_to
        if pressed_dir == direction:
            return False
        if pressed_dir == opposites[direction]:
            charge_dir[0]   = None
            charge_count[0] = 0
            return False
        if pressed_dir == charge_dir[0] and now_ms - charge_last_ms[0] <= MASH_DECAY_MS:
            charge_count[0] += 1
        else:
            charge_dir[0]   = pressed_dir
            charge_count[0] = 1
        charge_last_ms[0] = now_ms
        if charge_count[0] >= MASH_REQUIRED:
            change_to       = pressed_dir
            charge_dir[0]   = None
            charge_count[0] = 0
            return True
        return False

    def _spacebar_attempt(now_ms):
        global _spacebar_idx
        guard = 0
        while _SPACEBAR_CYCLE[_spacebar_idx % len(_SPACEBAR_CYCLE)] == direction and guard < len(_SPACEBAR_CYCLE):
            _spacebar_idx += 1
            guard += 1
        pressed_dir = _SPACEBAR_CYCLE[_spacebar_idx % len(_SPACEBAR_CYCLE)]
        if _try_charge(pressed_dir, now_ms):
            _spacebar_idx += 1

    tick_accum    = 0.0
    dt_ms = 1000.0 / 60.0
    game_start_ms = pygame.time.get_ticks()

    while True:
        now_ms = pygame.time.get_ticks()

        for event in pygame.event.get():
            music_manager.handle_event(event)
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            elif event.type in (pygame.JOYDEVICEADDED, pygame.JOYDEVICEREMOVED):
                _refresh_joysticks()
            elif event.type == pygame.JOYBUTTONDOWN and event.joy == 0:
                if _joy_is_debug_btn(event):
                    debug_overlay_visible = not debug_overlay_visible
                elif _joy_is_pause_btn(event):
                    if pause_menu(is_multiplayer=False, mode_label="Trust Issues"): return "menu"
                elif settings["control_scheme"] == "spacebar" or not _joysticks:
                    if _joy_x_pressed(event, 0):
                        _spacebar_attempt(now_ms)
            elif event.type == pygame.KEYDOWN:
                if settings["control_scheme"] == "spacebar":
                    if event.key == pygame.K_SPACE:
                        _spacebar_attempt(now_ms)
                else:
                    kd = get_key_directions()
                    if event.key in kd:
                        _try_charge(kd[event.key], now_ms)
                if event.key == pygame.K_F5:
                    debug_overlay_visible = not debug_overlay_visible
                elif event.key == pygame.K_ESCAPE:
                    if pause_menu(is_multiplayer=False, mode_label="Trust Issues"): return "menu"
                elif event.key == pygame.K_m:
                    if confirm_quit_to_menu(): return "menu"
            elif event.type == pygame.ACTIVEEVENT:
                if event.state == pygame.APPINPUTFOCUS and not event.gain:
                    pygame.mixer.music.pause()
                    quit_to_menu = pause_menu(is_multiplayer=False, mode_label="Trust Issues")
                    pygame.mixer.music.unpause()
                    if quit_to_menu: return "menu"
            elif event.type == pygame.WINDOWFOCUSLOST:
                pygame.mixer.music.pause()
                quit_to_menu = pause_menu(is_multiplayer=False, mode_label="Trust Issues")
                pygame.mixer.music.unpause()
                if quit_to_menu: return "menu"

        joy_dir = _joy_direction(0)
        if joy_dir and joy_dir != last_joy_dir[0]:
            _try_charge(joy_dir, now_ms)
        last_joy_dir[0] = joy_dir

        if charge_dir[0] is not None and now_ms - charge_last_ms[0] > MASH_DECAY_MS:
            charge_dir[0]   = None
            charge_count[0] = 0

        tick_accum += DIFFICULTY * (dt_ms / 1000.0)
        if tick_accum >= 1.0:
            tick_accum -= 1.0
            direction = change_to
            mv = {"UP": (0, -CELL_SIZE), "DOWN": (0, CELL_SIZE), "LEFT": (-CELL_SIZE, 0), "RIGHT": (CELL_SIZE, 0)}
            snake_pos[0] += mv[direction][0]
            snake_pos[1] += mv[direction][1]
            if settings["wrap_around"]:
                gw = (SCREEN_WIDTH  // CELL_SIZE) * CELL_SIZE
                gh = (SCREEN_HEIGHT // CELL_SIZE) * CELL_SIZE
                if snake_pos[0] < 0:      snake_pos[0] = gw - CELL_SIZE
                elif snake_pos[0] >= gw:  snake_pos[0] = 0
                if snake_pos[1] < 0:      snake_pos[1] = gh - CELL_SIZE
                elif snake_pos[1] >= gh:  snake_pos[1] = 0
            snake_body.insert(0, list(snake_pos))

            ate_idx = None
            for i, f in enumerate(food_list):
                if snake_pos == f:
                    ate_idx = i
                    break
            if ate_idx is not None:
                score += 1
                food_list[ate_idx] = spawn_food(snake_body + food_list)
            else:
                snake_body.pop()

        wall_kill = not settings["wrap_around"]
        game_over = (
            (wall_kill and (snake_pos[0] < 0 or snake_pos[0] >= SCREEN_WIDTH or
                            snake_pos[1] < 0 or snake_pos[1] >= SCREEN_HEIGHT)) or
            any(seg == snake_pos for seg in snake_body[1:])
        )
        if game_over:
            data = load_save()
            if score > data.get("trust_best", 0):
                data["trust_best"] = score
                _trust_best = score
                save_save(data)
            record_game_stats(now_ms - game_start_ms, score)
            pixel_fill_effect()
            result = game_over_menu(is_multiplayer=False, score1=score, high_score=_trust_best)
            if result == "play_again":
                reset_single_game()
                score = 0
                _spacebar_idx = 0
                music_manager.play_heroic(volume=0.5)
                draw_countdown()
                food_list = []
                for _ in range(FOOD_COUNT):
                    food_list.append(spawn_food(snake_body + food_list))
                charge_dir[0] = None; charge_count[0] = 0; last_joy_dir[0] = None
                tick_accum    = 0.0
                dt_ms = 1000.0 / 60.0
                game_start_ms = pygame.time.get_ticks()
                continue
            elif result == "main_menu":
                return "menu"
            else:
                pygame.quit(); sys.exit()

        draw_background()
        draw_snake(snake_pos, snake_body, direction, True, burst_active=False)
        if settings["fog_of_war"]:
            draw_fog_of_war(snake_pos, direction)
        for fx, fy in food_list:
            draw_food_pickup((fx, fy), draw_apple, 0.9)

        if charge_dir[0]:
            pips = "".join("#" if i < charge_count[0] else "." for i in range(MASH_REQUIRED))
            charge_str = f"Charging {charge_dir[0]}: [{pips}]"
        else:
            charge_str = "Mash a direction to charge a turn"
        hud_str = f"TRUST ISSUES  |  Score: {score}  |  {charge_str}"
        hud_s = render_fit("ui", hud_str, COLORS["cyan"], SCREEN_WIDTH - 260, 22, min_size=14)
        screen.blit(hud_s, hud_s.get_rect(center=(SCREEN_WIDTH // 2, 18)))

        if debug_overlay_visible:
            draw_debug_overlay(tick_accum)
        pygame.display.update()
        fps_cap = settings["fps_limit"]
        dt_ms = min(clock.tick(fps_cap if fps_cap > 0 else 0), 100)


_CHAOS_POOL = {
    "grid_opacity":   [0, 127, 255],
    "wrap_around":    [True, False],
    "control_scheme": ["wasd_arrows", "ijkl", "arrows_only", "spacebar"],
    "fps_limit":      [30, 60, 120, 0],
}
_CHAOS_LABELS = {
    "grid_opacity":   "Grid Lines",
    "wrap_around":    "Wrap-Around",
    "control_scheme": "Controls",
    "fps_limit":      "FPS Cap",
}

def _chaos_value_str(key, val):
    if key == "grid_opacity":
        return {0: "OFF", 127: "50%", 255: "100%"}[val]
    if key == "wrap_around":
        return "ON" if val else "OFF"
    if key == "control_scheme":
        return {"wasd_arrows": "WASD+Arrows", "ijkl": "IJKL",
                "arrows_only": "Arrows only", "spacebar": "Wildcard"}[val]
    if key == "fps_limit":
        return "Unlim." if val == 0 else f"{val} FPS"
    return str(val)

def chaos_mode_game():
    global snake_pos, snake_body, food_pos, food_spawn, food2_pos, direction, change_to, score
    global leftover, burst1, debug_overlay_visible, _spacebar_idx, _chaos_best
    snapshot = dict(settings)
    try:
        music_manager.play_heroic(volume=0.5)
        reset_single_game()
        score = 0
        _spacebar_idx = 0
        draw_countdown()

        CHAOS_INTERVAL_MS = 10000
        last_chaos_ms   = pygame.time.get_ticks()
        game_start_ms   = pygame.time.get_ticks()
        tick_accum      = 0.0
        dt_ms = 1000.0 / 60.0
        banner_text     = ""
        banner_until_ms = 0

        def _reroll():
            nonlocal banner_text, banner_until_ms
            keys = random.sample(list(_CHAOS_POOL.keys()), 2)
            changes = []
            for k in keys:
                cur = settings[k]
                choices = [v for v in _CHAOS_POOL[k] if v != cur]
                new_val = random.choice(choices) if choices else cur
                settings[k] = new_val
                changes.append(f"{_CHAOS_LABELS[k]} -> {_chaos_value_str(k, new_val)}")
            banner_text = "CHAOS: " + "  |  ".join(changes)
            banner_until_ms = pygame.time.get_ticks() + 2500

        while True:
            now_ms = pygame.time.get_ticks()

            for event in pygame.event.get():
                music_manager.handle_event(event)
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                elif event.type in (pygame.JOYDEVICEADDED, pygame.JOYDEVICEREMOVED):
                    _refresh_joysticks()
                elif event.type == pygame.JOYBUTTONDOWN and event.joy == 0:
                    if _joy_is_debug_btn(event):
                        debug_overlay_visible = not debug_overlay_visible
                    elif _joy_is_pause_btn(event):
                        if pause_menu(is_multiplayer=False, mode_label="Chaos Mode"):
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
                        kd = get_key_directions()
                        if event.key in kd: change_to = kd[event.key]
                    if event.key == pygame.K_F5:
                        debug_overlay_visible = not debug_overlay_visible
                    elif event.key == pygame.K_ESCAPE:
                        if pause_menu(is_multiplayer=False, mode_label="Chaos Mode"):
                            return "menu"
                    elif event.key == pygame.K_m:
                        if confirm_quit_to_menu():
                            return "menu"
                elif event.type == pygame.ACTIVEEVENT:
                    if event.state == pygame.APPINPUTFOCUS and not event.gain:
                        pygame.mixer.music.pause()
                        quit_to_menu = pause_menu(is_multiplayer=False, mode_label="Chaos Mode")
                        pygame.mixer.music.unpause()
                        if quit_to_menu:
                            return "menu"
                elif event.type == pygame.WINDOWFOCUSLOST:
                    pygame.mixer.music.pause()
                    quit_to_menu = pause_menu(is_multiplayer=False, mode_label="Chaos Mode")
                    pygame.mixer.music.unpause()
                    if quit_to_menu:
                        return "menu"

            if now_ms - last_chaos_ms >= CHAOS_INTERVAL_MS:
                last_chaos_ms = now_ms
                _reroll()

            effective_difficulty = DIFFICULTY * (BURST_MULTIPLIER if burst1["active"] else 1.0)
            tick_accum += effective_difficulty * (dt_ms / 1000.0)
            if tick_accum >= 1.0:
                tick_accum -= 1.0
                opposites = {"UP": "DOWN", "DOWN": "UP", "LEFT": "RIGHT", "RIGHT": "LEFT"}
                joy_dir = _joy_direction(0)
                if joy_dir and joy_dir != opposites[direction]:
                    change_to = joy_dir
                if change_to != opposites[direction]:
                    direction = change_to
                mv = {"UP": (0, -CELL_SIZE), "DOWN": (0, CELL_SIZE), "LEFT": (-CELL_SIZE, 0), "RIGHT": (CELL_SIZE, 0)}
                snake_pos[0] += mv[direction][0]
                snake_pos[1] += mv[direction][1]
                if settings["wrap_around"]:
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
                    food_pos = spawn_food(snake_body + ([food2_pos] if settings['double_food'] else []))
                elif settings["double_food"] and snake_pos == food2_pos:
                    score += 1; ate = True
                    food2_pos = spawn_food(snake_body + [food_pos])
                if not ate:
                    snake_body.pop()

            wall_kill = not settings["wrap_around"]
            game_over = (
                (wall_kill and (snake_pos[0] < 0 or snake_pos[0] >= SCREEN_WIDTH or
                                snake_pos[1] < 0 or snake_pos[1] >= SCREEN_HEIGHT)) or
                any(seg == snake_pos for seg in snake_body[1:])
            )
            if game_over:
                data = load_save()
                if score > data.get("chaos_best", 0):
                    data["chaos_best"] = score
                    _chaos_best = score
                    save_save(data)
                record_game_stats(now_ms - game_start_ms, score)
                pixel_fill_effect()
                result = game_over_menu(is_multiplayer=False, score1=score, high_score=_chaos_best)
                if result == "play_again":
                    settings.update(snapshot)
                    reset_single_game()
                    score = 0
                    _spacebar_idx = 0
                    music_manager.play_heroic(volume=0.5)
                    draw_countdown()
                    tick_accum    = 0.0
                    dt_ms = 1000.0 / 60.0
                    last_chaos_ms = pygame.time.get_ticks()
                    game_start_ms = pygame.time.get_ticks()
                    banner_text   = ""
                    continue
                elif result == "main_menu":
                    return "menu"
                else:
                    pygame.quit(); sys.exit()

            draw_background()
            draw_leftover(leftover, now_ms)
            draw_snake(snake_pos, snake_body, direction, True, burst_active=burst1["active"])
            if settings["fog_of_war"]:
                draw_fog_of_war(snake_pos, direction)
            draw_food_pickup(food_pos, draw_apple, 0.95)
            if settings["double_food"]:
                draw_food_pickup(food2_pos, draw_apple, 0.75)

            pulse = 0.5 + 0.5 * math.sin(now_ms / 150.0)
            title_col = (int(180 + 75 * pulse), int(60 * pulse), int(200 + 55 * pulse))
            time_to_chaos = max(0, CHAOS_INTERVAL_MS - (now_ms - last_chaos_ms))
            hud_str = f"CHAOS MODE  |  Score: {score}  |  Next shuffle in {time_to_chaos / 1000:.1f}s"
            hud_s = render_fit("ui", hud_str, title_col, SCREEN_WIDTH - 260, 22, min_size=14)
            screen.blit(hud_s, hud_s.get_rect(center=(SCREEN_WIDTH // 2, 18)))

            if banner_text and now_ms < banner_until_ms:
                bs = render_fit("ui_bold", banner_text, COLORS["yummers"], SCREEN_WIDTH - 40, 26, min_size=14, bold=True)
                screen.blit(bs, bs.get_rect(center=(SCREEN_WIDTH // 2, 54)))

            if debug_overlay_visible:
                draw_debug_overlay(tick_accum)
            pygame.display.update()
            fps_cap = settings["fps_limit"]
            dt_ms = min(clock.tick(fps_cap if fps_cap > 0 else 0), 100)
    finally:
        settings.update(snapshot)


def rewind_game():
    global snake_pos, snake_body, food_pos, food_spawn, food2_pos, direction, change_to, score
    global leftover, burst1, debug_overlay_visible, _spacebar_idx, _rewind_best
    music_manager.play_heroic(volume=0.5)
    reset_single_game()
    score = 0
    _spacebar_idx = 0
    draw_countdown()
    _tip_popup("Rewind Mode", [
        "Press R (or controller button 4) to rewind ~10 seconds back.",
        "You get 10 charges per life. Short cooldown between uses.",
        "Rewind only works once the run has been going for a bit.",
    ], tip_key="rewind_mode")
    if settings["control_scheme"] == "spacebar":
        _tip_popup("Wildcard Controls", [
            "One button turns you: Right -> Down -> Left -> Up, in that order.",
            "Each press advances the cycle by one step.",
            "Plan your turns ahead, you can't skip or reverse the cycle.",
        ], tip_key="wildcard_controls")

    REWIND_WINDOW_MS  = 10000
    SNAPSHOT_EVERY_MS = 100
    MAX_CHARGES       = 10
    REWIND_COOLDOWN_MS = 2500

    history        = []
    charges        = MAX_CHARGES
    flash_until_ms  = 0
    last_rewind_ms  = -REWIND_COOLDOWN_MS
    last_snap_ms   = pygame.time.get_ticks()
    tick_accum     = 0.0
    dt_ms          = 1000.0 / 60.0
    game_start_ms  = pygame.time.get_ticks()

    def _do_rewind(now_ms):
        nonlocal history, charges, flash_until_ms, last_rewind_ms
        global snake_pos, snake_body, direction, change_to, score, burst1, _spacebar_idx
        if charges <= 0 or not history:
            return
        if now_ms - game_start_ms < REWIND_WINDOW_MS:
            return
        if now_ms - last_rewind_ms < REWIND_COOLDOWN_MS:
            return
        target = history[0]
        snake_pos  = list(target["pos"])
        snake_body = [list(seg) for seg in target["body"]]
        direction  = target["dir"]
        change_to  = direction
        score      = target["score"]
        burst1["active"] = target["burst_active"]
        burst1["end_ms"] = target["burst_end_ms"]
        if settings["control_scheme"] == "spacebar":
            _spacebar_idx = target.get("spacebar_idx", _spacebar_idx)
        charges -= 1
        history = []
        last_rewind_ms = now_ms
        flash_until_ms = now_ms + 350

    while True:
        now_ms = pygame.time.get_ticks()

        for event in pygame.event.get():
            music_manager.handle_event(event)
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            elif event.type in (pygame.JOYDEVICEADDED, pygame.JOYDEVICEREMOVED):
                _refresh_joysticks()
            elif event.type == pygame.JOYBUTTONDOWN and event.joy == 0:
                if _joy_is_debug_btn(event):
                    debug_overlay_visible = not debug_overlay_visible
                elif _joy_is_pause_btn(event):
                    if pause_menu(is_multiplayer=False, mode_label="Rewind"): return "menu"
                elif event.button == 4:
                    _do_rewind(now_ms)
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
                if event.key == pygame.K_r:
                    _do_rewind(now_ms)
                elif event.key == pygame.K_F5:
                    debug_overlay_visible = not debug_overlay_visible
                elif event.key == pygame.K_ESCAPE:
                    if pause_menu(is_multiplayer=False, mode_label="Rewind"): return "menu"
                elif event.key == pygame.K_m:
                    if confirm_quit_to_menu(): return "menu"
            elif event.type == pygame.ACTIVEEVENT:
                if event.state == pygame.APPINPUTFOCUS and not event.gain:
                    pygame.mixer.music.pause()
                    quit_to_menu = pause_menu(is_multiplayer=False, mode_label="Rewind")
                    pygame.mixer.music.unpause()
                    if quit_to_menu: return "menu"
            elif event.type == pygame.WINDOWFOCUSLOST:
                pygame.mixer.music.pause()
                quit_to_menu = pause_menu(is_multiplayer=False, mode_label="Rewind")
                pygame.mixer.music.unpause()
                if quit_to_menu: return "menu"

        if burst1["active"] and now_ms >= burst1["end_ms"]:
            burst1["active"] = False
        if leftover is not None and now_ms - leftover["born"] >= LEFTOVER_LINGER_MS:
            leftover = None

        if now_ms - last_snap_ms >= SNAPSHOT_EVERY_MS:
            last_snap_ms = now_ms
            history.append({
                "t":    now_ms,
                "pos":  list(snake_pos),
                "body": [list(seg) for seg in snake_body],
                "dir":  direction,
                "spacebar_idx": _spacebar_idx,
                "score": score,
                "burst_active": burst1["active"],
                "burst_end_ms": burst1["end_ms"],
            })
            cutoff = now_ms - REWIND_WINDOW_MS
            while len(history) > 1 and history[0]["t"] < cutoff:
                history.pop(0)

        effective_difficulty = DIFFICULTY * (BURST_MULTIPLIER if burst1["active"] else 1.0)
        tick_accum += effective_difficulty * (dt_ms / 1000.0)
        if tick_accum >= 1.0:
            tick_accum -= 1.0
            opposites = {"UP": "DOWN", "DOWN": "UP", "LEFT": "RIGHT", "RIGHT": "LEFT"}
            joy_dir = _joy_direction(0)
            if joy_dir and joy_dir != opposites[direction]:
                change_to = joy_dir
            if change_to != opposites[direction]:
                direction = change_to
            mv = {"UP": (0, -CELL_SIZE), "DOWN": (0, CELL_SIZE), "LEFT": (-CELL_SIZE, 0), "RIGHT": (CELL_SIZE, 0)}
            snake_pos[0] += mv[direction][0]
            snake_pos[1] += mv[direction][1]
            if settings["wrap_around"]:
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
                if leftover is None:
                    leftover = {"pos": spawn_food(snake_body), "born": now_ms}
                food_pos = spawn_food(snake_body + ([food2_pos] if settings['double_food'] else []))
            elif settings["double_food"] and snake_pos == food2_pos:
                score += 1; ate = True
                if leftover is None:
                    leftover = {"pos": spawn_food(snake_body), "born": now_ms}
                food2_pos = spawn_food(snake_body + [food_pos])
            if not ate:
                snake_body.pop()

            if leftover is not None and snake_pos == leftover["pos"]:
                burst1["active"] = True; burst1["end_ms"] = now_ms + BURST_DURATION_MS
                leftover = None

        wall_kill = not settings["wrap_around"]
        game_over = (
            (wall_kill and (snake_pos[0] < 0 or snake_pos[0] >= SCREEN_WIDTH or
                            snake_pos[1] < 0 or snake_pos[1] >= SCREEN_HEIGHT)) or
            any(seg == snake_pos for seg in snake_body[1:])
        )
        if game_over:
            data = load_save()
            if score > data.get("rewind_best", 0):
                data["rewind_best"] = score
                _rewind_best = score
                save_save(data)
            record_game_stats(now_ms - game_start_ms, score)
            pixel_fill_effect()
            result = game_over_menu(is_multiplayer=False, score1=score, high_score=_rewind_best)
            if result == "play_again":
                reset_single_game()
                score = 0
                _spacebar_idx = 0
                music_manager.play_heroic(volume=0.5)
                draw_countdown()
                history       = []
                charges       = MAX_CHARGES
                last_rewind_ms = -REWIND_COOLDOWN_MS
                tick_accum    = 0.0
                dt_ms         = 1000.0 / 60.0
                last_snap_ms  = pygame.time.get_ticks()
                game_start_ms = pygame.time.get_ticks()
                continue
            elif result == "main_menu":
                return "menu"
            else:
                pygame.quit(); sys.exit()

        draw_background()
        draw_leftover(leftover, now_ms)
        draw_snake(snake_pos, snake_body, direction, True, burst_active=burst1["active"])
        if settings["fog_of_war"]:
            draw_fog_of_war(snake_pos, direction)
        draw_food_pickup(food_pos, draw_apple, 0.95)
        if settings["double_food"]:
            draw_food_pickup(food2_pos, draw_apple, 0.75)

        if burst1["active"]:
            remaining = max(0, burst1["end_ms"] - now_ms)
            pulse = 0.5 + 0.5 * math.sin(now_ms / 80.0)
            bf = get_font("ui", 22)
            bs = bf.render(f"Burst active for {remaining/1000:.1f}s", True, (int(255*pulse), 200, 0))
            screen.blit(bs, (10, 60))

        if now_ms < flash_until_ms:
            flash_frac = (flash_until_ms - now_ms) / 350.0
            fs = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            fs.fill((120, 200, 255, int(90 * flash_frac)))
            screen.blit(fs, (0, 0))

        pips = "".join("<" if i < charges else "." for i in range(MAX_CHARGES))
        if now_ms - game_start_ms < REWIND_WINDOW_MS:
            ready_str = f"ready in {(REWIND_WINDOW_MS - (now_ms - game_start_ms)) / 1000:.1f}s"
        elif now_ms - last_rewind_ms < REWIND_COOLDOWN_MS:
            ready_str = f"cooldown {(REWIND_COOLDOWN_MS - (now_ms - last_rewind_ms)) / 1000:.1f}s"
        else:
            ready_str = "R to rewind"
        hud_str = f"REWIND  |  Score: {score}  |  Charges [{pips}]  |  {ready_str} {REWIND_WINDOW_MS//1000}s"
        hud_s = render_fit("ui", hud_str, (150, 210, 255), SCREEN_WIDTH - 260, 22, min_size=14)
        screen.blit(hud_s, hud_s.get_rect(center=(SCREEN_WIDTH // 2, 18)))

        if debug_overlay_visible:
            draw_debug_overlay(tick_accum)
        pygame.display.update()
        dt_ms = min(clock.tick(settings["fps_limit"] if settings["fps_limit"] > 0 else 0), 100)


def _save_settings():
    d = load_save()
    for k in _SETTINGS_BOOL_KEYS + _SETTINGS_INT_KEYS + _SETTINGS_STR_KEYS:
        d[k] = settings.get(k)
    save_save(d)

_PANEL_ROW_KEYS = [
    "music", "wrap", "lightmode", "grid", "controls",
    "timer", "fps", "hardcore", "double_food", "start_length", "fog", "snake_pattern", "bg_style", "seed"
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
    elif key == "start_length":
        cyc = {3: 5, 5: 8, 8: 12, 12: 16, 16: 3}
        settings["start_length"] = cyc.get(settings["start_length"], 3)
        _save_settings()
    elif key == "fog":
        settings["fog_of_war"] = not settings["fog_of_war"]; _save_settings()
    elif key == "snake_pattern":
        settings["snake_pattern"] = not settings["snake_pattern"]; _save_settings()
    elif key == "bg_style":
        cyc = {"plain": "vignette", "vignette": "diagonal", "diagonal": "plain"}
        settings["bg_style"] = cyc.get(settings["bg_style"], "plain")
        _save_settings()
    elif key == "seed":
        seed_input_overlay()

def stats_screen():
    title_font = get_font("title", 60)
    row_font   = get_font("ui", 24)
    sub_font   = get_font("ui", 20)
    back_font  = get_font("ui", 26)
    btn_font   = get_font("menu", 30)

    status_msg = ""
    status_until_ms = 0
    fuse_a = [None]
    fuse_b = [None]
    DELETE_HOLD_MS = 5000
    delete_hold_start = None
    delete_awaiting_release = False

    while True:
        data = load_save()
        draw_background()
        mouse_pos = pygame.mouse.get_pos()
        lm  = settings["light_mode"]
        txt = (20, 20, 20) if lm else COLORS["white"]
        dim = (80, 80, 80) if lm else (140, 140, 140)

        now_ms = pygame.time.get_ticks()
        pressed = pygame.key.get_pressed()
        if pressed[pygame.K_DELETE] and not delete_awaiting_release:
            if delete_hold_start is None:
                delete_hold_start = now_ms
            held_ms = now_ms - delete_hold_start
            if held_ms >= DELETE_HOLD_MS:
                data = load_save()
                for k in _STATS_INT_KEYS:
                    data[k] = 0
                data["score"] = 0
                data["apples"] = set()
                for t in SA_TARGETS:
                    data[f"sa_best_{t}"] = 0
                data["shrink_best"] = 0
                data["dm_best_ms"] = 0
                data["pacifist_best"] = 0
                data["trust_best"] = 0
                data["chaos_best"] = 0
                data["rewind_best"] = 0
                save_save(data)
                _reload_state_from_save()
                status_msg = "All stats wiped."
                status_until_ms = now_ms + 2500
                delete_hold_start = None
                held_ms = 0
                delete_awaiting_release = True
        else:
            if not pressed[pygame.K_DELETE]:
                delete_awaiting_release = False
            delete_hold_start = None
            held_ms = 0

        title_s = title_font.render("Statistics", True, COLORS["purpleguy"])
        screen.blit(title_s, title_s.get_rect(center=(SCREEN_WIDTH // 2, 60)))

        back_col = COLORS["purpleguy"] if pygame.Rect(0, 0, 160, 46).collidepoint(mouse_pos) else dim
        back_s = back_font.render("< Back", True, back_col)
        back_r = back_s.get_rect(topleft=(22, 14))
        screen.blit(back_s, back_r)
        back_hit = pygame.Rect(0, 0, back_r.right + 10, 50)

        longest_str  = _fmt_time_ms(data.get("longest_game_ms", 0))  if data.get("longest_game_ms", 0)  > 0 else "—"
        shortest_str = _fmt_time_ms(data.get("shortest_game_ms", 0)) if data.get("shortest_game_ms", 0) > 0 else "—"

        rows = [
            ("Apples Eaten (All Time)", str(data.get("total_apples", 0))),
            ("Games Played",            str(data.get("games_played", 0))),
            ("Longest Game",            longest_str),
            ("Shortest Game",           shortest_str),
            ("Games With Cheats",       str(data.get("games_cheated", 0))),
            ("Local Multiplayer Games", str(data.get("games_mp", 0))),
        ]

        col_left  = SCREEN_WIDTH // 2 - 260
        col_right = SCREEN_WIDTH // 2 + 260
        row_y     = 150
        row_h     = 42
        for label, value in rows:
            ls = row_font.render(label, True, txt)
            vs = row_font.render(value, True, COLORS["purpleguy"])
            screen.blit(ls, ls.get_rect(midleft=(col_left, row_y)))
            screen.blit(vs, vs.get_rect(midright=(col_right, row_y)))
            row_y += row_h

        row_y += 8
        pygame.draw.line(screen, (60, 60, 80), (col_left, row_y), (col_right, row_y), 1)
        row_y += 24

        mp_games = data.get("games_mp", 0)
        mp_sub = [
            ("P1 Wins",  data.get("mp_p1_wins", 0)),
            ("P2 Wins",  data.get("mp_p2_wins", 0)),
            ("No One (Tie)", data.get("mp_ties", 0)),
        ]
        for label, value in mp_sub:
            ls = sub_font.render(f"— {label}", True, dim if mp_games == 0 else txt)
            vs = sub_font.render(str(value), True, dim if mp_games == 0 else COLORS["cyan"])
            screen.blit(ls, ls.get_rect(midleft=(col_left + 20, row_y)))
            screen.blit(vs, vs.get_rect(midright=(col_right, row_y)))
            row_y += 36

        row_y += 30
        import_s = btn_font.render("[ Import Save ]", True, txt)
        export_s = btn_font.render("[ Export Save ]", True, txt)
        import_r = import_s.get_rect(center=(SCREEN_WIDTH // 2 - 140, row_y))
        export_r = export_s.get_rect(center=(SCREEN_WIDTH // 2 + 140, row_y))
        if import_r.collidepoint(mouse_pos): import_s = btn_font.render("[ Import Save ]", True, COLORS["green"])
        if export_r.collidepoint(mouse_pos): export_s = btn_font.render("[ Export Save ]", True, COLORS["cyan"])
        screen.blit(import_s, import_r)
        screen.blit(export_s, export_r)

        hint_s = sub_font.render("Import overwrites your current save. Export copies it elsewhere.", True, dim)
        screen.blit(hint_s, hint_s.get_rect(center=(SCREEN_WIDTH // 2, row_y + 40)))

        row_y += 74
        pick_a_label = f"[ A: {os.path.basename(fuse_a[0])} ]" if fuse_a[0] else "[ Pick File A ]"
        pick_b_label = f"[ B: {os.path.basename(fuse_b[0])} ]" if fuse_b[0] else "[ Pick File B ]"
        pick_a_s = btn_font.render(pick_a_label, True, COLORS["green"] if fuse_a[0] else txt)
        pick_b_s = btn_font.render(pick_b_label, True, COLORS["green"] if fuse_b[0] else txt)
        pick_a_r = pick_a_s.get_rect(center=(SCREEN_WIDTH // 2 - 140, row_y))
        pick_b_r = pick_b_s.get_rect(center=(SCREEN_WIDTH // 2 + 140, row_y))
        if pick_a_r.collidepoint(mouse_pos) and not fuse_a[0]:
            pick_a_s = btn_font.render(pick_a_label, True, COLORS["yummers"])
        if pick_b_r.collidepoint(mouse_pos) and not fuse_b[0]:
            pick_b_s = btn_font.render(pick_b_label, True, COLORS["yummers"])
        screen.blit(pick_a_s, pick_a_r)
        screen.blit(pick_b_s, pick_b_r)

        fuse_hint_s = sub_font.render("Fuse Saves: pick two save files, the best of each stat carries over.", True, dim)
        fuse_hint_y = row_y + 34
        screen.blit(fuse_hint_s, fuse_hint_s.get_rect(center=(SCREEN_WIDTH // 2, fuse_hint_y)))

        # Reserved zone for delete-status messaging, starts clear of the fuse hint
        # and never overlaps it no matter what state (idle/holding/just-wiped) is active.
        zone_top = fuse_hint_y + 38
        bar_y    = max(SCREEN_HEIGHT - 68, zone_top + 26)
        msg_y    = bar_y - 26
        hint_y   = bar_y

        if held_ms > 0:
            frac = min(1.0, held_ms / DELETE_HOLD_MS)
            bar_w, bar_h = 260, 14
            bar_x = SCREEN_WIDTH // 2 - bar_w // 2
            pygame.draw.rect(screen, (60, 20, 20), (bar_x, bar_y, bar_w, bar_h), border_radius=4)
            pygame.draw.rect(screen, (255, 60, 60), (bar_x, bar_y, int(bar_w * frac), bar_h), border_radius=4)
            pygame.draw.rect(screen, (255, 120, 120), (bar_x, bar_y, bar_w, bar_h), 1, border_radius=4)
            wipe_s = sub_font.render("Wiping all stats...", True, (255, 100, 100))
            screen.blit(wipe_s, wipe_s.get_rect(center=(SCREEN_WIDTH // 2, msg_y)))
        elif status_msg and pygame.time.get_ticks() < status_until_ms:
            st_s = sub_font.render(status_msg, True, COLORS["yummers"])
            screen.blit(st_s, st_s.get_rect(center=(SCREEN_WIDTH // 2, hint_y)))
        else:
            del_hint_s = sub_font.render("Hold DELETE for 5 seconds to wipe all stats.", True, dim)
            screen.blit(del_hint_s, del_hint_s.get_rect(center=(SCREEN_WIDTH // 2, hint_y)))

        pygame.display.update()
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return
            if event.type == pygame.MOUSEBUTTONDOWN:
                if back_hit.collidepoint(event.pos):
                    return
                elif import_r.collidepoint(event.pos):
                    result = import_save_file()
                    if result is True:
                        status_msg = "Save imported."
                    elif result is False:
                        status_msg = "Import failed — check the log."
                    else:
                        status_msg = ""
                    status_until_ms = pygame.time.get_ticks() + 2500
                elif export_r.collidepoint(event.pos):
                    result = export_save_file()
                    if result is True:
                        status_msg = "Save exported."
                    elif result is False:
                        status_msg = "Export failed — check the log."
                    else:
                        status_msg = ""
                    status_until_ms = pygame.time.get_ticks() + 2500
                elif pick_a_r.collidepoint(event.pos):
                    path = _pick_file("open")
                    if path:
                        fuse_a[0] = path
                        status_msg = "File A selected."
                        status_until_ms = pygame.time.get_ticks() + 2500
                elif pick_b_r.collidepoint(event.pos):
                    path = _pick_file("open")
                    if path:
                        fuse_b[0] = path
                        status_msg = "File B selected."
                        status_until_ms = pygame.time.get_ticks() + 2500
                if fuse_a[0] and fuse_b[0]:
                    ok = fuse_save_files(fuse_a[0], fuse_b[0])
                    status_msg = "Fused! Best of both saves is now active." if ok else "Fuse failed — check the log."
                    status_until_ms = pygame.time.get_ticks() + 3000
                    fuse_a[0] = None
                    fuse_b[0] = None

def _mark_tip_seen(key):
    global _seen_tips
    if key in _seen_tips:
        return
    _seen_tips = set(_seen_tips)
    _seen_tips.add(key)
    d = load_save()
    d["seen_tips"] = _seen_tips
    save_save(d)

def _tip_popup(title, lines, tip_key=None):
    """Blocking one-shot popup. Shows once per tip_key ever (persisted), unless tip_key is None."""
    if tip_key is not None:
        if tip_key in _seen_tips:
            return
        _mark_tip_seen(tip_key)

    font_title = get_font("title", 44)
    font_line  = get_font("ui", 22)
    font_hint  = get_font("ui", 16)
    bw, bh = 620, 130 + len(lines) * 30
    bx = (SCREEN_WIDTH - bw) // 2
    by = (SCREEN_HEIGHT - bh) // 2
    opened_at = pygame.time.get_ticks()

    while True:
        lm  = settings["light_mode"]
        txt = (20, 20, 20) if lm else COLORS["white"]
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 170))
        screen.blit(overlay, (0, 0))
        pygame.draw.rect(screen, (18, 18, 35) if not lm else (245, 245, 250), (bx, by, bw, bh), border_radius=10)
        pygame.draw.rect(screen, COLORS["purpleguy"], (bx, by, bw, bh), 2, border_radius=10)

        ts = render_fit("title", title, COLORS["purpleguy"], bw - 40, 44, min_size=24)
        screen.blit(ts, ts.get_rect(center=(SCREEN_WIDTH // 2, by + 40)))
        for i, line in enumerate(lines):
            ls = render_fit("ui", line, txt, bw - 60, 22, min_size=14)
            screen.blit(ls, ls.get_rect(center=(SCREEN_WIDTH // 2, by + 90 + i * 30)))

        ready = pygame.time.get_ticks() - opened_at > 300
        hint_s = font_hint.render("Press any key / click to continue" if ready else "...", True, (140, 140, 160))
        screen.blit(hint_s, hint_s.get_rect(center=(SCREEN_WIDTH // 2, by + bh - 22)))
        pygame.display.update()
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if not ready:
                continue
            if event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN, pygame.JOYBUTTONDOWN):
                return

def how_to_play_screen():
    font_title = get_font("title", 56)
    font_h2    = get_font("title", 30)
    font_body  = get_font("ui", 19)
    font_small = get_font("ui", 15)
    font_back  = get_font("ui", 26)

    SECTIONS = [
        ("Controls", [
            "Default: WASD or Arrow Keys. Change scheme in Settings.",
            "IJKL is available for lefty/alt setups.",
            "Wildcard: one button (Space) cycles Right -> Down -> Left -> Up",
            "  each press. Good with one hand, or just to mess around.",
            "Controllers: D-pad / left stick to steer, most face buttons confirm.",
        ]),
        ("Modes", [
            "Endless: survive as long as you can, high score tracked.",
            "Score Attack: race to a target score, best time tracked.",
            "Shrink: your snake shrinks every few seconds. Eat or vanish.",
            "Deathmatch: the walls close in over time.",
            "Pacifist %: score ticks up on its own. Eating food kills you.",
            "Trust Issues: mash a direction to actually turn that way.",
            "Chaos Mode: random settings reshuffle every 10 seconds.",
            "Rewind: banked charges let you undo the last few seconds.",
        ]),
        ("Settings Highlights", [
            "Fog of War: only see a cone ahead of your head.",
            "Hardcore: no pause, no bursts, no wrap. Full commitment.",
            "Seed: lock food spawns to a fixed sequence for practice runs.",
            "Background style: plain, vignette, or diagonal.",
        ]),
        ("Cheat Console", [
            "Press ` (backtick) or ё to open it from the main menu.",
            "Type a code and hit ENTER. Wrong codes just get roasted.",
            "We're not telling you what the codes are. Find out yourself.",
        ]),
        ("Credits", [
            "Built by SkullDozer.",
            "Music and visual assets by PIXXEL.",
            "Thanks for playing NotASnake.",
        ]),
    ]

    scroll = 0
    max_scroll = 0

    while True:
        draw_background()
        lm  = settings["light_mode"]
        txt = (20, 20, 20) if lm else COLORS["white"]
        dim = (90, 90, 90) if lm else (150, 150, 150)
        mouse_pos = pygame.mouse.get_pos()

        title_s = font_title.render("How to Play", True, COLORS["green"])
        screen.blit(title_s, title_s.get_rect(center=(SCREEN_WIDTH // 2, 50)))

        back_col = COLORS["purpleguy"] if pygame.Rect(0, 0, 160, 46).collidepoint(mouse_pos) else dim
        back_s = font_back.render("< Back", True, back_col)
        back_r = back_s.get_rect(topleft=(22, 14))
        screen.blit(back_s, back_r)

        content_top = 110
        content_bottom = SCREEN_HEIGHT - 20
        clip_rect = pygame.Rect(0, content_top, SCREEN_WIDTH, content_bottom - content_top)
        screen.set_clip(clip_rect)

        y = content_top - scroll
        col_x = SCREEN_WIDTH // 2 - 380
        col_w = 760

        for heading, lines in SECTIONS:
            hs = font_h2.render(heading, True, COLORS["yummers"])
            screen.blit(hs, (col_x, y))
            y += 42
            for line in lines:
                ls = render_fit("ui", line, txt, col_w, 19, min_size=13)
                screen.blit(ls, (col_x + 10, y))
                y += 27
            y += 20

        max_scroll = max(0, y + scroll - content_bottom)
        screen.set_clip(None)

        if max_scroll > 0:
            hint_s = font_small.render("Scroll wheel / arrows to read more", True, dim)
            screen.blit(hint_s, hint_s.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 14)))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEWHEEL:
                scroll = max(0, min(max_scroll, scroll - event.y * 40))
            if event.type == pygame.MOUSEBUTTONDOWN:
                if back_r.collidepoint(event.pos) or pygame.Rect(0, 0, 160, 46).collidepoint(event.pos):
                    return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return
                elif event.key == pygame.K_DOWN:
                    scroll = min(max_scroll, scroll + 40)
                elif event.key == pygame.K_UP:
                    scroll = max(0, scroll - 40)
            if event.type == pygame.JOYBUTTONDOWN:
                if event.button == 1:
                    return
            if event.type == pygame.JOYHATMOTION:
                if event.value[1] < 0:
                    scroll = min(max_scroll, scroll + 40)
                elif event.value[1] > 0:
                    scroll = max(0, scroll - 40)

        pygame.display.update()
        clock.tick(60)

def main_menu():
    global DIFFICULTY, debug_overlay_visible
    music_manager.play_music('menu', volume=0.5)

    diff_font     = get_font("ui", 28)
    controls_font = get_font("ui", 18)
    panel_font    = get_font("ui", 24)

    diff_names = list(DIFFICULTY_LEVELS.keys())
    current_diff_idx = 1
    for i, name in enumerate(diff_names):
        if DIFFICULTY_LEVELS[name] == DIFFICULTY:
            current_diff_idx = i
            break

    menu_sel = 0
    nav_active = False
    _joy_axis_last = {}

    PANEL_W       = 360
    panel_open    = False
    panel_x       = SCREEN_WIDTH
    panel_target  = SCREEN_WIDTH
    PANEL_SPEED   = 40
    MENU_SHIFT    = PANEL_W // 2
    panel_sel     = 0
    PANEL_ROWS    = 14
    PANEL_ROW_H   = 56
    PANEL_TOP     = 70
    PANEL_BOTTOM  = SCREEN_HEIGHT - 34
    panel_scroll  = 0

    single_rect  = pygame.Rect(0, 0, 0, 0)
    multi_rect   = pygame.Rect(0, 0, 0, 0)
    how_to_rect  = pygame.Rect(0, 0, 0, 0)
    exit_rect    = pygame.Rect(0, 0, 0, 0)

    cheats = CheatConsole()
    claude_easter_egg = [False]

    def toggle_panel():
        nonlocal panel_open, panel_target, panel_scroll
        panel_open   = not panel_open
        panel_target = SCREEN_WIDTH - PANEL_W if panel_open else SCREEN_WIDTH
        if not panel_open:
            panel_scroll = 0

    def _scroll_to_sel():
        nonlocal panel_scroll
        row_top = 80 + panel_sel * PANEL_ROW_H
        row_bot = row_top + 50
        if row_top - panel_scroll < PANEL_TOP:
            panel_scroll = max(0, row_top - PANEL_TOP)
        elif row_bot - panel_scroll > PANEL_BOTTOM:
            panel_scroll = row_bot - PANEL_BOTTOM

    def _cheat_mouseless():
        toggle_panel()
        return "Settings opened." if panel_open else "Settings closed."

    def _cheat_cheats():
        return "Cheating is a no-no!"

    def _cheat_claudeareyouhere():
        claude_easter_egg[0] = not claude_easter_egg[0]
        return "..." if claude_easter_egg[0] else "Cheat disabled."

    def _cheat_untildawn():
        settings["light_mode"] = not settings["light_mode"]
        _save_settings()
        return f"Theme: {'Light' if settings['light_mode'] else 'Dark'}."

    def _cheat_hello():
        return "Hello!"

    cheat_dispatch = {
        "mouseless":        _cheat_mouseless,
        "cheats":           _cheat_cheats,
        "claudeareyouhere": _cheat_claudeareyouhere,
        "untildawn":        _cheat_untildawn,
        "helloskd":         _cheat_hello,
        "helloskulldozer":  _cheat_hello,
    }

    while True:
        if panel_x < panel_target:
            panel_x = min(panel_x + PANEL_SPEED, panel_target)
        elif panel_x > panel_target:
            panel_x = max(panel_x - PANEL_SPEED, panel_target)

        slide_ratio  = 1.0 - (panel_x - (SCREEN_WIDTH - PANEL_W)) / PANEL_W
        slide_ratio  = max(0.0, min(1.0, slide_ratio))
        btn_cx       = SCREEN_WIDTH // 2 - int(MENU_SHIFT * slide_ratio)

        draw_background()
        mouse_pos = pygame.mouse.get_pos() if not cheats.open else (-1, -1)

        lm = settings["light_mode"]
        txt   = (20, 20, 20)      if lm else COLORS["white"]
        dim   = (80, 80, 80)      if lm else (140, 140, 140)

        high_score = load_high_score()

        title_max_w = 2 * min(btn_cx, panel_x - btn_cx) - 40
        title_surface = render_fit("title", "NotASnake v3.5", COLORS["green"], title_max_w, 100, min_size=40)
        title_rect = title_surface.get_rect(center=(btn_cx, SCREEN_HEIGHT // 2 - 210))
        screen.blit(title_surface, title_rect)

        if claude_easter_egg[0]:
            ce_font = get_font("ui_bold", 18, bold=True)
            ce_s = ce_font.render("claude was here", True, (217, 119, 87))
            screen.blit(ce_s, ce_s.get_rect(midbottom=(btn_cx, title_rect.top - 10)))

        hs_surface = diff_font.render(f"High Score: {high_score}", True, COLORS["purpleguy"])
        hs_rect = hs_surface.get_rect(center=(btn_cx, SCREEN_HEIGHT // 2 - 140))
        screen.blit(hs_surface, hs_rect)
        apple_size = 18
        apple_gap  = 44
        apple_y    = SCREEN_HEIGHT // 2 - 96
        for _ai, _at in enumerate(SA_TARGETS):
            draw_apple(btn_cx + (_ai - 1) * apple_gap, apple_y, apple_size, _at in _earned_apples)

        diff_label = diff_font.render("Difficulty:", True, txt)
        screen.blit(diff_label, diff_label.get_rect(center=(btn_cx, SCREEN_HEIGHT // 2 - 45)))

        arrow_left  = diff_font.render("<", True, txt)
        arrow_right = diff_font.render(">", True, txt)
        diff_name_str = diff_names[current_diff_idx]
        diff_colors = {"Story game": txt, "The Classic": COLORS["green"],
                       "Faster!": COLORS["purpleguy"], "Whoosh!!!": COLORS["red"]}
        diff_val_surface = diff_font.render(diff_name_str, True, diff_colors[diff_name_str])

        arrow_left_rect  = arrow_left.get_rect(center=(btn_cx - 100, SCREEN_HEIGHT // 2))
        diff_val_rect    = diff_val_surface.get_rect(center=(btn_cx, SCREEN_HEIGHT // 2))
        arrow_right_rect = arrow_right.get_rect(center=(btn_cx + 100, SCREEN_HEIGHT // 2))

        if arrow_left_rect.collidepoint(mouse_pos):
            arrow_left = diff_font.render("<", True, COLORS["purpleguy"])
        if arrow_right_rect.collidepoint(mouse_pos):
            arrow_right = diff_font.render(">", True, COLORS["purpleguy"])

        screen.blit(arrow_left,      arrow_left_rect)
        screen.blit(diff_val_surface, diff_val_rect)
        screen.blit(arrow_right,     arrow_right_rect)

        btn_max_w = 2 * min(btn_cx, panel_x - btn_cx) - 40
        single_text = render_fit("menu", "Single Player", COLORS["green"] if (nav_active and menu_sel == 0) or single_rect.collidepoint(mouse_pos) else txt, btn_max_w, 72, min_size=30)
        single_rect = single_text.get_rect(center=(btn_cx, SCREEN_HEIGHT // 2 + 50))
        multi_text  = render_fit("menu", "Local Multiplayer", COLORS["cyan"] if (nav_active and menu_sel == 1) or multi_rect.collidepoint(mouse_pos) else txt, btn_max_w, 72, min_size=30)
        multi_rect  = multi_text.get_rect(center=(btn_cx, SCREEN_HEIGHT // 2 + 128))
        how_to_text = render_fit("menu", "How to Play", COLORS["purpleguy"] if (nav_active and menu_sel == 2) or how_to_rect.collidepoint(mouse_pos) else txt, btn_max_w, 60, min_size=26)
        how_to_rect = how_to_text.get_rect(center=(btn_cx, SCREEN_HEIGHT // 2 + 200))
        exit_text   = render_fit("menu", "Exit", COLORS["red"] if (nav_active and menu_sel == 3) or exit_rect.collidepoint(mouse_pos) else txt, btn_max_w, 60, min_size=26)
        exit_rect   = exit_text.get_rect(center=(btn_cx, SCREEN_HEIGHT // 2 + 264))

        screen.blit(single_text, single_rect)
        screen.blit(multi_text,  multi_rect)
        screen.blit(how_to_text, how_to_rect)
        screen.blit(exit_text,   exit_rect)

        gear_font = get_font("ui", 28)
        joy_count = pygame.joystick.get_count()
        if panel_open:
            gear_label = "[ Close ]"
        elif joy_count > 0:
            gear_label = "[ Settings  Share/Select ]"
        else:
            gear_label = "[ Settings ]"
        gear_color = COLORS["purpleguy"] if panel_open else txt
        gear_surf  = gear_font.render(gear_label, True, gear_color)
        gear_rect  = gear_surf.get_rect(topright=(SCREEN_WIDTH - 16, 16))
        if gear_rect.collidepoint(mouse_pos):
            gear_surf = gear_font.render(gear_label, True, COLORS["purpleguy"])
        screen.blit(gear_surf, gear_rect)

        stats_surf = gear_font.render("[ Stats ]", True, txt)
        stats_rect = stats_surf.get_rect(topleft=(16, 16))
        if stats_rect.collidepoint(mouse_pos):
            stats_surf = gear_font.render("[ Stats ]", True, COLORS["purpleguy"])
        screen.blit(stats_surf, stats_rect)

        setting_rects = {}   # reset each frame; filled during panel draw
        max_scroll = max(0, PANEL_ROWS * PANEL_ROW_H - (PANEL_BOTTOM - PANEL_TOP))
        panel_scroll = max(0, min(panel_scroll, max_scroll))

        if panel_x < SCREEN_WIDTH:
            panel_surf = pygame.Surface((PANEL_W, SCREEN_HEIGHT), pygame.SRCALPHA)
            panel_surf.fill((15, 15, 30, 220))
            screen.blit(panel_surf, (panel_x, 0))

            px = panel_x + 24  # left edge of text inside panel

            pt = panel_font.render("Settings", True, COLORS["green"])
            screen.blit(pt, (panel_x + PANEL_W // 2 - pt.get_width() // 2, 24))

            pygame.draw.line(screen, (60, 60, 80), (panel_x + 16, 60), (panel_x + PANEL_W - 16, 60), 1)

            row_idx = [0]
            clip_rect = pygame.Rect(panel_x, PANEL_TOP, PANEL_W, PANEL_BOTTOM - PANEL_TOP)
            screen.set_clip(clip_rect)

            def draw_setting(y, label, val_str, val_col, desc_lines):
                idx = row_idx[0]
                row_idx[0] += 1
                draw_y = y - panel_scroll
                is_sel = panel_open and idx == panel_sel
                if is_sel:
                    hi = pygame.Surface((PANEL_W - 8, 48), pygame.SRCALPHA)
                    hi.fill((80, 80, 180, 60))
                    screen.blit(hi, (panel_x + 4, draw_y - 2))
                    pygame.draw.rect(screen, COLORS["purpleguy"], (panel_x + 4, draw_y - 2, PANEL_W - 8, 48), 1)
                row_w   = PANEL_W - 40
                lbl     = render_fit("ui", label, COLORS["white"], row_w * 0.5, 24, min_size=14)
                screen.blit(lbl, (px, draw_y))
                val_highlight = is_sel or vs_hover(draw_y, val_str)
                val_col_final = COLORS["purpleguy"] if val_highlight else val_col
                val_max_w = (panel_x + PANEL_W - 16) - (px + lbl.get_width()) - 10
                vs   = render_fit("ui", val_str, val_col_final, val_max_w, 24, min_size=12)
                vr   = vs.get_rect(topright=(panel_x + PANEL_W - 16, draw_y))
                screen.blit(vs, vr)
                if desc_lines:
                    desc_max_w = PANEL_W - (px - panel_x) - 24
                    ds = render_fit("ui", desc_lines[0], (140, 140, 160), desc_max_w, 18, min_size=11)
                    screen.blit(ds, (px, draw_y + 26))
                row_h = 50
                div_y = draw_y + row_h
                pygame.draw.line(screen, (40, 40, 60),
                                 (panel_x + 16, div_y), (panel_x + PANEL_W - 16, div_y), 1)
                if draw_y + row_h < PANEL_TOP or draw_y > PANEL_BOTTOM:
                    vr = pygame.Rect(-1000, -1000, 0, 0)
                return vr, y + row_h + 6

            def vs_hover(y, val_str):
                """Check if the value button for a row at y is hovered."""
                vs_tmp = panel_font.render(val_str, True, COLORS["white"])
                vr_tmp = vs_tmp.get_rect(topright=(panel_x + PANEL_W - 16, y))
                return vr_tmp.collidepoint(mouse_pos)

            cur_y = 80

            mute_val = "[ MUTED ]" if settings["music_muted"] else "[ ON ]"
            mute_col = COLORS["red"] if settings["music_muted"] else COLORS["green"]
            mute_rect, cur_y = draw_setting(cur_y, "Music", mute_val, mute_col,
                                            ["Toggle music on/off"])
            setting_rects["music"] = mute_rect

            wrap_val = "[ ON ]" if settings["wrap_around"] else "[ OFF ]"
            wrap_col = COLORS["green"] if settings["wrap_around"] else (160, 160, 160)
            wrap_rect, cur_y = draw_setting(cur_y, "Wrap-Around", wrap_val, wrap_col,
                                            ["Walls wrap to opposite side"])
            setting_rects["wrap"] = wrap_rect

            lm_val = "[ LIGHT ]" if settings["light_mode"] else "[ DARK ]"
            lm_col = (255, 230, 80) if settings["light_mode"] else (160, 160, 220)
            lm_rect, cur_y = draw_setting(cur_y, "Theme", lm_val, lm_col,
                                          ["Toggle Dark / Light theme"])
            setting_rects["lightmode"] = lm_rect

            go = settings["grid_opacity"]
            grid_labels = {0: "[ OFF ]", 127: "[ 50% ]", 255: "[ 100% ]"}
            grid_val = grid_labels[go]
            grid_col = (160, 160, 160) if go == 0 else ((180, 255, 180) if go == 127 else COLORS["green"])
            grid_rect, cur_y = draw_setting(cur_y, "Grid Lines", grid_val, grid_col,
                                            ["Show grid: Off / 50% / 100%"])
            setting_rects["grid"] = grid_rect

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

            tmr_val = "[ ON ]" if settings["show_timer"] else "[ OFF ]"
            tmr_col = COLORS["green"] if settings["show_timer"] else (160, 160, 160)
            tmr_rect, cur_y = draw_setting(cur_y, "Timer", tmr_val, tmr_col,
                                           ["Show elapsed time on HUD"])
            setting_rects["timer"] = tmr_rect

            fps_labels = {30: "[ 30 FPS ]", 60: "[ 60 FPS ]", 120: "[ 120 FPS ]", 0: "[ Unlim. ]"}
            fps_val = fps_labels.get(settings["fps_limit"], "[ 60 FPS ]")
            fps_col = (180, 255, 180)
            fps_rect, cur_y = draw_setting(cur_y, "FPS Cap", fps_val, fps_col,
                                           ["30 / 60 / 120 / Unlim."])
            setting_rects["fps"] = fps_rect

            hc_val = "[ ON ]" if settings["hardcore"] else "[ OFF ]"
            hc_col = (255, 60, 60) if settings["hardcore"] else (160, 160, 160)
            hc_rect, cur_y = draw_setting(cur_y, "!! Hardcore", hc_val, hc_col,
                                          ["No pause, no burst, no wrap."])
            setting_rects["hardcore"] = hc_rect

            df_val = "[ ON ]" if settings["double_food"] else "[ OFF ]"
            df_col = COLORS["cyan"] if settings["double_food"] else (160, 160, 160)
            df_rect, cur_y = draw_setting(cur_y, "Double Food", df_val, df_col,
                                          ["Two food items always active"])
            setting_rects["double_food"] = df_rect

            sl_val = f"[ {settings['start_length']} ]"
            sl_rect, cur_y = draw_setting(cur_y, "Start Length", sl_val, COLORS["cyan"],
                                          ["Snake's starting body length"])
            setting_rects["start_length"] = sl_rect

            fog_val = "[ ON ]" if settings["fog_of_war"] else "[ OFF ]"
            fog_col = (150, 140, 220) if settings["fog_of_war"] else (160, 160, 160)
            fog_rect, cur_y = draw_setting(cur_y, "Fog of War", fog_val, fog_col,
                                           ["Limited vision around your head"])
            setting_rects["fog"] = fog_rect

            pat_val = "[ ON ]" if settings["snake_pattern"] else "[ OFF ]"
            pat_col = (120, 220, 160) if settings["snake_pattern"] else (160, 160, 160)
            pat_rect, cur_y = draw_setting(cur_y, "Body Pattern", pat_val, pat_col,
                                           ["Scale pattern on snake body"])
            setting_rects["snake_pattern"] = pat_rect

            bg_labels = {"plain": "[ Plain ]", "vignette": "[ Vignette ]", "diagonal": "[ Diagonal ]"}
            bg_val = bg_labels.get(settings["bg_style"], "[ Plain ]")
            bg_rect, cur_y = draw_setting(cur_y, "Background", bg_val, (180, 180, 255),
                                          ["Cycle: Plain / Vignette / Diagonal"])
            setting_rects["bg_style"] = bg_rect

            seed_display = f"[ {ACTIVE_SEED[:12]}.. ]" if len(ACTIVE_SEED) > 12 else (f"[ {ACTIVE_SEED} ]" if ACTIVE_SEED else "[ none ]")
            seed_col = COLORS["purpleguy"] if ACTIVE_SEED else (160, 160, 160)
            seed_rect, cur_y = draw_setting(cur_y, "Seed [debug]", seed_display, seed_col,
                                            ["Set for reproducible food RNG"])
            setting_rects["seed"] = seed_rect

            screen.set_clip(None)
            if max_scroll > 0:
                hint_txt = "Scroll for more \u2193" if panel_scroll < max_scroll else "\u2191 Scroll up for more"
                hint = controls_font.render(hint_txt, True, (130, 130, 160))
                screen.blit(hint, hint.get_rect(midbottom=(panel_x + PANEL_W // 2, SCREEN_HEIGHT - 4)))

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

        cheats.draw(SCREEN_WIDTH, SCREEN_HEIGHT)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type in (pygame.JOYDEVICEADDED, pygame.JOYDEVICEREMOVED):
                _refresh_joysticks()
            if cheats.open:
                cheats.feed_event(event, cheat_dispatch)
                continue
            if _cheat_key_open(event):
                cheats.toggle()
                continue
            if event.type == pygame.MOUSEWHEEL:
                if panel_open and panel_x < SCREEN_WIDTH:
                    panel_scroll -= event.y * 30
                    panel_scroll = max(0, min(panel_scroll, max_scroll))
                    panel_sel = max(0, min(PANEL_ROWS - 1, round(panel_scroll / PANEL_ROW_H)))
            if event.type == pygame.MOUSEBUTTONDOWN:
                if stats_rect.collidepoint(event.pos):
                    stats_screen()
                elif gear_rect.collidepoint(event.pos):
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
                    elif setting_rects.get("start_length") and setting_rects["start_length"].collidepoint(event.pos):
                        cyc = {3: 5, 5: 8, 8: 12, 12: 16, 16: 3}
                        settings["start_length"] = cyc.get(settings["start_length"], 3)
                        _save_settings()
                    elif setting_rects.get("fog") and setting_rects["fog"].collidepoint(event.pos):
                        settings["fog_of_war"] = not settings["fog_of_war"]
                        _save_settings()
                    elif setting_rects.get("snake_pattern") and setting_rects["snake_pattern"].collidepoint(event.pos):
                        settings["snake_pattern"] = not settings["snake_pattern"]
                        _save_settings()
                    elif setting_rects.get("bg_style") and setting_rects["bg_style"].collidepoint(event.pos):
                        cyc = {"plain": "vignette", "vignette": "diagonal", "diagonal": "plain"}
                        settings["bg_style"] = cyc.get(settings["bg_style"], "plain")
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
                        return "single"
                    elif multi_rect.collidepoint(event.pos):
                        music_manager.stop_music()
                        return "multi"
                    elif how_to_rect.collidepoint(event.pos):
                        return "how_to"
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
                        return "single"
                    elif multi_rect.collidepoint(event.pos):
                        music_manager.stop_music()
                        return "multi"
                    elif how_to_rect.collidepoint(event.pos):
                        return "how_to"
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
                    menu_sel = (menu_sel - 1) % 4
                    nav_active = True
                elif event.key == pygame.K_DOWN:
                    menu_sel = (menu_sel + 1) % 4
                    nav_active = True
                elif event.key == pygame.K_RETURN:
                    if menu_sel == 0: return "single"
                    elif menu_sel == 1:
                        music_manager.stop_music(); return "multi"
                    elif menu_sel == 2: return "how_to"
                    else: pygame.quit(); sys.exit()
                elif event.key == pygame.K_1:
                    return "single"
                elif event.key == pygame.K_2:
                    music_manager.stop_music()
                    return "multi"
                elif event.key == pygame.K_3:
                    return "how_to"
                elif event.key == pygame.K_4 or event.key == pygame.K_ESCAPE:
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
                        if menu_sel == 0: return "single"
                        elif menu_sel == 1:
                            music_manager.stop_music()
                            return "multi"
                        elif menu_sel == 2: return "how_to"
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
                    _scroll_to_sel()
                else:
                    if event.value[1] > 0:    menu_sel = (menu_sel - 1) % 4; nav_active = True
                    elif event.value[1] < 0:  menu_sel = (menu_sel + 1) % 4; nav_active = True
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
                        else:          menu_sel   = (menu_sel - 1) % 4; nav_active = True
                    elif cur > 0.55 and prev <= 0.55:
                        if panel_open: panel_sel = (panel_sel + 1) % PANEL_ROWS
                        else:          menu_sel   = (menu_sel + 1) % 4; nav_active = True
                    if panel_open:
                        _scroll_to_sel()
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
    font_big  = get_font("title", 180)
    font_hint = get_font("ui", 24)
    hint_col  = (30, 30, 30) if settings["light_mode"] else COLORS["white"]
    for count in (3, 2, 1):
        start = pygame.time.get_ticks()
        while pygame.time.get_ticks() - start < 1000:
            lost_focus = False
            for event in pygame.event.get():
                music_manager.handle_event(event)
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.ACTIVEEVENT:
                    if event.state == pygame.APPINPUTFOCUS and not event.gain:
                        lost_focus = True
                elif event.type == pygame.WINDOWFOCUSLOST:
                    lost_focus = True
            if lost_focus:
                pygame.mixer.music.pause()
                lost_at = pygame.time.get_ticks()
                regained = False
                while not regained:
                    for ev in pygame.event.get():
                        if ev.type == pygame.QUIT:
                            pygame.quit(); sys.exit()
                        elif ev.type == pygame.WINDOWFOCUSGAINED:
                            regained = True
                        elif ev.type == pygame.ACTIVEEVENT and ev.state == pygame.APPINPUTFOCUS and ev.gain:
                            regained = True
                    pygame.time.wait(50)
                pygame.mixer.music.unpause()
                start += pygame.time.get_ticks() - lost_at
                continue
            elapsed = pygame.time.get_ticks() - start
            alpha   = max(0, 255 - int(elapsed / 1000 * 255))
            draw_background()
            num_surf = font_big.render(str(count), True, COLORS["green"])
            num_surf.set_alpha(alpha)
            num_rect = num_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            screen.blit(num_surf, num_rect)
            hint_surf = font_hint.render("Get ready...", True, hint_col)
            hint_rect = hint_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 110))
            screen.blit(hint_surf, hint_rect)
            pygame.display.flip()
            clock.tick(60)

_FOG_OVERLAY = None
_FOG_HOLES   = {}

def _build_fog_hole_right():
    size = 460
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    cy = size // 2
    blobs = [
        (size * 0.30, cy, 95,  255),
        (size * 0.46, cy, 130, 255),
        (size * 0.64, cy, 150, 255),
        (size * 0.82, cy, 130, 255),
        (size * 0.94, cy - 20, 90, 255),
        (size * 0.94, cy + 20, 90, 255),
    ]
    for bx, by, r, a in blobs:
        pygame.draw.circle(surf, (255, 255, 255, a), (int(bx), int(by)), r)
    return surf

def _get_fog_hole(direction):
    if direction in _FOG_HOLES:
        return _FOG_HOLES[direction]
    base = _build_fog_hole_right()
    rot = {"RIGHT": 0, "UP": 90, "LEFT": 180, "DOWN": -90}[direction]
    surf = pygame.transform.rotate(base, rot) if rot else base
    _FOG_HOLES[direction] = surf
    return surf

def draw_fog_of_war(head_pos, direction):
    global _FOG_OVERLAY
    if _FOG_OVERLAY is None:
        _FOG_OVERLAY = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    _FOG_OVERLAY.fill((5, 5, 10, 255))
    hole = _get_fog_hole(direction)
    hw, hh = hole.get_size()
    hx = head_pos[0] + CELL_SIZE // 2 - hw // 2
    hy = head_pos[1] + CELL_SIZE // 2 - hh // 2
    _FOG_OVERLAY.blit(hole, (hx, hy), special_flags=pygame.BLEND_RGBA_SUB)
    screen.blit(_FOG_OVERLAY, (0, 0))

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
            if settings.get("snake_pattern", True):
                _draw_scale(pos, idx, body_color)
            border_color = (0, 200, 0) if is_head1 else (0, 0, 200)
            pygame.draw.rect(screen, border_color, pygame.Rect(
                pos[0], pos[1], CELL_SIZE, CELL_SIZE
            ), 1)

def _draw_scale(pos, idx, body_color):
    shade = tuple(max(0, c - 45) for c in body_color)
    cx = pos[0] + CELL_SIZE // 2
    cy = pos[1] + CELL_SIZE // 2
    row_offset = -CELL_SIZE * 0.16 if idx % 2 == 0 else CELL_SIZE * 0.16
    sw = CELL_SIZE * 0.55
    sh = CELL_SIZE * 0.4
    pts = [
        (cx, cy + row_offset - sh / 2),
        (cx + sw / 2, cy + row_offset),
        (cx, cy + row_offset + sh / 2),
        (cx - sw / 2, cy + row_offset),
    ]
    pygame.draw.polygon(screen, shade, pts)

def single_player_game():
    music_manager.play_music('ingame', loop=True, volume=0.5)
    global snake_pos, snake_body, food_pos, food_spawn, food2_pos, direction, change_to, score
    global leftover, burst1
    global debug_overlay_visible
    global _spacebar_idx

    reset_single_game()
    _spacebar_idx = 0  # reset spacebar cycle
    draw_countdown()
    if settings["control_scheme"] == "spacebar":
        _tip_popup("Wildcard Controls", [
            "One button turns you: Right -> Down -> Left -> Up, in that order.",
            "Each press advances the cycle by one step.",
            "Plan your turns ahead, you can't skip or reverse the cycle.",
        ], tip_key="wildcard_controls")

    tick_accum  = 0.0
    dt_ms = 1000.0 / 60.0
    game_start_ms = pygame.time.get_ticks()
    moment_shown    = False
    moment_until_ms = 0
    MOMENT_SCORE  = 50
    MOMENT_TEXT   = "..huh. okay. you're actually good at this. good luck."

    cheats     = CheatConsole()
    haste_mult = [1.0]
    force_die  = [False]
    cheated_this_game = [False]

    def _cheat_hardcore():
        settings["hardcore"] = not settings["hardcore"]
        if settings["hardcore"]:
            settings["wrap_around"] = False
        return f"Hardcore {'ON' if settings['hardcore'] else 'OFF'}."

    def _cheat_hasted():
        haste_mult[0] += 0.5
        return f"Haste x{haste_mult[0]:.1f}"

    def _cheat_wasted():
        force_die[0] = True
        return "wasted."

    def _cheat_oldspice():
        global leftover
        leftover = {"pos": spawn_food(snake_body), "born": pygame.time.get_ticks()}
        return "Leftover spawned."

    def _cheat_portalled():
        settings["wrap_around"] = not settings["wrap_around"]
        return f"Wrap-around {'ON' if settings['wrap_around'] else 'OFF'}."

    def _cheat_untildawn():
        settings["light_mode"] = not settings["light_mode"]
        _save_settings()
        return f"Theme: {'Light' if settings['light_mode'] else 'Dark'}."

    def _cheat_claude():
        music_manager._play_effect_sound()
        return "..."

    def _cheat_hello():
        return "Hello!"

    def _cheat_denied():
        return "Access was denied"

    def _cheat_svcheats():
        return "Can't change replicated ConVar sv_cheats from console of client, only server operator can change its value."

    def _cheat_thousandyards():
        settings["fog_of_war"] = not settings["fog_of_war"]
        return f"Fog of War {'ON' if settings['fog_of_war'] else 'OFF'}."

    def _cheat_securitybreach():
        nonlocal moment_shown, moment_until_ms
        moment_shown = True
        moment_until_ms = pygame.time.get_ticks() + 2800
        return "Five nights, huh?"

    cheat_dispatch = {
        "nowthisishard":    _cheat_hardcore,
        "hasted":           _cheat_hasted,
        "wasted":           _cheat_wasted,
        "oldspice":         _cheat_oldspice,
        "portalled":        _cheat_portalled,
        "noclip":           _cheat_portalled,
        "untildawn":        _cheat_untildawn,
        "claudeareyouhere": _cheat_claude,
        "helloskd":         _cheat_hello,
        "helloskulldozer":  _cheat_hello,
        "sv_cheats 1":      _cheat_svcheats,
        "impulse 101":      _cheat_denied,
        "thousandyards":    _cheat_thousandyards,
        "securitybreach":   _cheat_securitybreach,
    }

    while True:
        now_ms = pygame.time.get_ticks()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type in (pygame.JOYDEVICEADDED, pygame.JOYDEVICEREMOVED):
                _refresh_joysticks()
            elif cheats.open:
                code = cheats.feed_event(event, cheat_dispatch)
                if code in cheat_dispatch:
                    cheated_this_game[0] = True
                continue
            elif _cheat_key_open(event):
                cheats.toggle()
                continue
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
                    pygame.mixer.music.pause()
                    quit_to_menu = False
                    if not settings["hardcore"]:
                        quit_to_menu = pause_menu(is_multiplayer=False, mode_label="SP Endless")
                    pygame.mixer.music.unpause()
                    if quit_to_menu:
                        return "menu"
            elif event.type == pygame.WINDOWFOCUSLOST:
                pygame.mixer.music.pause()
                quit_to_menu = False
                if not settings["hardcore"]:
                    quit_to_menu = pause_menu(is_multiplayer=False, mode_label="SP Endless")
                pygame.mixer.music.unpause()
                if quit_to_menu:
                    return "menu"

        if burst1["active"] and now_ms >= burst1["end_ms"]:
            burst1["active"] = False
            print("Speedy end..")

        if leftover is not None and now_ms - leftover["born"] >= LEFTOVER_LINGER_MS:
            leftover = None
            print("Too slow! Burst pickup faded")

        if settings["hardcore"] and leftover is not None:
            leftover = None

        effective_difficulty = DIFFICULTY * (BURST_MULTIPLIER if burst1["active"] else 1.0) * haste_mult[0]

        tick_accum += effective_difficulty * (dt_ms / 1000.0)
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
                food_pos = spawn_food(snake_body + ([food2_pos] if settings['double_food'] else []))
                print(f"Yummies food1! Score: {score}")
            elif settings["double_food"] and snake_pos == food2_pos:
                score += 1; ate = True
                if leftover is None and not settings["hardcore"]:
                    leftover = {"pos": spawn_food(snake_body), "born": now_ms}
                food2_pos = spawn_food(snake_body + [food_pos])
                print(f"Yummies food2! Score: {score}")
            if not ate:
                snake_body.pop()

            if not moment_shown and score >= MOMENT_SCORE:
                moment_shown = True
                moment_until_ms = now_ms + 2800

            if leftover is not None and snake_pos == leftover["pos"]:
                if not settings["hardcore"]:  # no burst in hardcore
                    burst1["active"] = True
                    burst1["end_ms"] = now_ms + BURST_DURATION_MS
                leftover = None
                print(f"Burst is a goner!")

        draw_background()
        draw_leftover(leftover, now_ms)
        draw_snake(snake_pos, snake_body, direction, True, burst_active=burst1["active"])
        if settings["fog_of_war"]:
            draw_fog_of_war(snake_pos, direction)

        draw_food_pickup(food_pos, draw_apple, 0.95)
        if settings["double_food"]:
            draw_food_pickup(food2_pos, draw_apple, 0.75)

        if burst1["active"]:
            remaining = max(0, burst1["end_ms"] - now_ms)
            pulse = 0.5 + 0.5 * math.sin(now_ms / 80.0)
            r = int(255 * pulse)
            burst_font = get_font("ui", 22)
            burst_surf = burst_font.render(f"Burst active for {remaining/1000:.1f}s", True, (r, 200, 0))
            screen.blit(burst_surf, (10, 35))

        if settings["hardcore"]:
            hc_font = get_font("ui", 18)
            hc_surf = hc_font.render("HARDCORE MODE", True, (255, 40, 40))
            screen.blit(hc_surf, (10, 35))

        if now_ms < moment_until_ms:
            age = 2800 - (moment_until_ms - now_ms)
            alpha = 255
            if age < 400:      alpha = int(255 * (age / 400))
            elif age > 2300:   alpha = int(255 * max(0, (2800 - age) / 500))
            mf = get_font("title", 32)
            ms = mf.render(MOMENT_TEXT, True, (255, 220, 120))
            ms.set_alpha(alpha)
            screen.blit(ms, ms.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 90)))

        game_over = (
            (not (settings["wrap_around"] and not settings["hardcore"]) and (
                snake_pos[0] < 0 or snake_pos[0] >= SCREEN_WIDTH or
                snake_pos[1] < 0 or snake_pos[1] >= SCREEN_HEIGHT
            )) or
            any(segment == snake_pos for segment in snake_body[1:]) or
            force_die[0]
        )

        if game_over:
            force_die[0] = False
            hs = load_high_score()
            if score > hs:
                save_high_score(score)
            record_game_stats(now_ms - game_start_ms, score, cheated=cheated_this_game[0])
            pixel_fill_effect()
            result = game_over_menu(is_multiplayer=False, score1=score, high_score=load_high_score())
            if result == "play_again":
                reset_single_game()
                _spacebar_idx = 0
                haste_mult[0] = 1.0
                cheated_this_game[0] = False
                cheats.open = False
                cheats.buf  = []
                music_manager.current_music = None
                music_manager.play_music('ingame', loop=True, volume=0.5)
                draw_countdown()
                tick_accum = 0.0
                dt_ms = 1000.0 / 60.0
                game_start_ms = pygame.time.get_ticks()
                moment_shown    = False
                moment_until_ms = 0
                continue
            elif result == "main_menu":
                return "menu"
            else:
                pygame.quit()
                sys.exit()

        if debug_overlay_visible:
            draw_debug_overlay(tick_accum=tick_accum, is_multiplayer=False)

        show_score(1, COLORS["white"], "consolas", 20, score, None, game_start_ms=game_start_ms)
        cheats.draw(SCREEN_WIDTH, SCREEN_HEIGHT)
        pygame.display.update()

        fps_cap = settings["fps_limit"]
        dt_ms = min(clock.tick(fps_cap if fps_cap > 0 else 0), 100)

def _mp_controller_warning():
    font_med = get_font("ui", 24)
    font_sm  = get_font("ui", 19)
    pygame.event.clear()
    open_time = pygame.time.get_ticks()
    while True:
        draw_background()
        lm  = settings["light_mode"]
        txt = (20, 20, 20) if lm else COLORS["white"]
        dim = (100, 100, 100) if lm else (160, 160, 160)
        now_ms = pygame.time.get_ticks()
        ready  = now_ms - open_time > 400

        title_s = render_fit("title", "Only 1 controller connected", COLORS["yummers"], SCREEN_WIDTH - 60, 58, min_size=24)
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
            s = render_fit("ui", line, c, SCREEN_WIDTH - 60, 24, min_size=14) if line else font_med.render("", True, c)
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
    global snake1_pos, snake1_body, snake2_pos, snake2_body, food_pos, food2_pos, food_spawn
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
    dt_ms = 1000.0 / 60.0
    game_start_ms = pygame.time.get_ticks()

    cheats          = CheatConsole()
    mp_boost_end_ms = [0]
    cheated_this_game = [False]

    def _cheat_godofwar():
        mp_boost_end_ms[0] = pygame.time.get_ticks() + 60000
        return "Both snakes hasted for 60s."

    def _cheat_yummers():
        global food_pos, leftover
        all_pos = snake1_body + snake2_body
        food_pos = spawn_food(all_pos)
        leftover = {"pos": spawn_food(all_pos + [food_pos]), "born": pygame.time.get_ticks()}
        return "Food and leftover respawned."

    def _cheat_claude():
        music_manager._play_effect_sound()
        return "..."

    def _cheat_untildawn():
        settings["light_mode"] = not settings["light_mode"]
        _save_settings()
        return f"Theme: {'Light' if settings['light_mode'] else 'Dark'}."

    def _cheat_hello():
        return "Hello!"

    def _cheat_denied():
        return "Access was denied"

    def _cheat_svcheats():
        return "Can't change replicated ConVar sv_cheats from console of client, only server operator can change its value."

    cheat_dispatch = {
        "godofwar":         _cheat_godofwar,
        "yummers":          _cheat_yummers,
        "untildawn":        _cheat_untildawn,
        "claudeareyouhere": _cheat_claude,
        "helloskd":         _cheat_hello,
        "helloskulldozer":  _cheat_hello,
        "sv_cheats 1":      _cheat_svcheats,
        "impulse 101":      _cheat_denied,
    }

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
            elif cheats.open:
                code = cheats.feed_event(event, cheat_dispatch)
                if code in cheat_dispatch:
                    cheated_this_game[0] = True
                continue
            elif _cheat_key_open(event):
                cheats.toggle()
                continue
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
                    pygame.mixer.music.pause()
                    quit_to_menu = pause_menu(is_multiplayer=True, mode_label="Multiplayer")
                    pygame.mixer.music.unpause()
                    if quit_to_menu:
                        return "menu"
            elif event.type == pygame.WINDOWFOCUSLOST:
                pygame.mixer.music.pause()
                quit_to_menu = pause_menu(is_multiplayer=True, mode_label="Multiplayer")
                pygame.mixer.music.unpause()
                if quit_to_menu:
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

        boost = 1.5 if now_ms < mp_boost_end_ms[0] else 1.0
        eff1 = DIFFICULTY * (BURST_MULTIPLIER if burst1["active"] else 1.0) * boost
        tick_accum1 += eff1 * (dt_ms / 1000.0)
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
            elif settings["double_food"] and snake1_pos == food2_pos:
                score1 += 1
                food2_pos = spawn_food(snake1_body + snake2_body + [food_pos])
            else:
                snake1_body.pop()

            if leftover is not None and snake1_pos == leftover["pos"]:
                burst1["active"] = True
                burst1["end_ms"] = now_ms + BURST_DURATION_MS
                leftover = None

        eff2 = DIFFICULTY * (BURST_MULTIPLIER if burst2["active"] else 1.0) * boost
        tick_accum2 += eff2 * (dt_ms / 1000.0)
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
            elif settings["double_food"] and snake2_pos == food2_pos:
                score2 += 1
                food2_pos = spawn_food(snake1_body + snake2_body + [food_pos])
            else:
                snake2_body.pop()

            if leftover is not None and snake2_pos == leftover["pos"]:
                burst2["active"] = True
                burst2["end_ms"] = now_ms + BURST_DURATION_MS
                leftover = None

        if not food_spawn:
            all_snake_positions = snake1_body + snake2_body
            occ = all_snake_positions + ([food2_pos] if settings["double_food"] else [])
            food_pos = spawn_food(occ)
            food_spawn = True

        draw_background()

        draw_leftover(leftover, now_ms)
        draw_snake(snake1_pos, snake1_body, direction1, True,  burst_active=burst1["active"])
        draw_snake(snake2_pos, snake2_body, direction2, False, burst_active=burst2["active"])

        draw_food_pickup(food_pos, draw_apple, 0.95)
        if settings["double_food"]:
            draw_food_pickup(food2_pos, draw_apple, 0.75)

        hud_font = get_font("ui", 20)
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
            record_game_stats(now_ms - game_start_ms, score1 + score2,
                               cheated=cheated_this_game[0], is_mp=True, winner=winner)
            pixel_fill_effect()
            result = game_over_menu(is_multiplayer=True, score1=score1, score2=score2, winner=winner)
            if result == "play_again":
                reset_multiplayer_game()
                cheated_this_game[0] = False
                cheats.open = False
                cheats.buf  = []
                music_manager.current_music = None
                music_manager.play_music('ingame', loop=True, volume=0.5)
                draw_countdown()
                tick_accum1 = tick_accum2 = 0.0
                dt_ms = 1000.0 / 60.0
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
        cheats.draw(SCREEN_WIDTH, SCREEN_HEIGHT)
        pygame.display.update()
        fps_cap = settings["fps_limit"]
        dt_ms = min(clock.tick(fps_cap if fps_cap > 0 else 0), 100)

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
                elif isinstance(choice, tuple) and choice[0] == "shrink":
                    result = shrink_game()
                    if result == "menu":
                        break
                elif isinstance(choice, tuple) and choice[0] == "deathmatch":
                    result = deathmatch_game()
                    if result == "menu":
                        break
                elif isinstance(choice, tuple) and choice[0] == "pacifist":
                    result = pacifist_percent_game()
                    if result == "menu":
                        break
                elif isinstance(choice, tuple) and choice[0] == "trust":
                    result = trust_issues_game()
                    if result == "menu":
                        break
                elif isinstance(choice, tuple) and choice[0] == "chaos":
                    result = chaos_mode_game()
                    if result == "menu":
                        break
                elif isinstance(choice, tuple) and choice[0] == "rewind":
                    result = rewind_game()
                    if result == "menu":
                        break
        elif game_mode == "multi":
            result = multiplayer_game()
            if result == "menu":
                continue
        elif game_mode == "how_to":
            how_to_play_screen()
        else:
            pygame.quit()
            sys.exit()