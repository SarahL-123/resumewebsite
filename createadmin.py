# This script adds an admin user to the database
# run it from the console
# note that all admins can edit everything (since I never intended to have multiple admins anyway)

from app_stuff import app, db
from app_stuff.models import AdminUser

import getpass
from werkzeug.security import generate_password_hash



def main():
    with app.app_context():

        while True:
            print("This creates an admin account for the website so you can create pages")
            username=input('Enter username:')
            print("Note: doesn't show the * but you can still type.")
            password = getpass.getpass(prompt="Enter password:")
            # print('Re-type password')
            password_again = getpass.getpass(prompt="Re-type password:")

            if password != password_again:
                print("----------")
                print("Passwords didn't match, please try again")
                continue

            while True:
                choice = input("Please confirm that the above is ok\nPress y, n, or q (to quit): ")

                if choice == 'q':
                    return 1
                elif choice == 'n':
                    continue
                elif choice == 'y':
                    break
            
            if choice=='y':
                break

        #Now save the data to the database

        # constructor hashes the password
        newadmin = AdminUser(username, password)

        db.session.add(newadmin)
        db.session.commit()
        print('Success, added new admin account')
        return 0

if __name__ == "__main__":
    main()