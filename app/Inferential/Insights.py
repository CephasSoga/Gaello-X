from pathlib import Path
from typing import Union, List

class Insight:
    def __init__(self, imagePath: Union[Path, str], labels: List[str], locations: List[str], assets: List[str], title: str, content:str) -> None:
        self.imagePath = imagePath
        self.labels = labels
        self.locations = locations
        self.assets = assets
        self.title = title
        self.content = content