import json
import math
import random
from array import array
from pathlib import Path

import pygame

pygame.mixer.pre_init(44100, -16, 1, 512)
pygame.init()

# =========================================================
# COMUNIDADE SAMUEL MAGGI // PAC-MAN EM PYTHON
# Projeto didatico em Pygame
# =========================================================

TILE = 28
HUD_H = 106
PAD_X = 24
FPS = 60

MAPA = [
    "#####################",
    "#o.......#.......o..#",
    "#.###.##.#.##.###...#",
    "#.....##...##.......#",
    "#.###.#.#####.#.###.#",
    "#.....#...#...#.....#",
    "#####.###.#.###.#####",
    "#.......#...#.......#",
    "#.#####.#.#.#.#####.#",
    "#.....#...#...#.....#",
    "###.#.#####.#####.#.#",
    "#...#.....G.....#...#",
    "#.###.###   ###.###.#",
    "#.....# G G G #.....#",
    "#.###.###   ###.###.#",
    "#...#.....P.....#...#",
    "###.#.#####.#####.#.#",
    "#.....#...#...#.....#",
    "#.#####.#.#.#.#####.#",
    "#.......#...#.......#",
    "#.###.##.#.##.###...#",
    "#o..#....#....#..o..#",
    "#####################",
]

ROWS = len(MAPA)
COLS = len(MAPA[0])
MAZE_W = COLS * TILE
MAZE_H = ROWS * TILE
W = MAZE_W + PAD_X * 2
H = HUD_H + MAZE_H + 18

# Paleta
BG = (5, 8, 14)
HUD_BG = (8, 12, 20)
WALL = (26, 98, 255)
WALL_DARK = (7, 27, 72)
PELLET = (248, 231, 190)
POWER = (255, 255, 255)
YELLOW = (255, 215, 0)
WHITE = (245, 248, 252)
MUTED = (128, 142, 162)
CYAN = (58, 221, 255)
GREEN = (55, 215, 132)
RED = (255, 72, 84)
PINK = (255, 117, 196)
ORANGE = (255, 169, 67)
BLUE_GHOST = (48, 90, 230)
PURPLE = (161, 100, 255)

screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("Comunidade Samuel Maggi // Pac-Man em Python")
clock = pygame.time.Clock()

FONT_XS = pygame.font.SysFont("consolas", 13, bold=True)
FONT_SM = pygame.font.SysFont("consolas", 16, bold=True)
FONT_MD = pygame.font.SysFont("consolas", 20, bold=True)
FONT_LG = pygame.font.SysFont("consolas", 34, bold=True)
FONT_XL = pygame.font.SysFont("consolas", 54, bold=True)

SAVE_FILE = Path(__file__).with_name("comunidade_samuel_maggi_highscore.json")

DIRS = {
    "LEFT": (-1, 0),
    "RIGHT": (1, 0),
    "UP": (0, -1),
    "DOWN": (0, 1),
}

ALL_DIRS = list(DIRS.values())


def tile_center(tile):
    col, row = tile
    return pygame.Vector2(
        PAD_X + col * TILE + TILE / 2,
        HUD_H + row * TILE + TILE / 2,
    )


def passable(tile):
    col, row = tile
    if col < 0 or col >= COLS or row < 0 or row >= ROWS:
        return False
    return MAPA[row][col] != "#"


def add_tile(tile, direction):
    return tile[0] + direction[0], tile[1] + direction[1]


def opposite(direction):
    return -direction[0], -direction[1]


def load_highscore():
    try:
        data = json.loads(SAVE_FILE.read_text(encoding="utf-8"))
        return int(data.get("highscore", 0))
    except Exception:
        return 0


def save_highscore(value):
    try:
        SAVE_FILE.write_text(
            json.dumps({"highscore": int(value)}, indent=2),
            encoding="utf-8",
        )
    except Exception:
        pass


# =========================================================
# AUDIO SINTETIZADO PELO PROPRIO PYTHON
# =========================================================

