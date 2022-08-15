from solana.publickey import PublicKey
from dataclasses import dataclass
from .Table import Table


@dataclass(unsafe_hash=True)
class Users(Table):

    # table name
    _table_name = "users"

    # column names
    uid: int
    address: PublicKey
    email: str
    twitter_id: int
    twitter_username: str
    twitter_avatar_url: str
    discord_id: int
    discord_username: str
    discord_avatar_url: str
    creation_timestamp: int
    updated_timestamp: int
