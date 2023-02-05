import cv2
import mediapipe as mp 
import pgzrun
import random
import sys
import math
import pygame as py

mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles  = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(model_complexity=0, min_detection_confidence=0.5, min_tracking_confidence=0.5)

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

WIDTH = 600
HEIGHT = 600
MAX_BULLETS = 10

level = 1
lives = 3
score = 0

gstate = 0
lines = []          # list of tuples of horizontal lines of walls
wall_gradient = -3  # steepness of wall
left_wall_x = 200   # x-coordinate of wall
distance = 0        # how far player has travelled
time = 15           # time left until game ends
playing = False     # True when in game, False when on title screen
best_distance = 0
# pretty_colour = (255, min(left_wall_x, 255), min(time * 20, 255))

player = Actor("player", (200, 580))
enemies = []
bullets = []
bombs = []
scroll = 0
bg = py.image.load("images/bg1.png").convert()
tiles = math.ceil(bg.get_height()/HEIGHT ) + 1
print("TIELS",tiles)


def draw():
    global  scroll
    if gstate == 0:
        screen.clear()
        i = 0
        while(i < tiles):
            screen.blit(bg,  (0, bg.get_height()*i + scroll))
            i += 1
        scroll -= 6
        if abs(scroll) > bg.get_height():
            scroll = 0
            
        for i in range(0, len(lines)):  # draw the walls
            x, x2, color = lines[i]
            screen.draw.line((0, i), (x, i), color)
            screen.draw.line((x + x2, i), (WIDTH, i), color)
        player.draw()
        for enemy in enemies:
            enemy.draw()
        for bullet in bullets: 
            bullet.draw()
        for bomb in bombs:
            bomb.draw()
        draw_text()
        
    if gstate == 2:
        screen.draw.text("PRESS SPACE TO START",
                         (150, 300), color="green", fontsize=40)
        screen.draw.text("BEST DISTANCE: "+str(int(best_distance / 10)),
                         (170, 400), color="green", fontsize=40)

def update(dt):
    gesture_detection()
    move_bullets()
    move_enemies()
    create_bombs()
    move_bombs()
    check_for_end_of_level()
    move_player()
    print(dt)
    




def move_player():
    if keyboard.right:
        player.x = player.x - 5
    if keyboard.left:
        player.x = player.x + 5
    if keyboard.up:
        player.y = player.y - 5
    if keyboard.down:
        player.y = player.y  + 5
    if player.x > WIDTH:
        player.x = WIDTH
    if player.x < 0:
        player.x = 0

def move_bullets():
    for bullet in bullets:
        bullet.y = bullet.y - 6
        if bullet.y < 0:
            bullets.remove(bullet)
    
def move_enemies():
    global score, gstate
    for enemy in enemies:
        enemy.x = enemy.x + enemy.vx
        if enemy.x > WIDTH or enemy.x < 0:
            enemy.vx = -enemy.vx
            animate(enemy, duration=0.1, y=enemy.y + 60)
            
        for bullet in bullets:
            try:
                if bullet.colliderect(enemy):
                    print(enemies.remove(enemy)) 
                    bullets.remove(bullet)
                    score = score + 1
            except Exception:
                pass

        if enemy.colliderect(player):
            sounds.boom.play()
            gstate = 2

def create_bombs():
    try: 
        if random.randint(0, 50 - level * 6) == 0:
            enemy = random.choice(enemies)
            bomb = Actor("bomb", enemy.pos)
            bombs.append(bomb)
    except: 
        return 0
    
def move_bombs():
    global lives, gstate
    for bomb in bombs:
        bomb.y = bomb.y + 10
        if bomb.colliderect(player):  
            bombs.remove(bomb)
            lives = lives - 1
            if lives == 0:
                screen.clear()
                gstate = 2
    
def check_for_end_of_level():
    global level
    if len(enemies) == 0:
        level = level + 1
        create_enemies()

def draw_text():
    screen.draw.text("Level " + str(level), (0, 0), color="yellow")
    screen.draw.text("Score " + str(score), (100, 0), color="red")
    screen.draw.text("Lives " + str(lives), (200, 0), color="blue")

def create_enemies():
    for x in range(0, 600, 60):
        for y in range(0, 200, 60):
            enemy = Actor("enemy1", (x, y))
            enemy.vx = level * 2
            enemies.append(enemy)

def create_bullets():
    bullet = Actor("bullet", pos=(player.x, player.y))
    bullets.append(bullet)
    sounds.singleshot.play()



def get_distance(p1, p2):
    try:return math.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)
    except:return 0

def get_shooting_gesture(hand, image, w, h) -> bool:
    idxFinger = hand.landmark[6]
    idxFingerPoint = mp_drawing._normalized_to_pixel_coordinates(idxFinger.x, idxFinger.y, w, h)
    thumb = hand.landmark[4]
    thumbPoint = mp_drawing._normalized_to_pixel_coordinates(thumb.x, thumb.y, w, h)
    cv2.circle(image, thumbPoint, 10, (0, 255, 255), -1)
    cv2.circle(image, idxFingerPoint, 10, (255, 0, 255), -1)
    d = get_distance(idxFingerPoint, thumbPoint)
    if d >= 90 and d <=100:
        print("💫 Not shooting",thumbPoint, idxFingerPoint, f'distance: {d:.2f}')
        return False
    elif d>=20 and d <=30:
        print("☢ Shooting", thumbPoint,idxFingerPoint, f'distance: {d:.2f}')
        return True
    return False

def get_position(hand, w, h):
    try:
        thumb = hand.landmark[4]
        value =  mp_drawing._normalized_to_pixel_coordinates(thumb.x, thumb.y, w, h)
        if value == None:
            return 0,0
        else:
            return value
    except:
        return 0,0
    
def handle_gestures(landmarks,w,h,image):
    for hand_landmarks in landmarks:
        gesture = get_shooting_gesture(hand_landmarks, image, w, h)
        pp = get_position(hand_landmarks, w, h)
        if gstate == 0:
            if pp:
                player.pos = pp[0], HEIGHT - 20 

            # print(gesture_detection)
            if gesture:
                # shoot bullet
                create_bullets()
        elif gstate == 2:
            pass

def gesture_detection():
    if cap.isOpened():
        success, image = cap.read()
        if not success:
            print("Ignoring empty camera frame.")
        image.flags.writeable = False
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = hands.process(image)
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)

        if results.multi_hand_landmarks:
            handle_gestures(results.multi_hand_landmarks,width,height,image)
            
        cv2.flip(image, 1)
        cv2.line(image, (0, 350), (640, 350), (255, 255, 255), 2)
        cv2.putText(image, "Shooting Game by Navneet Shandilya", (640//3, 400),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)
        cv2.imshow('GERSTURE RECOGNIZING WINDOW', image)
        if cv2.waitKey(5) & 0xFF == 27:
            cap.release()
            cv2.destroyAllWindows()
            sys.exit()
pgzrun.go()