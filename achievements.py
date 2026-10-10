MODE_KEYS = ["endless", "sa", "shrink", "deathmatch", "pacifist", "trust", "chaos", "rewind", "mp"]

def _has_nondefault_setting(data):
    defaults = {
        "music_muted": False, "wrap_around": False, "light_mode": False,
        "show_timer": False, "hardcore": False, "double_food": True,
        "fog_of_war": False, "snake_pattern": True,
        "grid_opacity": 0, "fps_limit": 60, "start_length": 3,
        "control_scheme": "wasd_arrows", "bg_style": "plain",
    }
    for k, dv in defaults.items():
        if data.get(k, dv) != dv:
            return True
    return False

ACHIEVEMENTS = [
    {
        "id": "no_jump",
        "name": "There is no jump.",
        "desc": "Press the space bar. Not using Wildcard.",
        "check": lambda d: d.get("ach_pressed_space_no_wildcard", False),
    },
    {
        "id": "die_instant",
        "name": "Uh, why?",
        "desc": "Die in 5 seconds within starting a game.",
        "check": lambda d: d.get("ach_died_instant", False),
    },
    {
        "id": "hardcore_start",
        "name": "Basic.",
        "desc": "Enable Hardcore mode and start a game.",
        "check": lambda d: d.get("ach_hardcore_start", False),
    },
    {
        "id": "fog_start",
        "name": "...a tank is still visible",
        "desc": "Enable Fog of War in settings and start a game.",
        "check": lambda d: d.get("ach_fog_start", False),
    },
    {
        "id": "sa_start",
        "name": "Attacked!",
        "desc": "Start a Score Attack game.",
        "check": lambda d: d.get("ach_mode_start_sa", False),
    },
    {
        "id": "sa_win_50",
        "name": "Small snake...",
        "desc": "Win a 50 point Score Attack game.",
        "check": lambda d: d.get("sa_best_50", 0) > 0,
    },
    {
        "id": "seeded_game",
        "name": "Seeded.",
        "desc": "Play a game with a seed set.",
        "check": lambda d: d.get("ach_seeded_game", False),
    },
    {
        "id": "shrink_start",
        "name": "Woah-woah-woah!!",
        "desc": "Start a Shrink game.",
        "check": lambda d: d.get("ach_mode_start_shrink", False),
    },
    {
        "id": "pacifist_start",
        "name": "DO NOT THE APPLE",
        "desc": "Start a Pacifist% game.",
        "check": lambda d: d.get("ach_mode_start_pacifist", False),
    },
    {
        "id": "deathmatch_start",
        "name": "This is very popular amongst teenagers.",
        "desc": "Start a Deathmatch game.",
        "check": lambda d: d.get("ach_mode_start_deathmatch", False),
    },
    {
        "id": "trust_start",
        "name": "Are you... sure?",
        "desc": "Start a Trust Issues game.",
        "check": lambda d: d.get("ach_mode_start_trust", False),
    },
    {
        "id": "chaos_start",
        "name": "What is a wildca-",
        "desc": "Start a Chaos Mode game.",
        "check": lambda d: d.get("ach_mode_start_chaos", False),
    },
    {
        "id": "rewind_start",
        "name": "I love that one Doctor.",
        "desc": "Start a Rewind game.",
        "check": lambda d: d.get("ach_mode_start_rewind", False),
    },
    {
        "id": "rewind_full_charge",
        "name": "Fully charged.",
        "desc": "Finish a Rewind game without using a single rewind.",
        "check": lambda d: d.get("ach_rewind_full_charge", False),
    },
    {
        "id": "rewind_no_charge",
        "name": "No taksies-backsies!",
        "desc": "Use up all rewind charges in one Rewind game.",
        "check": lambda d: d.get("ach_rewind_no_charge", False),
    },
    {
        "id": "all_modes",
        "name": "Been there, seen it all",
        "desc": "Start a game in every mode.",
        "check": lambda d: all(d.get(f"ach_mode_start_{m}", False) for m in MODE_KEYS),
    },
    {
        "id": "mp_start",
        "name": "MP",
        "desc": "Start a Local Multiplayer game.",
        "check": lambda d: d.get("ach_mode_start_mp", False),
    },
    {
        "id": "mp_solo_death",
        "name": "One man's treasure...",
        "desc": "Lose a Local MP game where only one player dies.",
        "check": lambda d: d.get("ach_mp_solo_death", False),
    },
    {
        "id": "mp_tie",
        "name": "No Happy Endings in Snake town.",
        "desc": "Tie in a Local MP game.",
        "check": lambda d: d.get("mp_ties", 0) > 0,
    },
    {
        "id": "mp_tie_zero_food",
        "name": "Brother, move!",
        "desc": "Tie a Local MP game where neither player ate any food.",
        "check": lambda d: d.get("ach_mp_tie_zero_food", False),
    },
    {
        "id": "cheat_used",
        "name": "Ban him!",
        "desc": "Activate any cheat.",
        "check": lambda d: d.get("games_cheated", 0) > 0,
    },
    {
        "id": "settings_changed_play",
        "name": "...way or the highway",
        "desc": "Start a game with any non-default setting active.",
        "check": lambda d: d.get("ach_nondefault_setting_play", False),
    },
    {
        "id": "screenshot_manual",
        "name": "*Click-click*",
        "desc": "Take a manual screenshot (F12).",
        "check": lambda d: d.get("ach_manual_screenshot", False),
    },
    {
        "id": "fog_death_10",
        "name": "Like a Bull in a China shop.",
        "desc": "Die 10 times total while playing with Fog of War enabled.",
        "check": lambda d: d.get("fog_deaths", 0) >= 10,
    },
    {
        "id": "wildcard_tutorial",
        "name": "It's not cool if some can't play...",
        "desc": "Enable Wildcard and get through its instruction popup.",
        "check": lambda d: "wildcard_controls" in d.get("seen_tips", set()),
    },
    {
        "id": "apples_100",
        "name": "Hungry snake.",
        "desc": "Eat 100 apples, all-time.",
        "check": lambda d: d.get("total_apples", 0) >= 100,
    },
    {
        "id": "apples_1000",
        "name": "A very hungry snake.",
        "desc": "Eat 1000 apples, all-time.",
        "check": lambda d: d.get("total_apples", 0) >= 1000,
    },
    {
        "id": "secret_50",
        "name": "More to discover...",
        "desc": "Get Good. That's how.",
        "desc_unlocked": "That's a great easter egg, nah?",
        "secret": True,
        "check": lambda d: d.get("ach_secret_50", False),
    },
]

_BY_ID = {a["id"]: a for a in ACHIEVEMENTS}

def ordered_ids(ids):
    """Return achievement IDs in the canonical display/unlock order."""
    wanted = set(ids)
    return [a["id"] for a in ACHIEVEMENTS if a["id"] in wanted]

def compute_unlocked(data):
    return {a["id"] for a in ACHIEVEMENTS if a["check"](data)}

def get_achievement(aid):
    return _BY_ID.get(aid)
