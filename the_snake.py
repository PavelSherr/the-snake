"""Скрипт реализует классическую игру 'Змейка' с использованием библиотеки Pygame.

Содержит базовую физику перемещения сетки, обработку пользовательского ввода,
генерацию случайных позиций объектов и канонический игровой цикл.
"""

from random import choice, randint

import pygame

# Константы для размеров поля и сетки:
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Направления движения:
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Цвета:
BOARD_BACKGROUND_COLOR = (0, 0, 0)
BORDER_COLOR = (93, 216, 228)
APPLE_COLOR = (255, 0, 0)
SNAKE_COLOR = (0, 255, 0)

# Скорость движения змейки:
SPEED = 10

# Настройка игрового окна:
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
pygame.display.set_caption('Змейка')
clock = pygame.time.Clock()


class GameObject:
    """Базовый класс для игровых объектов."""

    def __init__(self, position=(0, 0), body_color=None):
        """Инициализирует базовые атрибуты игрового объекта."""
        self.position = position
        self.body_color = body_color

    def _draw_cell(self, cell_position=None, cell_color=None):
        """Отрисовывает одну ячейку на игровом поле."""
        target_position = cell_position or self.position
        target_color = cell_color or self.body_color

        rect = pygame.Rect(target_position, (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, target_color, rect)
        pygame.draw.rect(screen, BORDER_COLOR, rect, 1)

    def draw(self):
        """Метод отрисовки (переопределяется в подклассах)."""
        raise NotImplementedError(
            'Метод draw() должен быть переопределен в подклассе.'
        )


class Apple(GameObject):
    """Класс, описывающий яблоко."""

    def __init__(self, occupied_positions=None):
        """Инициализирует яблоко случайной позицией."""
        super().__init__(body_color=APPLE_COLOR)
        self.randomize_position(
            occupied_positions if occupied_positions is not None else []
        )

    def randomize_position(self, occupied_positions):
        """Устанавливает случайное положение яблока на поле."""
        while True:
            col_index = randint(0, GRID_WIDTH - 1)
            row_index = randint(0, GRID_HEIGHT - 1)
            self.position = (col_index * GRID_SIZE, row_index * GRID_SIZE)
            if self.position not in occupied_positions:
                break

    def draw(self):
        """Отрисовывает яблоко на игровой поверхности."""
        self._draw_cell()


class Snake(GameObject):
    """Класс, описывающий змейку."""

    def __init__(self):
        """Инициализирует змейку в центре экрана."""
        center_x = GRID_WIDTH // 2 * GRID_SIZE
        center_y = GRID_HEIGHT // 2 * GRID_SIZE
        start_pos = (center_x, center_y)
        super().__init__(position=start_pos, body_color=SNAKE_COLOR)
        self.reset()

    def reset(self):
        """Сбрасывает состояние змейки после проигрыша."""
        self.length = 1
        self.positions = [self.position]
        self.direction = choice([UP, DOWN, LEFT, RIGHT])
        self.last = None

    def update_direction(self, next_direction):
        """Обновляет направление движения змейки."""
        if next_direction:
            self.direction = next_direction

    def get_head_position(self):
        """Возвращает позицию головы змейки."""
        return self.positions

    def move(self):
        """Обновляет позицию змейки, учитывая её движение."""
        head_x, head_y = self.get_head_position()
        dir_x, dir_y = self.direction

        # Вычисляем новые координаты с учетом прохождения сквозь стены
        new_x = (head_x + dir_x * GRID_SIZE) % SCREEN_WIDTH
        new_y = (head_y + dir_y * GRID_SIZE) % SCREEN_HEIGHT
        new_head = (new_x, new_y)

        # Добавляем новую голову в начало списка
        self.positions.insert(0, new_head)

        # Тернарный оператор для обработки хвоста
        self.last = (
            self.positions.pop() if len(self.positions) > self.length else None
        )

    def draw(self):
        """Отрисовывает змейку на игровой поверхности."""
        # 1. Сначала затираем старый хвост цветом фона
        if self.last:
            self._draw_cell(
                cell_position=self.last,
                cell_color=BOARD_BACKGROUND_COLOR
            )

        # 2. Перерисовываем прошлую голову как обычный сегмент тела
        if len(self.positions) > 1:
            self._draw_cell(cell_position=self.positions)

        # 3. Рисуем новую голову
        self._draw_cell(cell_position=self.get_head_position())


def handle_keys(game_object):
    """Обрабатывает нажатия клавиш и возвращает новое направление."""
    key_to_direction = {
        pygame.K_UP: UP,
        pygame.K_DOWN: DOWN,
        pygame.K_LEFT: LEFT,
        pygame.K_RIGHT: RIGHT,
    }

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit
        elif event.type == pygame.KEYDOWN:
            new_dir = key_to_direction.get(event.key)
            if new_dir:
                curr_dir = game_object.direction
                # Если сумма векторов дает (0, 0), направления противоположны
                if (new_dir + curr_dir != 0 or
                        new_dir + curr_dir != 0):
                    return new_dir
    return None


def main():
    """Основной цикл игры."""
    pygame.init()

    # Создаем игровые объекты
    snake = Snake()
    apple = Apple(occupied_positions=snake.positions)

    # Очищаем экран перед стартом
    screen.fill(BOARD_BACKGROUND_COLOR)

    while True:
        clock.tick(SPEED)

        # 1. ВВОД: Обрабатываем ввод пользователя и получаем вектор поворота
        next_dir = handle_keys(snake)

        # 2. ОБРАБОТКА: Передаем вектор змейке и двигаем её
        snake.update_direction(next_dir)
        snake.move()

        # Сохраняем позицию головы для проверки столкновений
        head_position = snake.get_head_position()

        # Проверяем коллизии (с яблоком или самой собой)
        if head_position == apple.position:
            snake.length += 1
            apple.randomize_position(snake.positions)
        elif head_position in snake.positions[1:]:
            snake.reset()
            screen.fill(BOARD_BACKGROUND_COLOR)
            apple.randomize_position(snake.positions)

        # 3. ВЫВОД: Отрисовываем объекты и обновляем сцену
        apple.draw()
        snake.draw()
        pygame.display.update()


if __name__ == '__main__':
    main()
