from solana.publickey import PublicKey
from dataclasses import dataclass
from .Table import Table


@dataclass(unsafe_hash=True)
class Users(Table):

    # table name
    _table_name = "assets"

    # column names
    uid: int
    file_path: str
    file_type: str
    file_name: str
    file_size_bytes: int
    user_uid: int
    purchase_type: str
    purchase_price: float
    transaction_signature: str
    confirmed: int
    confirmation_attempts: int
    creation_timestamp: int
    confirmation_timestamp: int
