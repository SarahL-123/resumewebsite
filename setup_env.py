# this is just for testing purposes

import os
from werkzeug.security import generate_password_hash

hashthis = input("Enter something to hash")

print("The hash of that is:")
print(generate_password_hash(hashthis))

print()
print("Random string for secret key")
print(os.urandom(32))