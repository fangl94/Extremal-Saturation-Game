# Extremal-Saturation-Game

This repository contains the code for two small games based on the theorems and results from my master's thesis.

## Games

### Extremal Game

In the Extremal Game, the player's objective is to avoid creating a convex n-gon. To win, the player must add points to the board without forming a convex n-gon. The winning condition is to add 2^(n-2) points while maintaining a non-convex configuration. However, be cautious: if you create a line by connecting three points, you'll lose.

### Saturation Game

In the Saturation Game, players aim to avoid creating a convex m-gon. They start with a random point set that doesn't contain any convex m-gon. The goal is to add as many points as possible to prevent the formation of a convex m-gon. The winning and losing conditions are the same as in the Extremal Game.

## Setup

These games are built using Flask. To run the games locally, execute the following command in your terminal:

```bash
python3 app.py
```

You'll need to install Flask if you haven't already. Use the following command to install it:

```bash
pip install Flask
```

After running the app, visit your local host at http://127.0.0.1:5000, or follow the instructions provided by your terminal to start playing the games.
