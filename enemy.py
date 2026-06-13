import random
import pygame
from pygame import Vector2, Surface, FRect
from base import Jouster, Platform
from util import move_towards, draw_dotted_line, draw_rect_alpha
from player import Player
from assets import ASSETS
from animation import AnimationManager
from game_globals import Globals
from game_globals import Globals

ENEMY_RADIUS = 6.0
ENEMY_TEAM_NUMBER = 999

LANE_Y_COORDINATES = [
    22,
    82,
    150
]

ENEMY_SWITCH_LANE_INTERVAL_MIN = 3.0
ENEMY_SWITCH_LANE_INTERVAL_MAX = 5.0

class Enemy(Jouster):
    def __init__(self, position: Vector2, animations: tuple[AnimationManager, ...]):
        team = random.randint(0, 999999) if Globals.enemy_friendly_fire else ENEMY_TEAM_NUMBER
        super().__init__(position, ENEMY_RADIUS, team, animations)
        self.target_x = -1.0
        self.target_y = -1.0
    
    def get_nearest_enemy(self, jousters: list[Jouster]) -> Player | None:
        enemies = [j for j in jousters if self.team != j.team]
        if enemies:
            enemies.sort(key=lambda p: p.position.distance_squared_to(self.position))
            return enemies[0]
        return None
    
    def update(self, delta: float, surf_width: float, platforms: list[Platform], jousters: list[Jouster]):
        super().update(delta, surf_width, platforms, jousters)

        # Stay out of lava
        if self.position.x < 48 or self.position.x > 208:
            if self.position.y > 170:
                super().flap()
        
        # Try to go to target y coord
        if self.target_y != -1 and self.position.y > self.target_y:
            self.flap()
        
        if self.target_x != -1:
            if self.position.x < self.target_x:
                self.face_right()
            elif self.position.x > self.target_x:
                self.face_left()
    
    def draw(self, surf: Surface):
        if Globals.debug_mode:
            pygame.draw.circle(surf, (255, 255, 0), (self.target_x, self.target_y), 2)
            draw_dotted_line(surf, (255, 255, 0), self.position, (self.target_x, self.target_y), dot_length=2)
        super().draw(surf)
        # pygame.draw.circle(surf, (0, 0, 255), self.position, self.radius)


class RandomLaneEnemy(Enemy):
    """
    Randomly switches between the 3 vertical lanes
    and barrels forward in a single direction
    """
    def __init__(self, position: Vector2, animations=None):
        if animations is None:
            super().__init__(position, (
                AnimationManager(ASSETS.enemy1_bird_idle, 16, 0),
                AnimationManager(ASSETS.enemy1_bird_walk, 16, 1.0),
                AnimationManager(ASSETS.enemy1_bird_fly, 16, 0),
                AnimationManager(ASSETS.enemy1_bird_flap, 16, 0),
                AnimationManager(ASSETS.enemy1_bird_skid, 16, 0)
            ))
        else:
            super().__init__(position, animations)
        
        self.lane_switch_timer = 0.0

    def update(self, delta: float, surf_width: float, platforms: list[Platform], jousters: list[Jouster]):
        # Keep going in the current direction
        if self.velocity.x < 0:
            self.target_x = self.position.x - 10
        elif self.velocity.x > 0:
            self.target_x = self.position.x + 10
        else:
            self.target_x = self.position.x + random.choice([10, -10])
        
        # Switch lanes
        self.lane_switch_timer = move_towards(self.lane_switch_timer, 0, delta)
        if self.lane_switch_timer == 0:
            self.target_y = random.choice(LANE_Y_COORDINATES)
            self.lane_switch_timer = random.uniform(ENEMY_SWITCH_LANE_INTERVAL_MIN, ENEMY_SWITCH_LANE_INTERVAL_MAX)

        super().update(delta, surf_width, platforms, jousters)

