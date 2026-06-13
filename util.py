import math
import pygame
from pygame import Surface, Color, Vector2


def move_towards(value: float, target: float, delta: float):
    """Moves `value` towards `target` by `delta`"""
    if value < target:
        value += delta
        if value >= target:
            return target
    elif value > target:
        value -= delta
        if value <= target:
            return target
    
    return value


def draw_circle_alpha(surf: Surface, color: Color, center: Vector2, radius: float):
    circle_surf = Surface((radius*2, radius*2), pygame.SRCALPHA)
    pygame.draw.circle(circle_surf, color, (radius, radius), radius)
    surf.blit(circle_surf, (center.x-radius, center.y-radius))


def draw_dotted_line(surface: Surface, color: Color, start_pos: Vector2, end_pos: Vector2, dot_length=6, gap=6, width=1):
    x1, y1 = start_pos
    x2, y2 = end_pos
    distance = math.hypot(x2 - x1, y2 - y1)
    if distance == 0: return
    
    step_length = dot_length + gap
    num_steps = int(distance / step_length)
    cx = (x2 - x1) / distance
    cy = (y2 - y1) / distance

    for i in range(num_steps):
        start_x = x1 + cx * i * step_length
        start_y = y1 + cy * i * step_length
        end_x = start_x + cx * dot_length
        end_y = start_y + cy * dot_length
        pygame.draw.line(surface, color, (int(start_x), int(start_y)), (int(end_x), int(end_y)), width)


def draw_rect_alpha(surface: Surface, color: Color, rect: pygame.Rect, alpha: int):
    rect_surf = Surface((rect.width, rect.height))
    rect_surf.fill(color)
    rect_surf.set_alpha(alpha)
    surface.blit(rect_surf, (rect.x, rect.y))
