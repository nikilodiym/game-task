import os
import random
import sys

import pygame

from player import Player
from core.game_manager import GameManager
from core.factory import EntityFactory
from core.events import EventManager, EventType
from core.strategies import SingleShotStrategy, SpreadShotStrategy

SCREEN_W = 1920
SCREEN_H = 1080
WORLD_W = 2400
WORLD_H = 2400
FPS = 60

BG_COLOR = (22, 38, 22)
GRID_COLOR = (28, 46, 28)

class Camera:
    def __init__(self):
        self.x = 0.0
        self.y = 0.0

    def update(self, target: pygame.math.Vector2) -> None:
        self.x = max(0, min(WORLD_W - SCREEN_W, target.x - SCREEN_W / 2))
        self.y = max(0, min(WORLD_H - SCREEN_H, target.y - SCREEN_H / 2))

    def apply(self, rect: pygame.Rect) -> pygame.Rect:
        return pygame.Rect(rect.x - int(self.x), rect.y - int(self.y), rect.w, rect.h)

    def to_world(self, screen_pos: tuple) -> tuple:
        return (screen_pos[0] + self.x, screen_pos[1] + self.y)

class WaveSpawner:
    GRACE = 4.0

    def __init__(self):
        self._spawn_timer = 0.0
        self._spawned = 0
        self._total = 0
        self._between = False
        self._grace_timer = 0.0

    def start_wave(self, wave: int) -> None:
        self._total = 8 + (wave - 1) * 4
        self._spawned = 0
        self._spawn_timer = 0.0
        self._between = False

    def update(self, dt: float, wave: int, alive_count: int,
               enemy_group: pygame.sprite.Group,
               all_sprites: pygame.sprite.Group,
               gm: GameManager) -> None:
        if self._between:
            self._grace_timer -= dt
            if self._grace_timer <= 0:
                self._between = False
                gm.advance_wave()
                self.start_wave(gm.wave)
            return

        if self._spawned >= self._total and alive_count == 0:
            self._between = True
            self._grace_timer = self.GRACE
            return

        if self._spawned < self._total:
            self._spawn_timer -= dt
            if self._spawn_timer <= 0:
                self._spawn_timer = max(0.6, 1.4 - wave * 0.05)
                batch = min(2, self._total - self._spawned)
                for _ in range(batch):
                    x, y = self._edge_pos()
                    e = EntityFactory.create_enemy_for_wave(wave, x, y)
                    enemy_group.add(e)
                    all_sprites.add(e)
                    self._spawned += 1

    def _edge_pos(self) -> tuple:
        edge = random.randint(0, 3)
        m = 60
        if edge == 0:
            return random.randint(0, WORLD_W), -m
        elif edge == 1:
            return random.randint(0, WORLD_W), WORLD_H + m
        elif edge == 2:
            return -m, random.randint(0, WORLD_H)
        else:
            return WORLD_W + m, random.randint(0, WORLD_H)

    @property
    def between_waves(self) -> bool:
        return self._between

    @property
    def grace_remaining(self) -> float:
        return self._grace_timer



def draw_background(surface: pygame.Surface, camera: Camera) -> None:
    surface.fill(BG_COLOR)
    grid = 100
    ox = int(camera.x) % grid
    oy = int(camera.y) % grid
    for x in range(-ox, SCREEN_W + grid, grid):
        pygame.draw.line(surface, GRID_COLOR, (x, 0), (x, SCREEN_H))
    for y in range(-oy, SCREEN_H + grid, grid):
        pygame.draw.line(surface, GRID_COLOR, (0, y), (SCREEN_W, y))


