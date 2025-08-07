from core.database import supabase_client
from core.models.chat_models import Message


def get_all_messages_by_conversation_id(conversation_id: str):
    response = (
        supabase_client.table("messages")
        .select("*")
        .eq("conversation_id", conversation_id)
        .order("created_at", desc=False)
        .execute()
    )

    data = getattr(response, "data", None)
    if not data or not isinstance(data, list) or len(data) == 0:
        raise ValueError("No data returned from Supabase when getting messages.")

    messages = [Message(**message) for message in data]

    return messages
