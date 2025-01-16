import hmac
import hashlib
import os
from dotenv import load_dotenv

load_dotenv()

SHARED_SECRET = os.getenv("SHARED_SECRET", "AEeyJhbGciOiJIUzUxMiIsImlzcyI6")

def verify_signature(body: str, signature_header: str) -> bool:
    try:
        parts = signature_header.split(',')
        if len(parts) != 2:
            return False

        t_part = parts[0]
        v1_part = parts[1]

        t = t_part.split('=')[1]
        v1 = v1_part.split('=')[1]

        body_to_sign = f"{t}.{body}".encode('utf-8')
        computed_hmac = hmac.new(SHARED_SECRET.encode('utf-8'), body_to_sign, hashlib.sha256).hexdigest()

        return hmac.compare_digest(computed_hmac, v1)
    except Exception as e:
        print(f"Error verifying signature: {e}")
        return False
