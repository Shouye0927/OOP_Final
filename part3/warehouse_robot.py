'''
Dino Fighter Ultimate: OOP Project Final Version
檔案名稱: warehouse_robot.py
'''
import random
import sys
import pygame
import math
from enum import Enum

# --- 基礎設定 ---
class Action(Enum):
    RUN = 0
    JUMP = 1
    SHOOT = 2
    DROP = 3

# 調色盤
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 50, 50)       
SKY_BLUE = (240, 248, 255)
UI_DARK = (40, 44, 52)
HEART_RED = (220, 20, 60)
AMMO_GOLD = (255, 215, 0)

DINO_COLOR = (80, 80, 80)
BULLET_COLOR = (255, 140, 0)
CACTUS_COLOR = (34, 139, 34)
BIRD_COLOR = (70, 130, 180)
BAT_COLOR = (75, 0, 130)

# --- 1. 粒子系統 ---

class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.size = random.randint(4, 7)
        self.life = random.randint(20, 40)
        angle = random.uniform(0, 6.28)
        speed = random.uniform(2, 6)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= 1
        self.size *= 0.95

    def draw(self, surface):
        if self.life > 0 and self.size > 1:
            pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), int(self.size))

class ParticleSystem:
    def __init__(self):
        self.particles = []

    def emit(self, x, y, color, count=10):
        for _ in range(count):
            self.particles.append(Particle(x, y, color))

    def update_and_draw(self, surface):
        self.particles = [p for p in self.particles if p.life > 0]
        for p in self.particles:
            p.update()
            p.draw(surface)

# --- 2. 核心 OOP 架構 ---

class GameObject:
    def __init__(self, x, y, w, h, color):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.color = color

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, (self.x, self.y, self.w, self.h))

    def collides_with(self, other):
        return (self.x < other.x + other.w and
                self.x + self.w > other.x and
                self.y < other.y + other.h and
                self.y + self.h > other.y)

class Bullet(GameObject):
    def __init__(self, x, y):
        super().__init__(x, y, 15, 6, BULLET_COLOR)
        self.speed = 15

    def move(self):
        self.x += self.speed
    
    def draw(self, surface):
        pygame.draw.rect(surface, self.color, (self.x, self.y, self.w, self.h), border_radius=3)

class Dino(GameObject):
    def __init__(self):
        super().__init__(50, 250, 40, 40, DINO_COLOR)
        self.is_jumping = False
        self.jump_velocity = 0
        self.gravity = 2.0      
        self.jump_strength = -25
        self.base_y = 250
        self.max_hp = 3
        self.hp = self.max_hp
        self.invincible_timer = 0 

    def update(self):
        self.y += self.jump_velocity
        if self.y < self.base_y:
            self.jump_velocity += self.gravity
            self.is_jumping = True
        else:
            self.y = self.base_y
            self.jump_velocity = 0
            self.is_jumping = False
        
        if self.invincible_timer > 0:
            self.invincible_timer -= 1

    def jump(self):
        if not self.is_jumping:
            self.jump_velocity = self.jump_strength

    def fast_drop(self):
        if self.is_jumping:
            self.jump_velocity = 20 

    def take_damage(self):
        if self.invincible_timer == 0:
            self.hp -= 1
            self.invincible_timer = 45 
            return True
        return False
    
    def heal(self):
        if self.hp < self.max_hp:
            self.hp += 1
            return True
        return False

    def draw(self, surface):
        if self.invincible_timer > 0 and self.invincible_timer % 4 < 2: return
        pygame.draw.rect(surface, self.color, (self.x, self.y, self.w, self.h))
        pygame.draw.rect(surface, self.color, (self.x + 20, self.y - 15, 25, 25)) 
        pygame.draw.circle(surface, WHITE, (self.x + 35, self.y - 8), 3) 
        pygame.draw.rect(surface, self.color, (self.x + 5, self.y + self.h, 8, 8)) 
        pygame.draw.rect(surface, self.color, (self.x + 25, self.y + self.h, 8, 8)) 

# --- 3. 障礙物體系 ---

class Obstacle(GameObject):
    def __init__(self, x, y, w, h, color, speed, shootable):
        super().__init__(x, y, w, h, color)
        self.speed = speed
        self.shootable = shootable

    def move(self, speed_multiplier):
        self.x -= self.speed * speed_multiplier

class Cactus(Obstacle):
    def __init__(self, start_x):
        super().__init__(start_x, 250, 25, 45, CACTUS_COLOR, 7, False)
    
    def draw(self, surface):
        pygame.draw.rect(surface, self.color, (self.x + 8, self.y, 10, self.h), border_radius=3)
        pygame.draw.rect(surface, self.color, (self.x, self.y + 10, 26, 8), border_radius=3)
        pygame.draw.rect(surface, self.color, (self.x, self.y + 5, 8, 15), border_radius=3)
        pygame.draw.rect(surface, self.color, (self.x + 18, self.y + 5, 8, 15), border_radius=3)

