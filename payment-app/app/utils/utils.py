import hashlib
import hmac


def verify_signature(secret_key: str, signature: str, payload_string: str) -> bool:
    computed_signature = hmac.new(
        secret_key.encode('utf-8'),
        payload_string.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(computed_signature, signature)
