import pygame
from pygame import Vector2, Surface, Rect
from animation import AnimationManager
from assets import ASSETS
from util import move_towards

RESPAWN_EFFECT_DURATION = 0.5


class Effect:
    def __init__(self, position: Vector2, animation: AnimationManager, render_offset: tuple[float, float]=(0, 0), auto_delete=True):
        self.position = Vector2(position)
        self.animation = animation
        self.render_offset = Vector2(render_offset)
        self.auto_delete = auto_delete
        self.should_delete = False
    
    def update(self, delta: float):
        is_last_frame = self.animation.frame_index == self.animation.frame_count-1
        prev_timer_target = self.animation.next_frame_time

        self.animation.update(delta)

        # Check if animation is finished
        if self.auto_delete and is_last_frame and prev_timer_target != self.animation.next_frame_time:
            self.should_delete = True

    def draw(self, surf: Surface):
        self.animation.draw(surf, self.position+self.render_offset)


class ExplodeEffect(Effect):
    def __init__(self, position: Vector2):
        super().__init__(position, AnimationManager(ASSETS.effect_explode, 16, 0.2), (-7, -7))


class PlayerRespawnEffect(Effect):
    def __init__(self, position: Vector2, player_number: int):
        effect_asset = ASSETS.effect_p1_respawn if player_number % 2 == 0 else ASSETS.effect_p2_respawn
        super().__init__(position, AnimationManager(effect_asset, 16, 0.25), (0, -6), auto_delete=False)
        self.move_up_timer = 0.0
        self.clip_start_y = position.y+12
        self.clip_rect = Rect(self.position.x, 0, self.animation.frame_width, 0)

    def update(self, delta):
        super().update(delta)

        # Move effect upwards
        self.move_up_timer = move_towards(self.move_up_timer, RESPAWN_EFFECT_DURATION, delta)
        t = self.move_up_timer / RESPAWN_EFFECT_DURATION
        final_y_pos = self.clip_start_y-self.animation.frame_height
        self.clip_rect.y = pygame.math.lerp(self.clip_start_y, final_y_pos, t)
        self.clip_rect.height = pygame.math.lerp(0, abs(self.clip_start_y-final_y_pos), t)+1
    
    def draw(self, surf: Surface):
        # Set clip rect so the effect emerges from the platform
        surf.set_clip(self.clip_rect)
        super().draw(surf)
        surf.set_clip(None)


class ScoreEffect(Effect):
    def __init__(self, position: Vector2):
        super().__init__(
            position,
            AnimationManager(ASSETS.score_250_y, ASSETS.score_250_y.width, 1.0),
            render_offset=(-10, -10)
        )