class Bird(Obstacle):
    def __init__(self, start_x):
        rand_y = random.randint(150, 230) 
        super().__init__(start_x, rand_y, 35, 25, BIRD_COLOR, 9, True)
    
    def draw(self, surface):
        pygame.draw.ellipse(surface, self.color, (self.x, self.y, self.w, self.h))
        pygame.draw.polygon(surface, WHITE, [(self.x+10, self.y+10), (self.x+20, self.y-10), (self.x+25, self.y+10)])
        pygame.draw.polygon(surface, AMMO_GOLD, [(self.x, self.y+10), (self.x-8, self.y+13), (self.x, self.y+16)])

class Bat(Obstacle):
    def __init__(self, start_x):
        rand_y = random.randint(200, 250) 
        super().__init__(start_x, rand_y, 30, 20, BAT_COLOR, 11, True)
    
    def draw(self, surface):
        center = (self.x + 15, self.y + 10)
        pygame.draw.circle(surface, self.color, center, 10)
        pygame.draw.polygon(surface, self.color, [(self.x+15, self.y+10), (self.x-5, self.y-5), (self.x+5, self.y+15)])
        pygame.draw.polygon(surface, self.color, [(self.x+15, self.y+10), (self.x+35, self.y-5), (self.x+25, self.y+15)])

class HealthPack(Obstacle):
    def __init__(self, start_x):
        rand_y = random.randint(180, 240)
        super().__init__(start_x, rand_y, 30, 30, WHITE, 9, False) 

    def draw(self, surface):
        pygame.draw.rect(surface, WHITE, (self.x, self.y, self.w, self.h), border_radius=5)
        pygame.draw.rect(surface, RED, (self.x, self.y, self.w, self.h), 2, border_radius=5)
        cx, cy = self.x + 15, self.y + 15
        pygame.draw.rect(surface, RED, (cx - 4, cy - 10, 8, 20))
        pygame.draw.rect(surface, RED, (cx - 10, cy - 4, 20, 8))

# --- 4. 介面管理 ---

