import gymnasium as gym
import numpy as np
import matplotlib.pyplot as plt
import pickle


def print_success_rate(rewards_per_episode):
    """Calculate and print the success rate of the agent."""
    total_episodes = len(rewards_per_episode)
    success_count = np.sum(rewards_per_episode)
    success_rate = (success_count / total_episodes) * 100
    print(f"✅ Success Rate: {success_rate:.2f}% ({int(success_count)} / {total_episodes} episodes)")
    return success_rate

def run(episodes, is_training=True, render=False):

    env = gym.make('FrozenLake-v1', map_name="8x8", is_slippery=True, render_mode='human' if render else None)

    if(is_training):
        q = np.zeros((env.observation_space.n, env.action_space.n)) # init a 64 x 4 array
    else:
        f = open('frozen_lake8x8.pkl', 'rb')
        q = pickle.load(f)
        f.close()

    learning_rate_a = 0.03 # alpha or learning rate
    discount_factor_g = 0.99 # gamma or discount rate. Near 0: more weight/reward placed on immediate state. Near 1: more on future state.
    epsilon = 1         # 1 = 100% random actions
    epsilon_decay_rate = 0.0000925        # epsilon decay rate. 1/0.0001 = 10,000
    rng = np.random.default_rng()   # random number generator

    rewards_per_episode = np.zeros(episodes)
    best_success_count = 0

    for i in range(episodes):
        state = env.reset()[0]  # states: 0 to 63, 0=top left corner,63=bottom right corner
        terminated = False      # True when fall in hole or reached goal
        truncated = False       # True when actions > 200

        while(not terminated and not truncated):
            if is_training and rng.random() < epsilon:
                action = env.action_space.sample() # actions: 0=left,1=down,2=right,3=up
            else:
                action = np.argmax(q[state,:])

            new_state,reward,terminated,truncated,_ = env.step(action)

            # 判斷是否掉進洞裡：
            # 1. terminated 為 True 代表遊戲結束 (可能是贏也可能是輸)
            # 2. reward == 0 代表沒拿到分 (排除掉贏的情況，因為贏的話 reward 會是 1)
            if terminated and reward == 0:
                reward = -0.2

            if is_training:
                q[state,action] = q[state,action] + learning_rate_a * (
                    reward + discount_factor_g * np.max(q[new_state,:]) - q[state,action]
                )

            state = new_state

        epsilon = max(epsilon - epsilon_decay_rate, 0)

        if(epsilon==0):
            learning_rate_a = 0.0001

        if reward == 1:
            rewards_per_episode[i] = 1

        if is_training and (i + 1) % 1000 == 0:
            successes = np.sum(rewards_per_episode[max(0, i-999):i+1])
            print(f"Episode {i+1}/{episodes}, Epsilon: {epsilon:.4f}, Successes (last 1000): {int(successes)}")

            #條 learning rate 反而讓後面學不上去，這個沒甚麼用
            # if successes > 620:
            #     learning_rate_a *= 0.5
            #     print(f"Success rate > 50%, adjusting learning rate to {learning_rate_a:.5f}")

        # 修改：將評估區間從 100 拉長到 500，避免因為短期運氣好 (Variance) 而存到虛高的模型
        if is_training and i >= 500:
            current_success_count = np.sum(rewards_per_episode[i-499:i+1])
            
            # 備份機制：如果最近 500 次成功超過 300 次 (60%)，且比之前的紀錄好，就先存起來
            if current_success_count > best_success_count and current_success_count >= 300:
                best_success_count = current_success_count
                with open('frozen_lake8x8.pkl', 'wb') as f:
                    pickle.dump(q, f)
                print(f"New best model saved! Success count (last 500): {int(best_success_count)}")

            if current_success_count >= 400: # 80% of 500
                print(f"Training stopped early at episode {i+1}: Last 500 episodes reached 80% success rate.")
                break

    env.close()

    sum_rewards = np.zeros(episodes)
    for t in range(episodes):
        sum_rewards[t] = np.sum(rewards_per_episode[max(0, t-100):(t+1)])
    plt.plot(sum_rewards)
    plt.savefig('frozen_lake8x8.png')
    
    if is_training == False:
        print(print_success_rate(rewards_per_episode))

    # 註解掉最後的強制存檔，避免「最後的結果」(可能較差) 覆蓋掉中間存的「最佳結果」
    # if is_training:
    #     f = open("frozen_lake8x8.pkl","wb")
    #     pickle.dump(q, f)
    #     f.close()

if __name__ == '__main__':
    mode = input("Input 0 for training, 1 for testing: ")
    if mode == '0':
        run(15000, is_training=True, render=False)
    elif mode == '1':
        run(1000, is_training=False, render=False)
