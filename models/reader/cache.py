import os
import json
from typing import Any, Dict, Tuple, Optional
from cachetools import TTLCache

from utils.logs import Logger
from utils.envHandler import getenv
from utils.paths import getFileSystemPath

class FileCache:
    def __init__(self, cache_size: float, ttl: int = 3600):
        self.cache_size = cache_size
        self.cache = TTLCache(maxsize=cache_size, ttl=ttl)
        self.logger = Logger("File-Cache")
    
    def readTxt(self, filename):
        if filename in self.cache:
            return self.cache[filename]
        else:
            try:
                with open(filename, 'r') as file:
                    data = file.read()
                    self.cache[filename] = data
                    return data
            except FileNotFoundError as file_not_found:
                self.logger.log("error", "File not found", file_not_found )
                return None
            except Exception as e:
                self.logger.log("error", "An error occurred while reading the file", e)
                return None
            
    def readJson(self, filepath) -> Optional[Dict[str, Any]]:
        try:
            with open(filepath, 'r') as file:
                content = json.load(file)
                self.cache[filepath] = content
            return content
        except FileNotFoundError as file_not_found:
            self.logger.log("error", "File not found", file_not_found)
            return {}
        except json.JSONDecodeError as json_decode_error:
            self.logger.log("error", "JSON decode error", json_decode_error)
            return {}
        except Exception as e:
            self.logger.log("error", "An error occurred while reading the JSON file", e)
            return {}
        

class CredentialsReader:
    def __init__(self, cache_size: float, ttl: int = 3600):
        self.cache = FileCache(cache_size, ttl)
        self.logger = Logger("Credentials-Reader")
    
    def read(self) ->  Optional[Dict[str, Any]]:
        try:
            # Read credentials from a JSON file and cache the result for 1 hour.
            base_path = getFileSystemPath(getenv("APP_BASE_PATH"))
            filepath = os.path.join(base_path, "credentials", "credentials.json")
            data = self.cache.readJson(filepath)
            return {"id": data.get("id"), "email": data.get("email")}
        except Exception as e:
            self.logger.log("error", "An error occurred while reading the credentials file", e)
            return {}
        

credentials_reader = CredentialsReader(cache_size=120)
cached_credentials = credentials_reader.read()


