import pygame, random, time

class Visualizer:
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    GREEN = (0, 255, 0)
    RED = (255, 0, 0)
    GRADIENT = [(130, 130, 130), (160, 160, 160), (190, 190, 190)]
    TITLE_COLOR = (76, 187, 23)

    PADDING_X = 100
    PADDING_Y = 140

    def __init__(self, height, width, lst, sorter):
        self.height = height
        self.width = width
        self.lst = lst
        self.FONT = pygame.font.SysFont("arial", 20)
        self.TITLE = pygame.font.SysFont("arial", 40, True)
        self.sorter = sorter

        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Sorting Algorithm Visualizer")

        self.set_bar(lst)

    def set_bar(self, lst):
        self.lst = lst
        self.min_value = min(lst)
        self.max_value = max(lst)
        self.bar_width = round((self.width - self.PADDING_X) / len(self.lst))
        self.bar_height = round((self.height - self.PADDING_Y) / (self.max_value - self.min_value))
        self.start_x = self.PADDING_X // 2

    def draw_screen(self):
        self.screen.fill(self.WHITE)
        
        line1 = self.FONT.render("R - Reset | SPACE - Start Sorting", 1, self.BLACK)
        line2 = self.FONT.render("I - Insertion | M - Merge | B - Bubble | O - Bogo | C - Cocktail", 1, self.BLACK)
        title = self.TITLE.render(f"Current Algorithm : {self.sorter} Sort", 1, self.TITLE_COLOR)
        time_passed = self.FONT.render(f"00:00", 1, self.BLACK)

        self.screen.blit(title, (self.width // 2 - title.get_width() // 2, 0))
        self.screen.blit(line1, (self.width // 2 - line1.get_width() // 2, 50))
        self.screen.blit(line2, (self.width // 2 - line2.get_width() // 2, 80))
        self.screen.blit(time_passed, (self.width // 2 - time_passed.get_width() // 2, 110))

        self.draw_bar()
        pygame.display.update()

    def draw_bar(self):
        for i, val in enumerate(self.lst):
            x = self.start_x + i * self.bar_width
            y = self.height - max((val - self.min_value) * self.bar_height, 10)
            
            color = self.GRADIENT[i % 3]
            pygame.draw.rect(self.screen, color, (x, y, self.bar_width, self.height))

    def bubble(self):
        for i in range(len(self.lst) - 1):
            for j in range(len(self.lst) - 1 - i):
                n1 = self.lst[j]
                n2 = self.lst[j + 1]

                if n1 > n2:
                    self.lst[j], self.lst[j + 1] = self.lst[j + 1], self.lst[j]
                yield True

    def dummy_merge(self):
        yield from self.merge_sort(0, len(self.lst) - 1)

    def merge_sort(self, left, right):
        if left >= right:
            return

        mid = (left + right) // 2
        yield from self.merge_sort(left, mid)
        yield from self.merge_sort(mid + 1, right)
        yield from self.actual_merge(left, mid, right)

    def actual_merge(self, left, mid, right):
        merged = []
        i = left
        j = mid + 1

        while i <= mid and j <= right:
            if self.lst[i] <= self.lst[j]:
                merged.append(self.lst[i])
                i += 1
            else:
                merged.append(self.lst[j])
                j += 1
            yield True

        while i <= mid:
            merged.append(self.lst[i])
            i += 1
            yield True

        while j <= right:
            merged.append(self.lst[j])
            j += 1
            yield True

        for i, val in enumerate(merged):
            self.lst[left + i] = val
            yield True
        
    def bogo(self):
        while self.lst != sorted(self.lst):
            random.shuffle(self.lst)
            pygame.time.delay(200)
            yield True

    def cocktail(self):
        n = len(self.lst)
        swapped = True
        start = 0
        end = n - 1
        while swapped:
            swapped = False
            for i in range(start, end):
                if self.lst[i] > self.lst [i+1]: 
                    self.lst[i], self.lst[i+1]= self.lst[i + 1], self.lst[i] 
                    swapped = True
                    yield True
            if not swapped:
                break
            swapped = False
            end -= 1
            for i in range(end - 1, start - 1, -1):
                if self.lst[i] > self.lst[i+1]: 
                    self.lst[i], self.lst [i+1] = self.lst[i+1], self.lst[i] 
                    swapped = True
                    yield True
            start += 1

    def insertion(self):
        for i in range(1, len(self.lst)): 
            current = self.lst[i]
            while True:
                ascending = i > 0 and self.lst[i-1] > current
                if not ascending:
                    break
                self.lst[i] = self.lst[i-1]
                i -= 1
                self.lst[i] = current
                yield True

    def show_time(self):
        start = time.time()