from langgraph.graph import StateGraph, START, END, MessagesState
from langgraph.checkpoint.memory import MemorySaver

from agents.state import (
    State, 
    generate_test_cases, 
    collect_additional_context_and_feedback, 
    update_test_cases, 
    should_process_feedback
)

# Setup LangGraph
checkpointer = MemorySaver()
graph = (StateGraph(State)
        .add_node("generate_test_cases", generate_test_cases)
        .add_node("collect_feedback", collect_additional_context_and_feedback)
        .add_node("update_test_cases", update_test_cases)
        .add_conditional_edges(
            "collect_feedback",
            should_process_feedback,
            {
                "update_test_cases": "update_test_cases",
                "end": END
            }
        )
        .add_edge(START, "generate_test_cases")
        .add_edge("generate_test_cases", "collect_feedback")
        .add_edge("update_test_cases", "collect_feedback")
        .add_edge("collect_feedback", END)
        .compile(interrupt_before=["collect_feedback"], checkpointer=checkpointer)
        )