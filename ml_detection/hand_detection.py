import cv2
import mediapipe


def main():
    mp_hands = mediapipe.solutions.hands
    mp_drawings = mediapipe.solutions.drawing_utils

    with mp_hands.Hands(min_detection_confidence=0.8, min_tracking_confidence=0.5) as mp_lib:
        cap = cv2.VideoCapture(0)
        while cap.isOpened():
            ret, frame = cap.read()
            # convert color space
            img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            # detection
            res = mp_lib.process(img)
            # convert back
            img = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            # render hands
            if res.multi_hand_landmarks:
                for num, hand in enumerate(res.multi_hand_landmarks):
                    mp_drawings.draw_landmarks(img, hand, mp_hands.HAND_CONNECTIONS)
            # display
            cv2.imshow("cap", img)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
