# don't add to version control
# this is just for testing

import os
from werkzeug.security import generate_password_hash, check_password_hash

print(generate_password_hash("123"))
# os.environ["CREATE_ACC_ID"] = "test"
# os.environ["CREATE_ACC_PW_HASH"] = generate_password_hash("123")

print(os.getenv("CREATE_ACC_ID"))
print(os.getenv("CREATE_ACC_PW_HASH"))

hashedpw = str(os.getenv("CREATE_ACC_PW_HASH"))

print(check_password_hash(hashedpw, "123"))

print(os.urandom(32))