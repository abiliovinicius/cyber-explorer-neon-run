
# CYBER EXPLORER - NEON RUN

from pygame import Rect
import math
import random

WIDTH = 900
HEIGHT = 600
TITLE = "Cyber Explorer - Neon Run"

PLAYER_SPEED = 220
ANIM_RATE = 0.10
CLICK_THRESHOLD = 6
SAFE_COLLISION_DIST = 28

# SPRITES

HERO_IDLE = ["hero_idle1", "hero_idle2", "hero_idle3", "hero_idle4"]
HERO_WALK = ["hero_walk1", "hero_walk2", "hero_walk3", "hero_walk4"]

ENEMY_A_IDLE = ["enemy_a_idle1", "enemy_a_idle2", "enemy_a_idle3", "enemy_a_idle4"]
ENEMY_A_WALK = ["enemy_a_walk1", "enemy_a_walk2", "enemy_a_walk3", "enemy_a_walk4"]

ENEMY_B_IDLE = ["enemy_b_idle1", "enemy_b_idle2", "enemy_b_idle3", "enemy_b_idle4"]
ENEMY_B_WALK = ["enemy_b_walk1", "enemy_b_walk2", "enemy_b_walk3", "enemy_b_walk4"]

BACKGROUND_NAME = "background"

SOUND_CLICK = "click"
SOUND_ALERT = "alert"
BG_MUSIC = "bg_music"


# HELPERS

def dist(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])

def clamp(v, a, b):
    return max(a, min(v, b))

def safe_play(name, enabled):
    if enabled:
        try:
            getattr(sounds, name).play()
        except:
            pass

# SCREEN EFFECTS

class ScreenEffects:
    def __init__(self):
        self.flash_timer = 0
        self.shake_timer = 0
        self.shake_power = 8

    def start_flash(self):
        self.flash_timer = 0.15

    def start_shake(self):
        self.shake_timer = 0.25

    def update(self, dt):
        if self.flash_timer > 0:
            self.flash_timer -= dt
        if self.shake_timer > 0:
            self.shake_timer -= dt

effects = ScreenEffects()


# ANIMATED SPRITE

class AnimatedSprite:
    def __init__(self, frames, pos):
        self.frames = frames
        self.actor = Actor(frames[0], pos=pos)
        self.index = 0
        self.timer = 0

    def update(self, dt):
        self.timer += dt
        if self.timer >= ANIM_RATE:
            self.timer = 0
            self.index = (self.index + 1) % len(self.frames)
            self.actor.image = self.frames[self.index]

    def set_pos(self, pos):
        self.actor.pos = pos

    def draw(self):
        self.actor.draw()

# PLAYER

class Player:
    def __init__(self, pos):
        self.pos = [float(pos[0]), float(pos[1])]
        self.target = self.pos[:]
        self.state = "idle"

        self.idle = AnimatedSprite(HERO_IDLE, pos)
        self.walk = AnimatedSprite(HERO_WALK, pos)

    def set_target(self, pos, sfx_enabled):
        self.target = [float(pos[0]), float(pos[1])]
        safe_play(SOUND_CLICK, sfx_enabled)

    def update(self, dt):
        dx = self.target[0] - self.pos[0]
        dy = self.target[1] - self.pos[1]
        d = math.hypot(dx, dy)

        if d <= CLICK_THRESHOLD:
            self.state = "idle"
            self.idle.set_pos((int(self.pos[0]), int(self.pos[1])))
            self.idle.update(dt)
            return

        self.state = "walk"

        ang = math.atan2(dy, dx)
        step = PLAYER_SPEED * dt

        self.pos[0] += math.cos(ang) * step
        self.pos[1] += math.sin(ang) * step

        cur = (int(self.pos[0]), int(self.pos[1]))
        self.walk.set_pos(cur)
        self.walk.update(dt)

    def draw(self):
        if self.state == "idle":
            self.idle.draw()
        else:
            self.walk.draw()

    def get_pos(self):
        return self.pos

# BASE ENEMY

