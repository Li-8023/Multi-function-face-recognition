import face_recognition
import psycopg2
import numpy as np
import pygame
import cv2


def retrieve_and_check_face():
    try:

        # Ask the user if they want to take a picture or enter an image path
        choice = input(
            "Do you want to take a picture or upload a picture? (t/u): ")

        if choice.lower() == 't':
            # Take a picture and get the image path
            image_path = take_picture()
        elif choice.lower() == 'u':
            # Ask the user for the image path
            image_path = input("Enter the path to the image: ")
        else:
            print("Invalid choice")
            return

        # Load the image using face_recognition
        input_image = face_recognition.load_image_file(image_path)

        # Convert the input image to face encodings
        input_face_encoding = face_recognition.face_encodings(input_image)[0]

        # Connect to the PostgreSQL database
        conn = psycopg2.connect(dbname="face_recognition_db",
                                user="postgres", password="1028", host="localhost")

        # Create a cursor
        with conn.cursor() as cursor:
            # Retrieve stored face information from the database
            cursor.execute("SELECT id, embedding FROM faces")

            face_encodings = cursor.fetchall()
            if not face_encodings:
                print("No faces found in the database.")
                return

            # taking each face encoding, converting it back into a numpy array
            known_face_ids = [face[0] for face in face_encodings]
            known_faces = [np.frombuffer(
                face[1], dtype=np.float64) for face in face_encodings]
            
            # Compare the input face with the known faces
            matches = face_recognition.compare_faces(
                known_faces, input_face_encoding, tolerance=0.5)
            
            if np.any(matches):
                print("The face is not a new face")


                # Fetch the name of the matched face
                match_index = np.where(matches)[0][0]
                match_face_id = known_face_ids[match_index]
                cursor.execute(
                    "SELECT name, voice_recording FROM faces WHERE id = %s", (match_face_id,))
                result = cursor.fetchone()
                if result is not None:
                    name, audio_path = result
                    print(f"The face is recognized as {name}")

                    # Ask the user if they want to play the audio
                    audio_choice = input("Do you want to play the audio?(y/n): ")
                    if audio_choice.lower() == 'y':
                        if audio_path is None:
                            print("No voice recorded")
                        else:
                            play_audio(audio_path)
                else:
                    print("No matching face found in the database.")

            else:
                print("It is a new face")

    except (psycopg2.Error, FileNotFoundError) as e:
        print("An error occurred:", e)


def play_audio(audio_path):
    try:
        # Initialize pygame
        pygame.init()

        # Load the audio file
        pygame.mixer.music.load(audio_path)

        # Play the audio
        pygame.mixer.music.play()

        # Wait until the audio finishes playing
        while pygame.mixer.music.get_busy():
            continue

        # Clean up resources
        pygame.mixer.music.stop()
        pygame.quit()

    except Exception as e:
        print("An error occurred:", e)


def take_picture():
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        raise IOError("Cannot open webcam")

    print("Press 'q' to take a picture and exit.")

    while True:
        ret, frame = cap.read()
        cv2.imshow('Webcam', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            cv2.imwrite('captured_image.jpg', frame)
            break

    cap.release()
    cv2.destroyAllWindows()

    return 'captured_image.jpg'