class UIManager:
    def __init__(self, width, height, font):
        self.width = width
        self.height = height
        self.font = font
    
    def draw_hud(self, surface, score, speed, hp, bullets_left):
        pygame.draw.rect(surface, UI_DARK, (0, 0, self.width, 50))
        pygame.draw.line(surface, WHITE, (0, 50), (self.width, 50), 2)
        
        score_text = self.font.render(f"SCORE: {int(score)}", True, WHITE)
        surface.blit(score_text, (20, 15))
        
        speed_text = self.font.render(f"SPEED: x{speed:.1f}", True, AMMO_GOLD)
        surface.blit(speed_text, (self.width // 2 - 50, 15))

        for i in range(hp):
            x = self.width - 140 + (i * 25)
            pygame.draw.circle(surface, HEART_RED, (x, 25), 6)
            pygame.draw.circle(surface, HEART_RED, (x+8, 25), 6)
            pygame.draw.polygon(surface, HEART_RED, [(x-6, 28), (x+14, 28), (x+4, 40)])

        for i in range(3):
            rect = (self.width - 140 + (i * 20), 42, 12, 5)
            pygame.draw.rect(surface, (100, 100, 100), rect, 1) 
            if i < bullets_left: pygame.draw.rect(surface, AMMO_GOLD, rect)

    def draw_screen(self, surface, title, subtitle, bg_color=(0,0,0,180)):
        overlay = pygame.Surface((self.width, self.height))
        overlay.set_alpha(bg_color[3])
        overlay.fill(bg_color[:3])
        surface.blit(overlay, (0,0))
        t_surf = self.font.render(title, True, WHITE)
        s_surf = self.font.render(subtitle, True, AMMO_GOLD)
        t_rect = t_surf.get_rect(center=(self.width//2, self.height//2 - 20))
        s_rect = s_surf.get_rect(center=(self.width//2, self.height//2 + 20))
        surface.blit(t_surf, t_rect)
        surface.blit(s_surf, s_rect)

# --- 5. 遊戲引擎 ---

class DinoGame:
    def __init__(self, width=700, height=350, fps=30):
        self.width = width
        self.height = height
        self.fps = fps
        self._init_pygame()
        self.ui = UIManager(width, height, self.font)
        self.particles = ParticleSystem() 
        self.state = 'WAITING' 
        self.reset()

    def _init_pygame(self):
        pygame.init()
        pygame.display.set_caption("Dino Fighter Ultimate")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial Bold", 20)
        self.window = pygame.display.set_mode((self.width, self.height))

    def reset(self, seed=None):
        random.seed(seed)
        self.dino = Dino()
        self.obstacles = []
        self.bullets = []
        self.particles = ParticleSystem()
        self.score = 0
        self.game_over = False
        self.spawn_timer = 0
        self.game_speed = 1.0

    def step(self, action: Action):
        if self.state != 'RUNNING': return False, self.state == 'GAME_OVER'

        if self.spawn_timer % 5 == 0: self.score += 1
        self.game_speed = 1.0 + (self.score / 600.0)
        current_spawn_threshold = max(20, 60 - int(self.score / 15))

        if action == Action.JUMP: self.dino.jump()
        elif action == Action.SHOOT:
            if len(self.bullets) < 3:
                self.bullets.append(Bullet(self.dino.x + self.dino.w, self.dino.y + 15))
        elif action == Action.DROP: self.dino.fast_drop()

        self.dino.update()

        self.spawn_timer += 1
        if self.spawn_timer > current_spawn_threshold:
            if random.random() < 0.6: 
                start_x = self.width + random.randint(0, 50)
                rng = random.random()
                if rng < 0.1:     self.obstacles.append(HealthPack(start_x)) 
                elif rng < 0.45:  self.obstacles.append(Cactus(start_x))
                elif rng < 0.75:  self.obstacles.append(Bird(start_x))
                else:             self.obstacles.append(Bat(start_x))
                self.spawn_timer -= current_spawn_threshold

        for b in self.bullets[:]:
            b.move()
            if b.x > self.width: self.bullets.remove(b)

        for obj in self.obstacles[:]:
            obj.move(self.game_speed)
            
            hit_by_bullet = False
            for b in self.bullets[:]:
                if b.collides_with(obj):
                    if obj.shootable:
                        self.score += 5
                        self.particles.emit(obj.x + obj.w//2, obj.y + obj.h//2, obj.color, 15)
                        self.particles.emit(b.x, b.y, BULLET_COLOR, 5) 
                        
                        self.bullets.remove(b)
                        self.obstacles.remove(obj)
                        hit_by_bullet = True
                        break
                    else:
                        self.particles.emit(b.x, b.y, WHITE, 5)
                        self.bullets.remove(b) 
                        break
            if hit_by_bullet: continue

            if self.dino.collides_with(obj):
                if isinstance(obj, HealthPack):
                    if self.dino.heal():
                        self.particles.emit(self.dino.x, self.dino.y, HEART_RED, 10)
                    self.obstacles.remove(obj)
                    continue 

                if self.dino.take_damage():
                    self.particles.emit(self.dino.x + 20, self.dino.y + 20, RED, 10)

                if self.dino.hp <= 0:
                    self.game_over = True
                    self.state = 'GAME_OVER'

            if obj.x < -50: self.obstacles.remove(obj)

        return True, self.game_over

    def render(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
        
        self.window.fill(SKY_BLUE)
        pygame.draw.line(self.window, (100, 100, 100), (0, 290), (self.width, 290), 3)

        self.dino.draw(self.window)
        for obj in self.obstacles: obj.draw(self.window)
        for b in self.bullets: b.draw(self.window)
        
        self.particles.update_and_draw(self.window)

        if self.state == 'RUNNING':
            self.ui.draw_hud(self.window, self.score, self.game_speed, self.dino.hp, 3 - len(self.bullets))
        elif self.state == 'WAITING':
            self.ui.draw_hud(self.window, 0, 1.0, 3, 3)
            self.ui.draw_screen(self.window, "DINO FIGHTER", "Press SPACE to Start")
        elif self.state == 'GAME_OVER':
            self.ui.draw_hud(self.window, self.score, self.game_speed, 0, 3 - len(self.bullets))
            self.ui.draw_screen(self.window, "GAME OVER", "Press R to Restart", bg_color=(0,0,0,200))
        
        pygame.display.update()
        self.clock.tick(self.fps)

if __name__ == "__main__":
    game = DinoGame()
    running = True
    while running:
        action = None 
        keys = pygame.key.get_pressed()
        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: running = False
                
                if game.state == 'WAITING':
                    if event.key == pygame.K_SPACE: game.state = 'RUNNING'
                elif game.state == 'GAME_OVER':
                    if event.key == pygame.K_r: game.reset(); game.state = 'RUNNING'
                elif game.state == 'RUNNING':
                    if event.key == pygame.K_SPACE or event.key == pygame.K_UP: action = Action.JUMP
                    elif event.key == pygame.K_f: action = Action.SHOOT
                    elif event.key == pygame.K_s or event.key == pygame.K_DOWN: action = Action.DROP
        
        if game.state == 'RUNNING':
             if action is None and (keys[pygame.K_s] or keys[pygame.K_DOWN]): action = Action.DROP
             game.step(action if action else Action.RUN)
        game.render()