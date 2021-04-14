import chess
import chess.polyglot
import chess.svg
import chess.pgn
import chess.engine
import traceback
from flask import Flask, Response, request, app
import webbrowser
import time
import sys
import threading

app = Flask(__name__)


def get_material_score():
    '''
    Calculates the material score on the board
    :param board: object representing the current game state
    :return: evaluation of material on board
    '''
    wp = len(board.pieces(chess.PAWN, chess.WHITE))
    bp = len(board.pieces(chess.PAWN, chess.BLACK))
    wn = len(board.pieces(chess.KNIGHT, chess.WHITE))
    bn = len(board.pieces(chess.KNIGHT, chess.BLACK))
    wb = len(board.pieces(chess.BISHOP, chess.WHITE))
    bb = len(board.pieces(chess.BISHOP, chess.BLACK))
    wr = len(board.pieces(chess.ROOK, chess.WHITE))
    br = len(board.pieces(chess.ROOK, chess.BLACK))
    wq = len(board.pieces(chess.QUEEN, chess.WHITE))
    bq = len(board.pieces(chess.QUEEN, chess.BLACK))

    material = 100 * (wp - bp) + 320 * (wn - bn) + 330 * (wb - bb) + 500 * (wr - br) + 900 * (wq - bq)
    return material


def get_piece_score():
    '''
    Calculates value of material positions on board
    :param board: object representing current game state
    :return: value representing positional score
    '''

    pawntable = [
        0, 0, 0, 0, 0, 0, 0, 0,
        5, 10, 10, -20, -20, 10, 10, 5,
        5, -5, -10, 0, 0, -10, -5, 5,
        0, 0, 0, 20, 20, 0, 0, 0,
        5, 5, 10, 25, 25, 10, 5, 5,
        10, 10, 20, 30, 30, 20, 10, 10,
        50, 50, 50, 50, 50, 50, 50, 50,
        0, 0, 0, 0, 0, 0, 0, 0]        # Table of pawn positional values
    knightstable = [
        -50, -40, -30, -30, -30, -30, -40, -50,
        -40, -20, 0, 5, 5, 0, -20, -40,
        -30, 5, 10, 15, 15, 10, 5, -30,
        -30, 0, 15, 20, 20, 15, 0, -30,
        -30, 5, 15, 20, 20, 15, 5, -30,
        -30, 0, 10, 15, 15, 10, 0, -30,
        -40, -20, 0, 0, 0, 0, -20, -40,
        -50, -40, -30, -30, -30, -30, -40, -50]     # table of knight positional values
    bishopstable = [
        -20, -10, -10, -10, -10, -10, -10, -20,
        -10, 5, 0, 0, 0, 0, 5, -10,
        -10, 10, 10, 10, 10, 10, 10, -10,
        -10, 0, 10, 10, 10, 10, 0, -10,
        -10, 5, 5, 10, 10, 5, 5, -10,
        -10, 0, 5, 10, 10, 5, 0, -10,
        -10, 0, 0, 0, 0, 0, 0, -10,
        -20, -10, -10, -10, -10, -10, -10, -20]     # table of knight positional values
    rookstable = [
        0, 0, 0, 5, 5, 0, 0, 0,
        -5, 0, 0, 0, 0, 0, 0, -5,
        -5, 0, 0, 0, 0, 0, 0, -5,
        -5, 0, 0, 0, 0, 0, 0, -5,
        -5, 0, 0, 0, 0, 0, 0, -5,
        -5, 0, 0, 0, 0, 0, 0, -5,
        5, 10, 10, 10, 10, 10, 10, 5,
        0, 0, 0, 0, 0, 0, 0, 0]       # table of knight positional values
    queenstable = [
        -20, -10, -10, -5, -5, -10, -10, -20,
        -10, 0, 0, 0, 0, 0, 0, -10,
        -10, 5, 5, 5, 5, 5, 0, -10,
        0, 0, 5, 5, 5, 5, 0, -5,
        -5, 0, 5, 5, 5, 5, 0, -5,
        -10, 0, 5, 5, 5, 5, 0, -10,
        -10, 0, 0, 0, 0, 0, 0, -10,
        -20, -10, -10, -5, -5, -10, -10, -20]      # table of knight positional values
    kingstable = [
        20, 30, 10, 0, 0, 10, 30, 20,
        20, 20, 0, 0, 0, 0, 20, 20,
        -10, -20, -20, -20, -20, -20, -20, -10,
        -20, -30, -30, -40, -40, -30, -30, -20,
        -30, -40, -40, -50, -50, -40, -40, -30,
        -30, -40, -40, -50, -50, -40, -40, -30,
        -30, -40, -40, -50, -50, -40, -40, -30,
        -30, -40, -40, -50, -50, -40, -40, -30]       # table of knight positional values

    pawnsq = sum([pawntable[i] for i in board.pieces(chess.PAWN, chess.WHITE)])
    pawnsq = pawnsq + sum([-pawntable[chess.square_mirror(i)]
                           for i in board.pieces(chess.PAWN, chess.BLACK)])
    knightsq = sum([knightstable[i] for i in board.pieces(chess.KNIGHT, chess.WHITE)])
    knightsq = knightsq + sum([-knightstable[chess.square_mirror(i)]
                               for i in board.pieces(chess.KNIGHT, chess.BLACK)])
    bishopsq = sum([bishopstable[i] for i in board.pieces(chess.BISHOP, chess.WHITE)])
    bishopsq = bishopsq + sum([-bishopstable[chess.square_mirror(i)]
                               for i in board.pieces(chess.BISHOP, chess.BLACK)])
    rooksq = sum([rookstable[i] for i in board.pieces(chess.ROOK, chess.WHITE)])
    rooksq = rooksq + sum([-rookstable[chess.square_mirror(i)]
                           for i in board.pieces(chess.ROOK, chess.BLACK)])
    queensq = sum([queenstable[i] for i in board.pieces(chess.QUEEN, chess.WHITE)])
    queensq = queensq + sum([-queenstable[chess.square_mirror(i)]
                             for i in board.pieces(chess.QUEEN, chess.BLACK)])
    kingsq = sum([kingstable[i] for i in board.pieces(chess.KING, chess.WHITE)])
    kingsq = kingsq + sum([-kingstable[chess.square_mirror(i)]
                           for i in board.pieces(chess.KING, chess.BLACK)])

    return pawnsq + knightsq + bishopsq + rooksq + queensq + kingsq


