import pygame
import sys

# 初始化Pygame
pygame.init()
pygame.mixer.init()

# 游戏配置
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Casual Breakout")  # 英文标题
clock = pygame.time.Clock()
FPS = 60

# 颜色定义
WHITE = (255, 255, 255)
BLUE = (50, 150, 255)
RED = (255, 80, 80)
YELLOW = (255, 200, 50)
BLACK = (0, 0, 0)
GRAY = (150, 150, 150)
LIGHT_BLUE = (100, 200, 255)


# 游戏状态枚举
class GameState:
    START = 0  # Start screen
    PLAYING = 1  # Playing game
    GAME_OVER = 2  # Game over
    WIN = 3  # Game win


# 挡板类 (Paddle)
class Paddle:
    def __init__(self):
        self.width = 100
        self.height = 15
        self.x = WIDTH // 2 - self.width // 2
        self.y = HEIGHT - 30
        self.speed = 8

    def draw(self):
        pygame.draw.rect(screen, BLUE, (self.x, self.y, self.width, self.height))
        pygame.draw.rect(screen, WHITE, (self.x, self.y, self.width, self.height), 1)

    def move(self, direction):
        if direction == "LEFT" and self.x > 0:
            self.x -= self.speed
        if direction == "RIGHT" and self.x < WIDTH - self.width:
            self.x += self.speed


# 小球类 (Ball)
class Ball:
    def __init__(self):
        self.radius = 10
        self.x = WIDTH // 2
        self.y = HEIGHT // 2
        self.speed_x = 3
        self.speed_y = 4
        self.is_moving = False  # Stop at first, press space to move

    def draw(self):
        pygame.draw.circle(screen, YELLOW, (self.x, self.y), self.radius)
        pygame.draw.circle(screen, WHITE, (self.x, self.y), self.radius, 1)

    def move(self):
        if self.is_moving:
            self.x += self.speed_x
            self.y += self.speed_y
            # Bounce on left/right wall
            if self.x <= self.radius or self.x >= WIDTH - self.radius:
                self.speed_x *= -1
            # Bounce on top wall
            if self.y <= self.radius:
                self.speed_y *= -1

    def check_paddle_collision(self, paddle):
        paddle_rect = pygame.Rect(paddle.x, paddle.y, paddle.width, paddle.height)
        ball_rect = pygame.Rect(self.x - self.radius, self.y - self.radius, self.radius * 2, self.radius * 2)
        if paddle_rect.colliderect(ball_rect):
            self.speed_y = -abs(self.speed_y)
            # Horizontal bounce optimization
            if self.x < paddle.x + paddle.width / 3:
                self.speed_x = -abs(self.speed_x)
            elif self.x > paddle.x + 2 * paddle.width / 3:
                self.speed_x = abs(self.speed_x)

    def check_game_over(self):
        return self.y > HEIGHT


# 砖块类 (Brick)
class Brick:
    def __init__(self, x, y):
        self.width = 70
        self.height = 20
        self.x = x
        self.y = y
        self.active = True

    def draw(self):
        if self.active:
            pygame.draw.rect(screen, RED, (self.x, self.y, self.width, self.height))
            pygame.draw.rect(screen, WHITE, (self.x, self.y, self.width, self.height), 1)

    def check_ball_collision(self, ball):
        if not self.active:
            return False
        brick_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        ball_rect = pygame.Rect(ball.x - ball.radius, ball.y - ball.radius, ball.radius * 2, ball.radius * 2)
        if brick_rect.colliderect(ball_rect):
            self.active = False
            return True
        return False


# 初始化游戏
def init_game():
    """Reset all game objects to initial state"""
    paddle = Paddle()
    ball = Ball()
    bricks = []
    # Generate brick matrix
    for row in range(5):
        for col in range(8):
            brick_x = 50 + col * 80
            brick_y = 50 + row * 30
            bricks.append(Brick(brick_x, brick_y))
    return paddle, ball, bricks


