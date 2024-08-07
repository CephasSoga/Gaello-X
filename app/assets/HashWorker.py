import bcrypt

class Hasher:
    def __init__(self): pass

    def hashPswd(self, pswd: str):
        # Generate a salt and hash the password
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(pswd.encode('utf-8'), salt)
        return hashed

    def matchPswds(self, storedPswd: bytes, inputPswd: str):
        # Verify the provided password against the stored hash
        return bcrypt.checkpw(inputPswd.encode('utf-8'), storedPswd)
    

if __name__ == "__main__":

    h = Hasher()
    r = h.hashPswd("123")
    m =  h.matchPswds(r, "123")
    print("res: ", r)
    print(m)