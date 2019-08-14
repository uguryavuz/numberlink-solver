import sys, os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"           # Mutes pygame import message.
import pygame, pygbutton                                    # For GUI.
from NumberlinkPuzzle import NumberlinkPuzzle               # Puzzle class.
from datetime import datetime

# Constants
SQUARE_SIZE, MARGIN = 40, 2

# Pygame font, window icon, and caption.
font = pygame.font.SysFont('Arial', 18)
pygbutton.PYGBUTTON_FONT = font
pygame.display.set_icon(pygame.image.load('Media/icon.png'))
pygame.display.set_caption("Numberlink Solver")


# Assert positive integer input.
def verified_pos_int(query_string):
    while True:
        print(query_string, end='')
        try:
            u_input = int(input())
            assert u_input > 0
            return u_input
        except AssertionError:
            print("Please input a positive integer.")
        except ValueError:
            print("Please input a positive integer.")


# Set width, height and amount of numbers.
WIDTH = verified_pos_int("Puzzle width: ")
HEIGHT = verified_pos_int("Puzzle height: ")
COUNT = verified_pos_int("Amount of numbers: ")
while COUNT > (WIDTH * HEIGHT) // 2:
    print("There can't be more numbers than half the number of cells.")
    COUNT = verified_pos_int("Amount of numbers: ")

# Set 2D grid array. grid[x][y] where top left corner is grid[0][0].
# Every square is represented by a number, and an array indicating which cells it is connected to.
grid = [[[None, [False, False, False, False]] for _ in range(HEIGHT)] for _ in range(WIDTH)]

pygame.init()
S_WIDTH, S_HEIGHT = (WIDTH+2) * SQUARE_SIZE + (WIDTH+1) * MARGIN, (HEIGHT+3) * SQUARE_SIZE + (HEIGHT+1) * MARGIN
screen = pygame.display.set_mode([S_WIDTH, S_HEIGHT])
clock = pygame.time.Clock()

DONE = False
ADDING_COLORS = True
CUR_LOC = None
COLOR_LOCS = []
PRINTED = False
SOLVE_ATTEMPTED = False
SOLVE_FAILED = False

addButton = pygbutton.PygButton(((SQUARE_SIZE + (WIDTH+1) * (MARGIN+SQUARE_SIZE)) // 2 - SQUARE_SIZE,
                                 (HEIGHT+1) * (MARGIN+SQUARE_SIZE) + SQUARE_SIZE//2,
                                 2*SQUARE_SIZE, SQUARE_SIZE), "Add")

solveButton = pygbutton.PygButton(((SQUARE_SIZE + (WIDTH+1) * (MARGIN+SQUARE_SIZE)) // 2 - SQUARE_SIZE,
                                 (HEIGHT+1) * (MARGIN+SQUARE_SIZE) + SQUARE_SIZE//2,
                                 2*SQUARE_SIZE, SQUARE_SIZE), "Solve")

jpgButton = pygbutton.PygButton(((SQUARE_SIZE + (WIDTH+1) * (MARGIN+SQUARE_SIZE) - (font.size("Save as .JPG")[0] + SQUARE_SIZE)) // 2,
                                 (HEIGHT+1) * (MARGIN+SQUARE_SIZE) + SQUARE_SIZE//2,
                                 font.size("Save as .JPG")[0] + SQUARE_SIZE, SQUARE_SIZE), "Save as .JPG")

solveButton.visible = False
jpgButton.visible = False

buttons = [addButton, solveButton, jpgButton]

def add_loc():
    global CUR_LOC, PRINTED
    if len(COLOR_LOCS) < 2 * COUNT and CUR_LOC and CUR_LOC not in COLOR_LOCS:
        COLOR_LOCS.append(CUR_LOC)
        if len(COLOR_LOCS) % 2 == 0:
            print(f"New number: {COLOR_LOCS[-1]}, {COLOR_LOCS[-2]}")
        PRINTED = False
        grid[CUR_LOC[0]][CUR_LOC[1]][0] = (len(COLOR_LOCS) + 1) // 2
    CUR_LOC = None


def solve():
    puzzle = NumberlinkPuzzle(WIDTH, HEIGHT, COLOR_LOCS)
    assignments = puzzle.solve(puzzle.generate_cnf())

    if not assignments:
        return False

    # print(assignments)
    for line in assignments:
        signed_vars = line.split()
        if len(signed_vars) > 1:
            for s_var in signed_vars[1:]:
                if s_var[0] != '-':
                    x, y = tuple(map(int, s_var.split('.')[1:]))
                    if s_var[0] == 'h':
                        # print(f'h: {x}, {y} -> {x+1}, {y}')
                        grid[x][y][1][0] = True
                        grid[x + 1][y][1][2] = True
                    else:
                        # print(f'v: {x}, {y} -> {x}, {y+1}')
                        grid[x][y][1][1] = True
                        grid[x][y + 1][1][3] = True

    return True

def is_quit_event(event):
    if event.type == pygame.QUIT:
        return True
    elif event.type == pygame.KEYDOWN:
        if event.key == pygame.K_ESCAPE:
            return True
        elif event.key == pygame.K_q and pygame.key.get_mods() & pygame.KMOD_META:
            return True
        elif event.key == pygame.K_F4 and pygame.key.get_mods() & pygame.KMOD_ALT:
            return True
    return False

