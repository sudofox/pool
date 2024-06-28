import pygame
import math
import time

# Constants
WIDTH, HEIGHT = 900, 500  # Overall window size
TABLE_WIDTH, TABLE_HEIGHT = 800, 400  # Size of the playable area
BORDER_SIZE = 50
BALL_RADIUS = 10
HOLE_RADIUS = 15
FRICTION = 0.02  # Increased friction
STOP_THRESHOLD = 0.1
FPS = 60
MESSAGE_DURATION = 2  # Duration to display messages in seconds

# Colors
WHITE = (255, 255, 255)
TABLE_GREEN = (0, 100, 0)  # Darker green for the table
BROWN = (139, 69, 19)
BLACK = (0, 0, 0)
NUMBERS_COLOR = BLACK
BALL_COLORS = [
    (255, 255, 255),  # Cue ball (not used in list of balls)
    (255, 215, 0),    # 1 - Yellow
    (0, 0, 255),      # 2 - Blue
    (255, 0, 0),      # 3 - Red
    (128, 0, 128),    # 4 - Purple
    (255, 140, 0),    # 5 - Orange
    (0, 128, 0),      # 6 - Green
    (128, 0, 0),      # 7 - Burgundy
    (0, 0, 0),        # 8 - Black
    (255, 215, 0),    # 9 - Yellow (striped)
    (0, 0, 255),      # 10 - Blue (striped)
    (255, 0, 0),      # 11 - Red (striped)
    (128, 0, 128),    # 12 - Purple (striped)
    (255, 140, 0),    # 13 - Orange (striped)
    (0, 128, 0),      # 14 - Green (striped)
    (128, 0, 0)       # 15 - Burgundy (striped)
]

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
font = pygame.font.Font(None, 24)  # Font for numbers on balls

