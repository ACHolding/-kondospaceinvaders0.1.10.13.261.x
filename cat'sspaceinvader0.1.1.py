#!/usr/bin/env python3.14
# -*- coding: utf-8 -*-
"""
program.py — AC KONDO'S SPACE INVADERS PY PORT 0.x
=================================================
PR: Python 3.14 · 60 FPS Speed = Famicom (60.0988 FPS) · Famicom 2C02 Graphics Engine
Original Game: Space Invaders (c) 1978 Taito Corp. (Created by Toshihiro Nishikado)
Python Port: AC Kondo's Space Invaders Py Port 0.x [c] Kondo 1999-2026
Famicom Version: (c) 1985 Taito Corp. (homage look only — no Nintendo/Taito assets)
FILES = OFF — All 2C02 CHR bitplanes, palettes, and 2A03 audio generated in RAM.
"""

from __future__ import annotations

import sys
if sys.version_info < (3, 14):
    sys.exit("Python 3.14+ required (run with python3.14 program.py)")

import math
import random
from array import array
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

try:
    import pygame
except ImportError:
    sys.exit("pygame-ce is required: pip install pygame-ce")

# ----------------------------------------------------------------------------
# FAMICOM / 2C02 HARDWARE CONSTANTS
# ----------------------------------------------------------------------------
TITLE = "ac kondo's space invaders py port 0.x"
FAMICOM_SPEED = 60
NTSC_FPS = 60.0988
SCREEN_W = 256
SCREEN_H = 240
SCALE = 3
WIN_W = SCREEN_W * SCALE
WIN_H = SCREEN_H * SCALE

# NTSC 2C02 64-Color Palette
NES_PALETTE: Tuple[Tuple[int, int, int], ...] = (
    (84, 84, 84), (0, 30, 116), (8, 16, 144), (48, 0, 136),
    (68, 0, 100), (92, 0, 48), (84, 4, 0), (60, 24, 0),
    (32, 42, 0), (8, 58, 0), (0, 64, 0), (0, 60, 0),
    (0, 50, 60), (0, 0, 0), (0, 0, 0), (0, 0, 0),
    (152, 150, 152), (8, 76, 196), (48, 50, 236), (92, 30, 228),
    (136, 20, 176), (160, 20, 100), (152, 34, 32), (120, 60, 0),
    (84, 90, 0), (40, 114, 0), (8, 124, 0), (0, 118, 40),
    (0, 102, 120), (0, 0, 0), (0, 0, 0), (0, 0, 0),
    (236, 238, 236), (76, 154, 236), (120, 124, 236), (176, 98, 236),
    (228, 84, 236), (236, 88, 180), (236, 106, 100), (212, 136, 32),
    (160, 170, 0), (116, 196, 0), (76, 208, 32), (56, 204, 108),
    (56, 180, 204), (60, 60, 60), (0, 0, 0), (0, 0, 0),
    (236, 238, 236), (168, 204, 236), (188, 188, 236), (212, 178, 236),
    (236, 174, 236), (236, 174, 212), (236, 180, 176), (228, 196, 144),
    (204, 210, 120), (180, 222, 120), (168, 226, 144), (152, 226, 180),
    (160, 214, 228), (160, 162, 160), (0, 0, 0), (0, 0, 0),
)

# 2C02 Palettes (4 colors each; index 0 is universal background $0F black)
BG_PALETTES = (
    (0x0F, 0x20, 0x11, 0x30),  # 0: White / Blue HUD text
    (0x0F, 0x2A, 0x1A, 0x3A),  # 1: Famicom Green (Bunkers & baseline)
    (0x0F, 0x28, 0x16, 0x38),  # 2: Gold / Red accents (Logo & Title)
    (0x0F, 0x2C, 0x24, 0x3C),  # 3: Cyan / Magenta (Score Table)
)

