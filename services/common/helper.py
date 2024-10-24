import os
import uuid
import json

from services.common.config import LOCAL_FOLDER

class FileUUIDGenerator:
    def __init__(self):
        """
        Initialize the FileUUIDGenerator with the folder path and the JSON file path.
        """
        self.folder_path = LOCAL_FOLDER
        self.json_file = "doc_id.json"

    def generate_unique_uuid(self):
        """
        Generate a new unique UUID that does not collide with existing UUIDs 
        from both the folder and the JSON file.

        :return: A unique UUID as a string.
        """
        # Get existing UUIDs from both the folder and the JSON file
        existing_uuids = self.get_existing_uuids_from_folder()
        existing_uuids.update(self.get_existing_uuids_from_json())

        # Generate a new UUID
        new_uuid = str(uuid.uuid4())

        # Keep generating new UUIDs until it's unique
        while new_uuid in existing_uuids:
            new_uuid = str(uuid.uuid4())

        return new_uuid

    def get_existing_uuids_from_folder(self):
        """
        Retrieve existing UUIDs from the file names in the folder.

        :return: A set of UUID strings extracted from file names in the folder.
        """
        existing_uuids = set()
        
        # Walk through all files in the folder
        for root, dirs, files in os.walk(self.folder_path):
            for file_name in files:
                # Try to parse the file name as a UUID
                try:
                    uuid_obj = uuid.UUID(file_name)
                    existing_uuids.add(str(uuid_obj))  # Add to the set if valid
                except ValueError:
                    # If the file name is not a valid UUID, ignore it
                    pass
        
        return existing_uuids

    def get_existing_uuids_from_json(self):
        """
        Retrieve existing UUIDs from the JSON file (doc_id.json).
        Handles cases where the file is missing, empty, or contains invalid JSON.

        :return: A set of UUID strings stored in the JSON file, or an empty set if the file is empty or invalid.
        """
        try:
            # Open the JSON file and load the UUID list
            with open(self.json_file, 'r') as f:
                content = f.read().strip()  # Read and strip whitespace
                if not content:  # Check if the file is empty
                    return set()  # Return an empty set if the file is empty
                uuid_list = json.loads(content)  # Load the content as JSON
                return set(uuid_list)  # Convert the list to a set
        except (FileNotFoundError, json.JSONDecodeError):
            # If the file doesn't exist or has an invalid format, return an empty set
            return set()
