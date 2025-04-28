import pygame
import random

def create_squares(num_squares, width, height, square_size):
    squares = []
    for _ in range(num_squares):
        square = {
            "x": random.randint(0, width - square_size),
            "y": random.randint(0, height - square_size),
            "color": (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)),
            "speed_x": random.choice([-5, 5]),
            "speed_y": random.choice([-5, 5])
        }
        squares.append(square)
    return squares

pygame.init()

WIDTH, HEIGHT = 1920, 1080
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("test")

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
SQUARE_SIZE = 50

num_squares = 25
squares = create_squares(num_squares, WIDTH, HEIGHT, SQUARE_SIZE)

font = pygame.font.Font(None, 50)

running = True
clock = pygame.time.Clock()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    for square in squares:
        square["x"] += square["speed_x"]
        square["y"] += square["speed_y"]

        if square["x"] <= 0 or square["x"] >= WIDTH - SQUARE_SIZE:
            square["speed_x"] = -square["speed_x"]
            square["color"] = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

        if square["y"] <= 0 or square["y"] >= HEIGHT - SQUARE_SIZE:
            square["speed_y"] = -square["speed_y"]
            square["color"] = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

    screen.fill(BLACK)
    for square in squares:
        pygame.draw.rect(screen, square["color"], (square["x"], square["y"], SQUARE_SIZE, SQUARE_SIZE))

    fps = clock.get_fps()
    fps_text = font.render(f"FPS: {int(fps)}", True, WHITE)
    screen.blit(fps_text, (10, 10))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()

