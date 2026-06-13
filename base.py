import pygame
from pygame import Vector2, Surface, FRect
from util import move_towards, draw_circle_alpha
from animation import AnimationManager
from game_globals import Globals

JOUSTER_GRAVITY = 2.0
JOUSTER_FLAP_Y_FORCE = 35.0
JOUSTER_FLAP_X_FORCE = 25.0
JOUSTER_GROUND_FLAP_FORCE = 60.0
JOUSTER_FLAP_COOLDOWN = 0.1
JOUSTER_FLAP_VISUAL_DURATION = 0.15
JOUSTER_TURNAROUND_MULTIPLIER = 2.0

JOUSTER_GROUND_ACCEL = 1.5

JOUSTER_MAX_X_VELOCITY = 150.0
JOUSTER_MAX_Y_VELOCITY = 100.0

JOUSTER_BOUNCE_DAMPING = 0.8

NEUTRAL_JOUST_DISTANCE = 2.5
JOUSTER_COLLISION_FORCE_MULTIPLIER = 100.0

JOUSTER_SPRITE_OFFSET = Vector2(0, -3.0)

LAVA_Y_POS = 180.0



class Platform:
    def __init__(self, x: float, y: float, sprite: Surface|None=None, size: tuple[int, int]|None=None):
        if size is None:
            width = sprite.width
            height = sprite.height
        else:
            width, height = size
        
        self.rect = FRect(x, y, width, height)
        self.sprite = sprite
    
    def draw(self, surf: Surface):
        if self.sprite is None:
            pygame.draw.rect(surf, (84, 41, 10), self.rect)
        else:
            surf.blit(self.sprite, self.rect)


class PhysCircle:
    def __init__(self, position: Vector2, radius: float):
        self.position = position
        self.velocity = Vector2(0, 0)
        self.radius = radius
    
    def get_left(self):
        return self.position - Vector2(self.radius, 0)

    def get_right(self):
        return self.position + Vector2(self.radius, 0)

    def get_top(self):
        return self.position - Vector2(0, self.radius)

    def get_bottom(self):
        return self.position + Vector2(0, self.radius)


