from pydantic_ai import Agent, RunContext
from core.models import Page, Section, TextResult, KPIResult
import json
from core.llm import model, settings
from core.research_agent import research_agent

REDACTOR_SYSTEM_PROMPT = """<role>
You are the Redactor Agent, a meticulous and autonomous report editor. Your single most important responsibility is to ensure the report you manage strictly adheres to the official methodology. You are relentless in your pursuit of this perfection.
</role>

<core_workflow>
Your operation is a continuous loop of "Assess, Plan, Act" until the report is perfect. You do not stop until the "Assess" phase passes with zero issues.

1.  **ASSESS:**
    a. First, call the `get_methodology()` tool to get the quality standards.
    b. Then, call the `read_report()` tool to get the current state of the report.
    c. Compare the report against the methodology. Identify ALL deviations (e.g., missing Introduction, missing Conclusion, incorrect order, poor formatting).

2.  **PLAN:**
    a. Based on your assessment and the user's most recent request, decide on the **single next action** to move the report closer to perfection.
    b. Examples of actions:
        - If the Introduction is missing, your plan is to delegate research for it.
        - If the user asks for a new section, your plan is to delegate research for that section.
        - If the Conclusion is missing, your plan is to delegate research for it.
        - If a section is out of order, your plan is to fix it.

3.  **ACT:**
    a. Execute the single action from your plan by calling the appropriate tool (e.g., `ask_research_agent_for_help`, `add_text_section`, `update_text_section`).

4.  **LOOP:**
    a. After the action is complete, you MUST immediately return to Step 1: ASSESS.

5.  **COMPLETE:**
    a. You are only finished with your task when the ASSESS step reveals zero deviations from the methodology.
    b. Only then will you provide a brief confirmation message to the user.
</core_workflow>

<restrictions>
- Your internal loops of assessing and fixing are your primary function. Do not explain them to the user.
- NEVER ask the user for clarification. Make expert assumptions.
- Your final output to the user is a simple confirmation of the original request, not a report of all the self-corrections you made.
</restrictions>"""


redactor_agent = Agent(
    model,
    system_prompt=REDACTOR_SYSTEM_PROMPT,
    model_settings=settings,
)


@redactor_agent.tool_plain
def get_methodology() -> str:
    """Returns the non-negotiable methodology and quality standards for structuring a report."""
    return """
    # Report Structure Methodology (Mandatory)

    A high-quality report MUST adhere to the following structure at all times. All content must be formatted in Markdown. LaTeX should be used for mathematical elements.

    ---

    ### 1. Introduction (Mandatory First Section)
    The report **MUST** begin with a section titled "Introduction". If this section is missing, it must be created and populated. This section must contain:
    - **Topic Introduction:** A brief overview of the subject.
    - **Problematic:** A clear and concise explanation of the core question or problem the report addresses.
    - **Hypothesis:** The proposition or theory that the report will investigate.
    - **Data Used:** A description of the data sources that will be used for the analysis.

    ---

    ### 2. Details (Main Body)
    This is the main body of the report, composed of multiple "sections".
    - A section is a self-contained piece of analysis (text, KPI, chart, etc.).
    - Sections must be logically ordered to build a narrative.

    ---

    ### 3. Conclusion (Mandatory Last Section)
    The report **MUST** end with a section titled "Conclusion". If this section is missing, it must be created and populated. This section must contain:
    - **Recap and Answers:** A summary of the key findings and a direct answer to the problematic stated in the introduction.
    - **Next Steps:** A discussion of potential future actions, further research, or implications of the findings.
    """


@redactor_agent.tool_plain
def read_report() -> Page:
    """Reads the report from the result.json file."""
    print("📖 Reading report ...")
    with open("result.json", "r") as f:
        data = json.load(f)
    return Page(**data)


def save_report(page: Page):
    """Saves the report to the result.json file."""
    print("💾 Saving report ...")
    with open("result.json", "w") as f:
        json.dump(page.model_dump(), f, indent=4)


@redactor_agent.tool
def add_text_section(ctx: RunContext[str], text: str) -> str:
    """Adds a new text section to the report."""
    print("📝 Adding text section ...")
    page = read_report()
    new_section = Section(type="text", result=TextResult(text=text))
    page.content.append(new_section)
    save_report(page)
    return f"Successfully added a new text section."


@redactor_agent.tool
def add_kpi_section(ctx: RunContext[str], kpi: str, description: str) -> str:
    """Adds a new KPI section to the report."""
    print("📊 Adding KPI section ...")
    page = read_report()
    new_section = Section(
        type="kpi", result=KPIResult(kpi=kpi, description=description)
    )
    page.content.append(new_section)
    save_report(page)
    return f"Successfully added a new KPI section."


@redactor_agent.tool
def update_text_section(ctx: RunContext[str], section_index: int, new_text: str) -> str:
    """Updates an existing text section in the report."""
    print("📝 Updating text section ...")
    page = read_report()
    if 0 <= section_index < len(page.content):
        if page.content[section_index].type == "text":
            page.content[section_index].result.text = new_text
            save_report(page)
            return f"Successfully updated text section {section_index}."
        else:
            return f"Error: Section {section_index} is not a text section."
    else:
        return f"Error: Section index {section_index} is out of bounds."


@redactor_agent.tool
def delete_section(ctx: RunContext[str], section_index: int) -> str:
    """Deletes a section from the report."""
    print("🗑️ Deleting section ...")
    page = read_report()
    if 0 <= section_index < len(page.content):
        page.content.pop(section_index)
        save_report(page)
        return f"Successfully deleted section {section_index}."
    else:
        return f"Error: Section index {section_index} is out of bounds."


@redactor_agent.tool_plain
def list_sections() -> str:
    """Lists all the sections in the report."""
    print("📝 Listing sections ...")
    page = read_report()
    if not page.content:
        return "The report is empty."

    sections_info = []
    for i, section in enumerate(page.content):
        if section.type == "text":
            sections_info.append(f"Section {i} (Text): {section.result.text[:50]}...")
        elif section.type == "kpi":
            sections_info.append(
                f"Section {i} (KPI): {section.result.kpi} - {section.result.description}"
            )

    return "\n".join(sections_info)


@redactor_agent.tool
def ask_research_agent_for_help(ctx: RunContext[str], query: str) -> str:
    """Asks the research agent for help with a specific query."""
    print("🧠 Asking research agent for help ...")
    response = research_agent.run_sync(query)
    return response