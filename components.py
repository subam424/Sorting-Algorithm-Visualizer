"""Sorting generators, animation state, timer, and Pygame interface."""
import random
from time import perf_counter

import pygame


class Timer:
    """Monotonic elapsed time, excluding pauses."""

    def __init__(self):
        self.reset()

    def reset(self):
        self.accumulated = 0.0
        self.started = None

    def start(self):
        if self.started is None:
            self.started = perf_counter()

    def pause(self):
        if self.started is not None:
            self.accumulated += perf_counter() - self.started
            self.started = None

    @property
    def elapsed(self):
        return self.accumulated + (perf_counter() - self.started if self.started is not None else 0)

    def text(self):
        centiseconds = int(self.elapsed * 100)
        minutes, remainder = divmod(centiseconds, 6000)
        seconds, hundredths = divmod(remainder, 100)
        return f"{minutes:02}:{seconds:02}.{hundredths:02}"


class Visualizer:
    BG = "#0D1423"
    PANEL = "#151F32"
    BORDER = "#29364D"
    TEXT = "#E8EFFA"
    MUTED = "#A0B0C9"
    ACCENT = "#72DBC4"
    ACTIVE = "#FFCE7A"
    BAR = "#759CEF"
    ALGORITHMS = {"Insertion": "I", "Merge": "M", "Bubble": "B", "Cocktail": "C", "Bogo": "O"}
    DESCRIPTIONS = {
        "Insertion": "Builds a sorted section, one value at a time.",
        "Merge": "Splits the list, then merges sorted sections.",
        "Bubble": "Compares neighbors and moves larger values right.",
        "Cocktail": "Bubble sort moving in both directions.",
        "Bogo": "Random shuffles; completion is not guaranteed soon.",
    }
    SPEEDS = (15, 60, 240)

    def __init__(self, height=780, width=1180, lst=None, sorter="Insertion", count=50):
        self.width, self.height = width, height
        self.count = count if lst is None else len(lst)
        self.sorter = sorter
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Sort Studio | Algorithm Visualizer")
        self.font = pygame.font.SysFont("Arial", 18)
        self.small = pygame.font.SysFont("Arial", 15)
        self.title = pygame.font.SysFont("Arial", 32, bold=True)
        self.number = pygame.font.SysFont("Arial", 29, bold=True)
        self.timer = Timer()
        self.speed_index = 1
        self.buttons = {}
        self.set_bar(lst if lst is not None else self.new_values())

    def new_values(self):
        # Keep Bogo usable; 50-element Bogo is effectively endless.
        size = min(self.count, 5) if self.sorter == "Bogo" else self.count
        values = list(range(1, size + 1))
        random.shuffle(values)
        return values

    def set_bar(self, values):
        self.lst = list(values)
        self.state = "Ready"
        self.generator = None
        self.active = ()
        self.steps = 0
        self.budget = 0.0
        self.timer.reset()

    def reset(self):
        self.set_bar(self.new_values())

    def select_algorithm(self, name):
        if name != self.sorter:
            was_bogo = self.sorter == "Bogo"
            self.sorter = name
            if was_bogo or name == "Bogo":
                self.reset()
            else:
                # Cancel the previous run without discarding the current data.
                self.set_bar(self.lst)

    def toggle_sort(self):
        if self.state == "Running":
            self.timer.pause()
            self.state = "Paused"
        elif self.state == "Paused":
            self.timer.start()
            self.state = "Running"
        else:
            self.timer.reset()
            self.steps = 0
            self.budget = 0.0
            self.generator = {
                "Insertion": self.insertion, "Merge": self.dummy_merge,
                "Bubble": self.bubble, "Cocktail": self.cocktail, "Bogo": self.bogo,
            }[self.sorter]()
            self.state = "Running"
            self.timer.start()

    def handle_event(self, event):
        action = None
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                action = "start"
            elif event.key == pygame.K_r:
                action = "reset"
            elif event.key in (pygame.K_LEFT, pygame.K_RIGHT):
                change = 1 if event.key == pygame.K_RIGHT else -1
                self.speed_index = max(0, min(2, self.speed_index + change))
            else:
                for name, key in self.ALGORITHMS.items():
                    if event.key == ord(key.lower()):
                        self.select_algorithm(name)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            action = next((name for name, rect in self.buttons.items() if rect.collidepoint(event.pos)), None)
        if action == "start":
            self.toggle_sort()
        elif action == "reset":
            self.reset()
        elif action in self.ALGORITHMS:
            self.select_algorithm(action)
        elif action and action.startswith("speed:"):
            self.speed_index = int(action[-1])

    def update(self, dt):
        if self.state != "Running":
            return
        self.budget += min(dt, 0.1) * self.SPEEDS[self.speed_index]
        while self.budget >= 1:
            self.budget -= 1
            try:
                self.active = next(self.generator)
                self.steps += 1
            except StopIteration:
                self.timer.pause()
                self.state = "Complete"
                self.active = ()
                self.generator = None
                self.budget = 0
                break

    def text(self, text, pos, color=None, font=None):
        self.screen.blit((font or self.font).render(text, True, color or self.TEXT), pos)

    def panel(self, rect):
        pygame.draw.rect(self.screen, self.PANEL, rect, border_radius=16)
        pygame.draw.rect(self.screen, self.BORDER, rect, width=1, border_radius=16)

    def button(self, action, label, rect, selected=False, primary=False):
        rect = pygame.Rect(rect)
        self.buttons[action] = rect
        hover = rect.collidepoint(pygame.mouse.get_pos())
        fill = self.ACCENT if primary else ("#263B54" if selected or hover else self.PANEL)
        pygame.draw.rect(self.screen, fill, rect, border_radius=9)
        pygame.draw.rect(self.screen, self.ACCENT if selected else self.BORDER, rect, 1, border_radius=9)
        label_surface = self.small.render(label, True, self.BG if primary else self.TEXT)
        self.screen.blit(label_surface, label_surface.get_rect(center=rect.center))

    def draw_screen(self):
        self.screen.fill(self.BG)
        self.buttons.clear()
        self.text("SORT STUDIO", (28, 22), font=self.title)
        self.text("A closer look at how order happens.", (30, 64), self.MUTED)
        self.text("ALGORITHM VISUALIZER", (self.width - 230, 40), self.ACCENT, self.small)
        self.panel(pygame.Rect(28, 108, 230, self.height - 140))
        self.text("ALGORITHMS", (48, 130), self.MUTED, self.small)
        for i, (name, key) in enumerate(self.ALGORITHMS.items()):
            self.button(name, f"{name}    [{key}]", (44, 165 + i * 49, 198, 40), name == self.sorter)
        self.text("ANIMATION SPEED", (48, 432), self.MUTED, self.small)
        for i, label in enumerate(("Slow", "Normal", "Fast")):
            self.button(f"speed:{i}", label, (44 + i * 67, 462, 62, 36), i == self.speed_index)
        self.text(f"{self.SPEEDS[self.speed_index]} steps / second", (48, 512), self.MUTED, self.small)
        label = {"Running": "Pause", "Paused": "Resume", "Complete": "Run again"}.get(self.state, "Start sorting")
        self.button("start", f"{label}   [SPACE]", (44, 558, 198, 44), primary=True)
        self.button("reset", "Shuffle & reset   [R]", (44, 614, 198, 42))
        self.text("Arrow keys adjust speed", (48, 680), self.MUTED, self.small)

        x, right_width = 280, self.width - 308
        gap = 14
        card_width = (right_width - gap * 2) // 3
        cards = (("ELAPSED ANIMATION", self.timer.text()), ("ITEMS", str(len(self.lst))), ("STATUS", self.state))
        for i, (heading, value) in enumerate(cards):
            left = x + i * (card_width + gap)
            self.panel(pygame.Rect(left, 108, card_width, 92))
            self.text(heading, (left + 18, 123), self.MUTED, self.small)
            self.text(value, (left + 18, 151), self.ACCENT if i == 0 else self.TEXT, self.number)
        self.panel(pygame.Rect(x, 218, right_width, self.height - 294))
        self.text(f"{self.sorter} sort", (x + 24, 239), font=self.number)
        self.text(self.DESCRIPTIONS[self.sorter], (x + 24, 281), self.MUTED, self.small)
        self.draw_bar(pygame.Rect(x + 24, 334, right_width - 48, self.height - 456))
        self.text("Active", (x + 40, self.height - 107), self.MUTED, self.small)
        pygame.draw.circle(self.screen, self.ACTIVE, (x + 28, self.height - 98), 4)
        self.text(f"Animation steps: {self.steps:,}", (x + 135, self.height - 107), self.MUTED, self.small)
        self.text("Timer includes animation pacing; pauses are excluded.", (x, self.height - 53), self.MUTED, self.small)
        pygame.display.flip()

    def draw_bar(self, plot):
        for i in range(5):
            y = plot.bottom - i * plot.height // 4
            pygame.draw.line(self.screen, self.BORDER, (plot.left, y), (plot.right, y))
        if not self.lst:
            return
        maximum = max(max(self.lst), 1)
        cell = plot.width / len(self.lst)
        for i, value in enumerate(self.lst):
            height = max(3, round(value / maximum * plot.height))
            color = self.ACCENT if self.state == "Complete" else (self.ACTIVE if i in self.active else self.BAR)
            rect = pygame.Rect(round(plot.x + i * cell), plot.bottom - height, max(1, int(cell) - 3), height)
            pygame.draw.rect(self.screen, color, rect, border_radius=min(4, rect.width // 2))

    def bubble(self):
        for end in range(len(self.lst) - 1, 0, -1):
            swapped = False
            for i in range(end):
                if self.lst[i] > self.lst[i + 1]:
                    self.lst[i], self.lst[i + 1] = self.lst[i + 1], self.lst[i]
                    swapped = True
                yield (i, i + 1)
            if not swapped:
                break

    def insertion(self):
        for i in range(1, len(self.lst)):
            j = i
            while j > 0:
                if self.lst[j - 1] <= self.lst[j]:
                    yield (j - 1, j)
                    break
                self.lst[j - 1], self.lst[j] = self.lst[j], self.lst[j - 1]
                yield (j - 1, j)
                j -= 1

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
        first, second = self.lst[left:mid + 1], self.lst[mid + 1:right + 1]
        i = j = 0
        for target in range(left, right + 1):
            if j == len(second) or (i < len(first) and first[i] <= second[j]):
                self.lst[target] = first[i]
                i += 1
            else:
                self.lst[target] = second[j]
                j += 1
            yield (target,)

    def cocktail(self):
        start, end = 0, len(self.lst) - 1
        while start < end:
            swapped = False
            for indices in (range(start, end), range(end - 1, start - 1, -1)):
                for i in indices:
                    if self.lst[i] > self.lst[i + 1]:
                        self.lst[i], self.lst[i + 1] = self.lst[i + 1], self.lst[i]
                        swapped = True
                    yield (i, i + 1)
            if not swapped:
                break
            start += 1
            end -= 1

    def bogo(self):
        while any(a > b for a, b in zip(self.lst, self.lst[1:])):
            random.shuffle(self.lst)
            yield tuple(range(len(self.lst)))
