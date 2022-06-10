"""Returns a valid connect message, for testing purposes

Use from command line with:
  $ make connect

Use from python as:
  from .connect import connect
  welcome_message = connect()

"""
import json
from .jwt_create import jwt_create


def connect() -> str:
    """Returns the connect message"""
    d = {"jwt": jwt_create()}
    message = "/connect" + json.dumps(d)
    return message


if __name__ == "__main__":
    print(connect())
