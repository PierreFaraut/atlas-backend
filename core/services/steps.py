from typing import List
from core.database import supabase_client
from core.models.chat_models import StepSearch, StepDatabase
from rich.console import Console

console = Console()


def save_search_step(
    message_id: str,
    description: str,
    agent_id: str,
    sources: List[str] = [],
    id: str = None,
    is_loading: bool = True,
):
    """
    Save a SearchStep to the database. If id is provided, update the existing step.
    Returns a StepSearch instance.
    """
    details = {
        "type": "search",
        "sources": sources,
    }
    step_data = {
        "message_id": message_id,
        "description": description,
        "agent_id": agent_id,
        "details": details,
        "is_loading": is_loading,
    }
    if id is None:
        response = supabase_client.table("steps").insert(step_data).execute()
    else:
        response = (
            supabase_client.table("steps").update(step_data).eq("id", str(id)).execute()
        )

    data = getattr(response, "data", None)
    if not data or not isinstance(data, list) or len(data) == 0:
        raise ValueError("No data returned from Supabase when saving search step.")

    step_data = data[0]
    step_details = step_data.get("details", {})
    step = StepSearch(
        id=step_data.get("id"),
        message_id=step_data.get("message_id"),
        description=step_data.get("description"),
        agent_id=step_data.get("agent_id"),
        sources=step_details.get("sources"),
        is_loading=step_data.get("is_loading"),
    )
    return step


def save_database_step(
    message_id: str,
    description: str,
    agent_id: str,
    query: str,
    database_id: str,
    id: str = None,
    results: str | None = None,
    is_loading: bool = True,
    result_type: str = "text",
):
    """
    Save a DatabaseStep to the database. If id is provided, update the existing step.
    Returns a StepDatabase instance.
    """
    details = {
        "type": "database",
        "database_id": database_id,
        "query": query,
        "result_type": result_type,
        "results": results,
    }
    step_data = {
        "message_id": message_id,
        "description": description,
        "agent_id": agent_id,
        "details": details,
        "is_loading": is_loading,
    }
    if id is None:
        response = supabase_client.table("steps").insert(step_data).execute()
    else:
        response = (
            supabase_client.table("steps").update(step_data).eq("id", str(id)).execute()
        )

    data = getattr(response, "data", None)
    if not data or not isinstance(data, list) or len(data) == 0:
        raise ValueError("No data returned from Supabase when saving database step.")

    step_data = data[0]
    step_details = step_data.get("details", {})
    step = StepDatabase(
        id=step_data.get("id"),
        message_id=step_data.get("message_id"),
        description=step_data.get("description"),
        agent_id=step_data.get("agent_id"),
        query=step_details.get("query"),
        database_id=step_details.get("database_id"),
        results=step_details.get("results"),
        result_type=step_details.get("result_type"),
        is_loading=step_data.get("is_loading"),
    )
    return step
