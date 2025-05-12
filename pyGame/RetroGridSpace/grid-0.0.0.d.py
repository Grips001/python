# Import necessary libraries
import pygame  # Used for game development functionalities
import sys  # System-specific parameters and functions
import random  # Generate pseudo-random numbers

# Constants
SCREEN_SIZE = (1280, 720)  # Defines the size of the game window
GRID_SIZE = 10  # Size of the grid cells for the game area
BORDER_WIDTH = 10  # Width of the border around the game area
RIGHT_BORDER_WIDTH = 130  # Width of the right-hand side border for UI elements
UI_BORDER_HEIGHT = 40  # Height of the bottom UI border
FPS = 60  # Frames per second, controls the game's refresh rate
MENU_START_Y = 150  # The Y starting position for the menu options
MENU_OPTION_SPACING = 60  # Space between each menu option

# Color Constants
BACKGROUND_COLOR = (5, 5, 15)  # Dark background color
GRID_LINE_COLOR = (40, 40, 80)  # Color for grid lines
BORDER_COLOR = (55, 55, 95)  # Color for borders
TEXT_COLOR = (0, 100, 250)  # Color for text
HIGHLIGHT_COLOR = (40, 40, 80)  # Color for highlighting selections
RANDOM_POINT_COLOR_RANGE = (0, 255)  # Range for generating random colors

# Drawing Constants
CIRCLE_RADIUS = 4  # Radius of circles drawn on the grid
NUM_RANDOM_POINTS = 20  # Number of random points to generate on the grid
SELECTION_BORDER_WIDTH = 2  # Width of the border for selected items

# Global Variables
menu_options = ["Start", "Exit"]  # Options shown in the game menu
options_rects = []  # Rectangles for clickable menu options
game_state = "menu"  # Initial game state, showing the menu
game_started = False  # Tracks if the game has started
grids_with_objects_colors = []  # Stores positions and colors of grid objects
last_valid_grid_x, last_valid_grid_y = 0, 0  # Last valid grid positions

# Pygame initialization
pygame.init()  # Initializes Pygame
font = pygame.font.SysFont("Consolas", 20, bold=True)  # Sets the font
screen = pygame.display.set_mode(SCREEN_SIZE)  # Creates the game window
static_surface = pygame.Surface(SCREEN_SIZE)  # Surface for static elements
clock = pygame.time.Clock()  # Clock to control game refresh rate
CHAR_WIDTH = font.size(" ")[0]  # Calculates the width of a character

# Function Definitions
# Each function is designed to handle specific tasks such as drawing elements, handling events, etc.


def draw_static_elements():
    # Fills the background and draws static elements like the grid and borders
    static_surface.fill(BACKGROUND_COLOR)
    # Loop to draw grid lines
    for y in range(BORDER_WIDTH, SCREEN_SIZE[1] - UI_BORDER_HEIGHT, GRID_SIZE):
        for x in range(BORDER_WIDTH, SCREEN_SIZE[0] - RIGHT_BORDER_WIDTH, GRID_SIZE):
            rect = pygame.Rect(x, y, GRID_SIZE, GRID_SIZE)
            pygame.draw.rect(static_surface, GRID_LINE_COLOR, rect, 1)
    # Drawing borders
    borders = [
        (0, 0, SCREEN_SIZE[0], BORDER_WIDTH),
        (0, 0, BORDER_WIDTH, SCREEN_SIZE[1]),
        (SCREEN_SIZE[0] - RIGHT_BORDER_WIDTH, 0, RIGHT_BORDER_WIDTH, SCREEN_SIZE[1]),
        (0, SCREEN_SIZE[1] - UI_BORDER_HEIGHT, SCREEN_SIZE[0], UI_BORDER_HEIGHT),
    ]
    for border in borders:
        pygame.draw.rect(static_surface, BORDER_COLOR, border)


