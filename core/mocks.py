from core.models import Page, Section, TextResult, KPIResult
import json

class MockResearchAgent:
    def run_sync(self, query: str) -> str:
        print(f"🧠 Mock Research Agent received query: {query}")
        if "legendary pokemon" in query.lower():
            return """## Legendary Pokémon\n\n- Articuno\n- Zapdos\n- Moltres\n- Mewtwo\n- Mew\n- Lugia\n- Ho-Oh\n- Kyogre\n- Groudon\n- Rayquaza\n- Deoxys\n- Jirachi\n- Celebi\n- Manaphy\n- Darkrai\n- Shaymin\n- Arceus\n- Victini\n- Reshiram\n- Zekrom\n- Kyurem\n- Keldeo\n- Meloetta\n- Genesect\n- Xerneas\n- Yveltal\n- Zygarde\n- Diancie\n- Hoopa\n- Volcanion\n- Magearna\n- Marshadow\n- Zeraora\n- Meltan\n- Melmetal\n- Zacian\n- Zamazenta\n- Eternatus\n- Kubfu\n- Urshifu\n- Regieleki\n- Regidrago\n- Glastrier\n- Spectrier\n- Calyrex\n- Enamorus\n- Koraidon\n- Miraidon\n- Walking Wake\n- Iron Leaves\n- Ogerpon\n- Pecharunt\n"""
        elif "nutritional value of bananas" in query.lower():
            return """## Nutritional Value of Bananas\n\nBananas are a rich source of essential nutrients, making them a popular and healthy fruit choice. A medium-sized banana (about 118 grams) typically provides:\n\n-   **Calories:** Approximately 105 kcal\n-   **Carbohydrates:** 27 grams, primarily in the form of natural sugars (glucose, fructose, sucrose) and dietary fiber.\n-   **Fiber:** 3.1 grams, contributing to digestive health and satiety.\n-   **Potassium:** 422 mg (9% of Daily Value), crucial for blood pressure regulation and heart health.\n-   **Vitamin B6:** 0.4 mg (24% of Daily Value), important for metabolism and brain function.\n-   **Vitamin C:** 10.3 mg (11% of Daily Value), an antioxidant that supports immune function.\n-   **Manganese:** 0.3 mg (16% of Daily Value), involved in bone health and metabolism.\n\nBananas also contain smaller amounts of magnesium, copper, and protein. Their natural sugars provide a quick energy boost, making them an excellent snack for athletes. The resistant starch in unripe bananas acts as a prebiotic, supporting gut health.\n"""
        elif "introduction to bananas" in query.lower():
            return """## Introduction to Bananas\n\nBananas, botanically classified as berries, are one of the world's most widely consumed fruits. Originating in Southeast Asia, they are now cultivated in tropical regions worldwide. This report aims to provide a comprehensive overview of bananas, covering their history, nutritional value, and economic importance.\n\n**Problematic:** Despite their global popularity, banana cultivation faces significant challenges, including disease susceptibility and environmental concerns. This report will explore these issues and potential solutions.\n\n**Hypothesis:** Sustainable cultivation practices and genetic advancements are crucial for the future of banana production.\n\n**Data Used:** Information for this report is sourced from scientific literature, agricultural reports, and economic data, supplemented by internal database queries where applicable.\n"""
        elif "conclusion about bananas" in query.lower():
            return """## Conclusion\n\nBananas are a vital global commodity, offering significant nutritional benefits and economic value. However, challenges such as disease and environmental impact necessitate a shift towards more sustainable and resilient cultivation methods.\n\n**Next Steps:** Future research should focus on developing disease-resistant varieties, optimizing sustainable farming techniques, and exploring new markets for diverse banana types to ensure the long-term viability of banana production.\n"""
        elif "annual global banana production in tonnes" in query.lower():
            return "115 million tonnes"
        else:
            return f"This is a mock research response for: {query}"

