#Project Title: Bots vs. Invaders
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math
import time
import random

W = 1000
H = 800
camera_mode = 'First-person view'
camera_pos = (-300, 0, 1100)
fovY = 60
GRID_ROWS = 5
GRID_COLS = 10
cell = 120
GRID_WIDTH = GRID_COLS * cell
GRID_HEIGHT = GRID_ROWS * cell

x0 = -GRID_WIDTH / 2
y0 = -GRID_HEIGHT / 2

MAX_BOTS = 8
INITIAL_RESOURCES = 8
ENEMY_HEALTH = 3
ENEMY_COLLIDE_DIST = 40
BULLET_HIT_DIST = 10
MIN_SPAWN_DIST = 30
MAX_INVADERS = 9

BUILDABLE_MAX_COL = 4
FP_MOVE_SPEED = 200

spawn_timer = 0
spawn_interval = 1

score = 0
lives = 5
enemy = [] # [x,y,z,health,row]
bots = [] # [row,col,wx,wy,cooldown]
bot_bullets = [] # [x,y,z,angle]
resources = INITIAL_RESOURCES
build_mode = False
selector = (2, 1)
last_time = time.time()
isOver = False
isPaused = False

#2D
def findZone(x1,y1,x2,y2):
    dx=x2-x1
    dy=y2-y1
    if abs(dx)>=abs(dy):
        if dx>=0 and dy>=0:
            return 0
        elif dx<0 and dy>=0:
            return 3
        elif dx<0 and dy<0:
            return 4
        elif dx>=0 and dy<0:
            return 7
    else:
        if dx>=0 and dy>=0:
            return 1
        elif dx<0 and dy>=0:
            return 2
        elif dx<0 and dy <0:
            return 5
        elif dx>=0 and dy<0:
            return 6

def zTOzero(x,y,z):
    if z==0:
        return x,y
    if z==1:
        return y,x
    if z==2:
        return y,-x
    if z==3:
        return -x,y
    if z==4:
        return -x,-y
    if z==5:
        return -y,-x
    if z==6:
        return -y,x
    if z==7:
        return x,-y

def zeroTOz(x,y,z):
    if z==0:
        return x,y
    if z==1:
        return y,x
    if z==2:
        return -y,x
    if z==3:
        return -x,y
    if z==4:
        return -x,-y
    if z==5:
        return -y,-x
    if z==6:
        return y,-x
    if z==7:
        return x,-y

def draw_point(x, y):
    glBegin(GL_POINTS)
    glVertex2f(x,y)
    glEnd()

def drawMPL(x1,y1,x2,y2):
    zone=findZone(x1,y1,x2,y2)
    x1n,y1n=zTOzero(x1,y1,zone)
    x2n,y2n=zTOzero(x2,y2,zone)
    dx=x2n-x1n
    dy=y2n-y1n
    d=2*dy-dx
    dE=2*dy
    dNE=(dy-dx)*2
    x=x1n
    y=y1n
    while x<=x2n:
        nx,ny=zeroTOz(x,y,zone)
        draw_point(nx,ny)
        if d<=0:
            d+=dE
        else:
            d+=dNE
            y+=1
        x+=1

def draw2DButtons():
    base_x = W - 160   
    base_y = H - 50   
    reset_x = base_x
    play_x = base_x + 60
    quit_x = base_x + 120
    btn_y = base_y
    # Reset button
    glColor3f(0,1,1)
    drawMPL(reset_x, btn_y, reset_x + 25, btn_y)
    drawMPL(reset_x, btn_y, reset_x + 10, btn_y + 10)
    drawMPL(reset_x, btn_y, reset_x + 10, btn_y - 10)
    # Play/Pause button
    glColor3f(1,0.5,0)
    if isPaused:
        #play
        drawMPL(play_x, btn_y + 10, play_x, btn_y - 10)
        drawMPL(play_x, btn_y + 10, play_x + 20, btn_y)
        drawMPL(play_x, btn_y - 10, play_x + 20, btn_y)
    else:
        #pause
        drawMPL(play_x + 5, btn_y + 10, play_x + 5, btn_y - 10)
        drawMPL(play_x + 15, btn_y + 10, play_x + 15, btn_y - 10)
    #cross
    glColor3f(1,0,0)
    drawMPL(quit_x, btn_y + 10, quit_x + 20, btn_y - 10)
    drawMPL(quit_x, btn_y - 10, quit_x + 20, btn_y + 10)

