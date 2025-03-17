from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Union
from langchain_core.output_parsers import PydanticOutputParser


class TestScenarioModel(BaseModel):
    input: Union[Dict[str, Any], str] = Field(description="Input data for the test scenario. Can be a dictionary of key-value pairs or a string.")
    steps: Union[Dict[str, Any], List[str]] = Field(description="Steps to execute the test scenario as a list of strings")

class TestCaseModel(BaseModel):
    brd_scope: str = Field(description="Business requirement document scope")
    brd_fr_no: str = Field(description="Business requirement functional requirement number")
    acceptance_criteria_no: str = Field(description="Acceptance criteria number")
    acceptance_criteria_summary: str = Field(description="Summary of acceptance criteria")
    test_scenario_id: str = Field(description="Unique identifier for the test scenario")
    test_scenarios: TestScenarioModel = Field(description="Test scenario")
    expected_result: str = Field(description="Expected result of the test case")
    reference_document: str = Field(description="Reference document")
    status: str = Field(description="Status of the test case")
    defect_comment: Optional[str] = Field(default="", description="Comments about defects")
    label: str = Field(description="Label for the test case")
    component: str = Field(description="Component being tested")

class TestCaseDataParser(BaseModel):
    test_cases: List[TestCaseModel] = Field(description="List of Testcases")

class TestDataParser(BaseModel):
    test_data: List[Dict[str, Any]] = Field(description="Test Data for Test Cases")

class GenerateTestRequest(BaseModel):
    text: str
    additional_context: Optional[str] = ""

class FeedbackRequest(BaseModel):
    feedback: str
    additional_context: str = ""

class SessionRequest(BaseModel):
    session_id: str
    
test_case_parser = PydanticOutputParser(pydantic_object=TestCaseDataParser)
test_data_parser = PydanticOutputParser(pydantic_object=TestDataParser)
