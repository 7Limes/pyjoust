import pygame
from pygame import Surface


ASSETS_PATH = 'assets'


def load_asset(path: str) -> Surface:
    img = pygame.image.load(f'{ASSETS_PATH}/{path}')
    return img.convert_alpha()


class AssetContainer:
    def load(self):
        self.p1_bird_idle = load_asset('bird/p1_bird_idle.png')
        self.p1_bird_walk = load_asset('bird/p1_bird_walk.png')
        self.p1_bird_fly = load_asset('bird/p1_bird_fly.png')
        self.p1_bird_flap = load_asset('bird/p1_bird_flap.png')
        self.p1_bird_skid = load_asset('bird/p1_bird_skid.png')

        self.p2_bird_idle = load_asset('bird/p2_bird_idle.png')
        self.p2_bird_walk = load_asset('bird/p2_bird_walk.png')
        self.p2_bird_fly = load_asset('bird/p2_bird_fly.png')
        self.p2_bird_flap = load_asset('bird/p2_bird_flap.png')
        self.p2_bird_skid = load_asset('bird/p2_bird_skid.png')

        self.enemy1_bird_idle = load_asset('bird/enemy_bird_idle.png')
        self.enemy1_bird_walk = load_asset('bird/enemy_bird_walk.png')
        self.enemy1_bird_fly = load_asset('bird/enemy_bird_fly.png')
        self.enemy1_bird_flap = load_asset('bird/enemy_bird_flap.png')
        self.enemy1_bird_skid = load_asset('bird/enemy_bird_skid.png')

        self.enemy2_bird_idle = load_asset('bird/enemy2_bird_idle.png')
        self.enemy2_bird_walk = load_asset('bird/enemy2_bird_walk.png')
        self.enemy2_bird_fly = load_asset('bird/enemy2_bird_fly.png')
        self.enemy2_bird_flap = load_asset('bird/enemy2_bird_flap.png')
        self.enemy2_bird_skid = load_asset('bird/enemy2_bird_skid.png')

        self.enemy3_bird_idle = load_asset('bird/enemy3_bird_idle.png')
        self.enemy3_bird_walk = load_asset('bird/enemy3_bird_walk.png')
        self.enemy3_bird_fly = load_asset('bird/enemy3_bird_fly.png')
        self.enemy3_bird_flap = load_asset('bird/enemy3_bird_flap.png')
        self.enemy3_bird_skid = load_asset('bird/enemy3_bird_skid.png')

        self.platform1 = load_asset('platform/platform1.png')
        self.platform2 = load_asset('platform/platform2.png')
        self.platform3 = load_asset('platform/platform3.png')
        self.platform4 = load_asset('platform/platform4.png')
        self.platform5 = load_asset('platform/platform5.png')
        self.platform6 = load_asset('platform/platform6.png')
        self.platform7 = load_asset('platform/platform7.png')
        self.bigplatform = load_asset('platform/bigplatform.png')

        self.effect_explode = load_asset('effect/explode.png')
        self.effect_p1_respawn = load_asset('effect/p1_respawn.png')
        self.effect_p2_respawn = load_asset('effect/p2_respawn.png')

        self.score_250_y = load_asset('score/score_250_y.png')

        self.font_joust = load_asset('font/joust-font.png')


ASSETS: AssetContainer = AssetContainer()
