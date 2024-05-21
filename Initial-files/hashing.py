import argon2

# Declare the password as a bytes object
password = b'Admin@123!'

# Hash the password using Argon2
ph = argon2.PasswordHasher()
hashed_password = ph.hash(password)

print("Hashed password:", hashed_password)
