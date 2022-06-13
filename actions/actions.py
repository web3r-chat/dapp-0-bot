# This files contains your custom actions which can be used to run
# custom Python code.
"""Custom actions for the bot"""

from typing import Any, Text, Dict, List
import logging
import jwt

from rasa_sdk import Action, Tracker  # type: ignore
from rasa_sdk.executor import CollectingDispatcher  # type: ignore
from rasa_sdk.events import SlotSet, EventType  # type: ignore

from . import settings
from .custom_forms import CustomFormValidationAction

from .canister_motoko import (
    canister_motoko,
    # canister_motoko_health,
    is_response_variant_ok,
)

BOT_VERSION = "0.1.0"
logger = logging.getLogger(__name__)
logger.info(f"BOT_VERSION: {BOT_VERSION}")

# for debug purposes
# canister_motoko_health()


class ActionBotChallenge(Action):  # pylint: disable type: ignore
    """Demo action to call api_greet of canister_cpp"""

    def name(self) -> Text:
        return "action_bot_version"

    async def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        dispatcher.utter_message(
            text=f"You are chatting with bot-0, version {BOT_VERSION}"
        )

        return []


class ActionConnect(Action):  # # type: ignore type: ignore
    """Verifies JWT, and if valid,
    (-) extracts the principal and store it.
    (-) fills the slots for the canister_motoko, used in responses"""

    def name(self) -> Text:
        return "action_connect"

    async def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        slots = {
            "jwt": None,
            "principal": None,
            "canister_motoko_id": None,
            "canister_motoko_candid_ui": None,
        }

        jwt_token = tracker.get_slot("jwt")
        if jwt_token is None:
            return []

        try:
            jwt_decoded = jwt.decode(
                jwt_token,
                settings.SECRET_JWT_KEY,
                algorithms=[settings.JWT_METHOD],
            )

            try:
                principal = jwt_decoded["sub"]
                slots["jwt"] = jwt_token
                slots["principal"] = principal
                slots["canister_motoko_id"] = settings.CANISTER_MOTOKO_ID  # type: ignore
                slots[
                    "canister_motoko_candid_ui"
                ] = settings.CANISTER_MOTOKO_CANDID_UI  # type: ignore
            except:
                dispatcher.utter_message(text="ERROR: jwt payload is not valid")

        except Exception as inst:  # pylint: disable=broad-except
            text = f"ERROR: jwt is not valid \n" f"{type(inst)}" f"{inst}"
            logger.debug(text)
            dispatcher.utter_message(text=text)

        return [SlotSet(slot, value) for slot, value in slots.items()]


class ValidateSmartcontractDemoForm(CustomFormValidationAction):
    """Validates Slots of the smartcontract_demo_form"""

    def name(self) -> Text:
        """Unique identifier of the action"""
        return "validate_smartcontract_demo_form"

    async def validate_smartcontract_demo_1_start(  # pylint: disable=no-self-use
        self,
        value: Text,
        _dispatcher: CollectingDispatcher,
        _tracker: Tracker,
        _domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """Validates value of 'smartcontract_demo_1_start' slot"""
        # We ask `Continue?`, for which a method is provided:
        return await super().continue_yes_or_no("smartcontract_demo_1_start", value)

    async def validate_smartcontract_demo_2_intro(  # pylint: disable=no-self-use
        self,
        value: Text,
        _dispatcher: CollectingDispatcher,
        _tracker: Tracker,
        _domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """Validates value of 'smartcontract_demo_2_intro' slot"""
        # We ask `Continue?`, for which a method is provided:
        return await super().continue_yes_or_no("smartcontract_demo_2_intro", value)

    async def validate_smartcontract_demo_3_ask_secret_message(  # pylint: disable=no-self-use
        self,
        value: Text,
        _dispatcher: CollectingDispatcher,
        tracker: Tracker,
        _domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """Validates value of 'smartcontract_demo_3_ask_secret_message' slot"""
        principal = tracker.get_slot("principal")
        response = canister_motoko.save_message(  # pylint: disable=no-member
            principal, value
        )
        if is_response_variant_ok(response):
            return {"smartcontract_demo_3_ask_secret_message": value}

        return {"smartcontract_demo_3_ask_secret_message": None}


class ActionSubmitSmartcontractDemoForm(Action):
    """Submits the form, which just resets all the slots."""

    def name(self) -> Text:
        """Unique identifier of the action"""
        return "action_submit_smartcontract_demo_form"

    async def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        """Executes the action"""
        slots = {
            "AA_CONTINUE_FORM": "yes",
            "smartcontract_demo_1_start": None,
            "smartcontract_demo_2_intro": None,
            "smartcontract_demo_3_ask_secret_message": None,
            "zz_confirm_form": None,
        }

        return [SlotSet(slot, value) for slot, value in slots.items()]
