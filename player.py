import pygame
from pygame import Vector2, Surface
from base import Jouster, Platform, JOUSTER_SPRITE_OFFSET
from animation import AnimationManager
from assets import ASSETS
from util import draw_circle_alpha
from game_globals import Globals
from bindings import Bindings, joystick

PLAYER_RADIUS = 6.0


def create_player_bindings() -> list[Bindings]:
    p1_bindings = Bindings()
    p1_bindings.add_binary_action('left', [
        lambda: pygame.key.get_pressed()[pygame.K_LEFT],
        lambda: joystick(0).get_hat(0)[0] < 0,
        lambda: joystick(0).get_axis(0) < 0
    ])
    p1_bindings.add_binary_action('right', [
        lambda: pygame.key.get_pressed()[pygame.K_RIGHT],
        lambda: joystick(0).get_hat(0)[0] > 0,
        lambda: joystick(0).get_axis(0) > 0
    ])
    p1_bindings.add_binary_action('flap', [
        lambda: pygame.key.get_pressed()[pygame.K_m],
        lambda: joystick(0).get_button(0)
    ])

    p2_bindings = Bindings()
    p2_bindings.add_binary_action('left', [
        lambda: pygame.key.get_pressed()[pygame.K_a],
        lambda: joystick(1).get_hat(0)[0] < 0,
        lambda: joystick(1).get_axis(0) < 0
    ])
    p2_bindings.add_binary_action('right', [
        lambda: pygame.key.get_pressed()[pygame.K_d],
        lambda: joystick(1).get_hat(0)[0] > 0,
        lambda: joystick(1).get_axis(0) > 0

    ])
    p2_bindings.add_binary_action('flap', [
        lambda: pygame.key.get_pressed()[pygame.K_SPACE],
        lambda: joystick(1).get_button(0)
    ])

    return [p1_bindings, p2_bindings]


PLAYER_CONTROLS = create_player_bindings()

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
        self.bindings = PLAYER_CONTROLS[player_number]
        self.visual_facing_left = False

    def update(self, delta: float, surf_width: float, platforms: list[Platform], jousters: list[Jouster]):
        if self.bindings.get_binary_action('left'):
            self.face_left()
            self.visual_facing_left = True
        elif self.bindings.get_binary_action('right'):
            self.face_right()
            self.visual_facing_left = False
        else:
            self.face_neutral()
        
        if self.bindings.get_pressed_binary_action('flap'):
            self.flap()

        super().update(delta, surf_width, platforms, jousters)
        self.bindings.save_previous_binary_actions()
    
    def should_bounce_off_ground(self):
        return super().should_bounce_off_ground() or self.bindings.get_binary_action('flap')

    def draw(self, surf: Surface):
        half_frame_size = Vector2(self.anim.frame_width, self.anim.frame_height) / 2
        sprite_position = self.position-half_frame_size+JOUSTER_SPRITE_OFFSET
        self.anim.draw(surf, sprite_position, flip_x=self.visual_facing_left)
        
        if Globals.debug_mode:
            draw_circle_alpha(surf, (255, 0, 0, 128), self.position, self.radius)

