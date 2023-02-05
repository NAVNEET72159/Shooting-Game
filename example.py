import cv2
import mediapipe as mp
import pgzrun
import sys
WIDTH = 640
HEIGHT = 350


mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands


cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

box = Rect((0, 250,), (10, 10))
hands = mp_hands.Hands(
    model_complexity=0, min_detection_confidence=0.5, min_tracking_confidence=0.5)


def draw():
    # screen.fill('white')
    screen.draw.filled_rect(box, 'red')


def update():

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
            for hand_landmarks in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(
                    image,
                    hand_landmarks,
                    mp_hands.HAND_CONNECTIONS,
                    mp_drawing_styles.get_default_hand_landmarks_style(),
                    mp_drawing_styles.get_default_hand_connections_style())
                data = hand_landmarks.landmark[8]
                coords = mp_drawing._normalized_to_pixel_coordinates(
                    data.x, data.y, width, height)
                cv2.circle(image, coords, 10, (0, 255, 255), -1)
                print(coords)
                try:
                    box.center = (WIDTH-coords[0], coords[1])
                except Exception as e:
                    print(e)
        cv2.flip(image, 1)
        cv2.line(image, (0, 350), (640, 350), (255, 255, 255), 2)
        cv2.putText(image, "OPENCV + PYGAME + MEDIAPIPE", (640//3, 400),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)
        cv2.imshow('MediaPipe Hands', image)
        if cv2.waitKey(5) & 0xFF == 27:
            cap.release()
            cv2.destroyAllWindows()
            sys.exit()


pgzrun.go()