#3D
def draw_text(x, y, text, font=GLUT_BITMAP_HELVETICA_18):
    glColor3f(1,1,1)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, W, 0, H)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    glRasterPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(font, ord(ch))
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

#bots and surroundings
def drawBoard():
    global cell, x0, y0
    x0 = -GRID_WIDTH / 2
    y0 = -GRID_HEIGHT / 2
    for row in range(GRID_ROWS):
        for col in range(GRID_COLS):
            if col >= 5:
                glColor3f(0.3, 0.3, 0.3)
            else:
                if (row + col) % 2 == 0:
                    glColor3f(0, 0.5, 0)
                else:
                    glColor3f(0, 0.4, 0)
            x = x0 + col * cell
            y = y0 + row * cell
            glBegin(GL_QUADS)
            glVertex3f(x, y, 0)
            glVertex3f(x + cell, y, 0)
            glVertex3f(x + cell, y + cell, 0)
            glVertex3f(x, y + cell, 0)
            glEnd()
    wallh = 50
    x_build0 = x0
    build_width = (BUILDABLE_MAX_COL + 1) * cell
    y_build0 = y0
    build_height = GRID_HEIGHT
    #walls
    glColor3f(0.5,0.25,0)
    glBegin(GL_QUADS)
    glVertex3f(x_build0, y_build0, 0)
    glVertex3f(x_build0 + build_width, y_build0, 0)
    glVertex3f(x_build0 + build_width, y_build0, wallh)
    glVertex3f(x_build0, y_build0, wallh)
    glEnd()
    glColor3f(0.5,0.25,0)
    glBegin(GL_QUADS)
    glVertex3f(x_build0, y_build0 + build_height, 0)
    glVertex3f(x_build0 + build_width, y_build0 + build_height, 0)
    glVertex3f(x_build0 + build_width, y_build0 + build_height, wallh)
    glVertex3f(x_build0, y_build0 + build_height, wallh)
    glEnd()
    #building wall
    glPushMatrix()
    b_center_x = x_build0 - (cell / 2)
    b_center_y = y_build0 + build_height / 2
    b_center_z = (wallh * 5) / 2
    glTranslatef(b_center_x, b_center_y, b_center_z)
    thickness = cell
    depth = build_height
    height = wallh * 5
    glScalef(thickness, depth, height)
    glColor3f(1,1,0.5)
    glutSolidCube(1)
    glPopMatrix()
    
    # bots
    for b in bots:
        row, col, bx, by, cooldown = b
        base_size = cell * 0.5
        top_size  = cell * 0.3
        ground_clearance = 6
        base_center_z = ground_clearance + base_size / 2
        top_center_z  = base_center_z + (base_size / 2) + (top_size / 2) + 2
        #base cube
        glPushMatrix()
        glTranslatef(bx, by, base_center_z)
        glColor3f(0.2, 0.6, 1)
        glScalef(base_size, base_size, base_size)
        glutSolidCube(1)
        glPopMatrix()
        #top cube
        glPushMatrix()
        glTranslatef(bx, by, top_center_z)
        glColor3f(0.5, 0.5, 0.5)       
        glScalef(top_size, top_size, top_size)
        glutSolidCube(1)
        glPopMatrix()
    #selector highlight
    if not isOver and not isPaused:
        if build_mode:
            row, col = selector
            if 0 <= col <= BUILDABLE_MAX_COL:
                hx = x0 + col * cell
                hy = y0 + row * cell
                glColor3f(1,1,0)
                glBegin(GL_QUADS)
                glVertex3f(hx, hy, 1)
                glVertex3f(hx + cell, hy, 1)
                glVertex3f(hx + cell, hy + cell, 1)
                glVertex3f(hx, hy + cell, 1)
                glEnd()