class Enemy:
    def __init__(self, pos, rect, idle, walk, speed):
        self.pos = [float(pos[0]), float(pos[1])]
        self.territory = Rect(rect)
        self.speed = speed

        self.idle = AnimatedSprite(idle, pos)
        self.walk = AnimatedSprite(walk, pos)

        self.state = "idle"
        self.destination = self._random_dest()

    def _random_dest(self):
        return [
            float(random.randint(self.territory.left+5, self.territory.right-5)),
            float(random.randint(self.territory.top+5, self.territory.bottom-5))
        ]

    def update(self, dt, player_pos):
        dx = self.destination[0] - self.pos[0]
        dy = self.destination[1] - self.pos[1]
        d = math.hypot(dx, dy)

        if d < 4:
            self.state = "idle"
            self.destination = self._random_dest()
            self.idle.set_pos((int(self.pos[0]), int(self.pos[1])))
            self.idle.update(dt)
            return

        self.state = "walk"
        ang = math.atan2(dy, dx)

        self.pos[0] += math.cos(ang) * self.speed * dt
        self.pos[1] += math.sin(ang) * self.speed * dt

        self.pos[0] = clamp(self.pos[0], self.territory.left, self.territory.right)
        self.pos[1] = clamp(self.pos[1], self.territory.top, self.territory.bottom)

        self.walk.set_pos((int(self.pos[0]), int(self.pos[1])))
        self.walk.update(dt)

    def draw(self):
        if self.state == "idle":
            self.idle.draw()
        else:
            self.walk.draw()

    def get_pos(self):
        return self.pos


# SPECIAL ENEMIES

class Scout(Enemy):
    def __init__(self, pos, rect):
        super().__init__(pos, rect, ENEMY_A_IDLE, ENEMY_A_WALK, speed=210)

class Stalker(Enemy):
    def __init__(self, pos, rect):
        super().__init__(pos, rect, ENEMY_B_IDLE, ENEMY_B_WALK, speed=160)
        self.radius = 200

    def update(self, dt, player_pos):
        if dist(self.pos, player_pos) < self.radius:
            px = clamp(player_pos[0], self.territory.left, self.territory.right)
            py = clamp(player_pos[1], self.territory.top, self.territory.bottom)
            self.destination = [px, py]
        super().update(dt, player_pos)

class Hunter(Enemy):
    def __init__(self, pos, rect):
        super().__init__(pos, rect, ENEMY_B_IDLE, ENEMY_B_WALK, speed=170)

    def update(self, dt, player_pos):
        px = clamp(player_pos[0], self.territory.left, self.territory.right)
        py = clamp(player_pos[1], self.territory.top, self.territory.bottom)
        self.destination = [px, py]
        super().update(dt, player_pos)

class Brute(Enemy):
    def __init__(self, pos, rect):
        super().__init__(pos, rect, ENEMY_A_IDLE, ENEMY_A_WALK, speed=85)


class NeonButton:
    def __init__(self, rect, text):
        self.rect = Rect(rect)
        self.text = text
        self.hover = False

    def contains(self, pos):
        return self.rect.collidepoint(pos)

    def update_hover(self, pos):
        self.hover = self.contains(pos)

    def draw(self):
        bg = (10,10,25)
        glow = (0,220,255) if self.hover else (0,150,200)
        screen.draw.filled_rect(self.rect, bg)
        screen.draw.rect(self.rect, glow)
        screen.draw.text(self.text, (self.rect.x + 14, self.rect.y + 10),
                         fontsize=30, color=glow)

# GAME MANAGER

