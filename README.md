# 🌌 Celestial Body Simulator (Pygame)

This project is a real-time simulator of gravitational interactions between celestial bodies, built with **Python**, **Pygame**, **NumPy** and **PyOpenGL**

Originally created as a personal project to explore orbital dynamics and interactive physics simulation, it models how planets, stars, and other objects attract each other using **Newtonian gravitational laws** — complete with custom rendering and live control features.

---

## ✨ Features

- Accurate gravity-based movement using Newton's laws of gravitation
- Real-time rendering of velocity, acceleration, and orbital motion
- Full control to pause/resume, interact, and reset - in game
- Adjustable parameters for mass, position, and velocity - code
- Shows oribital period - calculated using Keplers Law
- Now in 3D

---

## 🧪 Technologies Used

- 🎮 `pygame` – for rendering and interaction
- 🧠 `numpy` – for numerical physics calculations
- 📈 `matplotlib` (future use) – for trajectory or energy graphs
- 🪩 `PyOpenGL` - for making it 3D

---

## 🚀 Installation

### 1. Create a virtual environment (recommended)

```bash
python -m venv venv
source venv/bin/activate      # On Windows: venv\Scripts\activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

---

## 🎮 Usage

Run the simulation with:

```bash
python main.py
```

### Controls

- `SPACE` – Pause/Resume simulation  
- `ESC` – Exit simulation  

---

## 🧠 Future Ideas

- Add object trails or orbital history paths
- Mouse drag to assign velocity vector to new body
- Allow a user to place down objects with params live in the game
- Use `matplotlib` for live graphing in a secondary window

---

## ✍️ Author

**Mikolaj Mikuliszyn**  
Personal Physics + Simulation Projects  
🔗 [GitHub Profile](https://github.com/miki-przygoda)

---

## 📝 License

This project is shared under the MIT License.  
Use, modify, or adapt freely for educational and experimental purposes.