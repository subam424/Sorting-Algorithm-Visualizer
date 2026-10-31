import pygame

from components import Visualizer

WIDTH, HEIGHT = 1180, 780
FPS = 60
ITEM_COUNT = 50


def main():
    pygame.init()
    try:
        visualizer = Visualizer(HEIGHT, WIDTH, count=ITEM_COUNT)
        clock = pygame.time.Clock()
        running = True
        while running:
            dt = clock.tick(FPS) / 1000
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    running = False
                else:
                    visualizer.handle_event(event)
            if running:
                visualizer.update(dt)
                visualizer.draw_screen()
    finally:
        pygame.quit()


if __name__ == "__main__":
    main()