def evaluate():
    '''
    Evaluates the given board position
    :param board: object representing the current game state
    :return: evaluation of current state
    '''
    if board.is_checkmate():
        if board.turn:
            return -9999
        else:
            return 9999
    if board.is_stalemate():
        return 0
    if board.is_insufficient_material():
        return 0

    e = get_material_score() + get_piece_score()
    if board.turn:
        return e
    else:
        return -e


def quiesce(a, b):
    s = evaluate()
    if (s >= b):
        return b
    if (a < s):
        a = s

    for move in board.legal_moves:
        if board.is_capture(move):
            board.push(move)
            score = -quiesce(-b, -a)
            board.pop()

            if (score >= b):
                return b
            if (score > a):
                a = score
    return a


def alphabeta(a, b, depth):
    best = -9999
    if depth == 0:
        return quiesce(a, b)
    for m in board.legal_moves:
        board.push(m)
        score = -alphabeta(-b, -a, depth - 1)
        board.pop()
        if score >= b:
            return score
        if score > best:
            best = score
        if score > a:
            a = score
    return best


def dmove(depth):
    '''
    Generates a move
    :return: a move to play
    '''
    try:            # get moves from opening
        m = chess.polyglot.MemoryMappedReader("C:/Users/Catte/PycharmProjects/Chess/human.bin").weighted_choice(board).move
        return m
    except IndexError:         # off main line
        best = chess.Move.null()
        bv = -99999
        a = -100000
        b = 100000
        for m in board.legal_moves:
            board.push(m)
            print(m)
            boardValue = -alphabeta(-b, -a, depth-1)
            if boardValue > bv:
                bv = boardValue
                best = m
            if boardValue > a:
                a = boardValue
            board.pop()
        return best


def devmove():
    m = dmove(2)
    print(m)
    board.push(m)


@app.route("/")
def main():
    global count, board
    if count == 1:
        count += 1
    ret = '<html><head>'
    ret += '<style>input {font-size: 20px; } button { font-size: 20px; }</style>'
    ret += '</head><body>'
    ret += '<img width=510 height=510 src="/board.svg?%f"></img></br>' % time.time()
    ret += '<form action="/game/" method="post"><button name="New Game" type="submit">New Game</button></form>'
    ret += '<form action="/undo/" method="post"><button name="Undo" type="submit">Undo Last Move</button></form>'
    ret += '<form action="/move/"><input type="submit" value="Make Human Move:"><input name="move" type="text"></input></form>'

    if board.is_stalemate():
        print("Its a draw by stalemate")
    elif board.is_checkmate():
        print("Checkmate")
    elif board.is_insufficient_material():
        print("Its a draw by insufficient material")
    elif board.is_check():
        print("Check")
    return ret


# Display Board
@app.route("/board.svg/")
def board():
    return Response(chess.svg.board(board=board, size=700), mimetype='image/svg+xml')


# Human Move
@app.route("/move/")
def move():
    try:
        move = request.args.get('move', default="")
        print(move)
        board.push_san(move)
        time.sleep(1)
        dev()
    except Exception:
        traceback.print_exc()
    return main()


# Recieve Human Move
@app.route("/recv/", methods=['POST'])
def recv():
    try:
        None
    except Exception:
        None
    return main()


def dev():
    try:
        devmove()
    except Exception:
        traceback.print_exc()
        print("illegal move, try again")
    return main()



# New Game
@app.route("/game/", methods=['POST'])
def game():
    print("Board Reset, Best of Luck for the next game.")
    board.reset()
    return main()


# Undo
@app.route("/undo/", methods=['POST'])
def undo():
    try:
        board.pop()
    except Exception:
        traceback.print_exc()
        print("Nothing to undo")
    return main()



# Main Function
def start_game():
    webbrowser.open("http://127.0.0.1:5000/")
    app.run()

if __name__ == '__main__':
    count = 1
    board = chess.Board()
    sys.setrecursionlimit(10**6)
    threading.stack_size(200000000)
    thread = threading.Thread(target=start_game)
    thread.start()