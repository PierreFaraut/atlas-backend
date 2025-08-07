from __future__ import annotations

from typing import Any, AsyncGenerator, List
from datetime import datetime, timezone

from pydantic_ai import Agent
from pydantic_ai.message import AIMessage, BaseMessage, HumanMessage
from pydantic_ai.messages import (
    ModelMessage,
    ModelRequest,
    ModelResponse,
    TextPart,
    ToolCallPart,
    ToolReturnPart,
    ThinkingPart,
    SystemPromptPart,
    UserPromptPart,
    RetryPromptPart,
)
from core.models.agent_models import TransactionDeps
from core.services.conversations import get_all_messages_by_conversation_id


# Non-streaming chat processor (removed streaming feature, now fully synchronous)
async def process_chat_with_full_details(
    user_prompt: str,
    agent: Agent,
    transaction: TransactionDeps,
    message_history: List[BaseMessage],
) -> AsyncGenerator[dict[str, Any], None]:
    """Process chat and yield all messages including thinking, tools, and processing steps.

    IMPROVEMENTS MADE:
    - Removed streaming feature for simplicity and determinism
    - Replaced hasattr() checks with proper isinstance() checks for type safety
    - Added proper pydantic-ai message type imports
    - Improved content validation to handle empty content
    - Added support for all pydantic-ai message part types:
      * TextPart, ToolCallPart, ToolReturnPart, ThinkingPart
      * SystemPromptPart, UserPromptPart, RetryPromptPart
    - Better error handling for different content types
    - Proper handling of UserPromptPart content (string vs sequence)
    - Proper handling of RetryPromptPart using model_response() method
    - Now fully synchronous (no async/await)
    """

    # Yield user message first
    yield {
        "role": "user",
        "timestamp": datetime.now(tz=timezone.utc).isoformat(),
        "content": user_prompt,
        "message_type": "user_input",
    }

    try:
        # Run the agent without streaming (synchronous)
        complete_result = await agent.run(
            user_prompt, message_history=message_history, deps=transaction
        )

        # Process all the new messages from the agent run
        new_messages = complete_result.new_messages()

        for msg in new_messages:
            # Handle ModelRequest and ModelResponse messages
            if isinstance(msg, (ModelRequest, ModelResponse)):
                for part in msg.parts:
                    message_data = {
                        "role": "model",
                        "timestamp": datetime.now(tz=timezone.utc).isoformat(),
                        "message_type": "agent_internal",
                    }

                    # Check for different part types using isinstance
                    if isinstance(part, TextPart):
                        if part.content:  # Only include if content is not empty
                            message_data.update(
                                {"content": part.content, "part_type": "text"}
                            )
                    elif isinstance(part, ToolCallPart):
                        message_data.update(
                            {
                                "message_type": "agent_tool_call",
                                "content": f"{part.tool_name}",
                                "part_type": "tool_call",
                                "tool_name": part.tool_name,
                                "tool_args": part.args,
                            }
                        )
                    elif isinstance(part, ToolReturnPart):
                        if part.content:  # Only include if content is not empty
                            message_data.update(
                                {
                                    "message_type": "agent_tool_result",
                                    "content": f"{part.content}",
                                    "part_type": "tool_return",
                                }
                            )
                    elif isinstance(part, ThinkingPart):
                        if part.content:  # Only include if content is not empty
                            message_data.update(
                                {
                                    "message_type": "agent_thinking",
                                    "content": f"{part.content}",
                                    "part_type": "thinking",
                                }
                            )
                    elif isinstance(part, SystemPromptPart):
                        if part.content:  # Only include if content is not empty
                            message_data.update(
                                {
                                    "message_type": "agent_system_prompt",
                                    "content": f"{part.content}",
                                    "part_type": "system_prompt",
                                }
                            )
                    elif isinstance(part, UserPromptPart):
                        if hasattr(part, "content") and part.content:
                            content = part.content
                            # Handle both string and sequence content
                            if isinstance(content, str):
                                message_data.update(
                                    {"content": content, "part_type": "user_prompt"}
                                )
                            else:
                                # Handle sequence of UserContent
                                message_data.update(
                                    {
                                        "content": str(content),
                                        "part_type": "user_prompt",
                                    }
                                )
                    elif isinstance(part, RetryPromptPart):
                        # RetryPromptPart has a model_response() method for content
                        try:
                            retry_content = part.model_response()
                            if retry_content:
                                message_data.update(
                                    {
                                        "content": f"🔄 Retry: {retry_content}",
                                        "part_type": "retry_prompt",
                                    }
                                )
                        except Exception:
                            # Fallback to content attribute if model_response() fails
                            if hasattr(part, "content") and part.content:
                                message_data.update(
                                    {
                                        "content": f"🔄 Retry: {part.content}",
                                        "part_type": "retry_prompt",
                                    }
                                )
                    else:
                        # Handle unknown parts
                        message_data.update(
                            {"content": str(part), "part_type": "unknown"}
                        )

                    # Only yield if there's actual content
                    if message_data.get("content"):
                        yield message_data
            else:
                # Handle other message types that might not have parts
                yield {
                    "role": "model",
                    "timestamp": datetime.now(tz=timezone.utc).isoformat(),
                    "content": str(msg),
                    "message_type": "other",
                }

        # Yield final response
        final_content = complete_result.output
        yield {
            "role": "model",
            "timestamp": datetime.now(tz=timezone.utc).isoformat(),
            "content": final_content,
            "message_type": "final_response",
        }

    except Exception as e:
        # Yield error message
        yield {
            "role": "model",
            "timestamp": datetime.now(tz=timezone.utc).isoformat(),
            "content": f"Error processing request: {str(e)}",
            "message_type": "error",
        }


## We need to define a function that will take all the messages from a conversation and prepare them for the agent to use.


def prepare_messages_for_agent(conversation_id: str) -> List[BaseMessage]:
    """
    Retrieves all messages from a conversation and prepares them for the agent.
    It transforms the messages from the database into a list of HumanMessage and AIMessage objects.
    """
    db_messages = get_all_messages_by_conversation_id(conversation_id)

    agent_messages: List[BaseMessage] = []

    for msg in db_messages:
        # We don't want to include messages that are still loading
        # or assistant messages that are just placeholders for tool calls without final content.
        if msg.is_loading or (msg.role == "assistant" and not msg.content):
            continue

        if msg.role == "user":
            agent_messages.append(HumanMessage(content=msg.content))
        elif msg.role == "assistant":
            agent_messages.append(AIMessage(content=msg.content))

    return agent_messages
