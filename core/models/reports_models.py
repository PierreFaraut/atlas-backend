from pydantic import BaseModel, Field
from typing import List


class TextResult(BaseModel):
    text: str = Field(..., description="The text content of the result")

    def to_markdown(self) -> str:
        return self.text


class KPIResult(BaseModel):
    kpi: str = Field(..., description="The KPI value")
    description: str = Field(None, description="Description of the KPI")

    def to_markdown(self) -> str:
        # markdown = '-----------------------'
        markdown = f"\n| **{self.kpi}** |"
        markdown += "\n-----------------------"
        markdown += f"\n| {self.description} |"
        markdown += "\n"
        return markdown


class Section(BaseModel):
    type: str = Field(..., description="The type of the section")
    result: KPIResult | TextResult = Field(..., description="The result of the section")

    def to_markdown(self) -> str:
        return self.result.to_markdown()


class Page(BaseModel):
    title: str = Field(..., description="The title of the page")
    sub_title: str = Field(..., description="The sub-title of the page")
    content: List[Section] = Field(..., description="The content of the page")

    def to_markdown(self) -> str:
        return_char = "\n"

        prep_text = f"# {self.title}\n\n"
        prep_text += f"> {self.sub_title}\n\n"
        prep_text += f"{return_char}{return_char}".join(
            [x.to_markdown() for x in self.content]
        )

        return prep_text
