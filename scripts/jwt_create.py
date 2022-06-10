"""Creates a jwt, for testing purposes.

Use from command line with:
  $ make jwt

Use from python as:
  from .jwt_create import jwt_create
  jwt_token = jwt_create()

"""
import os
import sys
import time
import jwt

SECRET_JWT_KEY = os.environ.get("SECRET_JWT_KEY")
JWT_METHOD = os.environ.get("JWT_METHOD")

## Anonymous
## principal = "2vxsx-fae"

# Internet Identity running on local network - anchor 10000
PRINCIPAL = "rk6eu-2qxxx-qbzq6-iqgjb-mxhrj-wodmj-u5hn4-ojhty-nsedv-ilqlo-sae"


def jwt_create() -> str:
    """Returns a jwt that is valid for 8 hours"""

    # https://jwt.io/introduction
    # jwt = jwt_header.jwt_payload.hash
    # (-) All components of the jwt are base64 encoded
    # (-) jwt_header = {"alg": "HS256", "typ": "JWT"} is inserted by jwt.encode

    jwt_payload = {
        "iss": "web3r.chat",
        "exp": time.time() + 8 * 60 * 60,
        "sub": PRINCIPAL,
    }

    if SECRET_JWT_KEY is None:
        print("SECRET_JWT_KEY is not defined as environment variable.")
        sys.exit(1)

    if JWT_METHOD is None:
        print("JWT_METHOD is not defined as environment variable.")
        sys.exit(1)

    return jwt.encode(
        jwt_payload,
        SECRET_JWT_KEY,
        algorithm=JWT_METHOD,
        headers=None,
        json_encoder=None,
    )


if __name__ == "__main__":
    print(f"SECRET_JWT_KEY = {SECRET_JWT_KEY}")
    print(f"JWT_METHOD = {JWT_METHOD}")
    print(jwt_create())
