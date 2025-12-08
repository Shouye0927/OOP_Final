'''
Gym Environment for Simple Dino Run
'''
import gymnasium as gym
from gymnasium import spaces
from gymnasium.envs.registration import register
import warehouse_robot as wr
import numpy as np

register(
    id='dino-run-v0', # 修改 ID 避免混淆
    entry_point='oop_project_env:DinoRunEnv',
)

class DinoRunEnv(gym.Env):
    metadata = {"render_modes": ["human"], 'render_fps': 30}

    def __init__(self, render_mode=None):
        self.render_mode = render_mode
        self.game = wr.DinoGame()
        
        # Action: 0=跑, 1=跳
        self.action_space = spaces.Discrete(2)

        # Observation: [恐龍Y高度, 最近障礙物距離X, 最近障礙物高度Y]
        # 用無限大作為邊界，因為距離可能很遠
        self.observation_space = spaces.Box(
            low=np.array([0, 0, 0]), 
            high=np.array([1000, 1000, 1000]), 
            dtype=np.float32
        )

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.game.reset(seed=seed)
        obs = self._get_obs()
        if self.render_mode == 'human':
            self.game.render()
        return obs, {}

    def step(self, action):
        game_action = wr.Action(action)
        _, is_done = self.game.step(game_action)

        reward = 1 # 活著就給分
        if is_done:
            reward = -10 # 死了扣分

        obs = self._get_obs()
        if self.render_mode == 'human':
            self.game.render()

        return obs, reward, is_done, False, {}

    def _get_obs(self):
        # 找出最近的一個障礙物
        dist = 999
        obs_y = 0
        
        if self.game.obstacles:
            # 找到第一個 X > 恐龍X 的障礙物
            for obj in self.game.obstacles:
                if obj.x > self.game.dino.x:
                    dist = obj.x - self.game.dino.x
                    obs_y = obj.y
                    break
        
        return np.array([self.game.dino.y, dist, obs_y], dtype=np.float32)

    def render(self):
        self.game.render()

if __name__=="__main__":
    # 測試 AI 隨機跳
    env = gym.make('dino-run-v0', render_mode='human')
    obs = env.reset()[0]
    
    for _ in range(500):
        # 10% 機率跳，不然一直跑
        action = 1 if np.random.rand() < 0.1 else 0
        obs, reward, terminated, _, _ = env.step(action)
        if terminated:
            env.reset()