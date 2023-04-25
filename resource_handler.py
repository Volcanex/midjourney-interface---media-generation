import os 

class ResourceHandler:
    def __init__(self, file_paths):
        self.file_paths = file_paths
        self.resources = {}

    def initialize_resources(self):
        print("Initializing resources...")
        for resource_id, file_path in self.file_paths.items():
            resource_type = self.detect_resource_type(file_path)

            if resource_type == 'image':
                self.resources[resource_id] = file_path
                print(f"Added image file with ID {resource_id} at path {file_path}")
            elif resource_type == 'voice':
                self.resources[resource_id] = file_path
                print(f"Added voice file with ID {resource_id} at path {file_path}")
            else:
                # Add logic here to handle other resource types when needed
                print(f"Unsupported resource type for file at path {file_path}")
                pass

        print("Resources initialized successfully.")
        return self.resources

    @staticmethod
    def detect_resource_type(file_path):
        _, file_extension = os.path.splitext(file_path)

        if file_extension.lower() in ['.png', '.jpg', '.jpeg', '.gif']:
            return 'image'
        elif file_extension.lower() in ['.mp3', '.wav', '.ogg']:  # Add this block
            return 'voice'
        else:
            # Add logic here to detect other resource types based on file extensions when needed
            pass