#Invader
def spawnAt(x, y, row_idx):
    for inv in enemy:
        _, ey, _, _, r = inv
        if r == row_idx:
            if abs(ey - y) < 0:
                if abs(inv[0] - x) < MIN_SPAWN_DIST:
                    return False
    return True

def spawnInvader():
    if len(enemy) >= MAX_INVADERS:
        return
    col = GRID_COLS - 1
    attempts = 0
    while attempts < 1:
        attempts += 1
        row = random.randint(0, GRID_ROWS - 1)
        wy = y0 + row * cell + cell / 2
        spawn_x = x0 + col * cell + cell / 2
        spawn_y = wy
        if spawnAt(spawn_x, spawn_y, row):
            enemy.append([spawn_x, spawn_y, 40, ENEMY_HEALTH, row])
            return

def drawInvaders(dt):
    global enemy, lives, score, spawn_timer, spawn_interval, isPaused, isOver
    if isOver or isPaused:
        return
    spawn_timer += dt
    if spawn_timer >= spawn_interval:
        spawnInvader()
        spawn_timer = 0
    x_min = x0
    for inv in enemy[:]:
        ex, ey, ez, eh, row_idx = inv
        speed = 50  #base speed
        speed +=  3 * score
        inv[0] -= speed * dt
        if inv[0] < x_min + cell * 0.5:
            lives -= 1
            if lives == 0:
                print(f"Game Over! Score: {score}")
                isOver = True
                return
            else:
                if inv in enemy:
                    enemy.remove(inv)
                print("An Invader reached house. Remaining Life:", lives)
                continue
        for b in bots[:]:
            brow, bcol, bx, by, cooldown = b
            bd = ((bx - inv[0])**2 + (by - inv[1])**2)**0.5
            if bd < ENEMY_COLLIDE_DIST:
                if b in bots:
                    bots.remove(b)
                global resources
                resources += 1
                score -= 1
                print("Bot destroyed by Invader. Resources retrieved.")
                break
        glPushMatrix()
        glTranslatef(inv[0], inv[1], ez)
        glScalef(1,1,1)
        #legs
        glColor3f(0.5,0,0)
        glTranslatef(0,-10,-30)
        gluCylinder(gluNewQuadric(),2,5,60,30,30) 
        glTranslatef(0,20,0)
        gluCylinder(gluNewQuadric(),2,5,60,30,30)
        #body
        if eh == 3:
            glColor3f(1,1,0)
        elif eh == 2:
            glColor3f(1,0.5,0)
        else:
            glColor3f(1,0,0)
        glTranslatef(0,-10,55)
        glScalef(1,1.5,2.5)
        glutSolidCube(20)
        #head
        glColor3f(0,0,0)
        glScalef(1,0.7,0.3)
        glTranslatef(0,0,35)
        gluSphere(gluNewQuadric(),20,50,50)
        #horns
        glColor3f(1,0,0)
        glTranslatef(0,-10,0)
        glRotatef(0,0,1,0)
        gluCylinder(gluNewQuadric(),5,2,40,30,30)
        glTranslatef(0,20,0)
        gluCylinder(gluNewQuadric(),5,2,40,30,30)
        glPopMatrix()