class Ball:
    def __init__(self, x, y, dx=0, dy=0, color=WHITE, number=None, stripe=False):
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.color = color
        self.number = number
        self.stripe = stripe
        self.angle = 0
        self.potted = False

    def move(self):
        if not self.potted:
            self.x += self.dx
            self.y += self.dy
            self.dx *= (1 - FRICTION)
            self.dy *= (1 - FRICTION)
            if abs(self.dx) < STOP_THRESHOLD:
                self.dx = 0
            if abs(self.dy) < STOP_THRESHOLD:
                self.dy = 0
            self.angle += math.hypot(self.dx, self.dy) / BALL_RADIUS
            self.collide_with_walls()

    def draw(self, screen):
        if not self.potted:
            ball_surface = pygame.Surface((2 * BALL_RADIUS, 2 * BALL_RADIUS), pygame.SRCALPHA)
            pygame.draw.circle(ball_surface, self.color, (BALL_RADIUS, BALL_RADIUS), BALL_RADIUS)
            if self.stripe:
                pygame.draw.rect(ball_surface, WHITE, (0, BALL_RADIUS - BALL_RADIUS // 4, 2 * BALL_RADIUS, BALL_RADIUS // 2))
            shine_surface = pygame.Surface((2 * BALL_RADIUS, 2 * BALL_RADIUS), pygame.SRCALPHA)
            pygame.draw.circle(shine_surface, (255, 255, 255, 30), (BALL_RADIUS // 2, BALL_RADIUS // 2), BALL_RADIUS // 2)
            ball_surface.blit(shine_surface, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
            rotated_surface = pygame.transform.rotate(ball_surface, math.degrees(self.angle))
            screen.blit(rotated_surface, (self.x - rotated_surface.get_width() // 2, self.y - rotated_surface.get_height() // 2))
            # Draw the number on the ball
            if self.number is not None:
                number_surface = font.render(str(self.number), True, NUMBERS_COLOR)
                screen.blit(number_surface, (self.x - number_surface.get_width() // 2, self.y - number_surface.get_height() // 2))

    def collide_with_walls(self):
        play_left = BORDER_SIZE
        play_right = WIDTH - BORDER_SIZE
        play_top = BORDER_SIZE
        play_bottom = HEIGHT - BORDER_SIZE
        if self.x - BALL_RADIUS < play_left:
            self.dx = abs(self.dx)
        if self.x + BALL_RADIUS > play_right:
            self.dx = -abs(self.dx)
        if self.y - BALL_RADIUS < play_top:
            self.dy = abs(self.dy)
        if self.y + BALL_RADIUS > play_bottom:
            self.dy = -abs(self.dy)

    def collide_with_ball(self, other):
        if not self.potted and not other.potted:
            dx = other.x - self.x
            dy = other.y - self.y
            dist = math.hypot(dx, dy)
            if dist < 2 * BALL_RADIUS:
                angle = math.atan2(dy, dx)
                sin_a = math.sin(angle)
                cos_a = math.cos(angle)

                # Rotate ball velocities to simplify the collision math
                v1x = self.dx * cos_a + self.dy * sin_a
                v1y = self.dy * cos_a - self.dx * sin_a
                v2x = other.dx * cos_a + other.dy * sin_a
                v2y = other.dy * cos_a - self.dx * sin_a

                # Exchange velocities in the rotated frame
                self.dx = v2x * cos_a - v1y * sin_a
                self.dy = v1y * cos_a + v2x * sin_a
                other.dx = v1x * cos_a - v2y * sin_a
                other.dy = v2y * cos_a + v1x * sin_a

                # Ensure balls are not overlapping
                overlap = 2 * BALL_RADIUS - dist
                self.x -= overlap / 2 * cos_a
                self.y -= overlap / 2 * sin_a
                other.x += overlap / 2 * cos_a
                other.y += overlap / 2 * sin_a

holes = [
    (BORDER_SIZE, BORDER_SIZE), (WIDTH // 2, BORDER_SIZE), (WIDTH - BORDER_SIZE, BORDER_SIZE),
    (BORDER_SIZE, HEIGHT - BORDER_SIZE), (WIDTH // 2, HEIGHT - BORDER_SIZE), (WIDTH - BORDER_SIZE, HEIGHT - BORDER_SIZE)
]

def draw_table(screen):
    screen.fill(BROWN)
    pygame.draw.rect(screen, TABLE_GREEN, (BORDER_SIZE, BORDER_SIZE, WIDTH - 2 * BORDER_SIZE, HEIGHT - 2 * BORDER_SIZE))
    for hole in holes:
        pygame.draw.circle(screen, BLACK, hole, HOLE_RADIUS)

def setup_balls():
    balls = []
    start_x = WIDTH // 4
    start_y = HEIGHT // 2
    balls.append(Ball(start_x, start_y, 0, 0, WHITE))  # Cue ball

    ball_index = 1
    for row in range(5):
        for col in range(row + 1):
            x = WIDTH * 3 // 4 + 2 * BALL_RADIUS * row
            y = start_y + 2 * BALL_RADIUS * (col - row / 2)
            stripe = ball_index >= 9
            balls.append(Ball(x, y, color=BALL_COLORS[ball_index], number=ball_index, stripe=stripe))
            ball_index += 1
    return balls

def check_potted(balls, score, turn, player_ball_type):
    potted_any = False
    for ball in balls:
        if not ball.potted and any(math.hypot(ball.x - hx, ball.y - hy) < HOLE_RADIUS for hx, hy in holes):
            ball.potted = True
            ball.dx = ball.dy = 0
            potted_any = True
            if ball.color != WHITE:
                if (player_ball_type == "SOLID" and ball.stripe) or (player_ball_type == "STRIPE" and not ball.stripe):
                    turn = "SOLID" if turn == "STRIPE" else "STRIPE"  # Foul for potting opponent's ball
                else:
                    score[turn] += 1
            else:
                turn = "SOLID" if turn == "STRIPE" else "STRIPE"  # Potting the cue ball is a foul
    return potted_any, turn

def all_balls_stopped(balls):
    return all(ball.dx == 0 and ball.dy == 0 for ball in balls if not ball.potted)

def main():
    balls = setup_balls()
    cue_ball = balls[0]
    running = True
    turn = "STRIPE"
    score = {"SOLID": 0, "STRIPE": 0}
    dragging = False
    drag_start = (0, 0)
    dragging_ball = None
    shot_made = False
    player_ball_type = None  # None until a player pots their first ball
    last_message_time = 0
    current_message = ""

    messages = [
        "Great shot!",
        "What a miss!",
        "Foul: potted the opponent's ball!",
        "Foul: potted the cue ball!",
        "Your turn!",
        "Opponent's turn!",
    ]

    def update_caption():
        nonlocal last_message_time, current_message
        if time.time() - last_message_time > MESSAGE_DURATION:
            pygame.display.set_caption(f"Pool Game - Turn: {turn} | Score - SOLID: {score['SOLID']} STRIPE: {score['STRIPE']}")
        else:
            pygame.display.set_caption(current_message)

    def display_message(message):
        nonlocal last_message_time, current_message
        current_message = message
        last_message_time = time.time()
        update_caption()

    update_caption()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = event.pos
                if cue_ball.potted:
                    # Prevent placing the cue ball on the wood
                    if BORDER_SIZE <= mouse_x <= WIDTH - BORDER_SIZE and BORDER_SIZE <= mouse_y <= HEIGHT - BORDER_SIZE:
                        cue_ball.x, cue_ball.y = mouse_x, mouse_y
                        cue_ball.potted = False
                elif math.hypot(cue_ball.x - mouse_x, cue_ball.y - mouse_y) < BALL_RADIUS:
                    dragging = True
                    drag_start = event.pos
                    dragging_ball = cue_ball
            elif event.type == pygame.MOUSEBUTTONUP and dragging:
                dragging = False
                drag_end = event.pos
                dx = (drag_start[0] - drag_end[0]) / 10
                dy = (drag_start[1] - drag_end[1]) / 10
                dragging_ball.dx = dx
                dragging_ball.dy = dy
                dragging_ball = None
                shot_made = True

        draw_table(screen)
        for ball in balls:
            ball.move()
            for other_ball in balls:
                if ball != other_ball:
                    ball.collide_with_ball(other_ball)
            ball.draw(screen)

        if dragging and dragging_ball:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            pygame.draw.line(screen, WHITE, (dragging_ball.x, dragging_ball.y), (mouse_x, mouse_y), 2)

        potted_any, turn = check_potted(balls, score, turn, player_ball_type)

        if player_ball_type is None:
            # Determine the player's ball type based on the first ball they pot
            for ball in balls:
                if ball.potted and ball.color != WHITE:
                    player_ball_type = "SOLID" if ball.number <= 7 else "STRIPE"
                    break

        if all_balls_stopped(balls):
            if shot_made:
                if not potted_any:
                    display_message(messages[5] if turn == "SOLID" else messages[4])
                    turn = "SOLID" if turn == "STRIPE" else "STRIPE"
                else:
                    display_message(messages[0])
                update_caption()
                shot_made = False
            else:
                update_caption()

        # Preview cue ball placement
        if cue_ball.potted:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            if BORDER_SIZE <= mouse_x <= WIDTH - BORDER_SIZE and BORDER_SIZE <= mouse_y <= HEIGHT - BORDER_SIZE:
                pygame.draw.circle(screen, WHITE, (mouse_x, mouse_y), BALL_RADIUS, 1)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()
