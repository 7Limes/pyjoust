import random
import pygame
from pygame import Vector2, Surface
from player import Player, PLAYER_CONTROLS
from base import Jouster, Platform, Spawner
from enemy import Enemy, RandomLaneEnemy, ChaseLaneEnemy, CautiousEnemy, ForwardThinkerEnemy
from collectable import Collectable, Egg
from assets import ASSETS
from util import move_towards
from effects import Effect, ExplodeEffect, PlayerRespawnEffect, ScoreEffect, TextEffect, RESPAWN_EFFECT_DURATION
from game_globals import Globals
from font import BitmapFont
from bindings import init_joystick_cache, reload_joystick_cache


WINDOW_SCALE = 4.0
BASE_RESOLUTION = (256, 192)

ENEMY_TYPES = [
    RandomLaneEnemy,
    ChaseLaneEnemy,
    CautiousEnemy,
    ForwardThinkerEnemy
]

PLAYER_RESPAWN_COOLDOWN = 3.0
SPAWN_PROTECTION_RADIUS = 40.0

MAX_ENEMY_COUNT = 3
ENEMY_SPAWN_COOLDOWN = (3.0, 7.0)


def main():
    pygame.init()

    scaled_resolution = Vector2(BASE_RESOLUTION) * WINDOW_SCALE
    win = pygame.display.set_mode(scaled_resolution, pygame.DOUBLEBUF)
    pygame.display.set_caption('joust')
    clock = pygame.time.Clock()
    font = pygame.font.SysFont('monospace', 15)

    pygame.joystick.init()
    init_joystick_cache()

    ASSETS.load()

    render_surf = Surface(BASE_RESOLUTION)
    bitmap_font = BitmapFont(ASSETS.font_joust, (8, 8), 16)

    platforms = [
        Platform(-100, -50, size=(BASE_RESOLUTION[0]+200, 50)),  # Ceiling
        Platform(0, 40, ASSETS.platform1),     # Top platforms
        Platform(-100, 40, None, (100, 5)),
        Platform(219, 40, ASSETS.platform2),
        Platform(256, 40, None, (100, 5)),
        Platform(74, 56, ASSETS.platform3),
        Platform(0, 104, ASSETS.platform4),    # Middle Platforms
        Platform(-100, 104, None, (100, 5)),
        Platform(177, 96, ASSETS.platform5),
        Platform(221, 104, ASSETS.platform6),
        Platform(256, 104, None, (100, 5)),
        Platform(89, 128, ASSETS.platform7),
        Platform(42, 168, ASSETS.bigplatform),  # Big platform
    ]

    jousters: list[Jouster] = []

    spawners: list[Spawner] = [
        Spawner(100, 50),
        Spawner(20, 98),
        Spawner(205, 90),
        Spawner(112, 162)
    ]

    collectables: list[Collectable] = []

    effects: list[Effect] = []

    player_respawn_timers: dict[int, float] = {}
    player_respawn_data: dict[int, tuple[Vector2, Effect]] = {}

    def find_spawn_pos():
        shuffled_spawners = list(spawners)
        random.shuffle(shuffled_spawners)
        for spawner in shuffled_spawners:
            # Skip if there's any jousters near the spawner
            if any(j.position.distance_to(spawner.position) < SPAWN_PROTECTION_RADIUS for j in jousters):
                continue
            return Vector2(spawner.position)
        
        # Fallback case; just pick one
        return Vector2(random.choice(spawners).position)

    def spawn_player(player_number: int, position: Vector2):
        jousters.append(Player(position, player_number))

    spawn_player(0, find_spawn_pos())
    # spawn_player(1, find_spawn_pos())

    enemy_spawn_timer = 0.0

    running = True
    while running:
        delta = clock.tick(60) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.JOYDEVICEADDED or event.type == pygame.JOYDEVICEREMOVED:
                reload_joystick_cache()
                    
        if pygame.key.get_just_pressed()[pygame.K_BACKSLASH]:
            Globals.debug_mode = not Globals.debug_mode
        # -- Game updates --

        # Spawn new enemies
        enemy_spawn_timer = move_towards(enemy_spawn_timer, 0, delta)
        if enemy_spawn_timer == 0:
            enemy_spawn_timer = random.uniform(*ENEMY_SPAWN_COOLDOWN)
            if len([j for j in jousters if not isinstance(j, Player)]) < MAX_ENEMY_COUNT:
                enemy_class = random.choice(ENEMY_TYPES)
                enemy: Enemy = object.__new__(enemy_class)
                enemy.__init__(find_spawn_pos())
                jousters.append(enemy)
        
        # Update jousters
        for jouster in jousters:
            jouster.update(delta, render_surf.width, platforms, jousters)

        # Update collectables
        for collectable in collectables:
            collectable.update(delta, render_surf.width, platforms, jousters)
        
        # Update effects
        for effect in effects:
            effect.update(delta)
        
        # Handle dead jousters
        for jouster in jousters:
            if jouster.is_dead:
                # Create explosion effect
                effects.append(ExplodeEffect(jouster.position))

                if isinstance(jouster, Player):
                    # Queue respawn
                    player_respawn_timers[jouster.player_number] = PLAYER_RESPAWN_COOLDOWN
                else:
                    # Create score effect
                    effects.append(ScoreEffect(jouster.position))
                    # Spawn an egg
                    collectables.append(Egg(jouster.position, jouster.velocity))
            
        # Handle collected collectables
        for collectable in collectables:
            if collectable.is_collected:
                effects.append(ScoreEffect(collectable.position))
        
        # Remove dead jousters
        jousters = [j for j in jousters if not j.is_dead]

        # Remove deleted collectables
        collectables = [c for c in collectables if not c.should_delete]

        # Remove deleted effects:
        effects = [e for e in effects if not e.should_delete]

        # Handle respawning
        for player_number, respawn_timer in list(player_respawn_timers.items()):
            respawn_timer = move_towards(respawn_timer, 0, delta)
            player_respawn_timers[player_number] = respawn_timer
            if respawn_timer <= RESPAWN_EFFECT_DURATION and player_number not in player_respawn_data:
                spawn_pos = find_spawn_pos()
                effect_pos = spawn_pos + Vector2(-8, -6)
                respawn_effect = PlayerRespawnEffect(effect_pos, player_number)
                effects.append(respawn_effect)
                player_respawn_data[player_number] = (spawn_pos, respawn_effect)
            
            if respawn_timer == 0:
                del player_respawn_timers[player_number]
        
        for player_number, respawn_data in list(player_respawn_data.items()):
            if player_number in player_respawn_timers:
                continue
            
            bindings = PLAYER_CONTROLS[player_number]
            any_pressed = bindings.get_binary_action('left') or bindings.get_binary_action('right') or bindings.get_binary_action('flap')
            if any_pressed:
                spawn_pos, respawn_effect = respawn_data
                respawn_effect.should_delete = True
                spawn_player(player_number, spawn_pos)
                del player_respawn_data[player_number]
        
        # -- Draw --

        render_surf.fill((6, 6, 6))

        for platform in platforms:
            platform.draw(render_surf)

        for effect in effects:
            effect.draw(render_surf)

        for jouster in jousters:
            jouster.draw(render_surf)
        
        for collectable in collectables:
            collectable.draw(render_surf)
        
        scaled_render_surf = pygame.transform.scale_by(render_surf, WINDOW_SCALE)
        win.blit(scaled_render_surf, (0, 0))
        win.blit(font.render(f'{clock.get_fps():.1f}', True, (255, 255, 255)), (0, 0))


        pygame.display.flip()


if __name__ == '__main__':
    main()