class MockRedactorAgent:
    def __init__(self):
        # Initialize with a default empty report structure
        self.page = Page(title="All About Bananas", sub_title="A comprehensive report on the world's most popular fruit.", content=[])
        self.methodology = self._get_methodology()
        self.research_agent = MockResearchAgent()

    def _get_methodology(self) -> str:
        """Returns the official methodology and quality standards for structuring a report."""
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

    def _assess_report(self) -> list[str]:
        """Assesses the current report against the methodology and returns a list of issues."""
        issues = []
        current_content = self.page.content
        
        # Check for Introduction
        has_intro = False
        if current_content and isinstance(current_content[0].result, TextResult) and "introduction" in current_content[0].result.text.lower():
            has_intro = True
        if not has_intro:
            issues.append("Missing or incorrect Introduction section at the beginning.")
        
        # Check for Conclusion
        has_conclusion = False
        if current_content and isinstance(current_content[-1].result, TextResult) and "conclusion" in current_content[-1].result.text.lower():
            has_conclusion = True
        if not has_conclusion:
            issues.append("Missing or incorrect Conclusion section at the end.")
            
        # Add more checks here as needed (e.g., formatting, logical flow)
        
        return issues

    def _save_report(self):
        """Saves the in-memory report to the result.json file."""
        with open("result.json", "w") as f:
            json.dump(self.page.model_dump(), f, indent=4)
        print("💾 Mock Redactor Agent saved report to result.json.")

    def run_sync(self, user_input: str) -> str:
        print(f"👤 Mock Redactor Agent received command: {user_input}")

        # Simulate the "Assess, Plan, Act" loop
        while True:
            issues = self._assess_report()
            
            # Prioritize fixing structural issues
            if issues:
                print(f"⚠️ Mock Redactor Agent found issues: {issues}. Planning to fix...")
                if "Missing or incorrect Introduction" in issues[0]:
                    research_result = self.research_agent.run_sync("introduction to bananas")
                    intro_section = Section(type="text", result=TextResult(text=research_result))
                    # Remove existing intro if it's not compliant but present
                    if self.page.content and isinstance(self.page.content[0].result, TextResult) and "introduction" in self.page.content[0].result.text.lower():
                        self.page.content.pop(0)
                    self.page.content.insert(0, intro_section) # Insert at the beginning
                    self._save_report()
                    print("📝 Added mock Introduction section.")
                    continue # Re-assess after fixing
                elif "Missing or incorrect Conclusion" in issues[0]:
                    research_result = self.research_agent.run_sync("conclusion about bananas")
                    conclusion_section = Section(type="text", result=TextResult(text=research_result))
                    # Remove existing conclusion if it's not compliant but present
                    if self.page.content and isinstance(self.page.content[-1].result, TextResult) and "conclusion" in self.page.content[-1].result.text.lower():
                        self.page.content.pop(-1)
                    self.page.content.append(conclusion_section) # Append at the end
                    self._save_report()
                    print("📝 Added mock Conclusion section.")
                    continue # Re-assess after fixing
                # Add more complex fixing logic here if needed
            
            # If no structural issues, or after fixing them, process user's request
            if "add a section about" in user_input.lower():
                topic = user_input.lower().split("add a section about")[-1].strip().replace(".", "")
                research_result = self.research_agent.run_sync(topic)
                new_section = Section(type="text", result=TextResult(text=research_result))
                # Insert new section before conclusion if conclusion exists
                if self.page.content and isinstance(self.page.content[-1].result, TextResult) and "conclusion" in self.page.content[-1].result.text.lower():
                    self.page.content.insert(len(self.page.content) - 1, new_section)
                else:
                    self.page.content.append(new_section)
                self._save_report()
                print(f"📝 Added mock section about: {topic}.")
                user_input = "" # Clear user input to prevent re-processing
                continue # Re-assess after adding user content
            elif "add a kpi for" in user_input.lower():
                kpi_description = user_input.lower().split("add a kpi for")[-1].strip().replace(".", "")
                # Mock research for KPI value
                kpi_value = self.research_agent.run_sync(kpi_description) # Research agent returns the value
                new_kpi_section = Section(type="kpi", result=KPIResult(kpi=kpi_value, description=kpi_description))
                
                # Insert new KPI section before conclusion if conclusion exists
                if self.page.content and isinstance(self.page.content[-1].result, TextResult) and "conclusion" in self.page.content[-1].result.text.lower():
                    self.page.content.insert(len(self.page.content) - 1, new_kpi_section)
                else:
                    self.page.content.append(new_kpi_section)
                self._save_report()
                print(f"📊 Added mock KPI for: {kpi_description}.")
                user_input = "" # Clear user input to prevent re-processing
                continue # Re-assess after adding user content
            elif "list sections" in user_input.lower():
                sections_info = []
                for i, section in enumerate(self.page.content):
                    if isinstance(section.result, TextResult):
                        sections_info.append(f"Section {i} (Text): {section.result.text[:50]}...")
                    elif isinstance(section.result, KPIResult):
                        sections_info.append(f"Section {i} (KPI): {section.result.kpi} - {section.result.description}")
                return f"Current sections:\n" + "\n".join(sections_info)
            
            # If no specific action was taken, and no issues, then we are done.
            self._save_report()
            return "Mock Redactor Agent processed the request and ensured report compliance."

mock_research_agent = MockResearchAgent()
mock_redactor_agent = MockRedactorAgent()