SPR_PALETTES = (
    (0x0F, 0x2A, 0x30, 0x1A),  # 0: Player Cannon (Green/White)
    (0x0F, 0x24, 0x34, 0x14),  # 1: Squid (30 pts - Magenta)
    (0x0F, 0x2C, 0x3C, 0x1C),  # 2: Crab (20 pts - Cyan)
    (0x0F, 0x28, 0x16, 0x30),  # 3: Octopus (10 pts - Orange/Gold) & UFO (Red)
)

# ----------------------------------------------------------------------------
# 8x8 2C02 CHR BITMAP FONT & SPRITE PATTERNS
# ----------------------------------------------------------------------------
_FONT_5X7: Dict[str, Tuple[int, ...]] = {
    'A': (14, 17, 17, 31, 17, 17, 17), 'B': (30, 17, 17, 30, 17, 17, 30),
    'C': (14, 17, 16, 16, 16, 17, 14), 'D': (30, 17, 17, 17, 17, 17, 30),
    'E': (31, 16, 16, 30, 16, 16, 31), 'F': (31, 16, 16, 30, 16, 16, 16),
    'G': (14, 17, 16, 23, 17, 17, 15), 'H': (17, 17, 17, 31, 17, 17, 17),
    'I': (14, 4, 4, 4, 4, 4, 14),      'J': (7, 2, 2, 2, 2, 18, 12),
    'K': (17, 18, 20, 24, 20, 18, 17), 'L': (16, 16, 16, 16, 16, 16, 31),
    'M': (17, 27, 21, 21, 17, 17, 17), 'N': (17, 17, 25, 21, 19, 17, 17),
    'O': (14, 17, 17, 17, 17, 17, 14), 'P': (30, 17, 17, 30, 16, 16, 16),
    'Q': (14, 17, 17, 17, 21, 18, 13), 'R': (30, 17, 17, 30, 20, 18, 17),
    'S': (15, 16, 16, 14, 1, 1, 30),   'T': (31, 4, 4, 4, 4, 4, 4),
    'U': (17, 17, 17, 17, 17, 17, 14), 'V': (17, 17, 17, 17, 17, 10, 4),
    'W': (17, 17, 17, 21, 21, 21, 10), 'X': (17, 17, 10, 4, 10, 17, 17),
    'Y': (17, 17, 10, 4, 4, 4, 4),     'Z': (31, 1, 2, 4, 8, 16, 31),
    '0': (14, 17, 19, 21, 25, 17, 14), '1': (4, 12, 4, 4, 4, 4, 14),
    '2': (14, 17, 1, 2, 4, 8, 31),     '3': (31, 2, 4, 2, 1, 17, 14),
    '4': (2, 6, 10, 18, 31, 2, 2),     '5': (31, 16, 30, 1, 1, 17, 14),
    '6': (6, 8, 16, 30, 17, 17, 14),   '7': (31, 1, 2, 4, 8, 8, 8),
    '8': (14, 17, 17, 14, 17, 17, 14), '9': (14, 17, 17, 15, 1, 2, 12),
    ' ': (0, 0, 0, 0, 0, 0, 0),        '.': (0, 0, 0, 0, 0, 12, 12),
    ',': (0, 0, 0, 0, 12, 4, 8),       ':': (0, 12, 12, 0, 12, 12, 0),
    '!': (4, 4, 4, 4, 4, 0, 4),        '?': (14, 17, 1, 2, 4, 0, 4),
    '-': (0, 0, 0, 31, 0, 0, 0),       '=': (0, 0, 31, 0, 31, 0, 0),
    '*': (4, 21, 14, 31, 14, 21, 4),   '[': (14, 8, 8, 8, 8, 8, 14),
    ']': (14, 2, 2, 2, 2, 2, 14),      "'": (4, 4, 8, 0, 0, 0, 0),
    '/': (1, 1, 2, 4, 8, 16, 16),      '(': (2, 4, 8, 8, 8, 4, 2),
    ')': (8, 4, 2, 2, 2, 4, 8),
}

