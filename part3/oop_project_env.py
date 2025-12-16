'''
Gym Wrapper for Dino Fighter Ultimate
檔案名稱: oop_project_env.py
'''
import gymnasium as gym
from gymnasium import spaces
from gymnasium.envs.registration import register
import dino as wr # 匯入你的遊戲檔案
import numpy as np

# 註冊環境 ID
register(
    id='dino-fighter-v0',
    entry_point='oop_project_env:DinoEnv', # 這裡一定要對應下面的 class 名稱
)

class DinoEnv(gym.Env):
    metadata = {"render_modes": ["human"], 'render_fps': 30}

    def __init__(self, render_mode=None):
        self.render_mode = render_mode
        self.game = wr.DinoGame()
        
        # Action: 0=RUN, 1=JUMP, 2=SHOOT, 3=DROP
        self.action_space = spaces.Discrete(4)

        # Observation: [Dino Y, Dino HP, Ammo, Nearest Obstacle Dist, Nearest Obstacle Type]
        self.observation_space = spaces.Box(
            low=np.array([0, 0, 0, 0, 0]), 
            high=np.array([1000, 3, 3, 1000, 5]), 
            dtype=np.float32
        )

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        
        # 1. 指揮遊戲本體重置
        self.game.reset(seed=seed)
        self.game.state = 'RUNNING' # AI 模式下直接開始
        obs = self._get_obs()
        if self.render_mode == 'human':
            self.game.render()
        return obs, {}

    def step(self, action):
        # 1. [翻譯動作] AI 給數字 (例如 1)，我轉成 Enum (Action.JUMP)
        game_action = list(wr.Action)[action]
        # 2. [執行遊戲] 讓遊戲跑一幀 (Frame)
        # 這裡用到了我設計的 Game Engine
        _, is_done = self.game.step(game_action)

        # 3. [設計獎勵結構 (Reward Structure)]
        # 活著就 +1 分 (鼓勵生存)
        reward = 1
        if is_done: reward = -100
        # 死掉就 -100 分 (懲罰死亡)
        obs = self._get_obs()
        if self.render_mode == 'human':
            self.game.render()
        # 5. 回傳 Gymnasium 標準格式
        # (新狀態, 獎勵, 是否結束, 被截斷, 資訊)
        return obs, reward, is_done, False, {}

    def _get_obs(self):
        # 找出最近的一個障礙物
        dist = 999
        obs_type = 0 # 0=None, 1=Cactus, 2=Bird, 3=Bat, 4=Heal
        
        if self.game.obstacles:
            # 找到第一個在恐龍右邊的障礙物
            for obj in self.game.obstacles:
                if obj.x > self.game.dino.x:
                    dist = obj.x - self.game.dino.x
                    if isinstance(obj, wr.Cactus): obs_type = 1
                    elif isinstance(obj, wr.Bird): obs_type = 2
                    elif isinstance(obj, wr.Bat): obs_type = 3
                    elif isinstance(obj, wr.HealthPack): obs_type = 4
                    break
        
        return np.array([
            self.game.dino.y,
            self.game.dino.hp,
            3 - len(self.game.bullets),
            dist,
            obs_type
        ], dtype=np.float32)

    def render(self):
        self.game.render()

# AI 測試區 (Random Agent)
if __name__=="__main__":
    env = gym.make('dino-fighter-v0', render_mode='human')
    obs = env.reset()[0]
    
    print("AI Running Random Agent...")
    for _ in range(500):
        action = env.action_space.sample()
        obs, reward, terminated, _, _ = env.step(action)
        if terminated:
            env.reset()