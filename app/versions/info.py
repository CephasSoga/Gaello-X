import json

class Version:
    # Default arguments at class  init time are the current version info.
    def __init__(
        self, 
        version: str = "1.411",
        name: str = "Gaello",
        target_resolutions: list[str] = ["1920x1080"],
        url: str = "https://www.gaello.io/downloads",
    ):
        self.version = float(version)
        self.name = name
        self.target_resolutions = target_resolutions
        self.url = url

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

