import pygame
import sys
import random
DIFFICULTY = 10
SCREEN_WIDTH = 1366
SCREEN_HEIGHT = 768
CELL_SIZE = 25  
COLORS = {
    "black": pygame.Color(0, 0, 0),
    "white": pygame.Color(255, 255, 255),
    "red": pygame.Color(255, 0, 0),
    "green": pygame.Color(0, 255, 0),
    "blue": pygame.Color(0, 0, 255),
    "head": pygame.Color(247, 33, 33),
    "food": pygame.Color(255, 200, 0)  
}


pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption(f"NotASnake v2.6")
clock = pygame.time.Clock()


def reset_game():
    global snake_pos, snake_body, food_pos, food_spawn, direction, change_to, score
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
    food_pos = spawn_food()
    food_spawn = True

def spawn_food():
    while True:
        new_pos = [
            random.randrange(1, (SCREEN_WIDTH // CELL_SIZE)) * CELL_SIZE,
            random.randrange(1, (SCREEN_HEIGHT // CELL_SIZE)) * CELL_SIZE
        ]
        if new_pos not in snake_body:
            return new_pos

def show_score(choice, color, font, size):
    score_font = pygame.font.SysFont(font, size)
    score_text = f"NotASnake v2.6 | Cell size: {CELL_SIZE}"
    score_surface = score_font.render(score_text, True, color)
    if choice == 1:
        screen.blit(score_surface, (10, 10))
    else:
        screen.blit(score_surface, (SCREEN_WIDTH//2 - 150, SCREEN_HEIGHT//1.25))


def pause_menu():
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
        quit_text = menu_font.render("Quit", True, COLORS["white"])
        quit_rect = quit_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100))

        if resume_rect.collidepoint(mouse_pos):
            resume_text = menu_font.render("Resume", True, COLORS["green"])
        if quit_rect.collidepoint(mouse_pos):
            quit_text = menu_font.render("Quit", True, COLORS["red"])

        screen.blit(resume_text, resume_rect)
        screen.blit(quit_text, quit_rect)

        info_font = pygame.font.SysFont("consolas", 22)
        info_text = f"Cell size: {CELL_SIZE}px | Grid: {SCREEN_WIDTH//CELL_SIZE}x{SCREEN_HEIGHT//CELL_SIZE}"
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
                if event.key == pygame.K_ESCAPE:
                    return False
                elif event.key == pygame.K_RETURN:
                    return True

        pygame.display.update()


def game_over_menu():
    menu_font = pygame.font.SysFont("times new roman", 72)

    while True:
        screen.fill(COLORS["black"])
        mouse_pos = pygame.mouse.get_pos()

        title_surface = pygame.font.SysFont("times new roman", 90).render("Game Over", True, COLORS["red"])
        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100))
        screen.blit(title_surface, title_rect)
        show_score(0, COLORS["white"], "times", 20)

        play_again_text = menu_font.render("Play Again", True, COLORS["white"])
        play_again_rect = play_again_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
        exit_text = menu_font.render("Exit", True, COLORS["white"])
        exit_rect = exit_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 150))

        if play_again_rect.collidepoint(mouse_pos):
            play_again_text = menu_font.render("Play Again", True, COLORS["green"])
        if exit_rect.collidepoint(mouse_pos):
            exit_text = menu_font.render("Exit", True, COLORS["red"])

        screen.blit(play_again_text, play_again_rect)
        screen.blit(exit_text, exit_rect)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if play_again_rect.collidepoint(event.pos):
                    return True
                elif exit_rect.collidepoint(event.pos):
                    return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return True
                elif event.key == pygame.K_ESCAPE:
                    return False

        pygame.display.update()


def main_menu():
    menu_font = pygame.font.SysFont("times new roman", 72)

    while True:
        screen.fill(COLORS["black"])
        mouse_pos = pygame.mouse.get_pos()

        title_surface = pygame.font.SysFont("times new roman", 100).render("NotASnake v2.6", True, COLORS["green"])
        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100))
        screen.blit(title_surface, title_rect)
        info_font = pygame.font.SysFont("consolas", 28)
        info_text = f"Cell size: {CELL_SIZE} | Grid: {SCREEN_WIDTH//CELL_SIZE}x{SCREEN_HEIGHT//CELL_SIZE}"
        info_surface = info_font.render(info_text, True, COLORS["white"])
        info_rect = info_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20))
        screen.blit(info_surface, info_rect)

        start_text = menu_font.render("Start Game", True, COLORS["white"])
        start_rect = start_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 80))
        exit_text = menu_font.render("Exit", True, COLORS["white"])
        exit_rect = exit_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 180))

        if start_rect.collidepoint(mouse_pos):
            start_text = menu_font.render("Start Game", True, COLORS["green"])
        if exit_rect.collidepoint(mouse_pos):
            exit_text = menu_font.render("Exit", True, COLORS["red"])

        screen.blit(start_text, start_rect)
        screen.blit(exit_text, exit_rect)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if start_rect.collidepoint(event.pos):
                    return
                elif exit_rect.collidepoint(event.pos):
                    pygame.quit()
                    sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

        pygame.display.update()


