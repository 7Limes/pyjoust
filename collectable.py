from abc import ABC
import pygame
from pygame import Vector2, Surface
from base import PhysCircle, Jouster, Platform
from player import Player
from util import move_towards


EGG_RADIUS = 3.5
EGG_GRAVITY = 2.0
EGG_BOUNCE_DAMPING = 0.3
EGG_HORIZONTAL_DRAG = 0.5


class Collectable(PhysCircle):
    def __init__(self, position: Vector2, radius: float):
        super().__init__(Vector2(position), radius)
        self.should_delete = False
        self.is_collected = False
    
    def mark_for_deletion(self):
        self.should_delete = True
    
    def mark_collected(self):
        self.is_collected = True
    
    def update(self, delta: float, surf_width: float, platforms: list[Platform], jousters: list[Jouster]):
        pass

    def draw(self, surf: Surface):
        pass


class Egg(Collectable):
    def __init__(self, position: Vector2, velocity: Vector2):
        super().__init__(position, EGG_RADIUS)
        self.velocity = Vector2(velocity)
    
    def update(self, delta: float, surf_width: float, platforms: list[Platform], jousters: list[Jouster]):
        self.velocity.y += EGG_GRAVITY
        self.velocity.x = move_towards(self.velocity.x, 0, EGG_HORIZONTAL_DRAG)
        self.position += self.velocity * delta

        # Delete if falls off screen
        if self.position.y > 1000:
            self.mark_for_deletion()
            return

        # Horizontal wrapping
        if self.get_right().x < 0:
            self.position.x = surf_width+self.radius
        if self.get_left().x > surf_width:
            self.position.x = -self.radius

        # Collide with platforms
        for platform in platforms:
            if platform.rect.collidepoint(self.get_bottom()):
                self.position.y = platform.rect.top - self.radius
                self.velocity.y = -abs(self.velocity.y) * EGG_BOUNCE_DAMPING
            if platform.rect.collidepoint(self.get_top()):
                self.position.y = platform.rect.bottom + self.radius
                self.velocity.y = abs(self.velocity.y) * EGG_BOUNCE_DAMPING
            if platform.rect.collidepoint(self.get_left()):
                self.position.x = platform.rect.right + self.radius
                self.velocity.x = abs(self.velocity.x) * EGG_BOUNCE_DAMPING
            if platform.rect.collidepoint(self.get_right()):
                self.position.x = platform.rect.left - self.radius
                self.velocity.x = -abs(self.velocity.x) * EGG_BOUNCE_DAMPING

        # Check for collection
        for jouster in jousters:
            if not isinstance(jouster, Player):
                continue

            if self.position.distance_to(jouster.position) < self.radius+jouster.radius:
                self.mark_collected()
                self.mark_for_deletion()

    def draw(self, surf: Surface):
        pygame.draw.circle(surf, (170, 255, 120), self.position, self.radius)
