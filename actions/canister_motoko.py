"""Functions to interact with canister_motoko, using ic-py

Reference: https://github.com/rocklabs-io/ic-py
"""
import base64
from typing import Union, List, Dict
import logging

from ic.canister import Canister  # type: ignore
from ic.client import Client  # type: ignore
from ic.identity import Identity  # type: ignore
from ic.agent import Agent  # type: ignore

from . import settings

logger = logging.getLogger(__name__)

# Read the private key from the .pem file for the `bot-0-action-server` Identity
private_key = base64.b64decode(settings.BOT_0_ACTION_SERVER_IC_IDENTITY_PEM_ENCODED)


# Create an `bot-0-action-server` Identity instance using the private key
identity = Identity.from_pem(private_key)

# Create an HTTP client instance for making HTTPS calls to the IC
# https://smartcontracts.org/docs/interface-spec/index.html#http-interface
client = Client(url=settings.IC_NETWORK_URL)

# Create an IC agent to communicate with IC canisters
agent = Agent(identity, client)

# Read canister_motoko candid from file
with open(
    settings.BASE_DIR / "actions/candid/canister_motoko.did", "r", encoding="utf-8"
) as f:
    canister_motoko_did = f.read()

# Create a canister_motoko canister instance
canister_motoko = Canister(
    agent=agent, canister_id=settings.CANISTER_MOTOKO_ID, candid=canister_motoko_did
)

# Configuration check
def canister_motoko_health() -> bool:
    """Call the canister_motoko.whoami() method."""
    logger.debug(f"principal of bot-0-action-server: {identity.sender().to_str()}")
    response = canister_motoko.whoami()  # pylint: disable=no-member
    logger.debug("Response from canister_motoko.whoami(): ")
    logger.debug(response)
    logger.info("canister_motoko is up & running.")
    return True


def is_response_variant_ok(
    response: Union[str, List[Dict[str, Union[str, Dict[str, str]]]]]
) -> bool:
    """Returns true if the response is of type=variant with a key=ok"""
    if response == "rejected":
        return False

    if not isinstance(response, list):
        return False

    r = response[0]

    # Format of the ic network, eg.:
    # [{'ok': None}]
    if "ok" in r.keys():
        return True

    # Format of the local network, eg.:
    # [{'type': 'variant', 'value': {'ok': None}}]
    if "type" in r.keys() and r["type"] == "variant":
        if isinstance(r["value"], dict):
            if "ok" in r["value"].keys():
                return True

    return False
