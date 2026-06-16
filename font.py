import pygame
from pygame import Vector2, Surface, Color

class BitmapFont:
    """
    A simple class for rendering ascii-ordered bitmap fonts.
    """

    def __init__(self, font_surface: Surface, glyph_size: tuple[int, int], glyphs_per_row: int):
        self.font_surface = font_surface
        self.glyph_size = glyph_size
        self.glyph_width, self.glyph_height = glyph_size
        self.glyphs_per_row = glyphs_per_row
    
    def render(self, text: str, color: Color=(255, 255, 255)) -> Surface:
        render_surf_width = self.glyph_width * len(text)
        render_surf = Surface((render_surf_width, self.glyph_height), pygame.SRCALPHA)

        for i, char in enumerate(text):
            char_index = ord(char)
            rect_x = char_index % self.glyphs_per_row * self.glyph_width
            rect_y = char_index // self.glyphs_per_row * self.glyph_height

            # Blit and recolor glyph
            glyph_surf = Surface(self.glyph_size, pygame.SRCALPHA)
            glyph_surf.blit(self.font_surface, (0, 0), (rect_x, rect_y, self.glyph_width, self.glyph_height))
            glyph_surf.fill(color, special_flags=pygame.BLEND_RGBA_MULT)

            # Blit the final glyph to surf
            blit_x = i * self.glyph_width
            render_surf.blit(glyph_surf, (blit_x, 0))
        
        return render_surf
    
    def render_text(self, surf: Surface, position: Vector2, text: str, color: Color=(255, 255, 255)):
        text_surf = self.render(text, color)
        surf.blit(text_surf, (position.x, position.y))
