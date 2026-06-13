import pygame
from pygame import Vector2, Surface
from base import Jouster, Platform, JOUSTER_SPRITE_OFFSET
from animation import AnimationManager
from assets import ASSETS
from util import draw_circle_alpha
from game_globals import Globals

PLAYER_RADIUS = 6.0

class Bindings:
    def __init__(self, left_bindings: list[int], right_bindings: list[int], flap_bindings: list[int]):
        self.left_bindings = left_bindings
        self.right_bindings = right_bindings
        self.flap_bindings = flap_bindings  

    def left_is_pressed(self) -> bool:
        keys = pygame.key.get_pressed()
        return any(keys[b] for b in self.left_bindings)

    def right_is_pressed(self) -> bool:
        keys = pygame.key.get_pressed()
        return any(keys[b] for b in self.right_bindings)

    def flap_is_pressed(self) -> bool:
        keys = pygame.key.get_pressed()
        return any(keys[b] for b in self.flap_bindings)
    
    def flap_just_pressed(self) -> bool:
        keys = pygame.key.get_just_pressed()
        return any(keys[b] for b in self.flap_bindings)

    def any_pressed(self) -> bool:
        keys = pygame.key.get_pressed()
        return keys[self.left] or keys[self.right] or keys[self.flap]

PLAYER_CONTROLS = [
    Bindings([pygame.K_LEFT], [pygame.K_RIGHT], [pygame.K_m]),
    Bindings([pygame.K_a], [pygame.K_d], [pygame.K_SPACE]),
]

class Player(Jouster):
    def __init__(self, position: Vector2, player_number: int):
        if player_number == 0:
            animations = (
                AnimationManager(ASSETS.p1_bird_idle, 16, 0),
                AnimationManager(ASSETS.p1_bird_walk, 16, 1.0),
                AnimationManager(ASSETS.p1_bird_fly, 16, 0),
                AnimationManager(ASSETS.p1_bird_flap, 16, 0),
                AnimationManager(ASSETS.p1_bird_skid, 16, 0)
            )
        else:
            animations = (
                AnimationManager(ASSETS.p2_bird_idle, 16, 0),
                AnimationManager(ASSETS.p2_bird_walk, 16, 1.0),
                AnimationManager(ASSETS.p2_bird_fly, 16, 0),
                AnimationManager(ASSETS.p2_bird_flap, 16, 0),
                AnimationManager(ASSETS.p2_bird_skid, 16, 0)
            )
        
        team = player_number if Globals.player_friendly_fire else 0
        super().__init__(position, PLAYER_RADIUS, team, animations)
        self.player_number = player_number
        self.keybinds = PLAYER_CONTROLS[player_number]
        self.visual_facing_left = False

    def update(self, delta: float, surf_width: float, platforms: list[Platform], jousters: list[Jouster]):
        if self.keybinds.left_is_pressed():
            self.face_left()
            self.visual_facing_left = True
        elif self.keybinds.right_is_pressed():
            self.face_right()
            self.visual_facing_left = False
        else:
            self.face_neutral()
        
        if self.keybinds.flap_just_pressed():
            self.flap()

        super().update(delta, surf_width, platforms, jousters)
    
    def should_bounce_off_ground(self):
        return super().should_bounce_off_ground() or self.keybinds.flap_is_pressed()

    def draw(self, surf: Surface):
        half_frame_size = Vector2(self.anim.frame_width, self.anim.frame_height) / 2
        sprite_position = self.position-half_frame_size+JOUSTER_SPRITE_OFFSET
        self.anim.draw(surf, sprite_position, flip_x=self.visual_facing_left)
        
        if Globals.debug_mode:
            draw_circle_alpha(surf, (255, 0, 0, 128), self.position, self.radius)

