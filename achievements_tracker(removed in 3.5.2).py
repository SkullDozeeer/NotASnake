import sys
import os
import time
import importlib.util

import pygame

def _base_dir():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def _load_achievements_module():
    ach_path = os.path.join(_base_dir(), "nasassets", "achievements.py")
    spec = importlib.util.spec_from_file_location("nas_achievements", ach_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

_ach = _load_achievements_module()

def _get_save_path():
    return os.path.join(_base_dir(), "nasassets", "save.txt")

_SETTINGS_BOOL_KEYS  = ["music_muted", "wrap_around", "light_mode", "show_timer", "hardcore", "double_food", "fog_of_war", "snake_pattern"]
_SETTINGS_INT_KEYS   = ["grid_opacity", "fps_limit", "start_length"]
_SETTINGS_STR_KEYS   = ["control_scheme", "bg_style"]
_STATS_INT_KEYS      = [
    "total_apples", "games_played", "games_cheated", "games_mp",
    "mp_p1_wins", "mp_p2_wins", "mp_ties", "longest_game_ms", "shortest_game_ms",
    "fog_deaths",
]
_ACH_FLAG_KEYS = [
    "ach_pressed_space_no_wildcard", "ach_died_instant", "ach_hardcore_start",
    "ach_fog_start", "ach_seeded_game", "ach_rewind_full_charge", "ach_rewind_no_charge",
    "ach_mp_solo_death", "ach_mp_tie_zero_food", "ach_nondefault_setting_play",
    "ach_manual_screenshot", "ach_secret_50",
] + [f"ach_mode_start_{m}" for m in ["endless", "sa", "shrink", "deathmatch", "pacifist", "trust", "chaos", "rewind", "mp"]]

def load_save_readonly():
    path = _get_save_path()
    data = {
        "score": 0, "seed": "", "double_food": True,
        "apples": set(), "sa_best_15": 0, "sa_best_30": 0, "sa_best_50": 0,
        "shrink_best": 0, "dm_best_ms": 0,
        "pacifist_best": 0, "trust_best": 0, "chaos_best": 0, "rewind_best": 0,
        "seen_tips": set(), "achievements": set(),
    }
    for k in _STATS_INT_KEYS:
        data[k] = 0
    for k in _ACH_FLAG_KEYS:
        data[k] = False
    for k in _SETTINGS_BOOL_KEYS:
        data[k] = False
    data["double_food"] = True
    data["snake_pattern"] = True
    for k in _SETTINGS_INT_KEYS:
        data[k] = 0
    data["fps_limit"] = 60
    data["start_length"] = 3
    data["control_scheme"] = "wasd_arrows"
    data["bg_style"] = "plain"

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
                elif key == "achievements":
                    if val:
                        data["achievements"] = set(x for x in val.split(",") if x.strip())
                elif key in _ACH_FLAG_KEYS:
                    data[key] = val == "1"
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
        pass
    except Exception as e:
        print(f"tracker: load_save borked: {e}")
    return data

COLORS = {
    "black": pygame.Color(0, 0, 0),
    "white": pygame.Color(255, 255, 255),
    "green": pygame.Color(0, 255, 0),
    "purpleguy": pygame.Color(160, 32, 240),
    "cyan": pygame.Color(0, 255, 255),
    "yummers": pygame.Color(255, 200, 0),
    "red": pygame.Color(255, 0, 0),
}

WIDTH, HEIGHT = 460, 640
POLL_MS = 300
FLASH_MS = 3000

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
    pygame.display.set_caption("NotASnake - Achievements Tracker")
    clock = pygame.time.Clock()

    font_title = pygame.font.SysFont("times new roman", 34)
    font_name  = pygame.font.SysFont("consolas", 17, bold=True)
    font_desc  = pygame.font.SysFont("consolas", 14)
    font_count = pygame.font.SysFont("consolas", 16)
    font_small = pygame.font.SysFont("consolas", 12)

    last_poll = 0
    unlocked = set()
    flash_queue = []
    scroll = 0
    first_load = True

    running = True
    while running:
        now_ms = pygame.time.get_ticks()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.VIDEORESIZE:
                screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
            elif event.type == pygame.MOUSEWHEEL:
                scroll = max(0, scroll - event.y * 30)

        if now_ms - last_poll >= POLL_MS:
            last_poll = now_ms
            data = load_save_readonly()
            newly = _ach.compute_unlocked(data)
            if not first_load:
                just_unlocked = newly - unlocked
                for aid in _ach.ordered_ids(just_unlocked):
                    a = _ach.get_achievement(aid)
                    if a:
                        # Start the lifetime only when this toast reaches the front.
                        flash_queue.append({"name": a["name"], "start_ms": None, "until_ms": None})
            unlocked = newly
            first_load = False

        if flash_queue:
            toast = flash_queue[0]
            if toast["start_ms"] is None:
                toast["start_ms"] = now_ms
                toast["until_ms"] = now_ms + FLASH_MS
            if now_ms >= toast["until_ms"]:
                flash_queue.pop(0)
                if flash_queue:
                    toast = flash_queue[0]
                    toast["start_ms"] = now_ms
                    toast["until_ms"] = now_ms + FLASH_MS

        w, h = screen.get_size()
        screen.fill(COLORS["black"])

        title_s = font_title.render("Achievements", True, COLORS["green"])
        screen.blit(title_s, title_s.get_rect(center=(w // 2, 30)))

        count_s = font_count.render(f"{len(unlocked)} / {len(_ach.ACHIEVEMENTS)}", True, COLORS["purpleguy"])
        screen.blit(count_s, count_s.get_rect(center=(w // 2, 60)))

        content_top = 90
        content_bottom = h - 10
        clip_rect = pygame.Rect(0, content_top, w, content_bottom - content_top)
        screen.set_clip(clip_rect)

        y = content_top - scroll
        pad_x = 16
        row_h = 52
        for a in _ach.ACHIEVEMENTS:
            is_unlocked = a["id"] in unlocked
            is_secret = a.get("secret", False)

            dot_col = COLORS["green"] if is_unlocked else (70, 70, 70)
            pygame.draw.circle(screen, dot_col, (pad_x + 6, y + 12), 6)

            if is_unlocked:
                name_col = COLORS["yummers"]
                desc_col = COLORS["white"]
                name_txt = a["name"]
                desc_txt = a.get("desc_unlocked", a["desc"])
            elif is_secret:
                name_col = (110, 110, 110)
                desc_col = (90, 90, 90)
                name_txt = "???"
                desc_txt = "???"
            else:
                name_col = COLORS["white"]
                desc_col = (140, 140, 140)
                name_txt = a["name"]
                desc_txt = a["desc"]

            name_s = font_name.render(name_txt, True, name_col)
            screen.blit(name_s, (pad_x + 22, y))
            desc_s = font_desc.render(desc_txt, True, desc_col)
            screen.blit(desc_s, (pad_x + 22, y + 22))

            pygame.draw.line(screen, (40, 40, 60), (pad_x, y + row_h - 8), (w - pad_x, y + row_h - 8), 1)
            y += row_h

        max_scroll = max(0, y + scroll - content_bottom)
        scroll = max(0, min(scroll, max_scroll))
        screen.set_clip(None)

        if flash_queue:
            toast = flash_queue[0]
            remaining = toast["until_ms"] - now_ms
            alpha = 255
            if remaining < 400:
                alpha = int(255 * (remaining / 400))
            title_ts = font_small.render("UNLOCKED", True, COLORS["yummers"])
            name_ts = font_name.render(toast["name"], True, COLORS["white"])
            bw = max(title_ts.get_width(), name_ts.get_width()) + 24
            bh = title_ts.get_height() + name_ts.get_height() + 20
            bx = w // 2 - bw // 2
            by = content_top + 4
            panel = pygame.Surface((bw, bh), pygame.SRCALPHA)
            panel.fill((15, 15, 30, min(230, alpha)))
            panel.blit(title_ts, (12, 8))
            panel.blit(name_ts, (12, 8 + title_ts.get_height() + 2))
            screen.blit(panel, (bx, by))
            pygame.draw.rect(screen, COLORS["purpleguy"], (bx, by, bw, bh), 2)

        pygame.display.flip()
        clock.tick(30)

    pygame.quit()

if __name__ == "__main__":
    main()
