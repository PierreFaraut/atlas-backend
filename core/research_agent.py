from pydantic_ai import Agent, RunContext
from core.models.agent_models import TransactionDeps
from core.services.steps import save_search_step, save_database_step
from core.llm import model, settings
from exa_py import Exa
import os
import sqlite3
from rich.console import Console

console = Console()

exa = Exa(api_key=os.environ.get("EXA_API_KEY"))

AGENT_ID = "research_agent"
RESEARCH_SYSTEM_PROMPT = """<role>
You are a world-class Research and Synthesis Agent. Your purpose is to provide definitive, comprehensive, and well-structured answers to complex queries. You are an expert at taking a simple question, understanding its true, deeper intent, and leveraging all available resources to deliver a complete response.
</role>

<data_sources>
You have access to two primary data sources:
1.  **Internal Database (`pokedex.sqlite`):** This database contains structured information, primarily about Pokémon. Use this for queries that seem to involve specific data points, lists, or relationships within the Pokémon universe (e.g., "list all legendary pokemon", "what are the stats of Pikachu", "pokemon of type fire").
2.  **Web Search (Exa):** Use this for general knowledge queries, current events, or any information not found within the internal database.
</data_sources>

<core_workflow>
1.  **Interpret and Plan:** Analyze the query to determine the best source(s) of information.
    - If the query is about structured data likely found in the `pokedex.sqlite` database, your plan should prioritize using `list_database_tables()`, `get_table_schema(table_name)`, and `run_sql_query(query)`.
    - If the query is general, requires current information, or is outside the scope of the Pokémon database, your plan should be to use `search_the_web(query)`.
    - For complex queries, you may combine both sources, using the database for structured data and web search for supplementary context or broader understanding.
2.  **Gather Information:** Execute your plan by calling the appropriate tool(s). Use them as many times as necessary to gather sufficient, high-quality information.
3.  **Synthesize and Write with Authority:** Critically evaluate all gathered information. Discard irrelevant details. Synthesize the findings into a coherent, well-written, and comprehensive answer.
    - Your writing must be objective, factual, and expert.
    - Use Markdown for clear, structured formatting (e.g., `## Headers`, `- Lists`, `**bolding**`).
    - For mathematical expressions, use LaTeX.
    - Do NOT include conversational text like "Here is the information you requested."
4.  **Final Answer:** Return ONLY the final, complete, and self-contained text that directly answers the query.
</core_workflow>

<restrictions>
- **NEVER ask for clarification.** It is your job to interpret the query's intent and deliver a complete answer.
- **NEVER return a partial answer.** Your response must be comprehensive.
- You DO NOT interact with the end-user. Your client is another AI agent (the Redactor Agent).
- Your response MUST be a complete, self-contained text.
</restrictions>"""


research_agent = Agent(
    model,
    system_prompt=RESEARCH_SYSTEM_PROMPT,
    model_settings=settings,
    deps_type=TransactionDeps,
)

DB_PATH = "data/pokedex.sqlite"


@research_agent.tool
def search_the_web(ctx: RunContext[str], query: str, description: str) -> str:
    """Searches the web for a given query using Exa and returns the results. Must provide a description to explain the goal of the search in the style of "We need to ..." """

    new_step = save_search_step(
        message_id=ctx.deps.message_id,
        description=description,
        agent_id=AGENT_ID,
        sources=[],
        is_loading=True,
    )

    result = exa.search_and_contents(query, num_results=5, text=True)

    save_search_step(
        message_id=ctx.deps.message_id,
        description=description,
        agent_id=AGENT_ID,
        sources=[source.url for source in result.results],
        id=new_step.id,
        is_loading=False,
    )
    return str(result)


@research_agent.tool
def list_database_tables(
    ctx: RunContext[str],
    description: str = "List all tables available in the internal SQLite database",
) -> str:
    """Lists all tables available in the internal SQLite database. Must provide a description  in the style of "We need to ..." to explain the goal of the search."""

    new_step = save_database_step(
        message_id=ctx.deps.message_id,
        description=description,
        agent_id=AGENT_ID,
        query="SELECT name FROM sqlite_master WHERE type='table';",
        database_id=DB_PATH,
        is_loading=True,
    )
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = [row[0] for row in cursor.fetchall()]
            if not tables:
                result = "Error: No tables found in the database."
            else:
                result = (
                    f"Success: The following tables are available: {', '.join(tables)}"
                )

            save_database_step(
                message_id=ctx.deps.message_id,
                description=description,
                agent_id=AGENT_ID,
                query="SELECT name FROM sqlite_master WHERE type='table';",
                database_id=DB_PATH,
                results=",".join(tables),
                id=new_step.id,
                is_loading=False,
                result_type="list",
            )
            return result
    except Exception as e:
        return f"Error: Could not list database tables. Reason: {e}"


@research_agent.tool
def get_table_schema(
    ctx: RunContext[str],
    table_name: str,
    description: str = "Get the schema for a specific table in the database",
) -> str:
    """Returns the schema (columns and their types) for a specific table in the database. Must provide a description  in the style of "We need to ..." to explain the goal of the search."""

    new_step = save_database_step(
        message_id=ctx.deps.message_id,
        description=description,
        agent_id=AGENT_ID,
        query=f"PRAGMA table_info({table_name});",
        database_id=DB_PATH,
        is_loading=True,
    )

    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute(f"PRAGMA table_info({table_name});")
            schema = cursor.fetchall()
            if not schema:
                result = f"Error: Table '{table_name}' not found."
            else:
                columns = [f"{col[1]} ({col[2]})" for col in schema]
                result = (
                    f"Success: Schema for table '{table_name}': {', '.join(columns)}"
                )

            save_database_step(
                message_id=ctx.deps.message_id,
                description=description,
                agent_id=AGENT_ID,
                query=f"PRAGMA table_info({table_name});",
                database_id=DB_PATH,
                results=",".join(columns),
                id=new_step.id,
                is_loading=False,
                result_type="list",
            )
            return result
    except Exception as e:
        return f"Error: Could not get schema for table {table_name}. Reason: {e}"


@research_agent.tool
def run_sql_query(
    ctx: RunContext[str],
    query: str,
    description: str = "Run a SQL query against the internal database",
) -> str:
    """Executes a SQL query against the internal database. Must provide a description  in the style of "We need to ..." to explain the goal of the query."""

    new_step = save_database_step(
        message_id=ctx.deps.message_id,
        description=description,
        agent_id=AGENT_ID,
        query=query,
        database_id=DB_PATH,
        is_loading=True,
    )
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute(query)

            columns = [description[0] for description in cursor.description]
            results = cursor.fetchall()

            if not results:
                return (
                    "Success: The query executed successfully but returned no results."
                )

            # Format results as a string
            formatted_results = f"Query Results ({len(results)} rows):\n"
            formatted_results += ", ".join(columns) + "\n"
            for row in results:
                formatted_results += ", ".join(map(str, row)) + "\n"

            save_database_step(
                message_id=ctx.deps.message_id,
                description=description,
                agent_id=AGENT_ID,
                query=query,
                database_id=DB_PATH,
                results=formatted_results,
                id=new_step.id,
                is_loading=False,
                result_type="text",
            )
            return formatted_results
    except Exception as e:
        return f"Error: The SQL query failed. Reason: {e}"
