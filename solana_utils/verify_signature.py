from solana.publickey import PublicKey
from nacl.signing import VerifyKey
import response_utils.exceptions as errors
import nacl.exceptions
import base58
import time

MAX_DELAY_SECONDS = 180


def verify_address_ownership(pubkey_str: str, signed_timestamp: int, signature_b58: bytes):
    latest_timestamp = int(time.time())
    slot_diff = latest_timestamp - int(signed_timestamp)
    slot_invalid = abs(slot_diff) > MAX_DELAY_SECONDS
    if slot_invalid:
        print(f"Received invalid timestamp: {signed_timestamp}. Difference from current timestamp: {latest_timestamp} is {slot_diff}, which must be less than {MAX_DELAY_SECONDS} slots old.")
        raise errors.InvalidTimestamp()
    pubkey = bytes(PublicKey(pubkey_str))
    msg = bytes(str(signed_timestamp), 'utf8')
    signature = base58.b58decode(signature_b58)
    try:
        VerifyKey(
            pubkey
        ).verify(
            smessage=msg,
            signature=signature
        )
    except nacl.exceptions.BadSignatureError as _e:
        raise errors.InvalidSignature()
    return True