def draw_menu():
    # Function to draw the game menu
    screen.fill(BACKGROUND_COLOR)
    options_rects.clear()
    menu_options[0] = "Continue" if game_started else "Start"
    # Loop to render and position menu options
    for i, option in enumerate(menu_options):
        text = font.render(option, True, TEXT_COLOR)
        text_rect = text.get_rect(
            center=(SCREEN_SIZE[0] / 2, MENU_START_Y + i * MENU_OPTION_SPACING)
        )
        options_rects.append(text_rect)
        screen.blit(text, text_rect)
    # Highlighting the option under the mouse cursor
    mouse_pos = pygame.mouse.get_pos()
    for rect in options_rects:
        if rect.collidepoint(mouse_pos):
            pygame.draw.rect(screen, HIGHLIGHT_COLOR, rect, 2)
    pygame.display.flip()  # Updates the entire screen


def check_click(mouse_pos):
    # Iterate through each menu option's rectangle
    for i, rect in enumerate(options_rects):
        # Check if the mouse click position is within the rectangle
        if rect.collidepoint(mouse_pos):
            # If true, return the index of the clicked option
            return i
    # If the click was outside all options, return None
    return None


def handle_events():
    global game_state, game_started  # Access global variables to modify them
    for event in pygame.event.get():  # Loop through all events in the event queue
        if event.type == pygame.QUIT:  # If the event is a QUIT event
            pygame.quit()  # Uninitialize all pygame modules
            sys.exit()  # Exit the program
        elif (
            event.type == pygame.MOUSEBUTTONDOWN and event.button == 1
        ):  # If left mouse button is pressed
            action = check_click(event.pos)  # Check if a menu option was clicked
            if action is not None:  # If a click was detected within a menu option
                if action == 0:  # If the first option was clicked
                    game_state = "running"  # Change the game state to running
                    game_started = True  # Mark the game as started
                elif action == 1:  # If the second option was clicked
                    pygame.quit()  # Uninitialize all pygame modules
                    sys.exit()  # Exit the program
        elif event.type == pygame.KEYDOWN:  # If a key is pressed down
            if (
                event.key == pygame.K_ESCAPE and game_state == "running"
            ):  # If the key is ESC while in running state
                game_state = "menu"  # Change the game state back to menu


def get_grid_position(pos, last_valid_pos):
    global last_valid_grid_x, last_valid_grid_y  # Access global variables to modify them
    x, y = pos  # Unpack the position tuple
    # Check if the position is outside the playable area (taking borders into account)
    if (
        x < BORDER_WIDTH
        or y < BORDER_WIDTH
        or x >= SCREEN_SIZE[0] - RIGHT_BORDER_WIDTH
        or y >= SCREEN_SIZE[1] - UI_BORDER_HEIGHT
    ):
        return last_valid_pos  # Return the last valid position if it's outside
    # Adjust the position to be within the playable area, considering grid size
    x = max(BORDER_WIDTH, min(SCREEN_SIZE[0] - RIGHT_BORDER_WIDTH - GRID_SIZE, x))
    y = max(BORDER_WIDTH, min(SCREEN_SIZE[1] - UI_BORDER_HEIGHT - GRID_SIZE, y))
    # Calculate grid position based on adjusted x, y
    grid_x = (x - BORDER_WIDTH) // GRID_SIZE
    grid_y = (y - BORDER_WIDTH) // GRID_SIZE
    # Update global variables with the new valid grid position
    last_valid_grid_x, last_valid_grid_y = grid_x, grid_y
    return grid_x, grid_y  # Return the new grid position