# 16x8 Sprite Art (encoded as 8 rows of 16-bit integers, split into two 8x8 CHR tiles)
SPRITE_PATTERNS: Dict[str, Tuple[int, ...]] = {
    "squid_0": (
        0b0000001111000000,
        0b0000111111110000,
        0b0001111111111000,
        0b0011100110011100,
        0b0011111111111100,
        0b0000011001100000,
        0b0000110110110000,
        0b0011000000001100,
    ),
    "squid_1": (
        0b0000001111000000,
        0b0000111111110000,
        0b0001111111111000,
        0b0011100110011100,
        0b0011111111111100,
        0b0000110000110000,
        0b0001100110011000,
        0b0000110000110000,
    ),
    "crab_0": (
        0b0001000000010000,
        0b0000100000100000,
        0b0001111111110000,
        0b0011011111011000,
        0b0111111111111100,
        0b0101111111110100,
        0b0101000000010100,
        0b0000110001100000,
    ),
    "crab_1": (
        0b0001000000010000,
        0b0100100000100100,
        0b0101111111110100,
        0b0111011111011100,
        0b0111111111111100,
        0b0011111111111000,
        0b0001000000010000,
        0b0010000000001000,
    ),
    "octopus_0": (
        0b0000111111110000,
        0b0111111111111110,
        0b1111111111111111,
        0b1110001111000111,
        0b1111111111111111,
        0b0001110000111000,
        0b0011001111001100,
        0b1100000000000011,
    ),
    "octopus_1": (
        0b0000111111110000,
        0b0111111111111110,
        0b1111111111111111,
        0b1110001111000111,
        0b1111111111111111,
        0b0000111001110000,
        0b0001100110011000,
        0b0000011001100000,
    ),
    "cannon": (
        0b0000000110000000,
        0b0000001111000000,
        0b0000001111000000,
        0b0001111111111000,
        0b0011111111111100,
        0b0011111111111100,
        0b0011111111111100,
        0b0011111111111100,
    ),
    "ufo": (
        0b0000011111100000,
        0b0001111111111000,
        0b0011111111111100,
        0b0110110110110110,
        0b1111111111111111,
        0b0011100110011100,
        0b0001000000001000,
        0b0000000000000000,
    ),
    "boom": (
        0b0100100000010010,
        0b0010010000100100,
        0b0001001001001000,
        0b1100000000000011,
        0b1100000000000011,
        0b0001001001001000,
        0b0010010000100100,
        0b0100100000010010,
    ),
}


