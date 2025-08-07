from dotenv import load_dotenv

load_dotenv()

import asyncio
from core.research_agent import research_agent as agent
from core.models.agent_models import TransactionDeps
from core.agent_utils import process_chat_with_full_details

from rich.console import Console
from rich.text import Text

from core.services.messages import save_message

console = Console()

# Color mapping for message_type
MESSAGE_TYPE_STYLES = {
    "user_input": "bold cyan",
    "agent_internal": "dim white",
    "agent_tool_call": "bold yellow",
    "agent_tool_result": "green",
    "agent_thinking": "italic magenta",
    "agent_system_prompt": "bold blue",
    "user_prompt": "cyan",
    "retry_prompt": "bold red",
    "final_response": "bold green",
    "error": "bold red",
    "other": "white",
    "unknown": "bold red",
}

ICON_MAP = {
    "user_input": "👤",
    "agent_internal": "🤖",
    "agent_tool_call": "🔧",
    "agent_tool_result": "📊",
    "agent_thinking": "💭",
    "agent_system_prompt": "🛠️",
    "user_prompt": "👤",
    "retry_prompt": "🔄",
    "final_response": "✅",
    "error": "❌",
    "other": "❓",
    "unknown": "❓",
}


def print_rich_message(message: dict):
    message_type = message.get("message_type", "other")
    style = MESSAGE_TYPE_STYLES.get(message_type, "white")
    icon = ICON_MAP.get(message_type, "")
    content = message.get("content", "")
    timestamp = message.get("timestamp", "")
    role = message.get("role", "")

    # Compose header
    header = f"[{timestamp}]"
    if role:
        header += f" [{role.upper()}]"
    if icon:
        header += f" {icon}"

    # Compose text
    text = Text(header, style="dim") + Text(" ")

    # Main content
    text.append(str(content), style=style)

    console.print(text)


async def main():
    conversation_id = "b1a3b532-3327-4031-a535-a7a349ad4660"
    new_message = save_message(conversation_id, content="", is_loading=True)
    new_transaction = TransactionDeps(message_id=new_message.id)

    user_input = "How many pokemon are there in all generations? "

    async for message in process_chat_with_full_details(
        user_input, agent, new_transaction
    ):
        # print_rich_message(message)

        ## All tools
        ## Final response should be saved to database in a new message with message_type "final_response"
        if message.get("message_type") == "final_response":
            new_message = save_message(
                conversation_id,
                content=message.get("content"),
                is_loading=False,
                id=new_message.id,
            )
            print(new_message)


if __name__ == "__main__":
    asyncio.run(main())