#Bots firing
def botShooting(dt):
    global bot_bullets, enemy, score
    if isOver:
        bot_bullets[:] = []
        return
    if isPaused:
        return
    for b in bots:
        row, col, bx, by, cooldown = b
        fire_rate = 1  
        cooldown -= dt
        y_target = cell * 0.6
        x_target = GRID_WIDTH * 1.5  
        should_fire = False
        for inv in enemy:
            inv_x, inv_y, _, _, _ = inv
            if inv_x > bx and abs(inv_y - by) <= y_target and (inv_x - bx) <= x_target:
                should_fire = True
                break
        #fire when cooldown elapsed
        if cooldown <= 0:
            if should_fire:
                # Fire one shot
                bot_bullets.append([bx, by, 10, 0])
                cooldown += fire_rate
            else:
                # Don't fire
                cooldown = 0
        b[4] = cooldown
    new_bb = []
    bspeed = 600 
    x_min = x0
    x_max = x0 + GRID_WIDTH
    y_min = y0
    y_max = y0 + GRID_HEIGHT
    for bb in bot_bullets:
        bx, by, bz, br = bb
        #movement
        bx += bspeed * dt * math.cos(math.radians(br))
        by += bspeed * dt * math.sin(math.radians(br))
        #bullet collisions logic
        if x_min <= bx <= x_max and y_min <= by <= y_max:
            hit = False
            for inv in enemy[:]:
                ex, ey, ez, eh, row_idx = inv
                d=((ex - bx)**2 + (ey - by)**2)**0.5

                if d < BULLET_HIT_DIST:
                    inv[3] -= 1
                    if inv[3] <= 0:
                        if inv in enemy:
                            enemy.remove(inv)
                        score += 2
                        print("Invader killed by Bot! +2 points.")
                    hit = True
                    break
            if not hit:
                new_bb.append([bx, by, bz, br])
                glPushMatrix()
                glTranslatef(bx, by, bz)
                glRotatef(br, 0, 0, 1)
                glColor3f(1,1,1)
                glutSolidCube(8)
                glPopMatrix()
    bot_bullets[:] = new_bb

def keyboardListener(key, x, y):
    global build_mode, selector, bots, resources, isOver, camera_pos, camera_mode, isPaused
    k = key
    #Build Mode
    if k == b'b' and not isOver:
        if isPaused:
            print("Build actions disabled while paused.")
            return
        build_mode = not build_mode
        r, c = selector
        if c > BUILDABLE_MAX_COL:
            c = BUILDABLE_MAX_COL
        selector = (r, c)
        print("Build mode:", build_mode)
        return
    
    if build_mode and not isOver:
        if isPaused:
            print("Build actions disabled while paused.")
            return
        #Place bot
        if k == b' ' :
            row, col = selector
            if col > BUILDABLE_MAX_COL:
                print("Cannot build here.")
                return
            occupied = any(b[0] == row and b[1] == col for b in bots)
            if not occupied and len(bots) < MAX_BOTS and resources > 0:
                wx = x0 + col * cell + cell / 2
                wy = y0 + row * cell + cell / 2
                bots.append([row, col, wx, wy, 1])
                resources -= 1
                print("Bot placed at tile", row, col)
            else:
                print("Cannot place Bot.")
            return
        #Withdraw bot
        if k == b'x':
            row, col = selector
            if col > BUILDABLE_MAX_COL:
                print("Cannot withdraw from non-buildable column.")
                return
            for b in bots[:]:
                if b[0] == row and b[1] == col:
                    bots.remove(b)
                    resources += 1
                    print("Bot withdrawn from tile", row, col, "resource returned.")
                    break
            else:
                print("No Bot to withdraw on selected tile.")
            return
        row, col = selector
        if k == b'w':
            col = min(BUILDABLE_MAX_COL, col + 1)
        elif k == b's':
            col = max(0, col - 1)
        elif k == b'a':
            row = min(GRID_ROWS - 1, row + 1)
        elif k == b'd':
            row = max(0, row - 1)
        selector = (row, col)
        return

