"""Performs Rasa smoke tests"""
# pylint: disable=invalid-name
from typing import Any, Optional, Dict
import os
import sys
import time
import pprint

##import pathlib

import requests
from requests import request
import socketio  # type: ignore

from .jwt_create import jwt_create

##ROOT_PATH = pathlib.Path(__file__).parent.parent.resolve()


HEALTH_CHECK_RETRIES = int(os.environ.get("HEALTH_CHECK_RETRIES", 100))
SLEEP_TIME = int(os.environ.get("SLEEP_TIME", 1))
SOCKET_IO_WAIT_TIME_MAX = int(os.environ.get("SOCKET_IO_WAIT_TIME_MAX", 100))

BOT_URL = os.environ.get("BOT_URL")
if BOT_URL is not None:
    BOT_URL = BOT_URL.rstrip("/")

VERBOSE = int(os.environ.get("VERBOSE", 1))

print("------------------------------------")
print("Smoketest settings:")
print(f"-BOT_URL                : {BOT_URL}")
print(f"-HEALTH_CHECK_RETRIES   : {HEALTH_CHECK_RETRIES}")
print(f"-SOCKET_IO_WAIT_TIME_MAX: {SOCKET_IO_WAIT_TIME_MAX}")
print(f"-VERBOSE                : {VERBOSE}")
print("------------------------------------")


def my_print(msg: Any, status_code: Optional[int] = None) -> None:
    """Pretty print msg"""
    if VERBOSE > 0:
        if status_code:
            print(f"status_code: {status_code}")

        if isinstance(msg, (list, dict)):
            pprint.pprint(msg)
        else:
            print(msg)


if BOT_URL is None:
    my_print("BOT_URL is not defined as environment variable.")
    sys.exit(1)


###################################
my_print("--\nBOT_URL")
my_print(BOT_URL)

###################################
my_print("--\nRasa Health check")

url = f"{BOT_URL}"
attempt = 0
while True:
    try:
        attempt += 1
        r = request("GET", url)

        if r.status_code == 200:
            my_print(f"attempt {attempt} succeeded")
            break

        my_print(f"attempt {attempt} failed")
        my_print(r.json(), r.status_code)
    except requests.exceptions.ConnectionError as err:
        my_print(f"attempt {attempt} failed with requests.exceptions.ConnectionError")

    if attempt < HEALTH_CHECK_RETRIES:
        time.sleep(SLEEP_TIME)
        continue

    my_print("Too many failures...")
    sys.exit(1)


#################################
my_print("--\nVerify REST channel is not active. It must return a 404 status code")

url = f"{BOT_URL}/webhooks/rest/webhook"
payload: Dict[str, str] = {"message": "hi"}
##headers: dict = {"Authorization": f"Bearer {access_token}"}
headers: Dict[str, str] = {}
params: Dict[str, str] = {}
r = request("POST", url, json=payload, headers=headers, params=params)
if r.status_code != 404:
    print("Bot did not respond with 404 status code.")
    my_print(r.json(), r.status_code)
    print("Remove the REST channel from credentials.yml !")
    sys.exit(1)

my_print(r.json(), r.status_code)

#################################
# Test socket.io channel, which is used by the chat widget

url = f"{BOT_URL}"

## Defaults of sio.connect
##headers: dict = {}
##auth = None
##transports=None
##namespaces=None
##socketio_path='socket.io'
##wait=True
##wait_timeout=1

sio = socketio.Client()
##sio = socketio.Client(logger=True, engineio_logger=True)


@sio.on("connect")  # type: ignore
def on_connect() -> None:
    """."""
    my_print(f"- Connected to socket.io - Session ID = {sio.sid}")


def send_bot_version_intent() -> None:
    """."""
    global received_response  # pylint: disable=global-statement
    received_response = False

    data = {"message": "/bot_version"}
    sio.emit(event="user_uttered", data=data)

    my_print(f"\n- Sent user_uttered event with: {data}")


def say_are_you_a_bot() -> None:
    """."""
    global received_response  # pylint: disable=global-statement
    received_response = False

    data = {"message": "are you a bot"}
    sio.emit(event="user_uttered", data=data)

    my_print(f"\n- Sent user_uttered event with: {data}")


@sio.on("bot_uttered")  # type: ignore
def on_bot_uttered(data: Any) -> None:
    """Registered with socket.io to be called when server emits bot_uttered event"""
    global received_response  # pylint: disable=global-statement
    received_response = True
    my_print("- Received bot_uttered event from Rasa:")
    my_print(data)


def wait_for_response() -> None:
    """."""
    sleep_time_total = 0
    while not received_response:
        if sleep_time_total > 2:
            my_print(f"{sleep_time_total} - Still waiting for bot_uttered response...")
        if sleep_time_total < SOCKET_IO_WAIT_TIME_MAX:
            time.sleep(SLEEP_TIME)
            sleep_time_total += SLEEP_TIME
            continue

        sys.exit(1)


received_response: bool

##
my_print("--\nVerify that socket.io connection fails without JWT")
try:
    sio.connect(url)
    my_print('Connection did not fail without {"token": "jwt_encoded_payload"}')
    sio.disconnect()
    sys.exit(1)
except socketio.exceptions.ConnectionError as err:
    my_print('Connection correctly fails without {"token": "jwt_encoded_payload"}')

##
my_print("--\nVerify that socket.io connects properly with JWT")

## Connect and pass a jwt_token in the auth argument
jwt_token = jwt_create()
sio.connect(
    url,
    headers={},
    auth={"token": jwt_token},
    transports=None,
    namespaces=None,
    socketio_path="socket.io",
    wait=True,
    wait_timeout=1,
)
my_print("Connection established!")

##
my_print("--\nVerify sending bot_version intent to socket.io connection")
send_bot_version_intent()
wait_for_response()

##
my_print("--\nVerify sending 'are you a bot' to socket.io connection")
say_are_you_a_bot()
wait_for_response()

##
my_print("--\nVerify disconnecting from socket.io connection")
sio.disconnect()


###################################
my_print("--\nSmoke tests passed! ")
sys.exit(0)
