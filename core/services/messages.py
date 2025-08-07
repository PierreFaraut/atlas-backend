from core.database import supabase_client
from core.models.chat_models import Message


def save_message(
    conversation_id: str,
    content: str,
    role_name: str = "assistant",
    is_loading: bool = True,
    id: str = None,
):
    """
    Save a message to the database. If id is provided, update the existing message.
    Returns a Message instance.
    """
    if id is None:
        response = (
            supabase_client.table("messages")
            .insert(
                {
                    "conversation_id": conversation_id,
                    "content": content,
                    "role": role_name,
                    "is_loading": is_loading,
                }
            )
            .execute()
        )
    else:
        response = (
            supabase_client.table("messages")
            .update(
                {
                    "conversation_id": conversation_id,
                    "content": content,
                    "role": role_name,
                    "is_loading": is_loading,
                }
            )
            .eq("id", str(id))
            .execute()
        )

    # Supabase returns a dict with a 'data' key containing a list of rows
    data = getattr(response, "data", None)
    if not data or not isinstance(data, list) or len(data) == 0:
        raise ValueError("No data returned from Supabase when saving message.")

    message = Message(**data[0])
    return message
