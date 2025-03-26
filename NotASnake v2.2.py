import pygame, sys, time, random # type: ignore

# Difficulty settings
# Real Sloth Gameplay - 5
# Standard - 25
# Hard - 50
# Insane - 100
# Dark Souls Type Shit - 200
difficulty = 25


dis_width = 1366
dis_height = 768


check_errors = pygame.init()
if check_errors[1] > 0:
    print(f"[!] NotASnake crashed due to {check_errors[1]} errors, cancelling start....")
    sys.exit(-10)
else:
    print("[+] NotASnake succesfully initialized")


pygame.display.set_caption("NotASnake")
game_window = pygame.display.set_mode((dis_width, dis_height))

black = pygame.Color(0, 0, 0)
white = pygame.Color(255, 255, 255)
red = pygame.Color(255, 0, 0)
green = pygame.Color(0, 255, 0)
blue = pygame.Color(0, 0, 255)


fps_controller = pygame.time.Clock()

def game_over():
    my_font = pygame.font.SysFont("times new roman", 150)
    game_over_surface = my_font.render("You Lost", True, red)
    game_over_rect = game_over_surface.get_rect(center=(dis_width//2, dis_height//2))
    game_window.fill(black)
    game_window.blit(game_over_surface, game_over_rect)
    show_score(0, red, "times", 20)
    pygame.display.flip()
    time.sleep(3)
    pygame.quit()
    sys.exit()

def show_score(choice, color, font, size):
    score_font = pygame.font.SysFont(font, size)
    score_surface = score_font.render("Score : " + str(score), True, color)
    score_rect = score_surface.get_rect()
    if choice == 1:
        score_rect.topleft = (dis_height/10, 15)
    else:
        score_rect.center = (dis_width//2, dis_height//1.25)
    game_window.blit(score_surface, score_rect)


def main_menu():
    menu_font = pygame.font.SysFont("times new roman", 72)
    
    while True:
        game_window.fill(black)
        mouse_pos = pygame.mouse.get_pos()

        
        title_font = pygame.font.SysFont("times new roman", 100)
        title_surface = title_font.render("NotASnake", True, red)
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


snake_pos = [100, 50]
snake_body = [[100, 50], [100-10, 50], [100-(2*10), 50]]
food_pos = [random.randrange(1, (dis_width//10)) * 10, 
            random.randrange(1, (dis_height//10)) * 10]
food_spawn = True
direction = "RIGHT"
change_to = direction
score = 0


main_menu()


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
                pygame.event.post(pygame.event.Event(pygame.QUIT))

    
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
        food_pos = [random.randrange(1, (dis_width//10)) * 10,
                    random.randrange(1, (dis_height//10)) * 10]
    food_spawn = True

    game_window.fill(black)
    for pos in snake_body:
        pygame.draw.rect(game_window, green, pygame.Rect(pos[0], pos[1], 10, 10))
    pygame.draw.rect(game_window, white, pygame.Rect(food_pos[0], food_pos[1], 10, 10))

    
    if snake_pos[0] < 0 or snake_pos[0] > dis_width-10:
        game_over()
    if snake_pos[1] < 0 or snake_pos[1] > dis_height-10:
        game_over()
    for block in snake_body[1:]:
        if snake_pos[0] == block[0] and snake_pos[1] == block[1]:
            game_over()


    show_score(1, white, "consolas", 20)

    
    pygame.display.update()
    fps_controller.tick(difficulty)
