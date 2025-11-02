import json
from random import choice
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

# Цвет фона - черный:
BOARD_BACKGROUND_COLOR = (0, 0, 0)


# Цвет границы ячейки
def get_border_color(color) -> list[int]:
    """
    Рассчитать цвет края для ячейки данного цвета
    :return: цвет края, немного затемнённый
    """
    return [int(c * 0.67) for c in color]


# Цвет яблока
APPLE_COLOR = (255, 0, 0)

# Цвет змейки
SNAKE_COLOR = (0, 255, 0)

# Скорость движения змейки:
SPEED = 10

# Настройка игрового окна:
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

# Заголовок окна игрового поля:
GAME_TITLE = 'Змейка!'
pygame.display.set_caption(GAME_TITLE)

# Настройка времени:
clock = pygame.time.Clock()

KEY_TO_DIRECTION = {
    pygame.K_UP: UP,
    pygame.K_RIGHT: RIGHT,
    pygame.K_DOWN: DOWN,
    pygame.K_LEFT: LEFT,
}


class GameObject:
    """
    Родительский класс для того, чтобы наследовать из него
    яблоко и змейку
    """

    def __init__(self, body_color=None,
                 position=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)):
        self.body_color = body_color
        self.position = position

    def draw(self):
        """Метод для рисовки объекта"""
        pass

    def draw_single_tile(self, position=None, color=None):
        """
        Функция для отрисовки единственной клетки объекта. Объекты могу
        состоять из нескольких клеток и использовать эту функцию для
        отрисовки всех
        """
        if position is None:
            position = self.position
        if color is None:
            color = self.body_color

        rect = pygame.Rect(position, (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, color, rect)
        pygame.draw.rect(screen, get_border_color(color), rect, 1)


class Apple(GameObject):
    """Класс яблока, такие яблоки будет кушать змейка"""

    def __init__(self):
        super().__init__(APPLE_COLOR)
        self.randomize_position()

    def randomize_position(self, forbidden_positions=()):
        """Метод для выставления случайной позиции яблока на поле"""
        all_cells = set((x * GRID_SIZE, y * GRID_SIZE)
                        for x in range(GRID_WIDTH)
                        for y in range(GRID_HEIGHT))
        rand_cell = choice(tuple(all_cells - set(forbidden_positions)))

        self.position = rand_cell

    def draw(self):
        """Метод для рисовки яблока"""
        self.draw_single_tile()


class Snake(GameObject):
    """Класс змейки, она будет кушать яблоки"""

    def __init__(self):
        position = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        super().__init__(SNAKE_COLOR, position)
        self.length = 1
        self.positions = [position]
        self.direction = RIGHT
        self.next_direction = None
        self.body_color = (0, 255, 0)
        self.is_apple_eaten = False

    def update_direction(self):
        """Метод для обновления направления движения змейки"""
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

    def move(self):
        """Метод для применения шага движения к змейке"""
        head_x, head_y = self.get_head_position()
        dx, dy = self.direction
        new_head = (
            (head_x + dx * GRID_SIZE) % SCREEN_WIDTH,
            (head_y + dy * GRID_SIZE) % SCREEN_HEIGHT
        )
        self.positions.insert(0, new_head)
        if not self.is_apple_eaten:
            self.positions.pop()
        else:
            self.is_apple_eaten = False

    def draw(self):
        """Метод для отрисовки змейки"""
        for position in self.positions:
            self.draw_single_tile(position)

    def get_head_position(self) -> tuple[int, int]:
        """
        Возвращяет позицию головы змейки
        :return: tuple[int, int] позиция змейки
        """
        return self.positions[0]

    def reset(self) -> None:
        """Метод для обнуления змейки"""
        self.positions = [self.get_head_position()]
        self.direction = RIGHT
        self.next_direction = None
        self.is_apple_eaten = False


def handle_keys(game_object):
    """
    Функция для считывания нажатий клавиш движения и применения
    направления к game_object
    :param: game_object: объект для применения направления движения
    """
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and game_object.direction != DOWN:
                game_object.next_direction = UP

            next_direction = KEY_TO_DIRECTION.get(event.key)
            if next_direction is not None:

                # чек если попытка двигаться в противоположном направлении
                directions = list(KEY_TO_DIRECTION.values())
                cur_dir_index = directions.index(next_direction)
                opposite_dir_index = (cur_dir_index + 2) % 4
                opposite_dir = directions[opposite_dir_index]

                if game_object.direction != opposite_dir:
                    game_object.next_direction = next_direction

            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                raise SystemExit


def save_max_length(max_length) -> None:
    """
    Сохраняет длину в файл
    :param: max_length: новая длина змейки для сохранения
    """
    with open('game_data.json', 'w', encoding='utf-8') as f:
        json.dump({'max_length': max_length}, f)


def load_max_length() -> int:
    """
    Загружает длину из файла
    :return: int максимальная длина
    """
    with open('game_data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
        loaded_number = data.get('max_length')

        if loaded_number is None:
            loaded_number = 1

        return loaded_number


def main() -> None:
    """Главная функция для запуска программы"""
    pygame.init()
    snake = Snake()
    apple = Apple()

    max_length = load_max_length()
    last_max_length = max_length

    while True:
        clock.tick(SPEED)
        handle_keys(snake)
        snake.update_direction()
        snake.move()

        # найти макс. длину
        last_max_length = max_length
        max_length = max(
            max_length, len(snake.positions)
        )
        # сохранять только при изменении длины
        if last_max_length != max_length:
            save_max_length(max_length)

            pygame.display.set_caption(
                f'{GAME_TITLE} Рекордная длина: {max_length}'
            )

        if snake.get_head_position() == apple.position:
            apple.randomize_position(snake.positions)
            snake.is_apple_eaten = True

        if (len(snake.positions) > 4
                and snake.get_head_position() in snake.positions[1:]):
            snake.reset()

        screen.fill(BOARD_BACKGROUND_COLOR)
        apple.draw()
        snake.draw()
        pygame.display.update()


if __name__ == '__main__':
    main()
