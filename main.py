from tkinter import *
from tkinter import messagebox
import threading
import json
import pyaudio
from vosk import Model, KaldiRecognizer, SetLogLevel

SetLogLevel(-1)

model_path = r"C:\Users\dahq2\OneDrive\Documents\outlook danah\OneDrive\Desktop\python!\XO project\vosk-model-small-en-us-0.15\vosk-model-small-en-us-0.15"
board = [["" for _ in range(3)] for _ in range(3)]
buttons = []

root = Tk()
root.title("Voice + AI XO Game")
root.resizable(False, False)

current_player = "X"

def draw_board():
    for r in range(3):
        row = []
        for c in range(3):
            b = Button(root, text="", font=('Helvetica', 32), height=2, width=5,
                       command=lambda row=r, col=c: player_move(row, col))
            b.grid(row=r, column=c)
            row.append(b)
        buttons.append(row)

def player_move(row, col):
    global current_player
    if board[row][col] == "" and current_player == "X":
        board[row][col] = "X"
        buttons[row][col].config(text="X")

        winner = check_winner()
        if winner:
            messagebox.showinfo("Game Over", f"{winner} wins!")
            reset_game()
            return
        elif check_draw():
            messagebox.showinfo("Game Over", "Draw!")
            reset_game()
            return

        current_player = "O"
        root.after(300, ai_move)

def ai_move():
    global current_player
    best_score = float('-inf')
    best_move = None

    for r in range(3):
        for c in range(3):
            if board[r][c] == "":
                board[r][c] = "O"
                score = minimax(board, 0, False)
                board[r][c] = ""
                if score > best_score:
                    best_score = score
                    best_move = (r, c)

    if best_move:
        r, c = best_move
        board[r][c] = "O"
        buttons[r][c].config(text="O")

    winner = check_winner()
    if winner:
        messagebox.showinfo("Game Over", f"{winner} wins!")
        reset_game()
        return
    elif check_draw():
        messagebox.showinfo("Game Over", "Draw!")
        reset_game()
        return

    current_player = "X"

def minimax(board, depth, is_max):
    winner = check_winner()
    if winner == "O":
        return 1
    elif winner == "X":
        return -1
    elif check_draw():
        return 0

    if is_max:
        best = float('-inf')
        for r in range(3):
            for c in range(3):
                if board[r][c] == "":
                    board[r][c] = "O"
                    score = minimax(board, depth+1, False)
                    board[r][c] = ""
                    best = max(score, best)
        return best
    else:
        best = float('inf')
        for r in range(3):
            for c in range(3):
                if board[r][c] == "":
                    board[r][c] = "X"
                    score = minimax(board, depth+1, True)
                    board[r][c] = ""
                    best = min(score, best)
        return best

def check_winner():
    for r in range(3):
        if board[r][0] == board[r][1] == board[r][2] != "":
            return board[r][0]
    for c in range(3):
        if board[0][c] == board[1][c] == board[2][c] != "":
            return board[0][c]
    if board[0][0] == board[1][1] == board[2][2] != "":
        return board[0][0]
    if board[0][2] == board[1][1] == board[2][0] != "":
        return board[0][2]
    return None

def check_draw():
    return all(all(cell != "" for cell in row) for row in board)

def reset_game():
    global board, current_player
    board = [["" for _ in range(3)] for _ in range(3)]
    current_player = "X"
    for r in range(3):
        for c in range(3):
            buttons[r][c].config(text="")

# VOICE COMMANDS
command_to_position = {
    "top left": (0, 0), "top": (0, 1), "top right": (0, 2),
    "left": (1, 0), "center": (1, 1), "right": (1, 2),
    "bottom left": (2, 0), "bottom": (2, 1), "bottom right": (2, 2)
}

def recognize_voice_move():
    global current_player
    if current_player != "X":
        return

    model = Model(model_path)
    recognizer = KaldiRecognizer(model, 16000)
    p = pyaudio.PyAudio()

    try:
        stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000,
                        input=True, frames_per_buffer=8192)
        stream.start_stream()
        print("Say your move...")

        while True:
            data = stream.read(4096, exception_on_overflow=False)
            if recognizer.AcceptWaveform(data):
                speech = json.loads(recognizer.Result())["text"]
                print("You said:", speech)
                if speech in command_to_position:
                    r, c = command_to_position[speech]
                    player_move(r, c)
                    break
                else:
                    print("Unrecognized.")
                    messagebox.showerror("Voice Error", "Try again.")
                    break
    except Exception as e:
        print("Voice Error:", e)
    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()

def start_voice_thread():
    threading.Thread(target=recognize_voice_move).start()

voice_btn = Button(root, text="🎤 Say Move", font=('Helvetica', 16), command=start_voice_thread)
voice_btn.grid(row=3, column=0, columnspan=3, pady=10)

draw_board()
root.mainloop()
