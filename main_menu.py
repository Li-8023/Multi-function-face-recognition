import os
from face_detect import store_face
from face_retrieve import retrieve_and_check_face
from face_delete import delete_face


def display_menu():
    print("Menu:")
    print("1. Store Face")
    print("2. Retrieve Face")
    print("3. Delete Face")
    print("0. Exit")


def main():
    while True:
        display_menu()
        choice = input("Enter your choice: ")

        if choice == "1":
            # image_path = input("Enter the path to the image: ")
            store_face()

        elif choice == "2":

            retrieve_and_check_face()
        
        elif choice == "3":
            name = input("Enter the name of the person you want to delete: ")
            delete_face(name)

        elif choice == "0":
            print("Exiting...")
            break

        else:
            print("Invalid choice. Please enter a valid option.")


if __name__ == "__main__":
    main()
