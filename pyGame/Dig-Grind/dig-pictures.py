import pygame
import random

# Initialize pygame
pygame.init()

# Initialize the mixer
pygame.mixer.init()

# Load the pop sound
pop_sound = pygame.mixer.Sound('pop.mp3')

# Load images
background_img = pygame.image.load('background.png')
square_img = pygame.image.load('square.png')
circle_img = pygame.image.load('circle.png')

# Constants
WIDTH, HEIGHT = 375, 375
ROWS, COLS = 3, 3
SQUARE_SIZE = WIDTH // COLS
ANIMATION_TIME_WIN = 2100  # milliseconds for the winning animation
ANIMATION_TIME_LOSE = 600  # milliseconds for the losing animation
BLINK_INTERVAL = 400  # milliseconds for each blink
BORDER_SIZE = 40  # Size of the border

# Game settings
NUM_CIRCLES = 1
MAX_CLICKS = 3

TEXT_COLOR = (255, 255, 255)  # White
SHADOW_COLOR = (0, 0, 0)  # Black for shadow
BLINK_COLOR = (0, 255, 0)  # Neon Green

# Resize images
background_img = pygame.transform.scale(background_img, (WIDTH + 2 * BORDER_SIZE, HEIGHT + 2 * BORDER_SIZE))
square_img = pygame.transform.scale(square_img, (SQUARE_SIZE, SQUARE_SIZE))
circle_img = pygame.transform.scale(circle_img, (SQUARE_SIZE // 2, SQUARE_SIZE // 2))

# Setup the screen
screen = pygame.display.set_mode((WIDTH + 2 * BORDER_SIZE, HEIGHT + 2 * BORDER_SIZE))
pygame.display.set_caption("Reveal the Circles")

# Font
font = pygame.font.SysFont("Bauhaus 93", 24, bold=False)

# Centering the grid
GRID_START_X = BORDER_SIZE
GRID_START_Y = BORDER_SIZE

def draw_grid(grid, circles_pos, reveal=False, blink=False):
    screen.blit(background_img, (0, 0))
    for row in range(ROWS):
        for col in range(COLS):
            rect = pygame.Rect(col * SQUARE_SIZE + GRID_START_X, row * SQUARE_SIZE + GRID_START_Y, SQUARE_SIZE, SQUARE_SIZE)
            if blink:
                color = BLINK_COLOR if (pygame.time.get_ticks() % (2 * BLINK_INTERVAL)) < BLINK_INTERVAL else background_img
                if isinstance(color, tuple):
                    pygame.draw.rect(screen, color, rect)
                else:
                    screen.blit(background_img, rect.topleft, rect)
            elif grid[row][col]:
                screen.blit(square_img, rect.topleft)
            else:
                pygame.draw.rect(screen, (0, 0, 0), rect)  # Draw a black rectangle to cover the square

            pygame.draw.rect(screen, (220, 20, 60), rect, 3)  # Outline in Crimson Red

    for row, col in circles_pos:
        if not grid[row][col]:
            rect = pygame.Rect(col * SQUARE_SIZE + GRID_START_X, row * SQUARE_SIZE + GRID_START_Y, SQUARE_SIZE, SQUARE_SIZE)
            screen.blit(circle_img, circle_img.get_rect(center=rect.center))

def draw_text(points, attempts_remaining):
    points_text = font.render(f"SCORE: {points}", True, TEXT_COLOR)
    attempts_text = font.render(f"ATTEMPTS: {attempts_remaining}", True, TEXT_COLOR)
    shadow_offset = 2
    text_height = BORDER_SIZE // 3

    points_shadow = font.render(f"SCORE: {points}", True, SHADOW_COLOR)
    attempts_shadow = font.render(f"ATTEMPTS: {attempts_remaining}", True, SHADOW_COLOR)
    screen.blit(points_shadow, (BORDER_SIZE + shadow_offset, text_height + shadow_offset))
    screen.blit(attempts_shadow, (WIDTH // 2 + BORDER_SIZE - attempts_text.get_width() // 2 + shadow_offset, text_height + shadow_offset))

    screen.blit(points_text, (BORDER_SIZE, text_height))
    screen.blit(attempts_text, (WIDTH // 2 + BORDER_SIZE - attempts_text.get_width() // 2, text_height))

def reset_grid():
    grid = [[True for _ in range(COLS)] for _ in range(ROWS)]
    circles_pos = set()
    while len(circles_pos) < NUM_CIRCLES:
        circles_pos.add((random.randint(0, ROWS-1), random.randint(0, COLS-1)))
    return grid, circles_pos, 0

def main():
    global points
    points = 0
    grid, circles_pos, clicks = reset_grid()
    run = True
    reveal_animation = False
    circle_found = False
    animation_start_time = 0
    blink = False
    animation_duration = ANIMATION_TIME_WIN

    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN and not reveal_animation:
                x, y = event.pos
                if y > BORDER_SIZE and y < HEIGHT + BORDER_SIZE and x > BORDER_SIZE and x < WIDTH + BORDER_SIZE:
                    col, row = (x - GRID_START_X) // SQUARE_SIZE, (y - GRID_START_Y) // SQUARE_SIZE
                    if 0 <= col < COLS and 0 <= row < ROWS:
                        if grid[row][col]:
                            pop_sound.play()
                            grid[row][col] = False
                            clicks += 1
                            if (row, col) in circles_pos:
                                points += 1
                                circle_found = True
                                reveal_animation = True
                                animation_start_time = pygame.time.get_ticks()
                                animation_duration = ANIMATION_TIME_WIN
                            elif clicks == MAX_CLICKS:
                                reveal_animation = True
                                animation_start_time = pygame.time.get_ticks()
                                circle_found = False
                                animation_duration = ANIMATION_TIME_LOSE

        screen.fill((0, 0, 0))
        attempts_remaining = MAX_CLICKS - clicks
        draw_text(points, attempts_remaining)
        if reveal_animation:
            current_time = pygame.time.get_ticks()
            if circle_found and (current_time - animation_start_time) % (2 * BLINK_INTERVAL) < BLINK_INTERVAL:
                blink = not blink
            draw_grid(grid, circles_pos, reveal=True, blink=circle_found)
            if current_time - animation_start_time > animation_duration:
                grid, circles_pos, clicks = reset_grid()
                reveal_animation = False
                circle_found = False
                blink = False
        else:
            draw_grid(grid, circles_pos)
        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