class SoundBank:
    def __init__(self):
        self.enabled = False
        self.muted = False
        self.chomp_index = 0

        self.start = None
        self.chomp_a = None
        self.chomp_b = None
        self.power = None
        self.ghost = None
        self.fruit = None
        self.death = None
        self.gameover = None
        self.level = None
        self.pause = None

        try:
            if pygame.mixer.get_init() is None:
                pygame.mixer.init(44100, -16, 1, 512)

            self.rate = pygame.mixer.get_init()[0]
            self.enabled = True

            self.start = self.melody([
                (392, .07), (523, .07), (659, .08), (784, .15)
            ], .75)

            self.chomp_a = self.tone(720, .035, .24, "square", -80)
            self.chomp_b = self.tone(580, .035, .22, "square", 90)
            self.power = self.tone(180, .24, .52, "square", 560)

            self.ghost = self.melody([
                (880, .05), (1175, .06), (1568, .11)
            ], .62)

            self.fruit = self.melody([
                (660, .06), (990, .06), (1320, .13)
            ], .56, wave="sine")

            self.death = self.tone(820, .58, .60, "square", -690)

            self.gameover = self.melody([
                (523, .11), (440, .11), (349, .14), (262, .28)
            ], .57)

            self.level = self.melody([
                (523, .07), (659, .07), (784, .08), (1047, .20)
            ], .58)

            self.pause = self.melody([
                (330, .05), (440, .08)
            ], .38, wave="sine")

        except pygame.error as error:
            self.enabled = False
            print("Audio indisponivel; jogo iniciado sem som:", error)

    def wave_value(self, kind, phase):
        s = math.sin(phase)

        if kind == "square":
            return 1.0 if s >= 0 else -1.0

        if kind == "triangle":
            return (2.0 / math.pi) * math.asin(s)

        return s

    def raw_tone(self, frequency, duration, volume=.5, wave="sine", slide=0):
        total = max(1, int(self.rate * duration))
        data = array("h")
        phase = 0.0
        fade = max(1, int(self.rate * .006))

        for i in range(total):
            progress = i / max(1, total - 1)
            freq = max(25.0, frequency + slide * progress)
            phase += math.tau * freq / self.rate

            envelope = 1.0

            if i < fade:
                envelope *= i / fade

            if i >= total - fade:
                envelope *= max(0.0, (total - i - 1) / fade)

            envelope *= 1.0 - progress * .12
            sample = self.wave_value(wave, phase) * volume * envelope
            sample = max(-1.0, min(1.0, sample))
            data.append(int(sample * 32767))

        return data

    def tone(self, frequency, duration, volume=.5, wave="sine", slide=0):
        if not self.enabled:
            return None

        data = self.raw_tone(frequency, duration, volume, wave, slide)
        return pygame.mixer.Sound(buffer=data.tobytes())

    def melody(self, notes, volume=.5, wave="square", gap=.012):
        if not self.enabled:
            return None

        data = array("h")
        silence = array("h", [0] * max(1, int(self.rate * gap)))

        for index, (frequency, duration) in enumerate(notes):
            data.extend(self.raw_tone(frequency, duration, volume, wave))

            if index < len(notes) - 1:
                data.extend(silence)

        return pygame.mixer.Sound(buffer=data.tobytes())

    def play(self, sound):
        if self.enabled and not self.muted and sound is not None:
            sound.play()

    def chomp(self):
        sound = self.chomp_a if self.chomp_index == 0 else self.chomp_b
        self.chomp_index = 1 - self.chomp_index
        self.play(sound)

    def toggle_mute(self):
        self.muted = not self.muted

        if self.muted and self.enabled:
            pygame.mixer.stop()

        return self.muted


class Particle:
    def __init__(self, pos, color):
        self.pos = pygame.Vector2(pos)
        angle = random.uniform(0, math.tau)
        speed = random.uniform(50, 145)
        self.vel = pygame.Vector2(math.cos(angle), math.sin(angle)) * speed
        self.life = random.uniform(0.3, 0.65)
        self.max_life = self.life
        self.color = color
        self.size = random.randint(2, 4)

    def update(self, dt):
        self.life -= dt
        self.pos += self.vel * dt
        self.vel *= 0.93

    def draw(self, surface):
        if self.life <= 0:
            return
        alpha = int(255 * self.life / self.max_life)
        layer = pygame.Surface((12, 12), pygame.SRCALPHA)
        pygame.draw.circle(layer, (*self.color, alpha), (6, 6), self.size)
        surface.blit(layer, (self.pos.x - 6, self.pos.y - 6))


