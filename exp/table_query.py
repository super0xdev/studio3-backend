import tables
from conf.consts import ADMIN_WALLET_ADDRESS

users = tables.Users.select(address=ADMIN_WALLET_ADDRESS)


