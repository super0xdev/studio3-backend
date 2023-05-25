from solana.publickey import PublicKey
from dataclasses_json import dataclass_json
from dataclasses import dataclass
from .Table import Table


@dataclass_json
@dataclass(unsafe_hash=True)
class Tags(Table):

    # table name
    _table_name = "tags"

    # column names
    id: int
    tag: str
