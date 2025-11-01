from random import randint
from abc import ABC, abstractmethod
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
BORDER_COLOR = (93, 216, 228)

# Цвет яблока
APPLE_COLOR = (255, 0, 0)

# Цвет змейки
SNAKE_COLOR = (0, 255, 0)

# Скорость движения змейки:
SPEED = 10

# Настройка игрового окна:
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

# Заголовок окна игрового поля:
pygame.display.set_caption('Змейка')

# Настройка времени:
clock = pygame.time.Clock()


class GameObject(ABC):
    """
    Родительский класс для того, чтобы наследовать из него
    яблоко и змейку
    """

    def __init__(self, body_color,
                 position=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)):
        self.body_color = body_color
        self.position = position

    @abstractmethod
    def draw(self):
        """Метод для рисовки объекта"""
        pass


class Apple(GameObject):
    """Класс яблока, такие яблоки будет кушать змейка"""

    def __init__(self):
        super().__init__(APPLE_COLOR)
        self.randomize_position()

    def randomize_position(self):
        """Метод для выставления случайной позиции яблока на поле"""
        rand_position = (
            randint(0, GRID_WIDTH - 1) * GRID_SIZE,
            randint(0, GRID_HEIGHT - 1) * GRID_SIZE,
        )
        self.position = rand_position

    def draw(self):
        """Метод для рисовки яблока"""
        rect = pygame.Rect(self.position, (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, self.body_color, rect)
        pygame.draw.rect(screen, BORDER_COLOR, rect, 1)


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
            rect = pygame.Rect(position, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(screen, self.body_color, rect)
            pygame.draw.rect(screen, BORDER_COLOR, rect, 1)

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
            elif event.key == pygame.K_DOWN and game_object.direction != UP:
                game_object.next_direction = DOWN
            elif event.key == pygame.K_LEFT and game_object.direction != RIGHT:
                game_object.next_direction = LEFT
            elif event.key == pygame.K_RIGHT and game_object.direction != LEFT:
                game_object.next_direction = RIGHT


def main() -> None:
    """Главная функция для запуска программы"""
    pygame.init()
    snake = Snake()
    apple = Apple()

    while True:
        clock.tick(SPEED)
        handle_keys(snake)
        snake.update_direction()
        snake.move()

        if snake.get_head_position() == apple.position:
            apple.randomize_position()
            snake.is_apple_eaten = True

        if snake.get_head_position() in snake.positions[1:]:
            snake.reset()

        screen.fill(BOARD_BACKGROUND_COLOR)
        apple.draw()
        snake.draw()
        pygame.display.update()


if __name__ == '__main__':
    main()