class ChaseLaneEnemy(RandomLaneEnemy):
    """
    Goes to the lane that the player is in
    """
    def __init__(self, position: Vector2):
        super().__init__(position, (
            AnimationManager(ASSETS.enemy2_bird_idle, 16, 0),
            AnimationManager(ASSETS.enemy2_bird_walk, 16, 1.0),
            AnimationManager(ASSETS.enemy2_bird_fly, 16, 0),
            AnimationManager(ASSETS.enemy2_bird_flap, 16, 0),
            AnimationManager(ASSETS.enemy2_bird_skid, 16, 0)
        ))

    def update(self, delta: float, surf_width: float, platforms: list[Platform], jousters: list[Jouster]):
        super().update(delta, surf_width, platforms, jousters)

        nearest_player = self.get_nearest_enemy(jousters)
        if nearest_player is not None:
            player_y = nearest_player.position.y
            self.target_y = sorted(LANE_Y_COORDINATES, key=lambda c: abs(player_y-c))[0]
    
    # def draw(self, surf: Surface):
    #     pygame.draw.circle(surf, (0, 255, 230), self.position, ENEMY_RADIUS)

class ChaseEnemy(Enemy):
    """
    Chases directly after the player
    """

    def __init__(self, position: Vector2):
        super().__init__(position, (
            AnimationManager(ASSETS.enemy2_bird_idle, 16, 0),
            AnimationManager(ASSETS.enemy2_bird_walk, 16, 1.0),
            AnimationManager(ASSETS.enemy2_bird_fly, 16, 0),
            AnimationManager(ASSETS.enemy2_bird_flap, 16, 0),
            AnimationManager(ASSETS.enemy2_bird_skid, 16, 0)
        ))

    def update(self, delta: float, surf_width: float, platforms: list[Platform], jousters: list[Jouster]):
        super().update(delta, surf_width, platforms, jousters)

        nearest_player = self.get_nearest_enemy(jousters)
        if nearest_player is not None:
            self.target_x = nearest_player.position.x
            self.target_y = nearest_player.position.y
    
    # def draw(self, surf: Surface):
    #     pygame.draw.circle(surf, (0, 255, 60), self.position, ENEMY_RADIUS)

class CautiousEnemy(Enemy):
    """
    Targets the area above the player whilst
    trying to avoid being hit
    """

    def __init__(self, position: Vector2):
        super().__init__(position, (
            AnimationManager(ASSETS.enemy3_bird_idle, 16, 0),
            AnimationManager(ASSETS.enemy3_bird_walk, 16, 1.0),
            AnimationManager(ASSETS.enemy3_bird_fly, 16, 0),
            AnimationManager(ASSETS.enemy3_bird_flap, 16, 0),
            AnimationManager(ASSETS.enemy3_bird_skid, 16, 0)
        ))

    def update(self, delta: float, surf_width: float, platforms: list[Platform], jousters: list[Jouster]):
        super().update(delta, surf_width, platforms, jousters)

        self.danger_rect = FRect(self.position.x-30, self.position.y-60, 60, 60)
        players_above = (j for j in jousters if isinstance(j, Player) and self.danger_rect.collidepoint(j.position))

        if any(players_above):
            # Try to move down and laterally
            self.target_y = self.position.y+20
            if self.velocity.x < 0:
                self.target_x = self.position.x-10
            elif self.velocity.x >= 0:
                self.target_x = self.position.x+10
        else:
            # Target above the player
            nearest_player = self.get_nearest_enemy(jousters)
            if nearest_player is not None:
                self.target_x = nearest_player.position.x
                self.target_y = nearest_player.position.y - 3
    
    def draw(self, surf: Surface):
        if Globals.debug_mode:
            draw_rect_alpha(surf, (200, 0, 0), self.danger_rect, 40)
        super().draw(surf)


class ForwardThinkerEnemy(Enemy):
    """
    Tries to target where the player is going to be
    """
    def __init__(self, position: Vector2):
        super().__init__(position, (
            AnimationManager(ASSETS.enemy3_bird_idle, 16, 0),
            AnimationManager(ASSETS.enemy3_bird_walk, 16, 1.0),
            AnimationManager(ASSETS.enemy3_bird_fly, 16, 0),
            AnimationManager(ASSETS.enemy3_bird_flap, 16, 0),
            AnimationManager(ASSETS.enemy3_bird_skid, 16, 0)
        ))
    
    def update(self, delta: float, surf_width: float, platforms: list[Platform], jousters: list[Jouster]):
        super().update(delta, surf_width, platforms, jousters)

        nearest_player = self.get_nearest_enemy(jousters)
        if nearest_player is not None:
            target_pos = nearest_player.position + nearest_player.velocity
            target_pos.y -= 3
            self.target_x = target_pos.x
            self.target_y = target_pos.y

