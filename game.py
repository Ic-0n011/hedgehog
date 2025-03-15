import curses as crs  # Модуль для работы с интерфейсом в терминале
from random import choice, randint  # Модуль для генерации случайных чисел
from abc import ABC, abstractmethod  # Модуль для создания абстрактных классов
import config as cfg  # Импорт констант из файла config
from texts import *  # Импорт текстовых сообщений и ASCII-арта из файла texts


class GameObject(ABC):
    instances = []  # Список всех созданных игровых объектов для отслеживания
    @abstractmethod
    def __init__(self, x, y):
        super().__init__()
        self.x = x  # Горизонтальная координата объекта на поле (int)
        self.y = y  # Вертикальная координата объекта на поле (int)
        GameObject.instances.append(self)  # Добавление объекта в общий список instances


class Game:
    def __init__(self, stdscr) -> None:
        self.stdscr = stdscr
        self.stdscr.nodelay(1)
        self.stdscr.timeout(50)
        self.running = True
        self.field = [
            [cfg.EMPTY for _ in range(cfg.FIELD_WIDTH)] for _ in range(cfg.FIELD_HEIGHT)
        ]
        self.empty_cells = [
            (x, y) for y in range(cfg.FIELD_HEIGHT) for x in range(cfg.FIELD_WIDTH)
        ]
        self.hedgehog = Hedgehog(cfg.FIELD_WIDTH // 2, cfg.FIELD_HEIGHT // 2)
        self.empty_cells.remove((cfg.FIELD_WIDTH // 2, cfg.FIELD_HEIGHT // 2))
        self.supplies = Supplies(*self.place_object(cfg.SUPPLY))
        self.generate_field()
        self.base_x, self.base_y = self.place_object(cfg.MINK)
        self.progress_bar = 0
        self.raccoon = None  # Экземпляр енота
        self.raccoon_delay = 0  # Задержка появления енота

    def place_object(self, obj) -> tuple[int, int]:
        """Размещает объект на игровом поле."""
        while self.empty_cells:
            x, y = choice(self.empty_cells)
            self.field[y][x] = obj
            self.empty_cells.remove((x, y))
            return x, y

    def generate_field(self) -> None:
        """Генерирует препятствия"""
        for _ in range(30):
            if self.empty_cells:
                self.place_object(cfg.OBSTACLE)

    def draw(self) -> None:
        crs.start_color()
        crs.init_pair(1, crs.COLOR_CYAN, crs.COLOR_BLACK)    # Еж
        crs.init_pair(2, crs.COLOR_GREEN, crs.COLOR_BLACK)   # Норка
        crs.init_pair(3, crs.COLOR_RED, crs.COLOR_BLACK)     # Препятствия
        crs.init_pair(4, crs.COLOR_YELLOW, crs.COLOR_BLACK)  # Информация
        crs.init_pair(5, crs.COLOR_MAGENTA, crs.COLOR_BLACK) # Енот

        self.stdscr.clear()
        height, width = self.stdscr.getmaxyx()
        if height < (cfg.FIELD_HEIGHT + 20) or width < cfg.FIELD_WIDTH + 2:
            self.stdscr.addstr(0, 0, "Увеличьте размер окна терминала.")
            self.stdscr.refresh()
            self.stdscr.getch()
            return

        buffer = []
        for y in range(cfg.FIELD_HEIGHT):
            for x in range(cfg.FIELD_WIDTH):
                ch = self.field[y][x]
                color = 0
                if ch == cfg.MINK:
                    color = 2
                elif ch == cfg.OBSTACLE:
                    color = 3
                elif ch == cfg.RACCOON:
                    color = 5
                if ch == cfg.SUPPLY and self.supplies.raised:
                    self.field[y][x] = cfg.EMPTY
                    self.empty_cells.append((x, y))
                buffer.append((y + 1, x + 1, ch, color))

        buffer.append((self.hedgehog.y + 1, self.hedgehog.x + 1, self.hedgehog.img, 1))

        for x in range(cfg.FIELD_WIDTH + 2):
            buffer.append((0, x, '─', 4))
            buffer.append((cfg.FIELD_HEIGHT + 1, x, '─', 4))
        for y in range(cfg.FIELD_HEIGHT + 2):
            buffer.append((y, 0, '│', 4))
            buffer.append((y, cfg.FIELD_WIDTH + 1, '│', 4))
        buffer.append((0, 0, '┌', 4))
        buffer.append((0, cfg.FIELD_WIDTH + 1, '┐', 4))
        buffer.append((cfg.FIELD_HEIGHT + 1, 0, '└', 4))
        buffer.append((cfg.FIELD_HEIGHT + 1, cfg.FIELD_WIDTH + 1, '┘', 4))

        info_lines = [
            f"Скорость: {self.hedgehog.speed}",
            f"Направление: {self.hedgehog.img}",
            f"Координаты: {self.hedgehog.x} {self.hedgehog.y}",
            f"Время: {self.elapsed_time} сек",
            f"Прогресс сбора: {self.progress_bar}",
            f"Припас: {self.supplies.type_of_supply[0]}",
            f"Шаги: {self.hedgehog.steps}",
        ]
        for idx, line in enumerate(info_lines):
            self.stdscr.addstr(cfg.FIELD_HEIGHT + 3 + idx, 0, line, crs.color_pair(4))

        for y, x, ch, color in buffer:
            if color:
                self.stdscr.addch(y, x, ch, crs.color_pair(color))
            else:
                self.stdscr.addch(y, x, ch)

         # Легенда
        legend_lines = [
            "Легенда:",
            f"{self.hedgehog.img} - Еж",
            f"{cfg.MINK} - Норка",
            f"{cfg.OBSTACLE} - Препятствие",
            f"{cfg.SUPPLY} - Припас",
            f"{cfg.RACCOON} - Енот",
            "",
            "Управление:",
            "Стрелки - движение",
            "Пробел - фыркать (тратит 1 заряд, радиус 4 клетки)"
        ]
        for idx, line in enumerate(legend_lines):
            self.stdscr.addstr(cfg.FIELD_HEIGHT + 3 + len(info_lines) + idx, 0, line, crs.color_pair(4))

        for y, x, ch, color in buffer:
            if color:
                self.stdscr.addch(y, x, ch, crs.color_pair(color))
            else:
                self.stdscr.addch(y, x, ch)
        self.stdscr.refresh()

    def handle_input(self) -> None:
        key = self.stdscr.getch()
        if key != -1:
            self.last_key = key

        if key == 27:  # ESC
            self.running = False
        elif self.last_key == crs.KEY_RIGHT or self.last_key == crs.KEY_B3:
            self.hedgehog.change_direction(-1)
        elif self.last_key == crs.KEY_LEFT or self.last_key == crs.KEY_B1:
            self.hedgehog.change_direction(1)
        elif self.last_key == crs.KEY_UP or self.last_key == crs.KEY_A2:
            self.hedgehog.change_speed(1)
        elif self.last_key == crs.KEY_DOWN or self.last_key == crs.KEY_C2:
            self.hedgehog.change_speed(-1)
        elif key == ord(' '):  # Пробел для фырканья
            if self.hedgehog.charge > 0:
                self.hedgehog.charge -= 1
                if self.raccoon and self.raccoon.active:

                    distance = max(abs(self.hedgehog.x - self.raccoon.x),
                                  abs(self.hedgehog.y - self.raccoon.y))
                    if distance <= 4:
                        self.raccoon.active = False
                        self.field[self.raccoon.y][self.raccoon.x] = cfg.EMPTY
                        self.empty_cells.append((self.raccoon.x, self.raccoon.y))


        self.last_key = -1
        dx, dy = cfg.DIRECTIONS[self.hedgehog.img]
        self.hedgehog.move(dx, dy)

    def check_collisions(self) -> str:
        x, y = self.hedgehog.x, self.hedgehog.y

        # Проверка выхода за границы поля
        if x < 0 or x >= cfg.FIELD_WIDTH or y < 0 or y >= cfg.FIELD_HEIGHT:
            return 'loss'

        cell = self.field[y][x]

        # Если еж наткнулся на препятствие, откатываем его движение
        if cell == cfg.OBSTACLE:
            dx, dy = cfg.DIRECTIONS[self.hedgehog.img]
            self.hedgehog.x -= dx  # Возвращаем ежа на предыдущую позицию
            self.hedgehog.y -= dy
            self.hedgehog.steps -= 1  # Уменьшаем счетчик шагов

        # Проигрыш только при потере всех жизней
        if self.hedgehog.health <= 0:
            return 'loss'

        # Логика для припасов
        if cell == cfg.SUPPLY:
            self.supplies.raised = True
            if not self.raccoon:
                raccoon_x, raccoon_y = self.place_object(cfg.RACCOON)
                self.raccoon = Raccoon(raccoon_x, raccoon_y)
                self.raccoon.active = True
                self.raccoon_delay = randint(2, 4)

        # Логика для норки
        if cell == cfg.MINK and self.supplies.raised:
            self.supplies.raised = False
            self.progress_bar += self.supplies.type_of_supply[1]
            self.supplies.x, self.supplies.y = self.place_object(cfg.SUPPLY)
            self.supplies.choosing_a_supply()
            if self.raccoon:
                self.raccoon.active = False
                self.field[self.raccoon.y][self.raccoon.x] = cfg.EMPTY
                self.empty_cells.append((self.raccoon.x, self.raccoon.y))

        # Столкновение с енотом
        if (self.raccoon and self.raccoon.active and
            self.raccoon.x == self.hedgehog.x and
            self.raccoon.y == self.hedgehog.y):
            self.raccoon.stealed(self.hedgehog, self.supplies)
            self.field[self.raccoon.y][self.raccoon.x] = cfg.EMPTY
            self.empty_cells.append((self.raccoon.x, self.raccoon.y))

        if self.progress_bar >= 3:
            return "win"

        return 'continue'

    def play(self) -> str:
        iterations = 0
        self.elapsed_time = 0
        self.last_key = -1
        while self.running:
            self.draw()
            self.handle_input()

            # Управление енотом
            if self.raccoon and self.supplies.raised:
                if self.raccoon_delay > 0:
                    self.raccoon_delay -= 1
                else:
                    old_x, old_y = self.raccoon.x, self.raccoon.y
                    self.raccoon.move_towards(self.hedgehog.x, self.hedgehog.y, self.field)
                    if (self.raccoon.x, self.raccoon.y) != (old_x, old_y):
                        self.field[old_y][old_x] = cfg.EMPTY
                        self.field[self.raccoon.y][self.raccoon.x] = cfg.RACCOON
                    # Проверка на кражу каждые 2-4 шага
                    if self.hedgehog.steps % randint(2, 4) == 0:
                        self.raccoon.stealed(self.hedgehog, self.supplies)
                        if not self.raccoon.active:
                            self.field[self.raccoon.y][self.raccoon.x] = cfg.EMPTY
                            self.empty_cells.append((self.raccoon.x, self.raccoon.y))

            # Если припас сброшен, деактивируем енота
            if not self.supplies.raised and self.raccoon and self.raccoon.active:
                self.raccoon.active = False
                self.field[self.raccoon.y][self.raccoon.x] = cfg.EMPTY
                self.empty_cells.append((self.raccoon.x, self.raccoon.y))

            crs.napms(100)
            iterations += 1
            self.elapsed_time = iterations * 0.1

            status = self.check_collisions()
            if status == 'win':
                self.show_ASCII_screen(ASCII_WIN, "Поздравляем! Вы выиграли!")
                return "win"
            elif status == 'loss':
                self.show_ASCII_screen(ASCII_LOSE, "Вы проиграли!")
                return "loss"
        return "exit"

    def show_ASCII_screen(self, ascii_art: str, message: str) -> None:
        """Отображает экран с ASCII-артом и сообщением о результате игры."""
        self.stdscr.clear()
        lines = ascii_art.split("\n")
        height, width = self.stdscr.getmaxyx()
        start_y = height // 2 - len(lines) // 2
        for i, line in enumerate(lines):
            start_x = width // 2 - len(line) // 2
            self.stdscr.addstr(start_y + i, start_x, line)
        self.stdscr.addstr(start_y + len(lines) + 1, width // 2 - len(message) // 2, message)
        self.stdscr.refresh()
        crs.napms(2000)


class Hedgehog(GameObject):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.img = "↓"
        self.direction = "↓"
        self.speed = 0
        self.health = 1
        self.charge = 6
        self.steps = 0

    def move(self, dx, dy) -> None:
        if self.speed:
            self.x += dx
            self.y += dy
            self.steps += 1  # Увеличиваем счетчик при каждом перемещении

    def change_direction(self, step) -> None:
        """Меняет направление корабля"""
        # Получаем список направлений
        directions_list = list(cfg.DIRECTIONS.keys())
        current_index = directions_list.index(self.img)
        new_index = (current_index + step) % len(directions_list)
        self.img = directions_list[new_index]  # Обновляем изображение корабля

        if cfg.DIRECTIONS[self.img][0] and cfg.DIRECTIONS[self.img][1]:
            self.direction = '↓' if cfg.DIRECTIONS[self.img][1] > 0 else '↑'
            self.direction += '→' if cfg.DIRECTIONS[self.img][0] > 0 else '←'
        else:
            self.direction = self.img

    def change_speed(self, delta) -> None:
        """Изменяет скорость корабля"""
        self.speed = max(0, min(2, self.speed + delta))


class Supplies(GameObject):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.raised = False
        self.supplys = {
            'Яблоко': 3,
            'Гриб': 2,
            'Ягода': 1,
        }
        self.type_of_supply = None
        self.choosing_a_supply()

    def choosing_a_supply(self):
        self.type_of_supply = choice(list(self.supplys.items()))


class Raccoon(GameObject):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.active = False  # Флаг активности енота

    def move_towards(self, target_x, target_y, field):
        dx = 1 if target_x > self.x else -1 if target_x < self.x else 0
        dy = 1 if target_y > self.y else -1 if target_y < self.y else 0
        new_x = self.x + dx
        new_y = self.y + dy
        # Проверяем, что новая клетка в пределах поля и не является препятствием
        if (0 <= new_x < cfg.FIELD_WIDTH and
            0 <= new_y < cfg.FIELD_HEIGHT and
            field[new_y][new_x] not in [cfg.OBSTACLE, cfg.MINK, cfg.SUPPLY]):
            self.x = new_x
            self.y = new_y

    def stealed(self, hedgehog, supplies):
        """Попытка украсть припас у ежа."""
        if (self.active and
            self.x == hedgehog.x and
            self.y == hedgehog.y and
            supplies.raised):
            hedgehog.health -= 1
            supplies.raised = False
            self.active = False

