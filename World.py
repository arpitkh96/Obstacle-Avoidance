__author__ = 'philippe'
from tkinter import *
from math import sqrt
import numpy as np
master = Tk()

triangle_size = 0.1
cell_score_min = -0.2
cell_score_max = 0.2
Width = 20
visibility=15
(x, y) = (15, 15)
actions = ["up", "down", "left", "right"]
visited = [[False for i in range(y)] for j in range(x)]
board = Canvas(master, width=x * Width, height=y * Width)
player = (0, y - 1)
score = 0
restart = False
walk_reward = -0.04
me=None
walls = []

specials = [(1, 1, "red", -0.5),(3, 3, "red", -0.5),(7, 7, "red", -0.5),(8, 8, "red", -0.5),(6, 3, "red", -0.5),(4, 6, "red", -0.5), (1, 2, "red", -0.5), (2, 1, "red", -0.5), (2, 2, "red", -0.5), (4, 1, "red", -0.5)]
cell_scores = {}
draw=False
rectangles=[]
def create_triangle(i, j, action):
    if action == actions[0]:
        return board.create_polygon((i + 0.5 - triangle_size) * Width, (j + triangle_size) * Width,
                                    (i + 0.5 + triangle_size) * Width, (j + triangle_size) * Width,
                                    (i + 0.5) * Width, j * Width,
                                    fill="white", width=1)
    elif action == actions[1]:
        return board.create_polygon((i + 0.5 - triangle_size) * Width, (j + 1 - triangle_size) * Width,
                                    (i + 0.5 + triangle_size) * Width, (j + 1 - triangle_size) * Width,
                                    (i + 0.5) * Width, (j + 1) * Width,
                                    fill="white", width=1)
    elif action == actions[2]:
        return board.create_polygon((i + triangle_size) * Width, (j + 0.5 - triangle_size) * Width,
                                    (i + triangle_size) * Width, (j + 0.5 + triangle_size) * Width,
                                    i * Width, (j + 0.5) * Width,
                                    fill="white", width=1)
    elif action == actions[3]:
        return board.create_polygon((i + 1 - triangle_size) * Width, (j + 0.5 - triangle_size) * Width,
                                    (i + 1 - triangle_size) * Width, (j + 0.5 + triangle_size) * Width,
                                    (i + 1) * Width, (j + 0.5) * Width,
                                    fill="white", width=1)


def render_grid():
    global specials, walls, Width, x, y, player,visited,draw,rectangles
    if not draw:
        return
    for i in range(x):
        l=[]
        for j in range(y):

            if visited[i][j]==False:
                l.append(board.create_rectangle(i * Width, j * Width, (i + 1) * Width, (j + 1) * Width, fill="white", width=1))
            else:
                l.append(board.create_rectangle(i * Width, j * Width, (i + 1) * Width, (j + 1) * Width, fill="grey", width=1))
        rectangles.append(l)
    for (i, j, c, w) in specials:
        board.itemconfigure(rectangles[i][j], fill='red')

def try_move(dx, dy):
    global player, x, y, score, me, restart,draw
    if restart == True:
        restart_game()
    state=findState()    
    new_x = player[0] + dx
    new_y = player[1] + dy
    rew=0
    if (new_x >= 0) and (new_x < x) and (new_y >= 0) and (new_y < y) and not ((new_x, new_y) in walls):

        player = (new_x, new_y)
    else:
        rew -= 0.5
        score-=0.5
        restart = True
        return rew,state,state,True
    for (i, j, c, w) in specials:
        if new_x == i and new_y == j:
            rew += w
            score +=w
            restart = True
            return rew,state,state,True
    if visited[new_x][new_y] == True:
        rew -= 0.2
    else:
        rew += 0.02
    visited[new_x][new_y] = True
    if draw:
        #print(findState(new_x,new_y))
        board.itemconfigure(rectangles[new_x][new_y], fill='grey')
        board.tag_raise(me)
        board.coords(me, new_x * Width + Width * 2 / 10, new_y * Width + Width * 2 / 10, new_x * Width + Width * 8 / 10,
                     new_y * Width + Width * 8 / 10)
    return rew,state,findState(),False
    # print "score: ", score


def findDistanceFromWall(celltype, p, q):
        global x,y,visibility
        i = 0
        if (celltype == 0):
            i = p
        elif celltype == 3:
            i = y-q-1
        elif celltype == 2:
            i = x - p-1
        elif celltype == 1:
            i = q
        if i > visibility:
            i = -1
        return i


def findDistanceFromObject(a,b, p, q):
    global visibility
    i = 0
    j=0
    if p-a>0 and b==q:
        i=2
        j=p-a-1
    elif a-p>0 and b==q:
        i= 0
        j=a-p-1
    elif q-b<0 and a==p:
        i=1
        j=b-q-1
    elif q-b>0 and a==p:
        i=1
        j=b-q-1

    if j > visibility:
        j = -1
    return i,j
def findState():
    global player
    x=player[0]
    y=player[1]
    l=[]
    for i in range(4):
        l.append(findDistanceFromWall(i,x,y))
    for (i, j, c, w) in specials:
        if (abs(x-i)<=visibility and y==j) or (abs(y-j)<=visibility and x==i):
            u,v=findDistanceFromObject(x,y,i,j)
            if l[u]>v or l[u]==-1:
                l[u]=v
    l.append(sqrt(x**2 + y**2))

    return np.reshape(np.array(l,dtype=np.float32),(1,5))


def call_up(event):
    try_move(0, -1)


def call_down(event):
    try_move(0, 1)


def call_left(event):
    try_move(-1, 0)


def call_right(event):
    try_move(1, 0)


def restart_game():
    global draw,player, score, me, restart,visited
    player = (0, y - 1)
    for new_x in range(x):
        for new_y in range(y):
            if visited[new_x][new_y]==True:
                visited[new_x][new_y]=False
                board.itemconfigure(rectangles[new_x][new_y], fill='white')

                
    visited[0][y - 1] = True
    score = 0
    restart = False
    if draw:
        board.coords(me, player[0] * Width + Width * 2 / 10, player[1] * Width + Width * 2 / 10,
                 player[0] * Width + Width * 8 / 10, player[1] * Width + Width * 8 / 10)


def has_restarted():
    return restart


master.bind("<Up>", call_up)
master.bind("<Down>", call_down)
master.bind("<Right>", call_right)
master.bind("<Left>", call_left)


def pause():
    global draw
    draw=False
def start():
    global draw
    draw=True
        
def stop():
    global draw
    draw=False
    master.destroy()

def start_game():
    global draw,me
    draw=True
    render_grid()
    me = board.create_rectangle(player[0] * Width + Width * 2 / 10, player[1] * Width + Width * 2 / 10,
                            player[0] * Width + Width * 8 / 10, player[1] * Width + Width * 8 / 10, fill="orange",
                            width=1, tag="me")

    board.grid(row=0, column=0)
    draw=False
    master.mainloop()
