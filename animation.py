import pygame
from pygame import Vector2, Surface


class AnimationManager:
    def __init__(self, frames_surface: Surface, frame_width: int, frame_interval: float):
        self.frames_image = frames_surface
        self.frame_height = self.frames_image.height
        self.frame_width = frame_width
        self.frame_count = self.frames_image.width // self.frame_width
        self.frame_interval = frame_interval

        self.frame_index = 0
        self.frame_timer = 0.0
        self.next_frame_time = self.frame_interval
    
    def update(self, delta: float):
        self.frame_timer += delta
        if self.frame_timer >= self.next_frame_time:
            self.next_frame_time += self.frame_interval
            self.frame_index = (self.frame_index + 1) % self.frame_count

    def draw(self, surf: Surface, position: Vector2, flip_x=False):
        frame_x = self.frame_width*self.frame_index

        frame_surf = Surface((self.frame_width, self.frame_height), pygame.SRCALPHA)
        frame_surf.blit(self.frames_image, (0, 0), (frame_x, 0, self.frame_width, self.frame_height))
        if flip_x:
            frame_surf = pygame.transform.flip(frame_surf, True, False)
        
        surf.blit(frame_surf, (position.x, position.y))
        