class Jouster(PhysCircle):
    def __init__(self, position: Vector2, radius: float, team: int, animations: tuple[AnimationManager, ...]):
        super().__init__(position, radius)
        self.is_dead = False
        self.is_grounded = False
        self.flap_cooldown_timer = 0.0
        self.flap_visual_timer = 0.0
        self.facing_dir = 0.0  # Either -1, 0, or 1
        self.team = team

        self.idle_anim = animations[0]
        self.walk_anim = animations[1]
        self.fly_anim = animations[2]
        self.flap_anim = animations[3]
        self.skid_anim = animations[4]
        self.anim = self.idle_anim

    def collides_with(self, other: Jouster) -> bool:
        return self.position.distance_to(other.position) < self.radius+other.radius

    def should_bounce_off_ground(self):
        return False

    # Movement methods
    def apply_force(self, force: Vector2):
        self.velocity += force
    
    def face_left(self):
        self.facing_dir = -1.0
        if self.is_grounded:
            self.velocity.x -= JOUSTER_GROUND_ACCEL
    
    def face_right(self):
        self.facing_dir = 1.0
        if self.is_grounded:
            self.velocity.x += JOUSTER_GROUND_ACCEL
    
    def face_neutral(self):
        self.facing_dir = 0.0
    
    def flap(self):
        if self.flap_cooldown_timer == 0:
            y_force = JOUSTER_GROUND_FLAP_FORCE if self.is_grounded else JOUSTER_FLAP_Y_FORCE
            self.velocity.y -= y_force

            xvel_force_multiplier = JOUSTER_FLAP_X_FORCE

            # Apply additional turnaround force
            if self.facing_dir == -1 and self.velocity.x > 0:
                xvel_force_multiplier *= JOUSTER_TURNAROUND_MULTIPLIER
            elif self.facing_dir == 1 and self.velocity.x < 0:
                xvel_force_multiplier *= JOUSTER_TURNAROUND_MULTIPLIER
            self.velocity.x += xvel_force_multiplier * self.facing_dir


            self.flap_cooldown_timer = JOUSTER_FLAP_COOLDOWN
            self.flap_visual_timer = JOUSTER_FLAP_VISUAL_DURATION
    
    def kill(self):
        self.is_dead = True
    
    def update_animations(self, delta: float):
        self.flap_visual_timer = move_towards(self.flap_visual_timer, 0, delta)

        if self.is_grounded and not self.should_bounce_off_ground():
            if self.velocity.x == 0:
                self.anim = self.idle_anim
            elif self.velocity.x > 0 and self.facing_dir == -1:
                self.anim = self.skid_anim
            elif self.velocity.x < 0 and self.facing_dir == 1:
                self.anim = self.skid_anim
            else:
                self.anim = self.walk_anim
                self.anim.update(abs(self.velocity.x) * 0.005)
        else:
            if self.flap_visual_timer == 0:
                self.anim = self.fly_anim
            else:
                self.anim = self.flap_anim
    
    def update(self, delta: float, surf_width: float, platforms: list[Platform], jousters: list[Jouster]):
        if self.is_dead:
            # Don't update if dead
            return

        # Apply gravity
        self.velocity.y += JOUSTER_GRAVITY

        # Clamp velocity
        self.velocity.x = pygame.math.clamp(self.velocity.x, -JOUSTER_MAX_X_VELOCITY, JOUSTER_MAX_X_VELOCITY)
        self.velocity.y = pygame.math.clamp(self.velocity.y, -JOUSTER_MAX_Y_VELOCITY, JOUSTER_MAX_Y_VELOCITY)
        
        self.position += self.velocity * delta

        # Horizontal wrapping
        if self.get_right().x < 0:
            self.position.x = surf_width+self.radius
        if self.get_left().x > surf_width:
            self.position.x = -self.radius

        # Collide with platforms
        self.is_grounded = False
        for platform in platforms:
            if platform.rect.collidepoint(self.get_bottom()):
                self.is_grounded = True
                self.position.y = platform.rect.top - self.radius
                if self.should_bounce_off_ground():
                    self.velocity.y = -abs(self.velocity.y) * JOUSTER_BOUNCE_DAMPING
                else:
                    self.velocity.y = 0
            if platform.rect.collidepoint(self.get_top()):
                self.position.y = platform.rect.bottom + self.radius
                self.velocity.y = abs(self.velocity.y) * JOUSTER_BOUNCE_DAMPING
            if platform.rect.collidepoint(self.get_left()):
                self.position.x = platform.rect.right + self.radius
                self.velocity.x = abs(self.velocity.x) * JOUSTER_BOUNCE_DAMPING
            if platform.rect.collidepoint(self.get_right()):
                self.position.x = platform.rect.left - self.radius
                self.velocity.x = -abs(self.velocity.x) * JOUSTER_BOUNCE_DAMPING
        
        # Fall into lava
        if self.position.y > LAVA_Y_POS:
            self.kill()
        
        # Collide with other jousters
        for jouster in jousters:
            if self is jouster:
                continue
            
            if self.collides_with(jouster):
                if self.team != jouster.team:
                    y_diff = self.position.y - jouster.position.y
                    if abs(y_diff) < NEUTRAL_JOUST_DISTANCE:
                        # Jousters at roughly the same height; neutral joust
                        pass
                    elif y_diff > 0:
                        self.kill()
                    elif y_diff < 0:
                        jouster.kill()
                
                collision_vector = self.position - jouster.position
                if collision_vector.magnitude_squared() != 0:
                    collision_force = collision_vector.normalize()
                    self.apply_force(collision_force * JOUSTER_COLLISION_FORCE_MULTIPLIER)
                    jouster.apply_force(collision_force * -JOUSTER_COLLISION_FORCE_MULTIPLIER)
        
        self.update_animations(delta)

        self.flap_cooldown_timer = move_towards(self.flap_cooldown_timer, 0, delta)
    
    def draw(self, surf: Surface):
        half_frame_size = Vector2(self.anim.frame_width, self.anim.frame_height) / 2
        sprite_position = self.position-half_frame_size+JOUSTER_SPRITE_OFFSET
        self.anim.draw(surf, sprite_position, flip_x=self.facing_dir==-1)

        if Globals.debug_mode:
            draw_circle_alpha(surf, (0, 0, 255, 128), self.position, self.radius)


class Spawner:
    def __init__(self, x: float, y: float):
        self.position = Vector2(x, y)
    
    def draw(self, surf: Surface):
        pygame.draw.circle(surf, (0, 0, 150), self.position, 5)
