import mysql.connector
import tables.sql.config as config
from solana.rpc.api import PublicKey
from dotenv import load_dotenv
import os
load_dotenv()

master_username = os.environ.get("master_username")
master_password = os.environ.get("master_password")


def pk2bin(pubkey_str):
    sample_pubkey = PublicKey(pubkey_str)
    return bytes(sample_pubkey).hex()


def initialize_connection_and_cursor():
    conn = mysql.connector.connect(user=master_username,
                                   password=master_password,
                                   host=config.endpoint,
                                   database=config.database)
    cursor = conn.cursor()
    return conn, cursor


def close_connection_and_cursor(conn, cursor):
    conn.commit()
    cursor.close()
    conn.close()

