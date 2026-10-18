"""
Snake Game in Python
Built with Python's standard library ('turtle', 'time', 'random').
No external dependencies required.

Controls:
  - Arrow Keys or W / A / S / D : Change direction
  - Spacebar                    : Pause / Resume (or Restart on Game Over)
  - R                           : Restart game anytime
  - Q or Esc                    : Exit game
"""

import turtle
import time
import random

# ================= Configuration =================
WINDOW_WIDTH = 8000
WINDOW_HEIGHT = 680
ARENA_SIZE = 560  # Playable square area: -280 to +280 on X and -300 to +260 on Y
GRID_SIZE = 20
INITIAL_DELAY = 0.11
MIN_DELAY = 0.04
SPEED_INCREMENT = 0.0025

# Color Palette (Dark Theme)
COLOR_BG = "#0f172a"          # Slate 900
COLOR_ARENA_BG = "#1e293b"    # Slate 800
COLOR_BORDER = "#334155"      # Slate 700
COLOR_HEAD = "#22c55e"        # Emerald green
COLOR_BODY = "#16a34a"        # Deep emerald green
COLOR_FOOD = "#f43f5e"        # Rose red
COLOR_TEXT = "#f8fafc"        # Slate 50
COLOR_MUTED = "#94a3b8"       # Slate 400
COLOR_ACCENT = "#38bdf8"      # Sky blue

# Arena Bounds
ARENA_LEFT = -280
ARENA_RIGHT = 280
ARENA_BOTTOM = -300
ARENA_TOP = 260

# ================= Game State =================
score = 0
high_score = 0
delay = INITIAL_DELAY
is_paused = False
is_game_over = False

current_direction = "stop"
next_direction = "stop"
segments = []

# ================= Screen Setup =================
screen = turtle.Screen()
screen.title("Python Snake Game")
screen.bgcolor(COLOR_BG)
screen.setup(width=WINDOW_WIDTH, height=WINDOW_HEIGHT)
screen.tracer(0)

# ================= Draw Arena Border =================
border_pen = turtle.Turtle()
border_pen.speed(0)
border_pen.hideturtle()
border_pen.penup()
border_pen.color(COLOR_BORDER, COLOR_ARENA_BG)
border_pen.pensize(3)
border_pen.goto(ARENA_LEFT, ARENA_BOTTOM)
border_pen.pendown()
border_pen.begin_fill()
for _ in range(2):
    border_pen.forward(ARENA_RIGHT - ARENA_LEFT)
    border_pen.left(90)
    border_pen.forward(ARENA_TOP - ARENA_BOTTOM)
    border_pen.left(90)
border_pen.end_fill()
border_pen.penup()

# ================= Game Objects =================
# Snake Head
head = turtle.Turtle()
head.speed(0)
head.shape("square")
head.color(COLOR_HEAD)
head.penup()
head.goto(0, 0)

# Food
food = turtle.Turtle()
food.speed(0)
food.shape("circle")
food.color(COLOR_FOOD)
food.penup()
food.shapesize(0.9, 0.9)


def get_random_food_position():
    """Returns random grid-aligned (x, y) coordinates within the arena."""
    min_gx = (ARENA_LEFT + GRID_SIZE) // GRID_SIZE
    max_gx = (ARENA_RIGHT - GRID_SIZE) // GRID_SIZE
    min_gy = (ARENA_BOTTOM + GRID_SIZE) // GRID_SIZE
    max_gy = (ARENA_TOP - GRID_SIZE) // GRID_SIZE

    x = random.randint(min_gx, max_gx) * GRID_SIZE
    y = random.randint(min_gy, max_gy) * GRID_SIZE
    return x, y


def place_food():
    """Places food at an unoccupied position inside the arena."""
    while True:
        fx, fy = get_random_food_position()
        if head.distance(fx, fy) < 15:
            continue
        if any(seg.distance(fx, fy) < 15 for seg in segments):
            continue
        food.goto(fx, fy)
        break


place_food()

# Scoreboard Pen
score_pen = turtle.Turtle()
score_pen.speed(0)
score_pen.hideturtle()
score_pen.penup()
score_pen.color(COLOR_TEXT)


def update_scoreboard():
    """Draws score header at the top of the screen."""
    score_pen.clear()
    score_pen.goto(0, 285)
    score_pen.write(
        f"Score: {score}     |     High Score: {high_score}",
        align="center",
        font=("Segoe UI", 15, "bold")
    )


# Message Pen (Game Over / Pause notices)
msg_pen = turtle.Turtle()
msg_pen.speed(0)
msg_pen.hideturtle()
msg_pen.penup()


def show_game_over_screen():
    """Renders Game Over banner and restart instructions."""
    msg_pen.clear()
    msg_pen.goto(0, 30)
    msg_pen.color("#ef4444")
    msg_pen.write("GAME OVER", align="center", font=("Segoe UI", 28, "bold"))

    msg_pen.goto(0, -15)
    msg_pen.color(COLOR_TEXT)
    msg_pen.write(f"Final Score: {score}", align="center", font=("Segoe UI", 14, "normal"))

    msg_pen.goto(0, -50)
    msg_pen.color(COLOR_ACCENT)
    msg_pen.write("Press SPACE or R to Play Again", align="center", font=("Segoe UI", 12, "bold"))


