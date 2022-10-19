

class InvalidTimestamp(Exception):
    def __init__(self):
        self.code = "INVALID_TIMESTAMP"


class InvalidSignature(Exception):
    def __init__(self):
        self.code = "INVALID_SIGNATURE"


class DuplicateWalletAddress(Exception):
    """Duplicate Wallet address"""
    def __init__(self):
        self.code = "DUPLICATE_WALLET_ADDRESS"


class MaxFileSizeExceeded(Exception):
    """Max File Size Exceeded"""
    def __init__(self):
        self.code = "MAX_FILE_SIZE_EXCEEDED"