def generate_random_grid_points():
    global grids_with_objects_colors  # Access global variable to modify it
    # Calculate the number of squares horizontally and vertically within the playable area
    num_squares_horizontal = (
        SCREEN_SIZE[0] - BORDER_WIDTH - RIGHT_BORDER_WIDTH
    ) // GRID_SIZE
    num_squares_vertical = (
        SCREEN_SIZE[1] - BORDER_WIDTH - UI_BORDER_HEIGHT
    ) // GRID_SIZE
    random_positions = set()  # Use a set to avoid duplicate positions
    # Keep generating random positions until we have the desired number
    while len(random_positions) < NUM_RANDOM_POINTS:
        x = random.randint(0, num_squares_horizontal - 1)  # Random x position
        y = random.randint(0, num_squares_vertical - 1)  # Random y position
        # Generate a random color for the point
        color = (
            random.randint(*RANDOM_POINT_COLOR_RANGE),
            random.randint(*RANDOM_POINT_COLOR_RANGE),
            random.randint(*RANDOM_POINT_COLOR_RANGE),
        )
        # Add the position and color as a tuple to the set
        random_positions.add(((x, y), color))
    # Convert the set to a list and store it in the global variable
    grids_with_objects_colors = list(random_positions)


def calculate_alignment_space():
    # Calculate the total width available for UI text, taking into account the left and right borders and the right UI area
    available_width = SCREEN_SIZE[0] - (BORDER_WIDTH * 2) - RIGHT_BORDER_WIDTH
    # Divide the available width by the width of a single character to determine how many characters can fit
    num_chars = available_width // CHAR_WIDTH
    return num_chars  # Return the total number of characters that can fit in the available space


# Main loop setup
draw_static_elements()  # Draw static parts of the game screen (borders, grid lines) once before the loop starts
generate_random_grid_points()  # Generate the initial set of random points on the grid

# Main game loop
while True:
    handle_events()  # Process input events (keyboard, mouse, etc.)

    if game_state == "menu":
        # If the game is currently displaying the menu:
        draw_menu()  # Draw the menu options on the screen
    elif game_state == "running":
        # If the game is in the running state (the game has started):
        screen.blit(
            static_surface, (0, 0)
        )  # Blit (copy) the static elements onto the main screen surface

        # Loop through each grid position and its associated color
        for grid_pos, color in grids_with_objects_colors:
            # Calculate the pixel position of the center of each grid square
            center_x = BORDER_WIDTH + (grid_pos[0] * GRID_SIZE) + (GRID_SIZE // 2)
            center_y = BORDER_WIDTH + (grid_pos[1] * GRID_SIZE) + (GRID_SIZE // 2)
            # Draw a circle at the calculated center position with the specified color
            pygame.draw.circle(screen, color, (center_x, center_y), CIRCLE_RADIUS)

        # Get the current position of the mouse
        mouse_pos = pygame.mouse.get_pos()
        # Calculate the grid position corresponding to the current mouse position
        last_valid_grid_x, last_valid_grid_y = get_grid_position(
            mouse_pos, (last_valid_grid_x, last_valid_grid_y)
        )

        # Draw a rectangle representing the player at the calculated grid position
        player_rect = pygame.Rect(
            BORDER_WIDTH + last_valid_grid_x * GRID_SIZE,
            BORDER_WIDTH + last_valid_grid_y * GRID_SIZE,
            GRID_SIZE,
            GRID_SIZE,
        )
        pygame.draw.rect(screen, TEXT_COLOR, player_rect)

        # Calculate the space available for the UI text and prepare the text
        num_chars = calculate_alignment_space()
        ui_text = f'{"ESC: MENU":<{num_chars//2}}{f"{last_valid_grid_x},{last_valid_grid_y}":>{num_chars//2}}'
        text_surf = font.render(ui_text, True, TEXT_COLOR)
        # Blit the text surface onto the main screen at the specified position
        screen.blit(
            text_surf,
            (
                10,
                SCREEN_SIZE[1]
                - UI_BORDER_HEIGHT
                + (UI_BORDER_HEIGHT - font.get_height()) // 2,
            ),
        )

        # Update the display to reflect any changes made to the screen
        pygame.display.flip()

    # Control the loop iteration speed to match the desired FPS
    clock.tick(FPS)