reset_game()
main_menu()

while True:
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
            elif event.key == pygame.K_ESCAPE:
                if pause_menu():
                    pygame.quit()
                    sys.exit()
        elif event.type == pygame.ACTIVEEVENT:
            if event.state == pygame.APPINPUTFOCUS and not event.gain:
                if pause_menu():
                    pygame.quit()
                    sys.exit()


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
    else:
        snake_body.pop()


    if not food_spawn:
        food_pos = spawn_food()
        food_spawn = True


    screen.fill(COLORS["black"])
   
    for idx, pos in enumerate(snake_body):
        if idx == 0:  
            color = COLORS["head"]
            
            pygame.draw.rect(screen, color, pygame.Rect(
                pos[0], pos[1], CELL_SIZE, CELL_SIZE
            ))
            eye_size = CELL_SIZE // 5
            if direction == "RIGHT":
                pygame.draw.rect(screen, COLORS["white"], pygame.Rect(
                    pos[0] + CELL_SIZE - eye_size*2, pos[1] + eye_size, 
                    eye_size, eye_size
                ))
                pygame.draw.rect(screen, COLORS["white"], pygame.Rect(
                    pos[0] + CELL_SIZE - eye_size*2, pos[1] + CELL_SIZE - eye_size*2, 
                    eye_size, eye_size
                ))
            elif direction == "LEFT":
                pygame.draw.rect(screen, COLORS["white"], pygame.Rect(
                    pos[0] + eye_size, pos[1] + eye_size, 
                    eye_size, eye_size
                ))
                pygame.draw.rect(screen, COLORS["white"], pygame.Rect(
                    pos[0] + eye_size, pos[1] + CELL_SIZE - eye_size*2, 
                    eye_size, eye_size
                ))
            elif direction == "UP":
                pygame.draw.rect(screen, COLORS["white"], pygame.Rect(
                    pos[0] + eye_size, pos[1] + eye_size, 
                    eye_size, eye_size
                ))
                pygame.draw.rect(screen, COLORS["white"], pygame.Rect(
                    pos[0] + CELL_SIZE - eye_size*2, pos[1] + eye_size, 
                    eye_size, eye_size
                ))
            elif direction == "DOWN":
                pygame.draw.rect(screen, COLORS["white"], pygame.Rect(
                    pos[0] + eye_size, pos[1] + CELL_SIZE - eye_size*2, 
                    eye_size, eye_size
                ))
                pygame.draw.rect(screen, COLORS["white"], pygame.Rect(
                    pos[0] + CELL_SIZE - eye_size*2, pos[1] + CELL_SIZE - eye_size*2, 
                    eye_size, eye_size
                ))
        else: 
            color_intensity = max(100, 255 - (idx * 5))
            body_color = (0, color_intensity, 0)
            pygame.draw.rect(screen, body_color, pygame.Rect(
                pos[0], pos[1], CELL_SIZE, CELL_SIZE
            ))
            pygame.draw.rect(screen, (0, 200, 0), pygame.Rect(
                pos[0], pos[1], CELL_SIZE, CELL_SIZE
            ), 1)
  
    pygame.draw.rect(screen, COLORS["food"], pygame.Rect(
        food_pos[0], food_pos[1], CELL_SIZE, CELL_SIZE
    ))
    pygame.draw.rect(screen, (255, 255, 200), pygame.Rect(
        food_pos[0] + CELL_SIZE//4, food_pos[1] + CELL_SIZE//4, 
        CELL_SIZE//4, CELL_SIZE//4
    ))


    game_over = (
        snake_pos[0] < 0 or snake_pos[0] >= SCREEN_WIDTH or
        snake_pos[1] < 0 or snake_pos[1] >= SCREEN_HEIGHT or
        any(segment == snake_pos for segment in snake_body[1:])
    )

    if game_over:
        if game_over_menu():
            reset_game()
        else:
            pygame.quit()
            sys.exit()

    show_score(1, COLORS["white"], "consolas", 20)
    pygame.display.update()
    clock.tick(DIFFICULTY)