class Game:
    def __init__(self):
        self.state = "menu"
        self.cursor_pos = (0,0)

        self.player = Player((120,420))
        self.goal = Rect((820,40,60,60))

        self.enemies = [
            Scout((200,240),(140,200,260,230)),
            Scout((300,260),(220,200,240,260)),
            Scout((260,440),(200,380,260,200)),
            Scout((400,150),(340,100,260,180)),

            Stalker((520,360),(450,300,260,250)),
            Stalker((620,260),(580,200,200,200)),
            Stalker((720,380),(660,320,200,200)),
            Stalker((480,210),(420,140,240,220)),

            Brute((340,420),(260,360,300,240)),
            Brute((560,160),(480,100,300,240)),

            Hunter((760,210),(700,140,180,260)),
            Hunter((820,360),(760,300,180,260)),
        ]

        bw,bh = 220,56
        cx = WIDTH//2 - bw//2

        self.btn_start = NeonButton((cx,220,bw,bh),"Start")
        self.btn_music = NeonButton((cx,300,bw,bh),"Music: ON")
        self.btn_sfx   = NeonButton((cx,380,bw,bh),"SFX: ON")
        self.btn_exit  = NeonButton((cx,460,bw,bh),"Exit")

        self.music_on = True
        self.sfx_on = True   

        self._play_music()

        self.lives = 6
        self.time_elapsed = 0
        self.damage_cd = 0

    def _play_music(self):
        try:
            sounds.bg_music.stop()
        except:
            pass

        if self.music_on:
            try:
                sounds.bg_music.set_volume(0.6)
                sounds.bg_music.play(-1)
            except:
                pass

            self.btn_music.text = "Music: ON"
        else:
            self.btn_music.text = "Music: OFF"

    def start_game(self):
        self.state = "playing"
        self.player = Player((120,420))
        self.lives = 6
        self.time_elapsed = 0
        self.damage_cd = 0

        for e in self.enemies:
            e.pos = e._random_dest()
            e.destination = e._random_dest()

    def update(self, dt):
        effects.update(dt)

        if self.state == "menu":
            mx,my = self.cursor_pos
            self.btn_start.update_hover((mx,my))
            self.btn_music.update_hover((mx,my))
            self.btn_sfx.update_hover((mx,my))
            self.btn_exit.update_hover((mx,my))
            return

        if self.state == "playing":
            self.time_elapsed += dt

            self.player.update(dt)
            ppos = self.player.get_pos()

            for e in self.enemies:
                e.update(dt, ppos)

            if self.damage_cd > 0:
                self.damage_cd -= dt

            self._check_collision(ppos)

            if self.goal.collidepoint(ppos):
                self.state = "victory"
                try: sounds.bg_music.stop()
                except: pass

    def _check_collision(self, p):
        for e in self.enemies:
            if dist(p, e.get_pos()) <= SAFE_COLLISION_DIST:
                if self.damage_cd <= 0:
                    self.lives -= 1
                    self.damage_cd = 1

                    effects.start_flash()
                    effects.start_shake()

                    safe_play(SOUND_ALERT, self.sfx_on)

                    self.player.set_target((120,420), self.sfx_on)

                    if self.lives <= 0:
                        self.state = "gameover"
                return

    def draw(self):
        screen.clear()

        try:
            screen.blit(BACKGROUND_NAME,(0,0))
        except:
            screen.fill((10,10,18))

        if self.state=="menu":
            self._draw_menu()
        elif self.state=="playing":
            self._draw_play()
        elif self.state=="victory":
            screen.draw.text("VICTORY!", (300,240), fontsize=64, color=(0,255,200))
            screen.draw.text("Click to menu", (300,320), color="white")
        elif self.state=="gameover":
            screen.draw.text("GAME OVER", (300,240), fontsize=64, color=(255,80,80))
            screen.draw.text("Click to menu", (300,320), color="white")

    def _draw_menu(self):
        screen.draw.text("CYBER EXPLORER", (260,100), fontsize=60, color=(0,200,255))
        self.btn_start.draw()
        self.btn_music.draw()
        self.btn_sfx.draw()
        self.btn_exit.draw()

    def _draw_play(self):
        screen.draw.filled_rect(self.goal,(0,220,200))
        for e in self.enemies:
            e.draw()
        self.player.draw()
        self._draw_hud()

    def _draw_hud(self):
        panel = Rect((12,10,180,48))
        screen.draw.filled_rect(panel,(8,8,25))
        screen.draw.rect(panel,(0,200,255))

        for i in range(6):
            r = Rect((20+i*26,18,20,20))
            if i < self.lives:
                screen.draw.filled_rect(r,(0,255,200))
            else:
                screen.draw.filled_rect(r,(40,40,60))
            screen.draw.rect(r,(0,180,220))

        screen.draw.text(f"{int(self.time_elapsed)}s",
                         (WIDTH-90,16), fontsize=34, color=(0,220,255))

    def on_mouse_down(self,pos):
        self.cursor_pos=pos

        if self.state=="menu":
            if self.btn_start.contains(pos): 
                self.start_game()

            elif self.btn_music.contains(pos):
                self.music_on = not self.music_on
                self._play_music()

            elif self.btn_sfx.contains(pos):
                self.sfx_on = not self.sfx_on
                self.btn_sfx.text = "SFX: ON" if self.sfx_on else "SFX: OFF"

            elif self.btn_exit.contains(pos):
                exit()

        elif self.state=="playing":
            self.player.set_target(pos, self.sfx_on)

        elif self.state in ("victory","gameover"):
            self.state="menu"
            self.lives=6
            self.time_elapsed=0
            self.damage_cd=0
            if self.music_on: self._play_music()

    def on_mouse_move(self,pos):
        self.cursor_pos=pos


# HOOKS

game = Game()

def update(dt):
    game.update(dt)

def draw():
    game.draw()

def on_mouse_down(pos):
    game.on_mouse_down(pos)

def on_mouse_move(pos):
    game.on_mouse_move(pos)
