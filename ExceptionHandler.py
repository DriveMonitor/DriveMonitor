class AuthenticationError(Exception):
    def __init__(self, message="Authentication failed"):
        self.message = message
        super().__init__(self.message)

class DriveAPIError(Exception):
    def __init__(self, message="Drive API encountered an error"):
        self.message = message
        super().__init__(self.message)
