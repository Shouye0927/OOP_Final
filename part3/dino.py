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

# 調色盤 (省略...)
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
        # ### [OOP] 組合 (Composition)
        # ParticleSystem "擁有" 多個 Particle 物件。
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

# ### [OOP] 基礎類別 (Base Class)
# 定義所有遊戲物件共有的屬性 (x, y, w, h) 和行為 (draw, collides_with)。
# 這符合 "Don't Repeat Yourself" (DRY) 原則。
class GameObject:
    def __init__(self, x, y, w, h, color):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.color = color

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, (self.x, self.y, self.w, self.h))

    # ### [OOP] 共用邏輯
    # 所有繼承 GameObject 的子類別 (Dino, Bullet, Obstacle) 自動擁有此功能，
    # 不需要重複寫碰撞偵測代碼。
    def collides_with(self, other):
        return (self.x < other.x + other.w and
                self.x + self.w > other.x and
                self.y < other.y + other.h and
                self.y + self.h > other.y)


# ### [OOP] 繼承 (Inheritance)
# Bullet 繼承自 GameObject，自動獲得 x, y, w, h 等屬性。
class Bullet(GameObject):
    def __init__(self, x, y):
        super().__init__(x, y, 15, 6, BULLET_COLOR)
        self.speed = 15

    def move(self):
        self.x += self.speed
    
    # ### [OOP] 多型 (Polymorphism) - 覆寫 (Override)
    # 子類別重新定義了父類別的 draw 方法。
    # 這裡將矩形改為圓角矩形，表現出與一般 GameObject 不同的行為。
    def draw(self, surface):
        pygame.draw.rect(surface, self.color, (self.x, self.y, self.w, self.h), border_radius=3)


# ### [OOP] 繼承 (Inheritance)
class Dino(GameObject):
    def __init__(self):
        super().__init__(50, 250, 40, 40, DINO_COLOR)
        self.is_jumping = False
        self.jump_velocity = 0
        self.gravity = 2.0      
        self.jump_strength = -25
        self.base_y = 250
        # ### [OOP] 封裝 (Encapsulation) - 數據保護
        # hp 和 invincible_timer 是物件內部的狀態，
        # 不應該由外部直接修改 (例如不要在外面寫 dino.hp -= 1)。
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

    # ### [OOP] 封裝 (Encapsulation) - 行為控制
    # 外部透過此方法與 Dino 互動。
    # 這個方法內部處理了「無敵時間」的邏輯判斷，外部呼叫者不需要知道細節，
    # 只要知道「呼叫此函數嘗試扣血」即可。
    def take_damage(self):
        if self.invincible_timer == 0:
            self.hp -= 1
            self.invincible_timer = 45 
            return True
        return False
    
    # ### [OOP] 封裝 (Encapsulation)
    # 同樣的，補血邏輯 (不能超過上限) 被封裝在這裡。
    def heal(self):
        if self.hp < self.max_hp:
            self.hp += 1
            return True
        return False

    # ### [OOP] 多型 (Polymorphism) - 覆寫
    # Dino 的畫法包含閃爍效果 (無敵時間) 和眼睛繪製，與父類別不同。
    def draw(self, surface):
        if self.invincible_timer > 0 and self.invincible_timer % 4 < 2: return
        pygame.draw.rect(surface, self.color, (self.x, self.y, self.w, self.h))
        pygame.draw.rect(surface, self.color, (self.x + 20, self.y - 15, 25, 25)) 
        pygame.draw.circle(surface, WHITE, (self.x + 35, self.y - 8), 3) 
        pygame.draw.rect(surface, self.color, (self.x + 5, self.y + self.h, 8, 8)) 
        pygame.draw.rect(surface, self.color, (self.x + 25, self.y + self.h, 8, 8)) 

# --- 3. 障礙物體系 ---

# ### [OOP] 中層抽象 (Abstraction)
# Obstacle 繼承 GameObject，並增加了 speed 和 shootable 屬性。
# 它作為所有具體障礙物 (Cactus, Bird, Bat) 的父類別。
class Obstacle(GameObject):
    def __init__(self, x, y, w, h, color, speed, shootable):
        super().__init__(x, y, w, h, color)
        self.speed = speed
        self.shootable = shootable

    def move(self, speed_multiplier):
        self.x -= self.speed * speed_multiplier


# ### [OOP] 多層繼承 (Multilevel Inheritance)
# Cactus -> Obstacle -> GameObject
class Cactus(Obstacle):
    def __init__(self, start_x):
        super().__init__(start_x, 250, 25, 45, CACTUS_COLOR, 7, False)
    
    # ### [OOP] 多型 - 具體實作
    # 仙人掌有自己獨特的形狀繪製方式。
    def draw(self, surface):
        pygame.draw.rect(surface, self.color, (self.x + 8, self.y, 10, self.h), border_radius=3)
        pygame.draw.rect(surface, self.color, (self.x, self.y + 10, 26, 8), border_radius=3)
        pygame.draw.rect(surface, self.color, (self.x, self.y + 5, 8, 15), border_radius=3)
        pygame.draw.rect(surface, self.color, (self.x + 18, self.y + 5, 8, 15), border_radius=3)

