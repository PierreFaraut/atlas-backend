from pydantic import BaseModel, Field
from typing import List, Literal, Union


class Step(BaseModel):
    """Represents a step"""

    id: str = Field(..., description="The unique identifier for the step")
    ### Basic informations
    message_id: str = Field(..., description="The unique identifier for the message")

    ### Agent Informations
    agent_id: str = Field(..., description="The id of the agent")

    ### Steps information
    description: str = Field(..., description="The description of the step")


class StepSearch(Step):
    """Represents a step in a research."""

    type: Literal["search"] = "search"
    sources: List[str] = Field(..., description="List of sources for the step")


class StepDatabase(Step):
    """Represents a step in a database query."""

    type: Literal["database"] = "database"
    query: str = Field(..., description="The SQL query executed in the step")
    database_id: str = Field(..., description="The unique identifier for the database")
    results: str | None = Field(
        default=None, description="The results of the SQL query executed in the step"
    )
    result_type: str = Field(
        default="text",
        description="The type of the result of the SQL query executed in the step",
    )


# Union de tous les types de steps possibles. Très pratique.
AnyStep = Union[StepSearch, StepDatabase]


class Message(BaseModel):
    """Represents a message in a conversation."""

    id: str = Field(..., description="The unique identifier for the message")
    conversation_id: str = Field(
        ..., description="The ID of the conversation this message belongs to"
    )
    role: Literal["user", "assistant"] = Field(
        ..., description="The role of the message sender"
    )
    content: str = Field(..., description="The content of the message")
    steps: List[AnyStep] = Field(
        default_factory=list,
        description="List of steps taken by the assistant to generate this message",
    )
    is_loading: bool = Field(
        default=False, description="Whether the message is loading or not"
    )


class Conversation(BaseModel):
    """Represents a conversation with a user."""

    id: str = Field(..., description="The unique identifier for the conversation")
    user_id: str = Field(..., description="The unique identifier for the user")
    messages: List[Message] = Field(
        ..., description="List of messages in the conversation"
    )
    title: str = Field(..., description="The title of the conversation")