class GridMover:
    def __init__(self, start_tile, speed):
        self.start_tile = start_tile
        self.tile = start_tile
        self.target_tile = start_tile
        self.pos = tile_center(start_tile)
        self.direction = (0, 0)
        self.speed = speed
        self.moving = False

    def reset_movement(self):
        self.tile = self.start_tile
        self.target_tile = self.start_tile
        self.pos = tile_center(self.start_tile)
        self.direction = (0, 0)
        self.moving = False

    def begin_move(self, direction):
        if direction == (0, 0):
            return False
        nxt = add_tile(self.tile, direction)
        if not passable(nxt):
            return False
        self.direction = direction
        self.target_tile = nxt
        self.moving = True
        return True

    def move_toward_target(self, dt, speed=None):
        if not self.moving:
            return True

        speed = speed or self.speed
        target = tile_center(self.target_tile)
        delta = target - self.pos
        distance = delta.length()
        step = speed * dt

        if distance <= step or distance < 0.001:
            self.pos = target
            self.tile = self.target_tile
            self.moving = False
            return True

        self.pos += delta.normalize() * step
        return False


class Player(GridMover):
    def __init__(self, start_tile):
        super().__init__(start_tile, speed=172)
        self.queued = DIRS["LEFT"]
        self.anim = 0.0

    def reset(self):
        self.reset_movement()
        self.queued = DIRS["LEFT"]
        self.anim = 0.0

    def update(self, dt):
        self.anim += dt * 10.5

        if self.moving:
            arrived = self.move_toward_target(dt)
            if not arrived:
                return

        # Chegou ao centro de uma celula: tenta primeiro a direcao pedida.
        if self.queued != (0, 0) and self.begin_move(self.queued):
            return

        # Se nao der, continua na direcao atual, caso exista caminho.
        self.begin_move(self.direction)

    def draw(self, surface):
        r = int(TILE * 0.38)
        center = (int(self.pos.x), int(self.pos.y))

        mouth = 0.20 + abs(math.sin(self.anim)) * 0.25
        angle = 0.0
        if self.direction == DIRS["LEFT"]:
            angle = math.pi
        elif self.direction == DIRS["UP"]:
            angle = -math.pi / 2
        elif self.direction == DIRS["DOWN"]:
            angle = math.pi / 2

        pygame.draw.circle(surface, YELLOW, center, r)

        p1 = (
            center[0] + math.cos(angle - mouth) * r * 1.2,
            center[1] + math.sin(angle - mouth) * r * 1.2,
        )
        p2 = (
            center[0] + math.cos(angle + mouth) * r * 1.2,
            center[1] + math.sin(angle + mouth) * r * 1.2,
        )
        pygame.draw.polygon(surface, BG, [center, p1, p2])


