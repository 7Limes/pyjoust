import pygame
from pygame import Vector2, Surface

class BitmapFont:
    def __init__(self, font_surface: Surface, glyph_size: tuple[int, int], glyphs_per_row: int):
        self.font_surface = font_surface
        self.glyph_width, self.glyph_height = glyph_size
        self.glyphs_per_row = glyphs_per_row
    
    def render_text(self, surf: Surface, position: Vector2, text: str):
        for i, char in enumerate(text):
            char_index = ord(char)
            rect_x = char_index % self.glyphs_per_row * self.glyph_width
            rect_y = char_index // self.glyphs_per_row * self.glyph_height
            blit_x = position.x + i * self.glyph_width
            surf.blit(self.font_surface, (blit_x, position.y), (rect_x, rect_y, self.glyph_width, self.glyph_height))
