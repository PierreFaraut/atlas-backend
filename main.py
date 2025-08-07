import functions_framework
from dotenv import load_dotenv

load_dotenv()

from core.research_agent import research_agent as agent
from core.models.agent_models import TransactionDeps
from core.agent_utils import process_chat_with_full_details

from core.services.messages import save_message


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
    request_json = request.get_json(silent=True)
    request_args = request.args

    if request_json and "user_input" in request_json:
        user_input = request_json["user_input"]
    elif request_args and "user_input" in request_args:
        user_input = request_args["user_input"]
    else:
        return "No user_input provided", 400

    if request_json and "conversation_id" in request_json:
        conversation_id = request_json["conversation_id"]
    elif request_args and "conversation_id" in request_args:
        conversation_id = request_args["conversation_id"]
    else:
        return "No conversation_id provided", 400

    def run_agent():
        new_message = save_message(conversation_id, content="", is_loading=True)
        new_transaction = TransactionDeps(message_id=new_message.id)

        for message in process_chat_with_full_details(
            user_input, agent, new_transaction
        ):
            if message.get("message_type") == "final_response":
                save_message(
                    conversation_id,
                    content=message.get("content"),
                    is_loading=False,
                    id=new_message.id,
                )

    run_agent()
    return "OK", 200