class Ghost(GridMover):
    def __init__(self, start_tile, color, personality, scatter_tile):
        super().__init__(start_tile, speed=128)
        self.color = color
        self.personality = personality
        self.scatter_tile = scatter_tile
        self.respawn_timer = 0.0
        self.direction = random.choice(ALL_DIRS)

    def reset(self):
        self.reset_movement()
        self.direction = random.choice(ALL_DIRS)
        self.respawn_timer = 0.0

    def valid_dirs(self):
        result = []
        for direction in ALL_DIRS:
            if passable(add_tile(self.tile, direction)):
                result.append(direction)
        return result

    def choose_direction(self, game):
        valid = self.valid_dirs()
        if not valid:
            return (0, 0)

        reverse = opposite(self.direction)
        if len(valid) > 1:
            without_reverse = [d for d in valid if d != reverse]
            if without_reverse:
                valid = without_reverse

        if game.power_timer > 0:
            return random.choice(valid)

        pc, pr = game.player.tile

        if game.mode == "scatter":
            target = self.scatter_tile
        elif self.personality == "chaser":
            target = (pc, pr)
        elif self.personality == "ambusher":
            dx, dy = game.player.direction
            target = (pc + dx * 4, pr + dy * 4)
        elif self.personality == "trickster":
            target = (pc + random.randint(-4, 4), pr + random.randint(-4, 4))
        else:
            gc, gr = self.tile
            dist = abs(gc - pc) + abs(gr - pr)
            target = self.scatter_tile if dist < 6 else (pc, pr)

        def dist2(direction):
            nc, nr = add_tile(self.tile, direction)
            return (nc - target[0]) ** 2 + (nr - target[1]) ** 2

        return min(valid, key=dist2)

    def update(self, dt, game):
        if self.respawn_timer > 0:
            self.respawn_timer -= dt
            return

        speed = self.speed
        if game.power_timer > 0:
            speed *= 0.72
        speed *= min(1.22, 1.0 + (game.level - 1) * 0.035)

        if self.moving:
            arrived = self.move_toward_target(dt, speed)
            if not arrived:
                return

        direction = self.choose_direction(game)
        self.begin_move(direction)

    def draw(self, surface, frightened, flash):
        if self.respawn_timer > 0:
            return

        color = self.color
        if frightened:
            color = WHITE if flash else BLUE_GHOST

        x = int(self.pos.x)
        y = int(self.pos.y)
        r = int(TILE * 0.37)

        pygame.draw.circle(surface, color, (x, y - 3), r)
        pygame.draw.rect(surface, color, (x - r, y - 3, r * 2, r + 6))

        feet = [
            (x - r, y + r),
            (x - r // 2, y + r - 4),
            (x, y + r),
            (x + r // 2, y + r - 4),
            (x + r, y + r),
        ]
        pygame.draw.polygon(surface, color, feet)

        if frightened:
            pygame.draw.circle(surface, WHITE, (x - 6, y - 3), 2)
            pygame.draw.circle(surface, WHITE, (x + 6, y - 3), 2)
            pygame.draw.line(surface, WHITE, (x - 7, y + 7), (x - 3, y + 4), 2)
            pygame.draw.line(surface, WHITE, (x - 3, y + 4), (x + 1, y + 7), 2)
            pygame.draw.line(surface, WHITE, (x + 1, y + 7), (x + 5, y + 4), 2)
            pygame.draw.line(surface, WHITE, (x + 5, y + 4), (x + 9, y + 7), 2)
            return

        for eye_x in (x - 6, x + 6):
            pygame.draw.circle(surface, WHITE, (eye_x, y - 5), 5)
            pygame.draw.circle(
                surface,
                (18, 30, 56),
                (eye_x + self.direction[0] * 2, y - 5 + self.direction[1] * 2),
                2,
            )


class Game:
    def __init__(self):
        self.highscore = load_highscore()
        self.sounds = SoundBank()
        self.state = "start"
        self.level = 1
        self.score = 0
        self.lives = 3
        self.mode = "scatter"
        self.mode_timer = 0.0
        self.mode_phase = 0
        self.power_timer = 0.0
        self.ghost_combo = 0
        self.message = ""
        self.message_timer = 0.0
        self.freeze_timer = 0.0
        self.particles = []
        self.fruit_active = False
        self.fruit_used = False
        self.fruit_timer = 0.0
        self.build_level()

    def scan_map(self):
        player_tile = None
        ghosts = []
        pellets = set()
        power = set()

        for row, line in enumerate(MAPA):
            for col, ch in enumerate(line):
                if ch == "P":
                    player_tile = (col, row)
                elif ch == "G":
                    ghosts.append((col, row))
                elif ch == ".":
                    pellets.add((col, row))
                elif ch == "o":
                    power.add((col, row))

        return player_tile, ghosts, pellets, power

    def build_level(self):
        player_tile, ghost_tiles, pellets, power = self.scan_map()

        self.pellets = pellets
        self.power_pellets = power
        self.total_collectibles = len(pellets) + len(power)
        self.player = Player(player_tile)

        while len(ghost_tiles) < 4:
            ghost_tiles.append(ghost_tiles[-1])

        colors = [RED, PINK, CYAN, ORANGE]
        personalities = ["chaser", "ambusher", "trickster", "coward"]
        scatters = [
            (COLS - 2, 1),
            (1, 1),
            (COLS - 2, ROWS - 2),
            (1, ROWS - 2),
        ]

        self.ghosts = [
            Ghost(ghost_tiles[i], colors[i], personalities[i], scatters[i])
            for i in range(4)
        ]

        self.power_timer = 0.0
        self.ghost_combo = 0
        self.mode = "scatter"
        self.mode_timer = 0.0
        self.mode_phase = 0
        self.fruit_active = False
        self.fruit_used = False
        self.fruit_timer = 0.0
        self.fruit_pos = tile_center((COLS // 2, 15))

    def new_game(self):
        self.level = 1
        self.score = 0
        self.lives = 3
        self.state = "playing"
        self.build_level()
        self.freeze_timer = 0.35
        self.message = "VALENDO!"
        self.message_timer = 1.0
        self.sounds.play(self.sounds.start)

    def reset_round(self):
        self.player.reset()
        for ghost in self.ghosts:
            ghost.reset()
        self.power_timer = 0.0
        self.ghost_combo = 0
        self.freeze_timer = 0.65

    def add_score(self, value):
        self.score += value
        if self.score > self.highscore:
            self.highscore = self.score
            save_highscore(self.highscore)

    def particles_at(self, pos, color, count):
        for _ in range(count):
            self.particles.append(Particle(pos, color))

    def update_mode(self, dt):
        self.mode_timer += dt
        schedule = [7, 20, 7, 20, 5, 999]
        duration = schedule[min(self.mode_phase, len(schedule) - 1)]

        if self.mode_timer >= duration:
            self.mode_timer = 0.0
            self.mode_phase += 1
            self.mode = "chase" if self.mode == "scatter" else "scatter"
            for ghost in self.ghosts:
                ghost.direction = opposite(ghost.direction)

    def update_collectibles(self):
        tile = self.player.tile

        if tile in self.pellets:
            self.pellets.remove(tile)
            self.add_score(10)
            self.sounds.chomp()

        if tile in self.power_pellets:
            self.power_pellets.remove(tile)
            self.add_score(50)
            self.sounds.play(self.sounds.power)
            self.power_timer = max(4.5, 8.0 - (self.level - 1) * 0.35)
            self.ghost_combo = 0
            self.particles_at(self.player.pos, WHITE, 18)
            for ghost in self.ghosts:
                ghost.direction = opposite(ghost.direction)

        eaten = self.total_collectibles - len(self.pellets) - len(self.power_pellets)
        progress = eaten / max(1, self.total_collectibles)

        if not self.fruit_used and not self.fruit_active and progress >= 0.60:
            self.fruit_active = True
            self.fruit_timer = 9.0

        if self.fruit_active:
            if self.player.pos.distance_to(self.fruit_pos) < TILE * 0.55:
                self.fruit_active = False
                self.fruit_used = True
                self.add_score(1000 + (self.level - 1) * 250)
                self.sounds.play(self.sounds.fruit)
                self.particles_at(self.fruit_pos, RED, 26)
                self.message = "+ FRUTA BONUS"
                self.message_timer = 1.3

    def update_collisions(self):
        for ghost in self.ghosts:
            if ghost.respawn_timer > 0:
                continue

            if self.player.pos.distance_to(ghost.pos) < TILE * 0.56:
                if self.power_timer > 0:
                    points = 200 * (2 ** self.ghost_combo)
                    self.ghost_combo = min(self.ghost_combo + 1, 3)
                    self.add_score(points)
                    self.sounds.play(self.sounds.ghost)
                    self.particles_at(ghost.pos, ghost.color, 22)
                    ghost.reset_movement()
                    ghost.respawn_timer = 1.5
                    self.message = f"+{points} FANTASMA"
                    self.message_timer = 1.0
                else:
                    self.lives -= 1
                    self.particles_at(self.player.pos, YELLOW, 30)
                    if self.lives <= 0:
                        self.state = "gameover"
                        self.sounds.play(self.sounds.gameover)
                        save_highscore(self.highscore)
                    else:
                        self.sounds.play(self.sounds.death)
                        self.reset_round()
                    break

    def next_level(self):
        self.level += 1
        self.add_score(1500)
        self.build_level()
        self.freeze_timer = 0.7
        self.message = f"NIVEL {self.level}"
        self.message_timer = 1.5
        self.sounds.play(self.sounds.level)

    def update(self, dt):
        for particle in self.particles:
            particle.update(dt)
        self.particles = [p for p in self.particles if p.life > 0]

        if self.message_timer > 0:
            self.message_timer -= dt

        if self.state != "playing":
            return

        if self.freeze_timer > 0:
            self.freeze_timer -= dt
            return

        if self.power_timer > 0:
            self.power_timer -= dt
            if self.power_timer <= 0:
                self.power_timer = 0
                self.ghost_combo = 0

        if self.fruit_active:
            self.fruit_timer -= dt
            if self.fruit_timer <= 0:
                self.fruit_active = False
                self.fruit_used = True

        self.update_mode(dt)
        self.player.update(dt)
        self.update_collectibles()

        for ghost in self.ghosts:
            ghost.update(dt, self)

        self.update_collisions()

        if not self.pellets and not self.power_pellets:
            self.next_level()

    def draw_maze(self, surface):
        surface.fill(BG)

        maze_rect = pygame.Rect(PAD_X, HUD_H, MAZE_W, MAZE_H)
        pygame.draw.rect(surface, (6, 10, 18), maze_rect)

        for row, line in enumerate(MAPA):
            for col, ch in enumerate(line):
                x = PAD_X + col * TILE
                y = HUD_H + row * TILE

                if ch == "#":
                    outer = pygame.Rect(x + 1, y + 1, TILE - 2, TILE - 2)
                    inner = outer.inflate(-8, -8)
                    pygame.draw.rect(surface, (8, 25, 72), outer, border_radius=7)
                    pygame.draw.rect(surface, WALL, outer, width=2, border_radius=7)
                    if inner.w > 0 and inner.h > 0:
                        pygame.draw.rect(surface, WALL_DARK, inner, border_radius=4)

        for tile in self.pellets:
            c = tile_center(tile)
            pygame.draw.circle(surface, PELLET, (round(c.x), round(c.y)), 3)

        pulse = 5 + int((math.sin(pygame.time.get_ticks() * 0.008) + 1) * 1.4)
        for tile in self.power_pellets:
            c = tile_center(tile)
            pygame.draw.circle(surface, POWER, (round(c.x), round(c.y)), pulse)

        if self.fruit_active:
            fx, fy = int(self.fruit_pos.x), int(self.fruit_pos.y)
            pygame.draw.circle(surface, RED, (fx - 5, fy), 7)
            pygame.draw.circle(surface, RED, (fx + 5, fy), 7)
            pygame.draw.line(surface, GREEN, (fx, fy - 5), (fx + 7, fy - 14), 3)

    def draw_hud(self, surface):
        pygame.draw.rect(surface, HUD_BG, (0, 0, W, HUD_H))
        pygame.draw.line(surface, (29, 40, 58), (0, HUD_H - 1), (W, HUD_H - 1), 1)

        title = FONT_MD.render("COMUNIDADE SAMUEL MAGGI", True, WHITE)
        surface.blit(title, (PAD_X, 15))

        subtitle = FONT_SM.render("PAC-MAN EM PYTHON", True, CYAN)
        surface.blit(subtitle, (PAD_X, 48))

        score = FONT_MD.render(f"SCORE {self.score:06d}", True, YELLOW)
        surface.blit(score, (W - PAD_X - score.get_width(), 15))

        high = FONT_XS.render(f"RECORDE {self.highscore:06d}   NIVEL {self.level:02d}", True, MUTED)
        surface.blit(high, (W - PAD_X - high.get_width(), 49))

        lives_label = FONT_XS.render("VIDAS", True, MUTED)
        surface.blit(lives_label, (W - PAD_X - 116, 75))

        for i in range(self.lives):
            cx = W - PAD_X - 72 + i * 23
            cy = 82
            pygame.draw.circle(surface, YELLOW, (cx, cy), 7)
            pygame.draw.polygon(surface, HUD_BG, [(cx, cy), (cx + 8, cy - 5), (cx + 8, cy + 5)])

        hint = FONT_XS.render("SETAS/WASD  •  P PAUSA", True, MUTED)
        surface.blit(hint, (PAD_X, 76))

    def draw_overlay(self, surface):
        if self.state == "start":
            shade = pygame.Surface((W, H), pygame.SRCALPHA)
            shade.fill((0, 0, 0, 175))
            surface.blit(shade, (0, 0))

            t1 = FONT_MD.render("COMUNIDADE SAMUEL MAGGI", True, WHITE)
            surface.blit(t1, (W // 2 - t1.get_width() // 2, H // 2 - 145))

            t2 = FONT_XL.render("PAC-MAN", True, YELLOW)
            surface.blit(t2, (W // 2 - t2.get_width() // 2, H // 2 - 95))

            t3 = FONT_MD.render("FEITO EM PYTHON + PYGAME", True, CYAN)
            surface.blit(t3, (W // 2 - t3.get_width() // 2, H // 2 - 25))

            t4 = FONT_SM.render("SETAS OU WASD PARA MOVER", True, WHITE)
            surface.blit(t4, (W // 2 - t4.get_width() // 2, H // 2 + 28))

            t5 = FONT_MD.render("PRESSIONE ESPACO", True, GREEN)
            surface.blit(t5, (W // 2 - t5.get_width() // 2, H // 2 + 76))

        elif self.state == "paused":
            shade = pygame.Surface((W, H), pygame.SRCALPHA)
            shade.fill((0, 0, 0, 150))
            surface.blit(shade, (0, 0))
            txt = FONT_LG.render("PAUSADO", True, WHITE)
            surface.blit(txt, (W // 2 - txt.get_width() // 2, H // 2 - 20))

        elif self.state == "gameover":
            shade = pygame.Surface((W, H), pygame.SRCALPHA)
            shade.fill((0, 0, 0, 190))
            surface.blit(shade, (0, 0))

            t1 = FONT_XL.render("GAME OVER", True, RED)
            surface.blit(t1, (W // 2 - t1.get_width() // 2, H // 2 - 95))

            t2 = FONT_MD.render(f"SCORE FINAL {self.score}", True, WHITE)
            surface.blit(t2, (W // 2 - t2.get_width() // 2, H // 2 - 20))

            t3 = FONT_MD.render("R PARA REINICIAR", True, GREEN)
            surface.blit(t3, (W // 2 - t3.get_width() // 2, H // 2 + 42))

        if self.freeze_timer > 0 and self.state == "playing":
            ready = FONT_LG.render("READY!", True, YELLOW)
            surface.blit(ready, (W // 2 - ready.get_width() // 2, HUD_H + MAZE_H // 2 - 20))

        if self.message_timer > 0 and self.message:
            msg = FONT_SM.render(self.message, True, WHITE)
            box = msg.get_rect(center=(W // 2, HUD_H + 22))
            bg = box.inflate(22, 12)
            pygame.draw.rect(surface, (18, 24, 36), bg, border_radius=10)
            pygame.draw.rect(surface, PURPLE, bg, 2, border_radius=10)
            surface.blit(msg, box)

    def draw(self, surface):
        self.draw_maze(surface)
        self.draw_hud(surface)

        frightened = self.power_timer > 0
        flash = frightened and self.power_timer < 2 and int(self.power_timer * 8) % 2 == 0

        for ghost in self.ghosts:
            ghost.draw(surface, frightened, flash)

        self.player.draw(surface)

        for particle in self.particles:
            particle.draw(surface)

        self.draw_overlay(surface)

    def handle_event(self, event):
        if event.type != pygame.KEYDOWN:
            return

        if event.key in (pygame.K_LEFT, pygame.K_a):
            self.player.queued = DIRS["LEFT"]
        elif event.key in (pygame.K_RIGHT, pygame.K_d):
            self.player.queued = DIRS["RIGHT"]
        elif event.key in (pygame.K_UP, pygame.K_w):
            self.player.queued = DIRS["UP"]
        elif event.key in (pygame.K_DOWN, pygame.K_s):
            self.player.queued = DIRS["DOWN"]

        if event.key == pygame.K_SPACE:
            if self.state == "start":
                self.new_game()
            elif self.state == "gameover":
                self.new_game()

        elif event.key == pygame.K_p:
            if self.state == "playing":
                self.state = "paused"
                self.sounds.play(self.sounds.pause)
            elif self.state == "paused":
                self.state = "playing"
                self.sounds.play(self.sounds.pause)

        elif event.key == pygame.K_m:
            muted = self.sounds.toggle_mute()
            self.message = "SOM DESLIGADO" if muted else "SOM LIGADO"
            self.message_timer = 1.0

        elif event.key == pygame.K_r and self.state == "gameover":
            self.new_game()


def main():
    game = Game()
    running = True

    while running:
        dt = min(clock.tick(FPS) / 1000.0, 0.05)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            else:
                game.handle_event(event)

        game.update(dt)
        game.draw(screen)
        pygame.display.flip()

    save_highscore(game.highscore)
    pygame.quit()


if __name__ == "__main__":
    main()
