import base64
import json


def base64url_decode(input_bytes: bytes) -> bytes:
    rem = len(input_bytes) % 4

    if rem > 0:
        input_bytes += b"=" * (4 - rem)

    return base64.urlsafe_b64decode(input_bytes)


def parse_jwt_for_expiration(string: str) -> int:
    jwt = string.encode("utf-8")

    signing_input, _ = jwt.rsplit(b".", 1)
    _, payload_segment = signing_input.split(b".", 1)

    payload = base64url_decode(payload_segment)
    payload_data = json.loads(payload)

    assert isinstance(payload_data["exp"], int)

    return payload_data["exp"]
