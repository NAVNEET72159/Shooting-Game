import cv2
import mediapipe as mp
import math
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands

cap = cv2.VideoCapture(0)


def fingerPosition(image, handNo=0):
    lmList = []
    if results.multi_hand_landmarks:
        myHand = results.multi_hand_landmarks[handNo]
        for id, lm in enumerate(myHand.landmark):
            # print(id,lm)
            h, w, c = image.shape
            cx, cy = int(lm.x * w), int(lm.y * h)
            lmList.append([id, cx, cy])
    return lmList

with mp_hands.Hands(
    model_complexity=0,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5) as hands:
  while cap.isOpened():
    success, image = cap.read()
    if not success:
      print("Ignoring empty camera frame.")
      # If loading a video, use 'break' instead of 'continue'.
      continue

    # To improve performance, optionally mark the image as not writeable to
    # pass by reference.
    image.flags.writeable = False
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = hands.process(image)

    # Draw the hand annotations on the image.
    image.flags.writeable = True
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    if results.multi_hand_landmarks:
      for hand_landmarks in results.multi_hand_landmarks:
        mp_drawing.draw_landmarks(
            image,
            hand_landmarks,
            mp_hands.HAND_CONNECTIONS,
            mp_drawing_styles.get_default_hand_landmarks_style(),
            mp_drawing_styles.get_default_hand_connections_style())


    # Flip the image horizontally for a selfie-view display.
        w = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        h = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        idxFinger = hand_landmarks.landmark[6]
        idxFingerPoint = mp_drawing._normalized_to_pixel_coordinates(idxFinger.x, idxFinger.y, w, h)
        thumb = hand_landmarks.landmark[4]
        thumbPoint = mp_drawing._normalized_to_pixel_coordinates(thumb.x, thumb.y, w, h)
        lmList = fingerPosition(image)
        print(lmList)
        cv2.circle(image, thumbPoint, 10, (0, 255, 255), -1)
        cv2.circle(image, idxFingerPoint, 10, (255, 0, 255), -1)
        d = math.sqrt((thumbPoint[0] - idxFingerPoint[0])**2 + (thumbPoint[1]- idxFingerPoint[1])**2)
        if d >= 80 and d <=100:
            print("Not shooting",thumbPoint, idxFingerPoint, f'distance: {d:.2f}')
        elif d>=24 and d <=40:
            print("🦙 Shooting", thumbPoint,
                  idxFingerPoint, f'distance: {d:.2f}')

    cv2.imshow('MediaPipe Hands', cv2.flip(image, 1))
    if cv2.waitKey(5) & 0xFF == 27:
      break
cap.release()
cv2.destroyAllWindows()