from solana.publickey import PublicKey
from dataclasses import dataclass
from dataclasses_json import dataclass_json
from .Table import Table


@dataclass_json
@dataclass(unsafe_hash=True)
class Assets(Table):

    # table name
    _table_name = "assets"

    # column names
    uid: int
    file_path: str
    meta_file_path: str
    thumbnail_file_path: str
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
    update_timestamp: int
