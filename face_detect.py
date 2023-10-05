import face_recognition
import psycopg2
import sys
import pyaudio
import wave
import cv2


def store_face():
    try:

        # Ask the user if they want to take a picture or enter a image path
        choice = input(
            "Do you want to take a picture or upload a picture? (t/u): ")

        if choice.lower() == "t":
            image_path = take_picture()
            print("taken_picture_image_path: ", image_path)
        elif choice.lower() == "u":
            image_path = input("Enter the path to the image: ")
            print("image_path: ", image_path)
        else:
            print("Invalid choice")
            return

        # Connect to the PostgreSQL database
        conn = psycopg2.connect(
            dbname="face_recognition_db",
            user="postgres",
            password="1028",
            host="localhost"
        )

        with conn:
            # Create a cursor
            with conn.cursor() as cursor:
                # Load the image you want to store
                image = face_recognition.load_image_file(image_path)

                # Detect face locations and encode the face
                face_locations = face_recognition.face_locations(image)

                # Check if any faces are detected
                if len(face_locations) == 0:
                    print("No faces detected")
                    return

                # get user input for the name
                name = input("Enter the name for the detected face: ")

                comment = input("Enter some comment for the detected face: ")

                audio_path = None

                # Ask user for audio recording choice
                record_choice = input("Do you want to record audio? (y/n): ")

                if record_choice.lower() == "y":
                    # Record audio, duration is 5 seconds
                    audio_path = record_audio(5)

                # Convert the image to face encodings
                face_encodings = face_recognition.face_encodings(
                    image, face_locations)

                # Insert face information into the database
                for encoding in face_encodings:
                    cursor.execute(
                        "INSERT INTO faces (name, embedding, voice_recording, comment) VALUES (%s, %s, %s, %s) RETURNING id",
                        (name, psycopg2.Binary(encoding.tobytes()), audio_path, comment)
                    )

                print("The image has been successfully stored in the database")

    except (psycopg2.Error, FileNotFoundError) as e:
        print("An error occurred:", e)


def record_audio(duration):
    try:
        # Set up audio stream
        CHUNK = 1024
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 44100

        audio = pyaudio.PyAudio()

        stream = audio.open(format=FORMAT, channels=CHANNELS,
                            rate=RATE, input=True, frames_per_buffer=CHUNK)

        print("Recording...")
        frames = []

        # Record audio for the specified duration
        for _ in range(int(RATE / CHUNK * duration)):
            data = stream.read(CHUNK)
            frames.append(data)

        print("Finished recording")

        # Stop and close the audio stream
        stream.stop_stream()
        stream.close()
        audio.terminate()

        # Save the recorded audio to a WAV file
        audio_path = "recorded_audio.wav"
        wave_file = wave.open('recorded_audio.wav', 'wb')
        wave_file.setnchannels(CHANNELS)
        wave_file.setsampwidth(audio.get_sample_size(FORMAT))
        wave_file.setframerate(RATE)
        wave_file.writeframes(b''.join(frames))
        wave_file.close()

        print("Audio saved as recorded_audio.wav")

        return audio_path
    except OSError as e:
        print("An error occurred:", e)


def take_picture():
    cap = cv2.VideoCapture(0)

    # Check if the webcam is opened correctly
    if not cap.isOpened():
        raise IOError("Cannot open webcam")

    print("Press 'q' to take a picture and exit.")
    while True:
        # Read the current frame from the webcam
        ret, frame = cap.read()

        if not ret:
            print("Could not read frame")
            continue
        # Display the current frame in a window
        cv2.imshow('Webcam', frame)

        # Wait for the user to press the 'q' key
        if cv2.waitKey(1) & 0xFF == ord('q'):
            # if 'q' is pressed, break the loop and save the picture

            cv2.imwrite('captured_image.jpg', frame)
            break

    # Release the webcam and destroy all windows
    cap.release()
    cv2.destroyAllWindows()

    return 'captured_image.jpg'
