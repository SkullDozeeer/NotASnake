import pygame, sys, time, random # type: ignore

difficulty = 25

dis_width = 1366
dis_height = 768

check_errors = pygame.init()
if check_errors[1] > 0:
    print(f"[!] NotASnake crashed due to {check_errors[1]} errors, cancelling start....")
    sys.exit(-10)
else:
    print("[+] NotASnake successfully initialized")

pygame.display.set_caption("NotASnake")
game_window = pygame.display.set_mode((dis_width, dis_height))

black = pygame.Color(0, 0, 0)
white = pygame.Color(255, 255, 255)
red = pygame.Color(255, 0, 0)
green = pygame.Color(0, 255, 0)
blue = pygame.Color(0, 0, 255)

fps_controller = pygame.time.Clock()

def reset_game():
    global snake_pos, snake_body, food_pos, food_spawn, direction, change_to, score
    snake_pos = [100, 50]
    snake_body = [[100, 50], [100-10, 50], [100-(2*10), 50]]
    direction = "RIGHT"
    change_to = direction
    score = 0
    food_pos = [
        random.randrange(1, (dis_width//10)) * 10,
        random.randrange(1, (dis_height//10)) * 10
    ]
    food_spawn = True

def show_score(choice, color, font, size):
    score_font = pygame.font.SysFont(font, size)
    score_surface = score_font.render("Score : " + str(score), True, color)
    score_rect = score_surface.get_rect()
    if choice == 1:
        score_rect.topleft = (dis_height/10, 15)
    else:
        score_rect.center = (dis_width//2, dis_height//1.25)
    game_window.blit(score_surface, score_rect)


def pause_menu():
    menu_font = pygame.font.SysFont("times new roman", 72)
    
    while True:
        overlay = pygame.Surface((dis_width, dis_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        game_window.blit(overlay, (0, 0))
        
        mouse_pos = pygame.mouse.get_pos()

        title_surface = menu_font.render("Paused", True, white)
        title_rect = title_surface.get_rect(center=(dis_width//2, dis_height//2 - 100))
        game_window.blit(title_surface, title_rect)

        resume_text = menu_font.render("Resume", True, white)
        resume_rect = resume_text.get_rect(center=(dis_width//2, dis_height//2))
        quit_text = menu_font.render("Quit", True, white)
        quit_rect = quit_text.get_rect(center=(dis_width//2, dis_height//2 + 100))

        if resume_rect.collidepoint(mouse_pos):
            resume_text = menu_font.render("Resume", True, green)
        if quit_rect.collidepoint(mouse_pos):
            quit_text = menu_font.render("Quit", True, red)

        game_window.blit(resume_text, resume_rect)
        game_window.blit(quit_text, quit_rect)

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
        game_window.fill(black)
        mouse_pos = pygame.mouse.get_pos()

        title_surface = pygame.font.SysFont("times new roman", 100).render("Game Over", True, red)
        title_rect = title_surface.get_rect(center=(dis_width//2, dis_height//2 - 100))
        game_window.blit(title_surface, title_rect)
        show_score(0, white, "times", 20)

        play_again_text = menu_font.render("Play Again", True, white)
        play_again_rect = play_again_text.get_rect(center=(dis_width//2, dis_height//2 + 50))
        exit_text = menu_font.render("Exit", True, white)
        exit_rect = exit_text.get_rect(center=(dis_width//2, dis_height//2 + 150))

        if play_again_rect.collidepoint(mouse_pos):
            play_again_text = menu_font.render("Play Again", True, green)
        if exit_rect.collidepoint(mouse_pos):
            exit_text = menu_font.render("Exit", True, red)

        game_window.blit(play_again_text, play_again_rect)
        game_window.blit(exit_text, exit_rect)

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
        game_window.fill(black)
        mouse_pos = pygame.mouse.get_pos()

        title_surface = pygame.font.SysFont("times new roman", 100).render("NotASnake", True, green)
        title_rect = title_surface.get_rect(center=(dis_width//2, dis_height//2 - 100))
        game_window.blit(title_surface, title_rect)

        start_text = menu_font.render("Start Game", True, white)
        start_rect = start_text.get_rect(center=(dis_width//2, dis_height//2 + 50))
        exit_text = menu_font.render("Exit", True, white)
        exit_rect = exit_text.get_rect(center=(dis_width//2, dis_height//2 + 150))

        if start_rect.collidepoint(mouse_pos):
            start_text = menu_font.render("Start Game", True, green)
        if exit_rect.collidepoint(mouse_pos):
            exit_text = menu_font.render("Exit", True, red)

        game_window.blit(start_text, start_rect)
        game_window.blit(exit_text, exit_rect)

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

#this shouldnt work, it doesnt have to work, but it may just do work, even if i will have to fix it later on :(
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP or event.key == ord("w"):
                change_to = "UP"
            if event.key == pygame.K_DOWN or event.key == ord("s"):
                change_to = "DOWN"
            if event.key == pygame.K_LEFT or event.key == ord("a"):
                change_to = "LEFT"
            if event.key == pygame.K_RIGHT or event.key == ord("d"):
                change_to = "RIGHT"
            if event.key == pygame.K_ESCAPE:
                if pause_menu():
                    pygame.quit()
                    sys.exit()
        elif event.type == pygame.ACTIVEEVENT:
            if event.state == pygame.APPINPUTFOCUS:
                if not event.gain:
                    if pause_menu():
                        pygame.quit()
                        sys.exit()

    for event in pygame.event.get():
        if event.type == pygame.ACTIVEEVENT:
            if event.state == pygame.APPINPUTFOCUS:
                if not event.gain:
                    pause_menu()

    if change_to == "UP" and direction != "DOWN":
        direction = "UP"
    if change_to == "DOWN" and direction != "UP":
        direction = "DOWN"
    if change_to == "LEFT" and direction != "RIGHT":
        direction = "LEFT"
    if change_to == "RIGHT" and direction != "LEFT":
        direction = "RIGHT"

    if direction == "UP":
        snake_pos[1] -= 10
    if direction == "DOWN":
        snake_pos[1] += 10
    if direction == "LEFT":
        snake_pos[0] -= 10
    if direction == "RIGHT":
        snake_pos[0] += 10

    snake_body.insert(0, list(snake_pos))
    if snake_pos[0] == food_pos[0] and snake_pos[1] == food_pos[1]:
        score += 1
        food_spawn = False
    else:
        snake_body.pop()

  
    if not food_spawn:
        food_pos = spawn_food()
        food_spawn = True


    def spawn_food():
        while True:
            new_pos = [
                random.randrange(1, (dis_width // 10)) * 10,
                random.randrange(1, (dis_height // 10)) * 10
            ]
            if new_pos not in snake_body:
                return new_pos



    if not food_spawn:
        food_pos = spawn_food()
        food_spawn = True

    game_window.fill(black)
    for pos in snake_body:
        pygame.draw.rect(game_window, green, pygame.Rect(pos[0], pos[1], 10, 10))
    pygame.draw.rect(game_window, white, pygame.Rect(food_pos[0], food_pos[1], 10, 10))

    game_over = False
    if snake_pos[0] < 0 or snake_pos[0] > dis_width-10:
        game_over = True
    if snake_pos[1] < 0 or snake_pos[1] > dis_height-10:
        game_over = True
    for block in snake_body[1:]:
        if snake_pos[0] == block[0] and snake_pos[1] == block[1]:
            game_over = True

    if game_over:
        if game_over_menu():
            reset_game()
            main_menu()
        else:
            pygame.quit()
            sys.exit()

    show_score(1, white, "consolas", 20)

    pygame.display.update()
    fps_controller.tick(difficulty)
