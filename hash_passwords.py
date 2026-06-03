import streamlit_authenticator as stauth

# List of plain passwords you want to use
passwords = ["samarth123", "tejashree", "ramesh123", "priya123", "amit123"]

# Generate hashed passwords
hashed_passwords = stauth.Hasher(passwords).generate()

print(hashed_passwords)