# ----------------------------------------------------------------------------
# 2C02 FAMICOM PPU GRAPHICS ENGINE
# ----------------------------------------------------------------------------
class FamicomPPU:
    """256x240 2C02-style Tile & Sprite Graphics Engine."""

    def __init__(self) -> None:
        self.surface = pygame.Surface((SCREEN_W, SCREEN_H))
        # Cache of rendered 8x8 tiles: (tile_id, pal_kind, pal_idx) -> pygame.Surface
        self.chr_pixels: Dict[str, List[List[int]]] = {}
        self.tile_cache: Dict[Tuple[str, str, int], pygame.Surface] = {}
        self._build_chr_rom()

    def _build_chr_rom(self) -> None:
        # 1. Compile 5x7 font into 8x8 2-bit CHR tiles
        for ch, rows in _FONT_5X7.items():
            grid = [[0] * 8 for _ in range(8)]
            for ry, rbits in enumerate(rows):
                for rx in range(5):
                    if rbits & (16 >> rx):
                        grid[ry][rx + 1] = 1
                        if ry < 3:
                            grid[ry][rx + 1] = 3  # subtle 2C02 highlight
            self.chr_pixels[f"font_{ch}"] = grid

        # 2. Compile 16x8 sprites into Left/Right 8x8 CHR tiles
        for name, rows16 in SPRITE_PATTERNS.items():
            left = [[0] * 8 for _ in range(8)]
            right = [[0] * 8 for _ in range(8)]
            c_idx = 2 if name == "ufo" else 1
            for ry, bits in enumerate(rows16):
                for rx in range(8):
                    if bits & (1 << (15 - rx)):
                        left[ry][rx] = c_idx
                    if bits & (1 << (7 - rx)):
                        right[ry][rx] = c_idx
            self.chr_pixels[f"{name}_L"] = left
            self.chr_pixels[f"{name}_R"] = right

        # 3. Compile projectile & baseline tiles
        p_shot = [[0] * 8 for _ in range(8)]
        e_shot = [[0] * 8 for _ in range(8)]
        for ry in range(1, 7):
            p_shot[ry][3] = 2
            p_shot[ry][4] = 2
            e_shot[ry][3 + (ry & 1)] = 3
        self.chr_pixels["pshot"] = p_shot
        self.chr_pixels["eshot"] = e_shot

    def _get_tile_surf(self, tid: str, kind: str, pal_idx: int) -> pygame.Surface:
        key = (tid, kind, pal_idx)
        surf = self.tile_cache.get(key)
        if surf is not None:
            return surf
        pal_table = BG_PALETTES if kind == "bg" else SPR_PALETTES
        pal = pal_table[pal_idx & 3]
        surf = pygame.Surface((8, 8), pygame.SRCALPHA)
        grid = self.chr_pixels.get(tid)
        if grid:
            for y in range(8):
                for x in range(8):
                    ci = grid[y][x]
                    if ci != 0:
                        surf.set_at((x, y), NES_PALETTE[pal[ci]])
        self.tile_cache[key] = surf
        return surf

    def clear(self) -> None:
        self.surface.fill(NES_PALETTE[0x0F])

    def draw_text(self, text: str, tx: int, ty: int, pal_idx: int = 0) -> None:
        up = text.upper()
        for i, ch in enumerate(up):
            tid = f"font_{ch}" if f"font_{ch}" in self.chr_pixels else "font_ "
            self.surface.blit(self._get_tile_surf(tid, "bg", pal_idx), ((tx + i) * 8, ty * 8))

    def draw_text_centered(self, text: str, ty: int, pal_idx: int = 0) -> None:
        tx = max(0, (32 - len(text)) // 2)
        self.draw_text(text, tx, ty, pal_idx)

    def draw_sprite16x8(self, name: str, x: int, y: int, pal_idx: int) -> None:
        self.surface.blit(self._get_tile_surf(f"{name}_L", "spr", pal_idx), (int(x), int(y)))
        self.surface.blit(self._get_tile_surf(f"{name}_R", "spr", pal_idx), (int(x) + 8, int(y)))

    def draw_sprite8x8(self, name: str, x: int, y: int, pal_idx: int) -> None:
        self.surface.blit(self._get_tile_surf(name, "spr", pal_idx), (int(x), int(y)))


# ----------------------------------------------------------------------------
# 2A03 FAMICOM PROCEDURAL AUDIO SYNTHESIZER (FILES = OFF)
# ----------------------------------------------------------------------------
class FamicomAPU:
    def __init__(self) -> None:
        self.ok = False
        self.rate = 22050
        self.sounds: Dict[str, pygame.mixer.Sound] = {}
        try:
            pygame.mixer.init(self.rate, -16, 1, 512)
            self.ok = True
            self._build_sounds()
        except Exception:
            self.ok = False

    def _make_sound(self, samples: List[float]) -> pygame.mixer.Sound:
        pcm = array("h", [int(max(-1.0, min(1.0, s)) * 28000) for s in samples])
        return pygame.mixer.Sound(buffer=pcm.tobytes())

    def _pulse_sweep(self, f0: float, f1: float, dur: float, duty: float = 0.5, vol: float = 0.25) -> List[float]:
        n = max(1, int(self.rate * dur))
        out = [0.0] * n
        phase = 0.0
        for i in range(n):
            t = i / n
            freq = f0 + (f1 - f0) * t
            phase = (phase + freq / self.rate) % 1.0
            val = 1.0 if phase < duty else -1.0
            out[i] = val * vol * ((1.0 - t) ** 0.8)
        return out

    def _noise_burst(self, dur: float, vol: float = 0.28, seed: int = 7) -> List[float]:
        n = max(1, int(self.rate * dur))
        rng = random.Random(seed)
        out = [0.0] * n
        cur = 0.0
        for i in range(n):
            t = i / n
            if i % 4 == 0:
                cur = rng.uniform(-1.0, 1.0)
            out[i] = cur * vol * ((1.0 - t) ** 1.4)
        return out

    def _build_sounds(self) -> None:
        # 4-note Space Invaders bass thump (A1, G1, F1, E1)
        for idx, freq in enumerate((98.0, 87.3, 82.4, 73.4)):
            self.sounds[f"march_{idx}"] = self._make_sound(self._pulse_sweep(freq, freq * 0.92, 0.075, 0.5, 0.30))
        self.sounds["shoot"] = self._make_sound(self._pulse_sweep(1200.0, 280.0, 0.14, 0.25, 0.22))
        self.sounds["inv_hit"] = self._make_sound(self._pulse_sweep(740.0, 140.0, 0.16, 0.5, 0.25))
        self.sounds["explosion"] = self._make_sound(self._noise_burst(0.45, 0.35, 19))
        self.sounds["ufo"] = self._make_sound(self._pulse_sweep(520.0, 780.0, 0.12, 0.5, 0.18))

    def play(self, name: str) -> None:
        if self.ok and name in self.sounds:
            try:
                self.sounds[name].play()
            except Exception:
                pass


# ----------------------------------------------------------------------------
# SPACE INVADERS GAME ENTITIES & ENGINE
# ----------------------------------------------------------------------------
@dataclass
class Invader:
    row: int
    col: int
    x: float
    y: float
    kind: str
    points: int
    pal: int
    alive: bool = True


@dataclass
class Bullet:
    x: float
    y: float
    vy: float
    from_player: bool


class Bunker:
    """22x16 pixel destructible Famicom green bunker."""

    TEMPLATE = (
        "    ##############    ",
        "   ################   ",
        "  ##################  ",
        " #################### ",
        "######################",
        "######################",
        "######################",
        "######################",
        "######################",
        "######################",
        "######################",
        "#######        #######",
        "######          ######",
        "#####            #####",
        "#####            #####",
        "#####            #####",
    )

    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y
        self.w = 22
        self.h = 16
        self.pixels = [[1 if ch == "#" else 0 for ch in row] for row in self.TEMPLATE]

    def hit_test(self, bx: int, by: int) -> bool:
        lx = bx - self.x
        ly = by - self.y
        if 0 <= lx < self.w and 0 <= ly < self.h and self.pixels[ly][lx]:
            # Erode a small blast crater
            for dy in range(-2, 3):
                for dx in range(-2, 3):
                    nx, ny = lx + dx, ly + dy
                    if 0 <= nx < self.w and 0 <= ny < self.h and dx * dx + dy * dy <= 5:
                        self.pixels[ny][nx] = 0
            return True
        return False

    def draw(self, surf: pygame.Surface) -> None:
        col = NES_PALETTE[0x2A]
        for ry in range(self.h):
            row = self.pixels[ry]
            for rx in range(self.w):
                if row[rx]:
                    surf.set_at((self.x + rx, self.y + ry), col)


class SpaceInvadersPyPort:
    def __init__(self) -> None:
        pygame.mixer.pre_init(22050, -16, 1, 512)
        pygame.init()
        pygame.display.set_caption(TITLE)
        self.screen = pygame.display.set_mode((WIN_W, WIN_H))
        self.clock = pygame.time.Clock()
        self.ppu = FamicomPPU()
        self.apu = FamicomAPU()

        self.state = "TITLE"  # TITLE, PLAY, GAMEOVER
        self.score = 0
        self.hi_score = 1978
        self.lives = 3
        self.wave = 1
        self.frame = 0

        self.player_x = 120.0
        self.player_y = 204.0
        self.player_dead_timer = 0

        self.invaders: List[Invader] = []
        self.bunkers: List[Bunker] = []
        self.bullets: List[Bullet] = []
        self.explosions: List[Tuple[float, float, int]] = []

        self.march_dir = 1
        self.march_timer = 0
        self.march_step = 0
        self.anim_frame = 0

        self.ufo_active = False
        self.ufo_x = 0.0
        self.ufo_dir = 1
        self.ufo_timer = 600

        self._init_wave(reset_bunkers=True)

    def _init_wave(self, reset_bunkers: bool = False) -> None:
        self.invaders.clear()
        self.bullets.clear()
        self.explosions.clear()
        start_y = min(96, 48 + (self.wave - 1) * 6)
        for r in range(5):
            if r == 0:
                kind, pts, pal = "squid", 30, 1
            elif r in (1, 2):
                kind, pts, pal = "crab", 20, 2
            else:
                kind, pts, pal = "octopus", 10, 3
            for c in range(11):
                ix = 24 + c * 18
                iy = start_y + r * 14
                self.invaders.append(Invader(r, c, float(ix), float(iy), kind, pts, pal))

        if reset_bunkers:
            self.bunkers = [Bunker(32 + i * 52, 176) for i in range(4)]

        self.march_dir = 1
        self.march_timer = 0
        self.march_step = 0

    def start_game(self) -> None:
        self.score = 0
        self.lives = 3
        self.wave = 1
        self.player_x = 120.0
        self.player_dead_timer = 0
        self._init_wave(reset_bunkers=True)
        self.state = "PLAY"

    def update(self) -> None:
        self.frame += 1
        keys = pygame.key.get_pressed()

        if self.state in ("TITLE", "GAMEOVER"):
            if keys[pygame.K_RETURN] or keys[pygame.K_SPACE] or keys[pygame.K_z]:
                self.start_game()
            return

        if self.player_dead_timer > 0:
            self.player_dead_timer -= 1
            if self.player_dead_timer == 0:
                if self.lives <= 0:
                    self.state = "GAMEOVER"
                else:
                    self.player_x = 120.0
            return

        # Player Movement
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.player_x = max(16.0, self.player_x - 1.8)
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.player_x = min(float(SCREEN_W - 32), self.player_x + 1.8)

        # Player Fire (1 active player shot on screen, just like 1978/1985 hardware)
        has_player_shot = any(b.from_player for b in self.bullets)
        if (keys[pygame.K_SPACE] or keys[pygame.K_z] or keys[pygame.K_f]) and not has_player_shot:
            self.bullets.append(Bullet(self.player_x + 7, self.player_y - 6, -3.5, True))
            self.apu.play("shoot")

        # Update Explosions
        self.explosions = [(x, y, t - 1) for x, y, t in self.explosions if t > 1]

        # Mystery UFO logic
        if not self.ufo_active:
            self.ufo_timer -= 1
            if self.ufo_timer <= 0:
                self.ufo_active = True
                self.ufo_dir = random.choice((-1, 1))
                self.ufo_x = 16.0 if self.ufo_dir == 1 else float(SCREEN_W - 32)
                self.ufo_timer = random.randint(700, 1100)
        else:
            self.ufo_x += self.ufo_dir * 1.2
            if self.frame % 10 == 0:
                self.apu.play("ufo")
            if self.ufo_x < 8 or self.ufo_x > SCREEN_W - 24:
                self.ufo_active = False

        # Invader March Tempo (speeds up as fewer invaders remain)
        alive_inv = [inv for inv in self.invaders if inv.alive]
        if not alive_inv:
            self.wave += 1
            self._init_wave(reset_bunkers=False)
            return

        delay = max(2, int(len(alive_inv) * 0.75))
        self.march_timer += 1
        if self.march_timer >= delay:
            self.march_timer = 0
            self.anim_frame ^= 1
            self.apu.play(f"march_{self.march_step & 3}")
            self.march_step += 1

            step_x = 3.0 * self.march_dir
            hit_edge = any(
                (inv.x + step_x < 12) or (inv.x + step_x > SCREEN_W - 28)
                for inv in alive_inv
            )
            if hit_edge:
                self.march_dir *= -1
                for inv in alive_inv:
                    inv.y += 6.0
                    if inv.y >= self.player_y - 8:
                        self.lives = 0
                        self.player_dead_timer = 60
                        self.apu.play("explosion")
            else:
                for inv in alive_inv:
                    inv.x += step_x

        # Enemy Firing
        enemy_shots = sum(1 for b in self.bullets if not b.from_player)
        if enemy_shots < 3 and random.random() < 0.035:
            shooter = random.choice(alive_inv)
            self.bullets.append(Bullet(shooter.x + 6, shooter.y + 8, 2.2, False))

        # Update Bullets & Collisions
        remaining_bullets: List[Bullet] = []
        for b in self.bullets:
            b.y += b.vy
            if b.y < 24 or b.y > 220:
                continue

            # Check Bunkers
            hit_bunker = False
            for bnk in self.bunkers:
                if bnk.hit_test(int(b.x), int(b.y)) or bnk.hit_test(int(b.x), int(b.y + 3)):
                    hit_bunker = True
                    break
            if hit_bunker:
                continue

            if b.from_player:
                # Check UFO
                if self.ufo_active and 30 <= b.y <= 42 and self.ufo_x <= b.x <= self.ufo_x + 16:
                    self.ufo_active = False
                    pts = random.choice((50, 100, 150, 300))
                    self.score += pts
                    self.hi_score = max(self.hi_score, self.score)
                    self.explosions.append((self.ufo_x, 32.0, 20))
                    self.apu.play("inv_hit")
                    continue

                # Check Invaders
                hit_inv = False
                for inv in alive_inv:
                    if inv.x <= b.x <= inv.x + 13 and inv.y <= b.y <= inv.y + 8:
                        inv.alive = False
                        hit_inv = True
                        self.score += inv.points
                        self.hi_score = max(self.hi_score, self.score)
                        self.explosions.append((inv.x, inv.y, 14))
                        self.apu.play("inv_hit")
                        break
                if hit_inv:
                    continue
            else:
                # Check Player Cannon
                if (
                    self.player_x <= b.x <= self.player_x + 15
                    and self.player_y <= b.y <= self.player_y + 8
                ):
                    self.lives -= 1
                    self.player_dead_timer = 55
                    self.explosions.append((self.player_x, self.player_y, 35))
                    self.apu.play("explosion")
                    continue

            remaining_bullets.append(b)
        self.bullets = remaining_bullets

    # ------------------------------------------------------------------------
    # RENDERING (2C02 NAMETABLE + OAM PIPELINE)
    # ------------------------------------------------------------------------
    def draw_hud(self) -> None:
        self.ppu.draw_text("SCORE<1> HI-SCORE SCORE<2>", 3, 1, pal_idx=0)
        self.ppu.draw_text(f"{self.score:04d}     {self.hi_score:04d}     0000", 4, 2, pal_idx=0)

    def draw_title_screen(self) -> None:
        self.ppu.clear()
        self.draw_hud()

        self.ppu.draw_text_centered("AC KONDO'S SPACE INVADERS", 5, pal_idx=2)
        self.ppu.draw_text_centered("PY PORT 0.X", 6, pal_idx=2)
        self.ppu.draw_text_centered("[C] KONDO 1999-2026", 8, pal_idx=1)

        self.ppu.draw_text_centered("*SCORE ADVANCE TABLE*", 11, pal_idx=0)
        self.ppu.draw_sprite16x8("ufo", 72, 104, pal_idx=3)
        self.ppu.draw_text("=? MYSTERY", 12, 13, pal_idx=3)

        self.ppu.draw_sprite16x8("squid_0", 72, 120, pal_idx=1)
        self.ppu.draw_text("=30 POINTS", 12, 15, pal_idx=1)

        self.ppu.draw_sprite16x8("crab_0", 72, 136, pal_idx=2)
        self.ppu.draw_text("=20 POINTS", 12, 17, pal_idx=2)

        self.ppu.draw_sprite16x8("octopus_0", 72, 152, pal_idx=3)
        self.ppu.draw_text("=10 POINTS", 12, 19, pal_idx=2)

        if (self.frame // 25) % 2 == 0:
            self.ppu.draw_text_centered("PRESS ENTER OR SPACE", 22, pal_idx=2)

        # Original game credit + this Python port branding
        self.ppu.draw_text_centered("ORIGINAL GAME [C] 1978 TAITO", 25, pal_idx=0)
        self.ppu.draw_text_centered("DEV: TOSHIHIRO NISHIKADO", 26, pal_idx=3)
        self.ppu.draw_text_centered("AC KONDO PY PORT 0.X", 28, pal_idx=1)

    def draw_play_screen(self) -> None:
        self.ppu.clear()
        self.draw_hud()

        # Bunkers
        for bnk in self.bunkers:
            bnk.draw(self.ppu.surface)

        # Invaders
        for inv in self.invaders:
            if inv.alive:
                spr = f"{inv.kind}_{self.anim_frame}"
                self.ppu.draw_sprite16x8(spr, int(inv.x), int(inv.y), inv.pal)

        # Mystery UFO
        if self.ufo_active:
            self.ppu.draw_sprite16x8("ufo", int(self.ufo_x), 32, pal_idx=3)

        # Player Cannon
        if self.player_dead_timer == 0:
            self.ppu.draw_sprite16x8("cannon", int(self.player_x), int(self.player_y), pal_idx=0)

        # Bullets
        for b in self.bullets:
            tid = "pshot" if b.from_player else "eshot"
            self.ppu.draw_sprite8x8(tid, int(b.x) - 3, int(b.y), pal_idx=0 if b.from_player else 3)

        # Explosions
        for ex, ey, _t in self.explosions:
            self.ppu.draw_sprite16x8("boom", int(ex), int(ey), pal_idx=3)

        # Famicom Green Floor Line & Lives Status
        pygame.draw.line(self.ppu.surface, NES_PALETTE[0x2A], (8, 218), (SCREEN_W - 8, 218), 1)
        self.ppu.draw_text(f"{self.lives}", 2, 28, pal_idx=1)
        for i in range(max(0, self.lives - 1)):
            self.ppu.draw_sprite16x8("cannon", 32 + i * 18, 224, pal_idx=0)
        self.ppu.draw_text("CREDIT 00", 20, 28, pal_idx=0)

        if self.state == "GAMEOVER":
            self.ppu.draw_text_centered("GAME OVER", 13, pal_idx=2)
            self.ppu.draw_text_centered("PRESS SPACE TO PLAY AGAIN", 15, pal_idx=0)

    def run(self) -> None:
        running = True
        while running:
            # Lock speed to NTSC Famicom rate (60.0988 FPS / FAMICOM_SPEED = 60)
            self.clock.tick(NTSC_FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    if self.state == "PLAY":
                        self.state = "TITLE"
                    else:
                        running = False

            self.update()
            if self.state == "TITLE":
                self.draw_title_screen()
            else:
                self.draw_play_screen()

            pygame.transform.scale(self.ppu.surface, (WIN_W, WIN_H), self.screen)
            pygame.display.flip()

        pygame.quit()


if __name__ == "__main__":
    SpaceInvadersPyPort().run()
