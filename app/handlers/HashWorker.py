import bcrypt

class Hasher:
    """
    A class used to hash and verify passwords using bcrypt.

    Attributes
    ----------
    None

    Methods
    -------
    hashPswd(pswd: str) -> bytes
        Generates a salt and hashes the provided password using bcrypt.

    matchPswds(storedPswd: bytes, inputPswd: str) -> bool
        Verifies the provided password against the stored hash using bcrypt.
    """
    def __init__(self): pass

    def hashPswd(self, pswd: str):
        """
        Generates a salt and hashes the provided password using bcrypt.

        Parameters
        ----------
        pswd : str
            The password to be hashed.

        Returns
        -------
        bytes
            The hashed password.
        """
        # Generate a salt and hash the password
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(pswd.encode('utf-8'), salt)
        return hashed

    def matchPswds(self, storedPswd: bytes, inputPswd: str):
        """
        Verifies the provided password against the stored hash using bcrypt.

        Parameters
        ----------
        storedPswd : bytes
            The stored hashed password.
        inputPswd : str
            The password to be verified.

        Returns
        -------
        bool
            True if the provided password matches the stored hash, False otherwise.
        """
        # Verify the provided password against the stored hash
        return bcrypt.checkpw(inputPswd.encode('utf-8'), storedPswd)
    

if __name__ == "__main__":

    h = Hasher()
    r = h.hashPswd("123")
    m =  h.matchPswds(r, "123")
    print("res: ", r)
    print(m)