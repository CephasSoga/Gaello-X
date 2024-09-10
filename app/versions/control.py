import aiohttp
from app.versions.info import Version
from utils.logs import Logger

logger = Logger("VersionControl")

class VersionController:
    current_version = Version()

    async def check_for_update(self, url: str):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=10) as response:
                    if response.status != 200:
                        logger.log("error", f"Version check failed with status {response.status}.")
                        return None
                    
                    # Fetch version data first
                    version_data = await response.json()

                    # Validate version data
                    if not all(key in version_data for key in ["version", "name", "target_resolutions", "url"]):
                        logger.log(
                            "error", 
                            "Invalid version data format.", 
                            ValueError("Invalid version data format. one or many of the following keys are missing: 'version', 'name', 'target_resolutions', 'url'."))
                        return None

                    # Create a new Version object from the data
                    latest_version = Version(**version_data)

                    # Compare versions
                    if latest_version > self.current_version:
                        logger.log("info", f"New version {latest_version.version} available.")
                        return latest_version
                    else:
                        logger.log("info", f"You are using the latest version ({self.current_version.version}).")
                        return None
                
        except aiohttp.ClientError as e:
            logger.log("error", f"Client error during version check: {e}")
            return None
        except Exception as e:
            logger.log("error", f"Unexpected error during version check: {e}")
            return None
