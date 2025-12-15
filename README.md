

This repository contains the final group project for the Object-Oriented Programming (OOP) course. It integrates **Reinforcement Learning (RL)** concepts with **OOP principles** across three distinct parts: solving Classic Control problems, tuning parameters for Frozen Lake, and designing a custom game environment ("Dino Fighter Ultimate") compatible with Gymnasium.

## Group Members

| Student ID | Name |
| :--- | :--- |
| **[B124020034]** | **[蔡承家]** |
| **[Student ID]** | **[Name]** |
| **[Student ID]** | **[Name]** |
| **[Student ID]** | **[Name]** |

---

## 🛠️ Installation & Setup

This project requires **Python 3.x** and the **Gymnasium** library.

### 1. Set up a Virtual Environment (Recommended)
```bash
# Create a virtual environment
python -m venv .venv

# Activate the virtual environment
# Windows:
.venv\Scripts\activate
# Mac/Linux:
source .venv/bin/activate

### 2\. Install Dependencies

Install the required packages, including Gymnasium (with classic control support), Pygame, and NumPy.

```bash
pip install "gymnasium[classic_control]"
pip install gymnasium[box2d]
pip install numpy matplotlib pygame
```

-----

## 📂 Part 1: Mountain Car (Q-Learning)

In this part, we use the **Q-Learning** algorithm to solve the classic Mountain Car problem. The continuous state space (position and velocity) is discretized to allow the Q-table to learn the optimal policy for driving the car up the hill.

### How to Run

```bash
# Train the agent (Default: 5000 episodes)
python part1/mountain_car.py --train --episodes 5000

# Evaluate and render the trained agent
python part1/mountain_car.py --render --episodes 10
```

-----

## ❄️ Part 2: Frozen Lake

The goal of this part is to tune the hyperparameters of a Q-Learning agent to achieve a **consistent success rate \> 0.70** on the Frozen Lake 8x8 map (Slippery).

### Methodology

We tuned the following parameters without changing the number of episodes or steps:

  * **`min_exploration_rate`**: Adjusted to ensure the agent continues to explore slightly even in late stages.
  * **`epsilon_decay_rate`**: Tuned to balance exploration (trying new paths) and exploitation (using the best-known path).

### How to Run

Running the script will perform training and then evaluate the agent's success rate. It also generates a training curve (`frozen_lake8x8.png`).

```bash
python part2/frozen_lake.py
```

### Results

  * **Final Success Rate**: `XX.XX%` (Replace with your actual result from the console output)
  * **Convergence Plot**: See `frozen_lake8x8.png`

-----

## 🦖 Part 3: Dino Fighter Ultimate (OOP Project)

This is the core of our project. We designed a custom side-scrolling shooter game, **Dino Fighter Ultimate**, using `pygame`. The project is structured using strict **Object-Oriented Programming (OOP)** principles and includes a wrapper to make it compatible with Gymnasium for RL training.

### 🎮 Game Controls (Human Mode)

  * **W** : Jump
  * **F**: Shoot (Consumes ammo)
  * **S**: Fast Drop(When jump)

### 🏗️ OOP Design Principles

We applied the four pillars of OOP to ensure modularity and extensibility:

#### 1\. Inheritance

We defined a base class `GameObject` that handles common properties like position (`x, y`), dimensions (`w, h`), and collision detection (`collides_with`).

  * **Parent Class**: `GameObject`
  * **Child Classes**: `Dino`, `Bullet`, `Obstacle` (which is further inherited by `Cactus`, `Bird`, `Bat`, `HealthPack`).
  * **Benefit**: Reduces code duplication. All objects automatically inherit collision logic.

#### 2\. Polymorphism

Different objects override standard methods to exhibit unique behaviors.

  * **`draw(surface)`**: The `Dino` class draws a character with eyes, while `Bullet` draws a rounded rectangle, and `Bird`/`Bat` use polygon drawing for complex shapes.
  * **`move()`**: `Bullet` moves to the right, while `Obstacle` subclasses move to the left. The game loop calls `obj.move()` without needing to know the specific type of object.

#### 3\. Encapsulation

Internal states are protected and modified only through specific methods.

  * **Health Management**: The `Dino` class encapsulates `hp` and `invincible_timer`. External code cannot modify HP directly; it must call `dino.take_damage()`, which internally checks if the dinosaur is currently invincible.
  * **Healing**: The `heal()` method ensures HP never exceeds `max_hp`.

#### 4\. Composition & Abstraction

  * **Composition**: The `DinoGame` class acts as a container that composes the `UIManager` (handling HUD) and `ParticleSystem` (handling visual effects).
  * **Abstraction**: The `DinoEnv` class abstracts the entire game into a Gym-compliant environment (`reset`, `step`, `render`), hiding the complex game loop from the RL agent.

### 🤖 RL Environment (Gym Wrapper)

We wrapped the game in a custom Gym environment (`DinoEnv`) defined in `oop_project_env.py`.

  * **Action Space**: `Discrete(4)` (RUN, JUMP, SHOOT, DROP)
  * **Observation Space**: `Box(5)` containing:
    1.  Dino Y-position
    2.  Dino HP
    3.  Ammo count
    4.  Distance to nearest obstacle
    5.  Type of nearest obstacle

### How to Run

**1. Play the Game (Human Mode)**

```bash
python part3/dino.py
```

**2. Run the RL Agent (Random Agent Test)**

```bash
python part3/oop_project_env.py
```

-----

## 📂 Project Structure

```text
OOP_Final-main/
├── part1/
│   ├── mountain_car.py      # Q-Learning implementation for Mountain Car
│   └── mountain_car.pkl     # Saved Q-table
├── part2/
│   ├── frozen_lake.py       # Tuning script for Frozen Lake
│   └── frozen_lake8x8.png   # Resulting success rate plot
├── part3/
│   ├── dino.py              # Main Game Core (OOP Implementation)
│   ├── oop_project_env.py   # Custom Gymnasium Wrapper
│   ├── Dino_UML.png         # UML Class Diagram
│   └── sprites/             # Game assets (images)
├── README.md                # Project Documentation
└── requirements.txt         # Dependencies
```

```
```