# 绘制开始界面 (Draw start screen)
def draw_start_screen():
    screen.fill(BLACK)
    # Title
    font_title = pygame.font.Font(None, 80)
    title_text = font_title.render("Casual Breakout", True, LIGHT_BLUE)
    screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, HEIGHT // 2 - 100))

    # Start tip
    font_start = pygame.font.Font(None, 40)
    start_text = font_start.render("Press SPACE to Start | Press ESC to Exit", True, WHITE)
    screen.blit(start_text, (WIDTH // 2 - start_text.get_width() // 2, HEIGHT // 2 + 20))

    # Operation guide
    font_tip = pygame.font.Font(None, 28)
    tip_text1 = font_tip.render("← → Control Paddle | SPACE Start Ball Movement", True, GRAY)
    tip_text2 = font_tip.render("R Restart Game | ESC Exit Game", True, GRAY)
    screen.blit(tip_text1, (WIDTH // 2 - tip_text1.get_width() // 2, HEIGHT // 2 + 80))
    screen.blit(tip_text2, (WIDTH // 2 - tip_text2.get_width() // 2, HEIGHT // 2 + 110))


# 初始化游戏对象
paddle, ball, bricks = init_game()
current_state = GameState.START
running = True

# 游戏主循环
while running:
    # ========== Event Handling ==========
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            # Global exit: ESC
            if event.key == pygame.K_ESCAPE:
                running = False

            # Start screen: Press SPACE to play
            if current_state == GameState.START and event.key == pygame.K_SPACE:
                current_state = GameState.PLAYING

            # Restart game: Press R (except start screen)
            if event.key == pygame.K_r and current_state != GameState.START:
                paddle, ball, bricks = init_game()
                current_state = GameState.PLAYING

            # Playing: Press SPACE to start ball movement
            if current_state == GameState.PLAYING and event.key == pygame.K_SPACE:
                ball.is_moving = True

    # ========== Game Logic by State ==========
    if current_state == GameState.PLAYING:
        # Paddle control (hold key)
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            paddle.move("LEFT")
        if keys[pygame.K_RIGHT]:
            paddle.move("RIGHT")

        # Ball movement and collision
        ball.move()
        ball.check_paddle_collision(paddle)

        # Brick collision detection
        for brick in bricks:
            if brick.check_ball_collision(ball):
                ball.speed_y *= -1
                break

        # Update game state
        if ball.check_game_over():
            current_state = GameState.GAME_OVER
        if all(not brick.active for brick in bricks):
            current_state = GameState.WIN

    # ========== Draw Interface ==========
    if current_state == GameState.START:
        draw_start_screen()

    else:
        screen.fill(BLACK)

        # Draw game elements
        paddle.draw()
        ball.draw()
        for brick in bricks:
            brick.draw()

        # Top permanent tip
        font_small = pygame.font.Font(None, 26)
        tip_text = font_small.render("ESC=Exit | R=Restart | SPACE=Start Ball", True, GRAY)
        screen.blit(tip_text, (10, 10))

        # Game over screen
        if current_state == GameState.GAME_OVER:
            font_large = pygame.font.Font(None, 72)
            text1 = font_large.render("Game Over!", True, WHITE)
            text2 = font_small.render("Press R to Restart | Press ESC to Exit", True, WHITE)
            screen.blit(text1, (WIDTH // 2 - text1.get_width() // 2, HEIGHT // 2 - 50))
            screen.blit(text2, (WIDTH // 2 - text2.get_width() // 2, HEIGHT // 2 + 20))

        # Game win screen
        if current_state == GameState.WIN:
            font_large = pygame.font.Font(None, 72)
            text1 = font_large.render("You Win!", True, WHITE)
            text2 = font_small.render("Press R to Restart | Press ESC to Exit", True, WHITE)
            screen.blit(text1, (WIDTH // 2 - text1.get_width() // 2, HEIGHT // 2 - 50))
            screen.blit(text2, (WIDTH // 2 - text2.get_width() // 2, HEIGHT // 2 + 20))

    # Update screen
    pygame.display.flip()
    clock.tick(FPS)

# Quit game
pygame.quit()
sys.exit()