import pygame, sys, time, random # type: ignore

# Difficulty settings for nerds and modders
# Easy      ->  10
# Medium    ->  25
# Hard      ->  40
# Harder    ->  60
# Impossible->  120
difficulty = 25


dis_width = 1366
dis_height = 768


check_errors = pygame.init()

if check_errors[1] > 0:
    print(
        f"[!] NotASnake crashed due to {check_errors[1]} errors when initialising game, cancelling start...."
    )
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


snake_pos = [100, 50]
snake_body = [[100, 50], [100 - 10, 50], [100 - (2 * 10), 50]]

food_pos = [
    random.randrange(1, (dis_width // 10)) * 10,
    random.randrange(1, (dis_height // 10)) * 10,
]
food_spawn = True

direction = "RIGHT"
change_to = direction

score = 0


def game_over():
    my_font = pygame.font.SysFont("times new roman", 150)
    game_over_surface = my_font.render("You Lost", True, red)
    game_over_rect = game_over_surface.get_rect(
        center=(dis_width // 2, dis_height // 2)
    )  # Solve of the You Lost! text problem was actually here lol
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
        score_rect.topleft = (dis_height / 10, 15)  # in-game score
    else:
        score_rect.center = (dis_width // 2, dis_height // 1.25)  # death score
    game_window.blit(score_surface, score_rect)


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

    snake_body.insert(
        0, list(snake_pos)
    )  # Add the new head to the beginning of the body
    if snake_pos[0] == food_pos[0] and snake_pos[1] == food_pos[1]:
        score += 1
        food_spawn = False
    else:
        snake_body.pop()  # Remove the tail if the snake didn't eat food

    if not food_spawn:
        food_pos = [
            random.randrange(1, (dis_width // 10)) * 10,
            random.randrange(1, (dis_height // 10)) * 10,
        ]
    food_spawn = True

    game_window.fill(black)
    for pos in snake_body:

        pygame.draw.rect(game_window, green, pygame.Rect(pos[0], pos[1], 10, 10))

    pygame.draw.rect(game_window, white, pygame.Rect(food_pos[0], food_pos[1], 10, 10))

    if snake_pos[0] < 0 or snake_pos[0] > dis_width - 10:
        game_over()
    if snake_pos[1] < 0 or snake_pos[1] > dis_height - 10:
        game_over()

    for block in snake_body[1:]:
        if snake_pos[0] == block[0] and snake_pos[1] == block[1]:
            game_over()

    show_score(1, white, "consolas", 20)

    pygame.display.update()

    fps_controller.tick(difficulty)

def start_game():
    """Starts the game in a separate thread."""
    def run_game():
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                # ... (rest of your game loop) ...

    game_thread = threading.Thread(target=run_game)
    game_thread.start()
    root.destroy()  # Close the menu after starting the game


def create_menu():
    """Creates the main menu using Tkinter."""
    global root
    root = tk.Tk()
    root.title("NotASnake - Menu")

    start_button = tk.Button(root, text="Start Game", command=start_game)
    start_button.pack(pady=10)

    exit_button = tk.Button(root, text="Exit", command=root.destroy)
    exit_button.pack(pady=10)

    root.mainloop()


if __name__ == "__main__":
    # Initialize Pygame (this part remains unchanged)
  
    
    pygame.display.set_caption("NotASnake")
    #game_window = pygame.display.set_mode((dis_width, dis_height)) #moved to inside start_game()


    # Create and run the Tkinter menu
    create_menu()
