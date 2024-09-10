import json

class Version:
    version: float = 1.411
    name: str = "Gaello"
    target_resolutions: list[str] = ["1920x1080"]
    url: str = "http://www.gaello.com/downloads/1920x1080/gaello.exe"

    def __eq__(self, other):
        if not isinstance(other, Version):
            raise TypeError("Cannot compare Version with non-Version type")
        return self.version == other.version

    def __lt__(self, other):
        if not isinstance(other, Version):
            raise TypeError("Cannot compare Version with non-Version type")
        return self.version < other.version
    
    def __gt__(self, other):
        if not isinstance(other, Version):
            raise TypeError("Cannot compare Version with non-Version type")
        return self.version > other.version
    
    def __repr__(self):
        return json.dumps(
            {
                "version": self.version,
                "name": self.name,
                "target_resolutions": self.target_resolutions,
                "url": self.url
            },
            indent=4 
        )