class Bird(Obstacle):
    def __init__(self, start_x):
        rand_y = random.randint(150, 230) 
        super().__init__(start_x, rand_y, 35, 25, BIRD_COLOR, 9, True)
    
    # ### [OOP] 多型 - 具體實作
    def draw(self, surface):
        pygame.draw.ellipse(surface, self.color, (self.x, self.y, self.w, self.h))
        pygame.draw.polygon(surface, WHITE, [(self.x+10, self.y+10), (self.x+20, self.y-10), (self.x+25, self.y+10)])
        pygame.draw.polygon(surface, AMMO_GOLD, [(self.x, self.y+10), (self.x-8, self.y+13), (self.x, self.y+16)])

class Bat(Obstacle):
    def __init__(self, start_x):
        rand_y = random.randint(200, 250) 
        super().__init__(start_x, rand_y, 30, 20, BAT_COLOR, 11, True)
    
    # ### [OOP] 多型 - 具體實作
    def draw(self, surface):
        center = (self.x + 15, self.y + 10)
        pygame.draw.circle(surface, self.color, center, 10)
        pygame.draw.polygon(surface, self.color, [(self.x+15, self.y+10), (self.x-5, self.y-5), (self.x+5, self.y+15)])
        pygame.draw.polygon(surface, self.color, [(self.x+15, self.y+10), (self.x+35, self.y-5), (self.x+25, self.y+15)])


#補包的部分
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
# ### [OOP] 單一職責原則 (SRP)
# 這個類別只負責「畫圖」，不負責遊戲邏輯 (例如不決定什麼時候扣血)。
class UIManager:
    def __init__(self, width, height, font):
        self.width = width
        self.height = height
        self.font = font
    
    def draw_hud(self, surface, score, speed, hp, bullets_left):
        # (繪製程式碼省略，這屬於封裝的實作細節)
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
        # ### [OOP] 組合 (Composition)
        # DinoGame 是一個容器，它組合了 UIManager, ParticleSystem。
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
        # ### [OOP] 組合 (Composition)
        # 遊戲重置時，重新創建 Dino 物件。
        self.dino = Dino()
        # ### [OOP] 聚合 (Aggregation)
        # 透過 List 儲存所有的障礙物與子彈物件。
        self.obstacles = []
        self.bullets = []
        self.particles = ParticleSystem()
        self.score = 0
        self.game_over = False
        self.spawn_timer = 0
        self.game_speed = 1.0


    #每一幀都會執行的邏輯
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
                # ### [OOP] 多型物件生成
                # 不管生成的是 HealthPack, Cactus, Bird 還是 Bat，
                # 它們都被視為 Obstacle 存入 self.obstacles 列表中。
                if rng < 0.1:     self.obstacles.append(HealthPack(start_x)) 
                elif rng < 0.45:  self.obstacles.append(Cactus(start_x))
                elif rng < 0.75:  self.obstacles.append(Bird(start_x))
                else:             self.obstacles.append(Bat(start_x))
                self.spawn_timer -= current_spawn_threshold

        for b in self.bullets[:]:
            b.move()
            if b.x > self.width: self.bullets.remove(b)

        for obj in self.obstacles[:]:
            # ### [OOP] 多型行為 (Polymorphic Behavior)
            # 這裡呼叫 obj.move() 或 obj.draw() 時，
            # 程式不需要檢查 obj 是仙人掌還是鳥，
            # 物件自己知道該怎麼移動、怎麼畫。
            obj.move(self.game_speed)
            
            hit_by_bullet = False
            for b in self.bullets[:]:
                # ### [OOP] 父類別方法複用
                # collides_with 是定義在 GameObject 中的，所有物件都能用。
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
                # ### [OOP] 類型檢查 (Type Checking)
                # 雖然通常用多型，但偶爾需要判斷特定類型 (isinstance) 來執行特殊邏輯 (補血)。
                if isinstance(obj, HealthPack):
                    if self.dino.heal():
                        self.particles.emit(self.dino.x, self.dino.y, HEART_RED, 10)
                    self.obstacles.remove(obj)
                    continue 
                
                # ### [OOP] 封裝方法的應用
                # 不直接寫 self.dino.hp -= 1，而是呼叫 take_damage()，
                # 確保無敵時間邏輯被正確執行。
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
        
        # ### [OOP] 多型繪圖
        # 遍歷所有障礙物，每個物件呼叫自己的 draw()。
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