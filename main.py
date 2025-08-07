import functions_framework
from dotenv import load_dotenv

import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s"
)
logger = logging.getLogger(__name__)

load_dotenv()

from core.research_agent import research_agent as agent
from core.models.agent_models import TransactionDeps
from core.agent_utils import (
    process_chat_with_full_details,
    prepare_messages_for_agent,
)

from core.services.messages import save_message


import asyncio


@functions_framework.http
def new_message_request(request):
    """HTTP Cloud Function.
    Args:
        request (flask.Request): The request object.
        <https://flask.palletsprojects.com/en/1.1.x/api/#incoming-request-data>
    Returns:
        The response text, or any set of values that can be turned into a
        Response object using `make_response`
        <https://flask.palletsprojects.com/en/1.1.x/api/#flask.make_response>.
    """
    logger.info("Received new_message_request")
    request_json = request.get_json(silent=True)
    request_args = request.args

    logger.info(f"request_json: {request_json}")
    logger.info(f"request_args: {request_args}")

    if request_json and "user_input" in request_json:
        user_input = request_json["user_input"]
        logger.info(f"User input found in JSON: {user_input}")
    elif request_args and "user_input" in request_args:
        user_input = request_args["user_input"]
        logger.info(f"User input found in args: {user_input}")
    else:
        logger.warning("No user_input provided")
        return "No user_input provided", 400

    if request_json and "conversation_id" in request_json:
        conversation_id = request_json["conversation_id"]
        logger.info(f"Conversation ID found in JSON: {conversation_id}")
    elif request_args and "conversation_id" in request_args:
        conversation_id = request_args["conversation_id"]
        logger.info(f"Conversation ID found in args: {conversation_id}")
    else:
        logger.warning("No conversation_id provided")
        return "No conversation_id provided", 400

    async def run_agent():
        logger.info(f"Saving new message for conversation_id={conversation_id}")
        new_message = save_message(conversation_id, content="", is_loading=True)
        logger.info(f"New message saved with id={new_message.id}")
        new_transaction = TransactionDeps(message_id=new_message.id)
        logger.info(f"Created TransactionDeps with message_id={new_message.id}")

        # Prepare historical messages for the agent
        message_history = prepare_messages_for_agent(conversation_id)
        logger.info(f"Prepared {len(message_history)} messages for the agent.")

        try:
            async for message in process_chat_with_full_details(
                user_prompt=user_input,
                agent=agent,
                transaction=new_transaction,
                message_history=message_history,
            ):
                logger.info(f"Agent message: {message}")
                if message.get("message_type") == "final_response":
                    logger.info("Final response received, saving message content.")
                    save_message(
                        conversation_id,
                        content=message.get("content"),
                        is_loading=False,
                        id=new_message.id,
                    )
        except Exception as e:
            logger.error(f"Error during agent processing: {e}", exc_info=True)
            raise

    try:
        asyncio.run(run_agent())
        logger.info("Agent run completed successfully.")
        return "OK", 200
    except Exception as e:
        logger.error(f"Error in new_message_request: {e}", exc_info=True)
        return f"Internal server error: {e}", 500
