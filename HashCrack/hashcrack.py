import crypt
import argparse

def find_password(filename, hash_val):
    with open(filename, 'r') as password_file:
        for passwd in password_file:
            passwd = passwd.strip()  # Strip new line characters
            hashed_passwd = crypt.crypt(passwd, hash_val)
            if hashed_passwd == hash_val:
                return passwd
    return None

def main():
    parser = argparse.ArgumentParser(description='Find a password given its hash in a password file.')
    parser.add_argument('filename', help='Path to the password file')
    parser.add_argument('hash_val', help='Hash value of the password to find')
    args = parser.parse_args()
    found_password = find_password(args.filename, args.hash_val)
    if found_password:
        print("Password found:", found_password)
    else:
        print("Password not found in the provided file.")

if __name__ == '__main__':
    main()