while not DONE:

    for event in pygame.event.get():  # User did something
        if is_quit_event(event):
            DONE = True  # Flag that we are DONE so we exit this loop
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # User clicks the mouse. Get the position
            pos = pygame.mouse.get_pos()
            if ADDING_COLORS:
                if (SQUARE_SIZE + MARGIN) < pos[0] < (WIDTH+1) * SQUARE_SIZE + WIDTH * MARGIN and \
                        ((SQUARE_SIZE + MARGIN) < pos[1] < (HEIGHT+1) * SQUARE_SIZE + HEIGHT * MARGIN):
                    CUR_LOC = pos[0] // (SQUARE_SIZE+MARGIN) - 1, pos[1] // (SQUARE_SIZE+MARGIN) - 1

        if 'click' in addButton.handleEvent(event):
            if ADDING_COLORS:
                add_loc()

        if 'click' in solveButton.handleEvent(event):
            CUR_LOC, PRINTED = None, False
            SOLVE_FAILED = not solve()
            SOLVE_ATTEMPTED = True
            solveButton.visible = False

        if 'click' in jpgButton.handleEvent(event):
            if not os.path.exists(os.getcwd() + '/Solutions'):
                os.makedirs(os.getcwd() + '/Solutions')
            fname = os.getcwd() + '/Solutions' + datetime.now().strftime("/%m-%d-%Y-%H.%M.%S.jpg")
            pygame.image.save(screen.subsurface(pygame.Rect(SQUARE_SIZE, SQUARE_SIZE,
                                                            WIDTH * (SQUARE_SIZE + MARGIN) + MARGIN,
                                                            HEIGHT * (SQUARE_SIZE + MARGIN) + MARGIN)), fname)

    if ADDING_COLORS and len(COLOR_LOCS) == 2 * COUNT:
        ADDING_COLORS = False
        addButton.visible = False
        solveButton.visible = True

    if not PRINTED and ADDING_COLORS:
        print(f"Selecting cells for {len(COLOR_LOCS) // 2 + 1}, cell #{len(COLOR_LOCS) % 2 + 1}.")
        PRINTED = True

    screen.fill((245, 245, 220))

    pygame.draw.rect(screen, (0, 0, 0), [SQUARE_SIZE, SQUARE_SIZE,
                                         WIDTH * SQUARE_SIZE + (WIDTH+1) * MARGIN,
                                         HEIGHT * SQUARE_SIZE + (HEIGHT+1) * MARGIN])

    # Draw grid
    for y in range(HEIGHT):
        for x in range(WIDTH):
            pygame.draw.rect(screen, (255, 255, 255),
                             [(x+1)*(SQUARE_SIZE+MARGIN), (y+1)*(SQUARE_SIZE+MARGIN),
                              SQUARE_SIZE, SQUARE_SIZE])
            if grid[x][y][0] is not None:
                text_surface = font.render(f"{grid[x][y][0]}", True, (0, 0, 0))
                text_size = font.size(f"{grid[x][y][0]}")
                screen.blit(text_surface,
                            ((MARGIN + SQUARE_SIZE) * (x+1) + (SQUARE_SIZE - text_size[0]) // 2,
                             (MARGIN + SQUARE_SIZE) * (y+1) + (SQUARE_SIZE - text_size[1]) // 2))
            for i, val in enumerate(grid[x][y][1]):
                if val:
                    p1 = [(x+1) * (MARGIN+SQUARE_SIZE) + SQUARE_SIZE // 2, (y+1) * (MARGIN+SQUARE_SIZE) + SQUARE_SIZE // 2]
                    p2 = p1.copy()
                    p2[i % 2] = p2[i % 2] + (1 if i // 2 == 0 else -1) * SQUARE_SIZE // 2
                    if grid[x][y][0] is not None:
                        p1[i % 2] = p1[i % 2] + (1 if i // 2 == 0 else -1) * SQUARE_SIZE // 3
                    pygame.draw.line(screen, (255, 0, 0), p1, p2, MARGIN)

    if SOLVE_ATTEMPTED:
        # Failed solve
        if SOLVE_FAILED:
            red_surface = pygame.Surface((WIDTH * (SQUARE_SIZE + MARGIN) + MARGIN,
                                          HEIGHT * (SQUARE_SIZE + MARGIN) + MARGIN))
            red_surface.set_alpha(75)
            red_surface.fill((255, 0, 0))
            screen.blit(red_surface, (SQUARE_SIZE, SQUARE_SIZE))

            for button in buttons:
                button.visible = False

            text_surface = font.render("Puzzle in unsolvable.", True, (0, 0, 0))
            text_size = font.size("Puzzle in unsolvable.")
            screen.blit(text_surface, ((S_WIDTH - text_size[0]) // 2, S_HEIGHT - SQUARE_SIZE - text_size[1] // 2))
        else:
            # Save .jpg button
            jpgButton.visible = True

    # Outline currently selected location
    if CUR_LOC:
        x, y = CUR_LOC
        pygame.draw.rect(screen, (255, 0, 0), [(x + 1) * (SQUARE_SIZE + MARGIN) - MARGIN, 
            (y + 1) * (SQUARE_SIZE + MARGIN) - MARGIN, SQUARE_SIZE + 1.5 * MARGIN, 
            SQUARE_SIZE + 1.5 * MARGIN], MARGIN)

    for button in buttons:
        button.draw(screen)

    clock.tick(60)
    pygame.display.flip()

pygame.quit()
