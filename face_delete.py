import face_recognition
import psycopg2


def delete_face(name):
    try:
        conn = psycopg2.connect(
            dbname="face_recognition_db",
            user="postgres",
            password="1028",
            host="localhost"
        )

        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT embedding FROM faces WHERE name = %s", (name,))
            face_encodings = cursor.fetchall()

            if len(face_encodings) == 0:
                print("No faces found for the given name")
                return
            cursor.execute("DELETE FROM faces WHERE name = %s", (name,))
            conn.commit()
        print("Faces deleted successfully")

    except psycopg2.Error as e:
        print("An error occurred while deleting")