def specialKeyListener(key, x, y):
    global camera_pos, camera_mode
    if not isOver and not isPaused:
        if key == GLUT_KEY_UP:
            camera_mode = 'First-person view'
            camera_pos = (-300, 0, 1100)
            print(f"Camera: {camera_mode}")
        elif key == GLUT_KEY_DOWN:
            camera_mode = "Invader's view"
            camera_pos = (900, 0, 500)
            print(f"Camera: {camera_mode}")
        elif key == GLUT_KEY_RIGHT:
            camera_mode = "Right neighbour's view"
            camera_pos = (0, -1100, 700)
            print(f"Camera: {camera_mode}")
        elif key == GLUT_KEY_LEFT:
            camera_mode = "Left neighbour's view"
            camera_pos = (0, 1100, 700)
            print(f"Camera: {camera_mode}")

def mouseListener(button, state, mx, my):
    if button != GLUT_LEFT_BUTTON or state != GLUT_DOWN:
        return
    ux = mx
    uy = H - my
    base_x = W - 160
    btn_y = H - 50
    reset_x = base_x
    play_x = base_x + 60
    quit_x = base_x + 120
    #Reset button area
    if reset_x <= ux <= reset_x + 25 and btn_y - 12 <= uy <= btn_y + 12:
        reset_game()
        print("Reset button clicked.")
        return
    #Play/Pause area
    if play_x <= ux <= play_x + 30 and btn_y - 12 <= uy <= btn_y + 12 and not isOver:
        global isPaused
        isPaused = not isPaused
        print("Pause status:", isPaused)
        return
    #Quit area
    if quit_x <= ux <= quit_x + 20 and btn_y - 12 <= uy <= btn_y + 12:
        print("Exiting. Score:", score)
        glutLeaveMainLoop()
        return



def setupCamera():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(fovY, W/H, 0.1, 3000)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    cx, cy, cz = camera_pos
    gluLookAt(cx, cy, cz, 0, 0, 0, 0, 0, 1)

def idle():
    glutPostRedisplay()

def showScreen():
    global last_time, isOver
    glEnable(GL_DEPTH_TEST)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glViewport(0, 0, W, H)
    setupCamera()
    now = time.time()
    if last_time:
        dt = now - last_time
    else:
        dt = 0
    if dt > 0.5:
        dt = 0.5
    last_time = now
    drawBoard()
    drawInvaders(dt)
    botShooting(dt)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, W, 0, H)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    glPointSize(5)
    draw2DButtons()
    if isOver:
        draw_text(460, H/2, f"Game Over!!!!!")
        draw_text(460, H/2-30, f"Final Score: {score}")
    else:
        draw_text(10, H-30, f"Life Remaining: {lives}")
        draw_text(10, H-60, f"Game Score: {score}")
        draw_text(10, H-90, f"Building Resources: {resources}")
        draw_text(10, H-120, f"Camera Mode: {camera_mode}")
        if isPaused:
            draw_text(460, H/2, f"Paused!!!")
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    glutSwapBuffers()

def reset_game():
    global score, lives, enemy, bots, bot_bullets, resources, isOver, last_time, selector, camera_mode, camera_pos, spawn_timer, isPaused
    score = 0
    lives = 5
    enemy = []
    bots = []
    bot_bullets = []
    resources = INITIAL_RESOURCES
    isOver = False
    isPaused = False
    last_time = time.time()
    spawn_timer = 0
    selector = (GRID_ROWS // 2, min(BUILDABLE_MAX_COL, GRID_COLS // 2))
    camera_mode = 'First-person view'
    camera_pos = (-300, 0, 1100)
    #Spawn a random initial number
    initial_count = random.randint(1, 5)
    for i in range(initial_count):
        spawnInvader()
    print("Game restarted!")

def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(W, H)
    glutInitWindowPosition(0, 0)
    glutCreateWindow(b"Bots vs. Invaders")
    glutDisplayFunc(showScreen)
    glutKeyboardFunc(keyboardListener)
    glutSpecialFunc(specialKeyListener)
    glutMouseFunc(mouseListener)
    glutIdleFunc(idle)
    reset_game()
    glutMainLoop()

if __name__ == "__main__":
    main()