def draw_ui(surface: pygame.Surface, player: Player, gm: GameManager,
            spawner: WaveSpawner, font: pygame.font.Font,
            big_font: pygame.font.Font, weapon_name: str) -> None:

    BAR_W, BAR_H = 380, 26
    BAR_X = (SCREEN_W - BAR_W) // 2
    BAR_Y = SCREEN_H - 54

    panel_rect = pygame.Rect(BAR_X - 10, BAR_Y - 10, BAR_W + 20, BAR_H + 20)
    panel_surf = pygame.Surface((panel_rect.w, panel_rect.h), pygame.SRCALPHA)
    panel_surf.fill((10, 10, 10, 170))
    surface.blit(panel_surf, panel_rect.topleft)
    pygame.draw.rect(surface, (60, 20, 20), (BAR_X, BAR_Y, BAR_W, BAR_H), border_radius=5)

    hp_ratio = max(0.0, player.hp / player.MAX_HP)
    fill_w = int(BAR_W * hp_ratio)
    if fill_w > 0:
        r = int(220 * (1 - hp_ratio) + 40 * hp_ratio)
        g = int(40 * (1 - hp_ratio) + 180 * hp_ratio)
        hp_color = (r, g, 40)
        pygame.draw.rect(surface, hp_color, (BAR_X, BAR_Y, fill_w, BAR_H), border_radius=5)

    pygame.draw.rect(surface, (160, 80, 80), (BAR_X, BAR_Y, BAR_W, BAR_H), 2, border_radius=5)

    hp_label = font.render(f"HP  {player.hp} / {player.MAX_HP}", True, (255, 210, 210))
    surface.blit(hp_label, hp_label.get_rect(center=(BAR_X + BAR_W // 2, BAR_Y + BAR_H // 2)))

    score_surf = font.render(f"Score:  {gm.score}", True, (255, 230, 80))
    surface.blit(score_surf, (16, 16))

    wave_surf = font.render(f"Wave  {gm.wave}", True, (80, 200, 255))
    surface.blit(wave_surf, wave_surf.get_rect(midtop=(SCREEN_W // 2, 16)))

    wpn_surf = font.render(f"[1] Single  [2] Spread   ({weapon_name})", True, (180, 180, 180))
    surface.blit(wpn_surf, wpn_surf.get_rect(topright=(SCREEN_W - 16, 16)))

    if spawner.between_waves:
        msg = big_font.render(
            f"Wave {gm.wave + 1} incoming in  {spawner.grace_remaining:.1f}s",
            True, (255, 255, 80)
        )
        surface.blit(msg, msg.get_rect(center=(SCREEN_W // 2, SCREEN_H // 2 - 30)))


def draw_death_screen(surface: pygame.Surface, gm: GameManager,
                      big_font: pygame.font.Font, font: pygame.font.Font) -> None:
    overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 160))
    surface.blit(overlay, (0, 0))

    surface.blit(
        big_font.render("YOU DIED", True, (210, 40, 40)),
        big_font.render("YOU DIED", True, (0, 0, 0)).get_rect(center=(SCREEN_W // 2 + 2, SCREEN_H // 2 - 78))
    )
    dead = big_font.render("YOU DIED", True, (210, 40, 40))
    surface.blit(dead, dead.get_rect(center=(SCREEN_W // 2, SCREEN_H // 2 - 80)))

    score = big_font.render(f"Score:  {gm.score}", True, (255, 225, 80))
    surface.blit(score, score.get_rect(center=(SCREEN_W // 2, SCREEN_H // 2)))

    wave_txt = font.render(f"Survived  {gm.wave}  wave{'s' if gm.wave != 1 else ''}", True, (200, 200, 200))
    surface.blit(wave_txt, wave_txt.get_rect(center=(SCREEN_W // 2, SCREEN_H // 2 + 60)))

    hint = font.render("R — restart       ESC — quit", True, (160, 160, 160))
    surface.blit(hint, hint.get_rect(center=(SCREEN_W // 2, SCREEN_H // 2 + 110)))


def _on_enemy_killed_item_drop(data, item_group, all_sprites):
    if random.random() < 0.18:
        pos = data.get("pos", pygame.math.Vector2(WORLD_W / 2, WORLD_H / 2))
        item = EntityFactory.create_item("health", pos.x, pos.y)
        if item:
            item_group.add(item)
            all_sprites.add(item)



class Game:
    def __init__(self):
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
        pygame.display.set_caption("Zombie Survivors")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 20, bold=True)
        self.big_font = pygame.font.SysFont("Arial", 46, bold=True)
        self._build_scene()

    def _build_scene(self) -> None:
        gm = GameManager()
        gm.reset()

        self.player = Player(WORLD_W / 2, WORLD_H / 2)
        self.camera = Camera()
        self.spawner = WaveSpawner()
        self.spawner.start_wave(gm.wave)

        self.all_sprites = pygame.sprite.Group()
        self.enemy_group = pygame.sprite.Group()
        self.bullet_group = pygame.sprite.Group()
        self.item_group = pygame.sprite.Group()
        self.all_sprites.add(self.player)

        self.weapon_name = "Single"

        em = EventManager()
        em.subscribe(
            EventType.ENEMY_KILLED,
            lambda d: _on_enemy_killed_item_drop(d, self.item_group, self.all_sprites)
        )

    def run(self) -> None:
        gm = GameManager()
        running = True

        while running:
            dt = min(self.clock.tick(FPS) / 1000.0, 0.05)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_r and gm.game_state == "dead":
                        self._build_scene()
                        gm = GameManager()
                    elif gm.game_state == "playing":
                        if event.key == pygame.K_1:
                            self.player.set_strategy(SingleShotStrategy())
                            self.weapon_name = "Single"
                        elif event.key == pygame.K_2:
                            self.player.set_strategy(SpreadShotStrategy())
                            self.weapon_name = "Spread"

            if gm.game_state == "dead":
                draw_background(self.screen, self.camera)
                for spr in self.all_sprites:
                    self.screen.blit(spr.image, self.camera.apply(spr.rect))
                draw_death_screen(self.screen, gm, self.big_font, self.font)
                pygame.display.flip()
                continue

            keys = pygame.key.get_pressed()
            self.player.handle_input(keys, dt)
            self.player.clamp(WORLD_W, WORLD_H)
            self.player.update(dt)

            self.camera.update(self.player.pos)

            mouse_world = self.camera.to_world(pygame.mouse.get_pos())
            self.player.rotate_to(mouse_world)

            self.player.try_shoot(mouse_world, [self.bullet_group, self.all_sprites])

            for e in list(self.enemy_group):
                e.update(dt, self.player.pos)

            for b in list(self.bullet_group):
                b.update(dt)

            for it in list(self.item_group):
                it.update(dt)

            # bullet ↔ enemy
            hits = pygame.sprite.groupcollide(
                self.bullet_group, self.enemy_group, True, False
            )
            for enemies in hits.values():
                for e in enemies:
                    e.take_damage(25)

            # player ↔ enemy
            for e in pygame.sprite.spritecollide(
                self.player, self.enemy_group, False, pygame.sprite.collide_circle
            ):
                if e.can_damage():
                    self.player.take_damage(e.damage)
                    e.reset_damage_cooldown()

            # player ↔ item
            for it in pygame.sprite.spritecollide(self.player, self.item_group, True):
                self.player.heal(it.heal_amount)
                EventManager().emit(EventType.ITEM_PICKED, {"heal": it.heal_amount})

            self.spawner.update(
                dt, gm.wave, len(self.enemy_group),
                self.enemy_group, self.all_sprites, gm
            )

            # ── Render ────────────────────────────────────────────────────
            draw_background(self.screen, self.camera)

            for spr in self.all_sprites:
                self.screen.blit(spr.image, self.camera.apply(spr.rect))

            draw_ui(self.screen, self.player, gm, self.spawner,
                    self.font, self.big_font, self.weapon_name)

            pygame.display.flip()

        pygame.quit()
        sys.exit()
