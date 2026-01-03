import pygame, random
from components import Visualizer
pygame.init()

WIDTH = 1100
HEIGHT = 750
FPS = 60
N = 50

def generate_list(n):
    lis = [x for x in range(1, n+1)]
    random.shuffle(lis)
    return lis

def main():
    run = True
    sort = False
    clock = pygame.time.Clock()
    sorter = "Insertion"
    sorting = None
    visualizer = Visualizer(HEIGHT, WIDTH, generate_list(N), sorter)
    while run:
        clock.tick(FPS)
        visualizer.draw_screen()

        if sort and sorting:
            try:
                next(sorting)
            except StopIteration:
                sort = False
                sorting = None

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    visualizer.set_bar(generate_list(N))
                    sort = False
                    sorting = None

                if event.key == pygame.K_SPACE and not sort:
                    sort = True
                    if sorter.lower() == "bubble":
                        sorting = visualizer.bubble()
                    if sorter.lower() == "merge":
                        sorting = visualizer.dummy_merge()
                    if sorter.lower() == "insertion":
                        sorting = visualizer.insertion()
                    if sorter.lower() == "bogo":
                        sorting = visualizer.bogo()
                    if sorter.lower() == "cocktail":
                        sorting = visualizer.cocktail()

                if event.key == pygame.K_i:
                    sorter = "Insertion"
                if event.key == pygame.K_m:
                    sorter = "Merge"
                if event.key == pygame.K_b:
                    sorter = "Bubble"
                if event.key == pygame.K_o:
                    sorter = "Bogo"
                if event.key == pygame.K_c:
                    sorter = "Cocktail"

                visualizer.sorter = sorter

    pygame.quit()

if __name__ == "__main__":
    main()