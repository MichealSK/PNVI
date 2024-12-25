import pygame
import random

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
GRID_SIZE = 5
SQUARE_SIZE = 50
GOAL_SQUARE_SIZE = 15
MARGIN = 5
COLORS = [(255, 165, 0), (173, 216, 230), (255, 255, 0), (128, 0, 128)]  # ORANGE, LIGHTBLUE, YELLOW, PURPLE
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# Create screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Grid Color Matching Game")

# Fonts
font = pygame.font.Font(None, 36)

# Helper functions
def generate_grid():
    """Generate a randomized grid that adheres to the color rules."""
    grid = [[None for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            available_colors = COLORS[:]
            # Remove invalid colors based on neighbors
            if row > 0 and grid[row - 1][col] in available_colors:
                available_colors.remove(grid[row - 1][col])
            if col > 0 and grid[row][col - 1] in available_colors:
                available_colors.remove(grid[row][col - 1])
            grid[row][col] = random.choice(available_colors)
    return grid

def draw_grid(grid, top_left, square_size):
    """Draw the grid on the screen with customizable square size."""
    x_offset, y_offset = top_left
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            color = grid[row][col]
            rect = pygame.Rect(
                x_offset + col * (square_size + MARGIN),
                y_offset + row * (square_size + MARGIN),
                square_size,
                square_size,
            )
            pygame.draw.rect(screen, color, rect)
            pygame.draw.rect(screen, BLACK, rect, 2)

def check_match(grid1, grid2):
    """Check if two grids match."""
    return grid1 == grid2

def cycle_color(grid, row, col):
    """Cycle through colors while respecting neighbor constraints."""
    current_color = grid[row][col]
    current_index = COLORS.index(current_color)
    for i in range(1, len(COLORS) + 1):
        new_color = COLORS[(current_index + i) % len(COLORS)]
        # Check neighbors
        neighbors = [current_color]
        if row > 0:
            neighbors.append(grid[row - 1][col])
        if row < GRID_SIZE - 1:
            neighbors.append(grid[row + 1][col])
        if col > 0:
            neighbors.append(grid[row][col - 1])
        if col < GRID_SIZE - 1:
            neighbors.append(grid[row][col + 1])
        if new_color not in neighbors:
            grid[row][col] = new_color
            return True  # Successfully changed color
    return False  # No valid color to switch to

# Initialize grids
main_grid = generate_grid()
goal_grid = generate_grid()

def main():
    global main_grid
    running = True
    message = ""

    while running:
        screen.fill(WHITE)

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_x, mouse_y = event.pos

                # Determine if a square in the main grid was clicked
                grid_start_x = (WIDTH - GRID_SIZE * (SQUARE_SIZE + MARGIN)) // 2
                grid_start_y = (HEIGHT - GRID_SIZE * (SQUARE_SIZE + MARGIN)) // 2

                if grid_start_x <= mouse_x < grid_start_x + GRID_SIZE * (SQUARE_SIZE + MARGIN) and \
                   grid_start_y <= mouse_y < grid_start_y + GRID_SIZE * (SQUARE_SIZE + MARGIN):

                    col = (mouse_x - grid_start_x) // (SQUARE_SIZE + MARGIN)
                    row = (mouse_y - grid_start_y) // (SQUARE_SIZE + MARGIN)

                    if not cycle_color(main_grid, row, col):
                        message = "Cannot switch color"
                    else:
                        message = ""

                    # Check for success
                    if check_match(main_grid, goal_grid):
                        message = "SUCCESS!"

        # Draw main grid
        grid_start_x = (WIDTH - GRID_SIZE * (SQUARE_SIZE + MARGIN)) // 2
        grid_start_y = (HEIGHT - GRID_SIZE * (SQUARE_SIZE + MARGIN)) // 2
        draw_grid(main_grid, (grid_start_x, grid_start_y), SQUARE_SIZE)

        # Draw goal grid
        goal_start_x = WIDTH - (GRID_SIZE * (GOAL_SQUARE_SIZE + MARGIN)) - 20
        goal_start_y = 20
        draw_grid(goal_grid, (goal_start_x, goal_start_y), GOAL_SQUARE_SIZE)

        # Draw message
        if message:
            message_surface = font.render(message, True, BLACK)
            screen.blit(message_surface, (20, 20))

        # Update display
        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()