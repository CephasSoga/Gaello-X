from pymongo import MongoClient

from app.versions.info import Version
from utils.logs import Logger
from utils.databases import mongoGet
from utils.asyncJobs import asyncWrap

logger = Logger("VersionControl")

class VersionController:
    current_version = Version()

    async def check_for_update(self, screen_resolution: tuple[int, int], connection: MongoClient):
        try:
            asyncMongoGet = asyncWrap(mongoGet)
            result = await asyncMongoGet(
                connection=connection,
                database="versions",
                collection="history", # simple  placeholder
                sortField="version",
                limit=5, 
            )
            if not result or len(result) == 0:
                logger.log("info", "No version data was found.")
                return None
            
            if any(not isinstance(x, dict) for x in result):
                logger.log(
                    "error",
                    "At least one of the returned values is not a dictionary.",
                    ValueError("Invalid version data format. All values must be dictionaries.")
                )
                return None

            # validate and parse result
            version_data: dict = self.support_this_screen_resolution(screen_resolution, result)
            
            _ = version_data.pop("_id")

            if not all(key in version_data for key in ["version", "name", "target_resolutions", "url"]):
                logger.log(
                    "error",
                    "Invalid version data format.",
                    ValueError("Invalid version data format. one or many of the following keys are missing: 'version', 'name', 'target_resolutions', 'url'.")
                )
                return None
            
            latest_version = Version(**version_data)

            # Compare versions
            if latest_version > self.current_version:
                logger.log("info", f"New version {latest_version.version} available.")
                return latest_version
            else:
                logger.log("info", f"You are using the latest version ({self.current_version.version}).")
                return None

        except Exception as e:
            logger.log("error", "Error during version check.", e)
            return None
        
    def support_this_screen_resolution(self, screen_resolution: tuple[int, int], vaersion_values: list[dict]) -> dict:
        # returns the first (latest as we sort by version number) version that supports this screen resolution
        resolution: str =  f"{screen_resolution[0]}x{screen_resolution[1]}"
        for value in vaersion_values:
            if resolution in value["target_resolutions"]:
                return value
        return None