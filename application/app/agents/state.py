import json

from typing import List, Dict, Any, Optional, Union
from langgraph.types import Command, interrupt
from langgraph.graph import StateGraph, START, END, MessagesState
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from utils.logger import logging
from core.config import config
from models.test_case import test_case_parser, test_data_parser
from models.llms import llm


# ===== AGENTS CONTENT =====
class State(MessagesState):
    additional_context: str = ""
    test_cases: List = []
    user_feedback: str = "" 


def generate_test_cases(state: State):
    """
    Agent to generate test cases based on user input
    """
    template = config.TEST_CASE_TEMPLATE
    if state.get("additional_context"):
        template=f"{template}\n\nAdditional Context: {state.get('additional_context')}"
    
    format_instructions = test_case_parser.get_format_instructions()
    template = f"{template}\n\n{format_instructions}"
    system_message = SystemMessage(content=template)
    response = llm.invoke([system_message] + state["messages"])

    try:
        data = test_case_parser.parse(response.content)
        test_cases = data.model_dump_json()
        formatted_data = json.dumps(test_cases, indent=2)
        return {
            "messages": state["messages"] + [AIMessage(content=formatted_data)],
            "test_cases": test_cases
        }
    except Exception as e:
        logging.warning(f"Pydantic parsing failed: {e}")
        raise

def collect_additional_context_and_feedback(state: State):
    """
    Collect user feedback and additional context
    """
    user_feedback = interrupt("Provide feedback:")
    additional_context = interrupt("Provide additional context:")
    feedback_content = user_feedback.strip() if len(user_feedback)>1 else ""
    additional_context_content = additional_context.strip() if len(additional_context)>1 else ""

    return {
        "user_feedback": feedback_content,
        "additional_context": additional_context_content if additional_context_content else state.get("additional_context", ""),
        "messages": state["messages"] + [HumanMessage(content=user_feedback)]
    }

def update_test_cases(state: State):
    """
    Update test cases based on user feedback
    """
    format_instructions = test_case_parser.get_format_instructions()

    system_message = SystemMessage(content=f"""
    You are a test case refinement assistant. Based on the original test cases and user feedback, 
    generate updated test cases. Return your response in valid JSON format.

    Original Test Cases: {json.dumps(state.get('test_cases',{}), indent=2)}
    User Feedback: {json.dumps(state.get('user_feedback',''))}
    Additional Context from User: {state.get('additional_context','')}
    Format Instructions: {format_instructions}
    """)

    response = llm.invoke([system_message])

    try:
        data = test_case_parser.parse(response.content)
        test_cases = data.model_dump_json()
        formatted_data = json.dumps(test_cases, indent=2)
        return {
            "messages": state["messages"] + [AIMessage(content=formatted_data)],
            "test_cases": test_cases
        }
    except Exception as e:
        logging.warning(f"Pydantic parsing failed: {e}")
        raise

def should_process_feedback(state: State):
    """
    Determine if we should process feedback or end the flow
    """
    if state.get("user_feedback") == "done" or state.get("user_feedback") == "exit":
        return "end"
    return "update_test_cases"
