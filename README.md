# 🧟 Whack a Zombie

A simple arcade-style **Whack-a-Mole** game implemented in **Python + Pygame**, where you use a hammer to whack zombies popping out of holes before time runs out.  

---

## 🎮 How to Play

- Run the game with:
  ```bash
  python game.py
  ```

- **Controls:**
  - **Mouse Left Click** → Swing hammer & hit zombies.
  - **P** → Pause / Resume game.
  - **M** → Mute / Unmute background music (hit sound still plays).
  - **Quit** → Close the window.

- **Game Flow:**
  1. Start from the intro screen, click **START**.
  2. Zombies will spawn randomly from 6 holes.
  3. Hit zombies before they disappear to gain points.
     - Green zombie = +1 point  
     - Red zombie = +2 points
  4. If you miss a zombie, your **miss counter** increases.
  5. When the timer reaches 0, the game ends.
  6. You can choose **Play Again** or **Go Back to Intro**.

---

## 🕹 Features

- **6 spawn locations** with background art.
- **Animated zombies** (idle, rising, hit, falling).
- **Hit detection** using mouse clicks.
- **Score HUD** with Hits, Misses, Accuracy, and Timer.
- **Pause Menu** with Continue / Go Back.
- **Background music** + hit sound effect.
- **Mute/Unmute toggle** for music (with key `M`).

---

## 📊 Scoring System

- Green Zombie → **+1 point**
- Red Zombie → **+2 points**
- Missed zombie → increases miss counter.

Accuracy is calculated as:

\[
\text{Accuracy} = \frac{\text{Hits}}{\text{Hits + Misses}} \times 100\%
\]  

---

## 🛠 Installation

1. Install Python (>= 3.8).
2. Install Pygame:
   ```bash
   pip install -r requirements.txt
   ```
3. Clone or download this repository.
4. Run the game:
   ```bash
   python game.py
   ```

---

## 🎵 Assets

- Backgrounds, sprites, and sounds are provided in the `assets/` and `images/` folders.
- All assets are resized and optimized for 1100×800 resolution.
- Zombie sprites (green/red) include idle & hit animations.
- Hammer cursor replaces default system cursor.

---

## 👨‍💻 Author

Developed by **Le Quang Thanh & Doan The Anh**  
For **Assignment 1 – Game Programming Course (Whack-a-Zombie)**.