def show_pause_screen(paused: bool):
    """Renders pause banner."""
    msg_pen.clear()
    if paused:
        msg_pen.goto(0, 20)
        msg_pen.color("#facc15")
        msg_pen.write("PAUSED", align="center", font=("Segoe UI", 26, "bold"))

        msg_pen.goto(0, -25)
        msg_pen.color(COLOR_MUTED)
        msg_pen.write("Press SPACE to Resume", align="center", font=("Segoe UI", 13, "normal"))


# ================= Control Handlers =================
def go_up():
    global next_direction
    if current_direction != "down" and not is_paused and not is_game_over:
        next_direction = "up"


def go_down():
    global next_direction
    if current_direction != "up" and not is_paused and not is_game_over:
        next_direction = "down"


def go_left():
    global next_direction
    if current_direction != "right" and not is_paused and not is_game_over:
        next_direction = "left"


def go_right():
    global next_direction
    if current_direction != "left" and not is_paused and not is_game_over:
        next_direction = "right"


def toggle_pause():
    global is_paused
    if is_game_over:
        restart_game()
        return
    if current_direction == "stop" and next_direction == "stop":
        return
    is_paused = not is_paused
    show_pause_screen(is_paused)


def restart_game():
    global score, delay, is_game_over, is_paused
    global current_direction, next_direction, segments

    msg_pen.clear()

    # Clear old segments off-screen
    for seg in segments:
        seg.goto(2000, 2000)
    segments.clear()

    # Reset head
    head.goto(0, 0)
    current_direction = "stop"
    next_direction = "stop"

    # Reset states
    score = 0
    delay = INITIAL_DELAY
    is_game_over = False
    is_paused = False

    update_scoreboard()
    place_food()


def quit_game():
    try:
        turtle.bye()
    except Exception:
        pass


def move_head():
    """Moves head coordinates according to current direction."""
    if current_direction == "up":
        head.sety(head.ycor() + GRID_SIZE)
    elif current_direction == "down":
        head.sety(head.ycor() - GRID_SIZE)
    elif current_direction == "left":
        head.setx(head.xcor() - GRID_SIZE)
    elif current_direction == "right":
        head.setx(head.xcor() + GRID_SIZE)


# ================= Event Listeners =================
screen.listen()

# Arrow Keys
screen.onkeypress(go_up, "Up")
screen.onkeypress(go_down, "Down")
screen.onkeypress(go_left, "Left")
screen.onkeypress(go_right, "Right")

# WASD
screen.onkeypress(go_up, "w")
screen.onkeypress(go_up, "W")
screen.onkeypress(go_down, "s")
screen.onkeypress(go_down, "S")
screen.onkeypress(go_left, "a")
screen.onkeypress(go_left, "A")
screen.onkeypress(go_right, "d")
screen.onkeypress(go_right, "D")

# Game Control Keys
screen.onkeypress(toggle_pause, "space")
screen.onkeypress(restart_game, "r")
screen.onkeypress(restart_game, "R")
screen.onkeypress(quit_game, "Escape")
screen.onkeypress(quit_game, "q")
screen.onkeypress(quit_game, "Q")

update_scoreboard()

# Initial instructional prompt
msg_pen.goto(0, -20)
msg_pen.color(COLOR_MUTED)
msg_pen.write("Press Arrow Keys or WASD to Start", align="center", font=("Segoe UI", 12, "italic"))

# ================= Main Game Loop =================
try:
    while True:
        screen.update()

        if is_paused or is_game_over:
            time.sleep(0.04)
            continue

        # Wait until player gives first directional input
        if current_direction == "stop" and next_direction == "stop":
            time.sleep(0.04)
            continue
        elif current_direction == "stop" and next_direction != "stop":
            msg_pen.clear()

        # Update actual movement direction for this tick
        current_direction = next_direction

        # Save previous head position for segment trailing
        prev_head_x = head.xcor()
        prev_head_y = head.ycor()

        # Move snake head forward
        move_head()

        # Check arena wall collision
        if (
            head.xcor() >= ARENA_RIGHT
            or head.xcor() <= ARENA_LEFT
            or head.ycor() >= ARENA_TOP
            or head.ycor() <= ARENA_BOTTOM
        ):
            is_game_over = True
            show_game_over_screen()
            continue

        # Check self-collision
        hit_self = False
        for seg in segments:
            if seg.distance(head) < 12:
                hit_self = True
                break

        if hit_self:
            is_game_over = True
            show_game_over_screen()
            continue

        # Check food collision
        if head.distance(food) < 15:
            # Create and attach a new body segment
            new_seg = turtle.Turtle()
            new_seg.speed(0)
            new_seg.shape("square")
            new_seg.color(COLOR_BODY)
            new_seg.penup()
            new_seg.goto(2000, 2000)  # Off-screen until placed in segment loop
            segments.append(new_seg)

            # Update score
            score += 10
            if score > high_score:
                high_score = score
            update_scoreboard()

            # Increase difficulty speed
            delay = max(MIN_DELAY, delay - SPEED_INCREMENT)

            # Relocate food
            place_food()

        # Move body segments to follow each other
        if len(segments) > 0:
            for i in range(len(segments) - 1, 0, -1):
                segments[i].goto(segments[i - 1].xcor(), segments[i - 1].ycor())
            segments[0].goto(prev_head_x, prev_head_y)

        time.sleep(delay)

except (turtle.Terminator, Exception):
    # Closes cleanly when window is dismissed
    pass
