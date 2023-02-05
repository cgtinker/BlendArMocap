import mediapipe as mp
import mediapipe_rotations as mpr
import cv2

mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_holistic = mp.solutions.holistic


def cvt2array(landmark_list):
    """ converts landmark list to list. """
    return [[landmark.x, landmark.y, landmark.z] for landmark in landmark_list.landmark]


cap = cv2.VideoCapture(0)
with mp_holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5) as holistic:
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
        results = holistic.process(image)

        # Get Detection Data
        pose, face, l_hand, r_hand = [], [], [], []

        if results.pose_landmarks:
            pose = cvt2array(results.pose_landmarks)
            pose_rotation_quaternion = mpr.pose(pose)

        if results.face_landmarks:
            face = cvt2array(results.face_landmarks)

        if results.left_hand_landmarks and results.right_hand_landmarks:
            l_hand = cvt2array(results.left_hand_landmarks)
            r_hand = cvt2array(results.right_hand_landmarks)
        elif results.left_hand_landmarks:
            l_hand = cvt2array(results.left_hand_landmarks)
        elif results.right_hand_landmarks:
            r_hand = cvt2array(results.right_hand_landmarks)

        # Calculate rotations
        l_hand_rotation_quaternion = mpr.hand(l_hand)
        r_hand_rotation_quaternion = mpr.hand(r_hand)
        hands_rotation_quaternion = mpr.hands([l_hand, r_hand])
        face_rotation_quaternion = mpr.face(face)
        holistic_rotation_quaternion = mpr.holistic(pose, face, [l_hand, r_hand])

        # Draw landmark annotation on the image.
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        mp_drawing.draw_landmarks(
            image,
            results.face_landmarks,
            mp_holistic.FACEMESH_CONTOURS,
            landmark_drawing_spec=None,
            connection_drawing_spec=mp_drawing_styles
                .get_default_face_mesh_contours_style())

        mp_drawing.draw_landmarks(
            image,
            results.pose_landmarks,
            mp_holistic.POSE_CONNECTIONS,
            landmark_drawing_spec=mp_drawing_styles
                .get_default_pose_landmarks_style())

        # Flip the image horizontally for a selfie-view display.
        cv2.imshow('MediaPipe Holistic', cv2.flip(image, 1))
        if cv2.waitKey(5) & 0xFF == 27:
            break
cap.release()
