import os
import json
import logging
import pandas as pd
from datetime import datetime
from http import HTTPStatus
from typing import Annotated, Any, List, Optional, Dict

from fastapi import APIRouter, Body, Header, Response, Request, HTTPException, status, Query
from fastapi.responses import FileResponse
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langgraph.graph import StateGraph, START, END, MessagesState
from langgraph.checkpoint.memory import MemorySaver


from models.test_case import GenerateTestRequest, FeedbackRequest, SessionRequest
from agents.graph import graph
from models.response import SessionResponse
from core.session_manager import session_manager
from core.config import config

logging = logging.getLogger(__name__)

router = APIRouter()

@router.post("/generate-tests")
async def generate_tests(request: GenerateTestRequest):
    try:
        session_id = session_manager.initialize_session()
        user_input = request.text
        additional_context = request.additional_context or ""

        initial_state = {
            "messages": [HumanMessage(content=user_input)],
            "additional_context": additional_context
        }
        
        thread_id = f"test_gen_{session_id}"
        thread_config = {"configurable": {"thread_id": thread_id}}
        result = graph.invoke(initial_state, config=thread_config)

        test_cases = result.get('test_cases', {})
        content = test_cases.strip('"').replace('\\"','"')
        json_data = json.loads(content)
        df = pd.DataFrame(json_data['test_cases'])


        session_manager.save_data_to_session(session_id=session_id, key="user_input", data=user_input)
        session_manager.save_data_to_session(session_id=session_id, key="additional_context", data=additional_context)
        session_manager.save_data_to_session(session_id=session_id, key="thread_id", data=thread_id)
        session_manager.save_data_to_session(session_id=session_id, key="test_cases", data=df)

        return {
            "session_id": session_id,
            "test_cases": df
        }

    except Exception as e:
        logging.error(f"Error generating tests: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    

@router.post("/update-tests")
async def update_tests(request: FeedbackRequest, session_id: str):
    try:
        thread_id = session_manager.fetch_session_data(session_id=session_id, key="thread_id")
        if thread_id is None:
            raise HTTPException(status_code=400, detail= "No active test generation in this session")
        
        if isinstance(thread_id, list) and thread_id:
            thread_id = thread_id[0] 
        
        thread_config = {'configurable':{"thread_id":thread_id}}
        feedback: str = request.feedback
        additional_context: str = request.additional_context
        
        graph.update_state(
            thread_config,
            {
                "user_feedback": feedback or "",
                "additional_context": additional_context or ""
            },
            as_node="collect_feedback"
        )
        result = graph.invoke(None, config=thread_config)
        test_cases = result.get('test_cases',{})
        content = test_cases.strip('"').replace('\\"','"')
        json_data = json.loads(content)
        df = pd.DataFrame(json_data['test_cases'])

        session_manager.save_data_to_session(session_id, "additional_context", additional_context)
        session_manager.save_data_to_session(session_id, "feedback", feedback)
        session_manager.save_data_to_session(session_id=session_id, key="test_cases", data=df)

        current_session_additional_context = session_manager.fetch_session_data(session_id, key= "additional_context")
        session_user_input = session_manager.fetch_session_data(session_id, key= "user_input")
        current_session_feedback = session_manager.fetch_session_data(session_id, key= "feedback")
        current_session_test_cases = session_manager.fetch_session_data(session_id, key= "test_cases")

        return{
            "session_id": session_id,
            "session_user_input":session_user_input,
            "current_session_additional_context": current_session_additional_context,
            "current_session_feedback": current_session_feedback,
            "current_session_test_cases": current_session_test_cases
        }

    except Exception as e:
        logging.error(f"Error updating tests: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/end-session")
async def terminate_session(session_id: str):
    try:
        success, session_details = session_manager.terminate_session(session_id=session_id)
        if not success:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return SessionResponse(
            session_id= session_id,
            created_at= session_details["created_at"].isoformat(),
            status= session_details["status"]
        )
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error ending session: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/session-status")
async def session_status(session_id:str):
    session = session_manager.retrieve_session_info(session_id=session_id)
    if not session:
        raise HTTPException(status_code=404,  detail="Session not found")
    return SessionResponse(
        session_id=session_id,
        created_at= session["created_at"].isoformat(),
        status= session["status"],
    )

@router.get("/sessions")
async def get_all_sessions_with_data():
    try:
        all_sessions_info = session_manager.retrieve_session_info()
        
        response = {
            "total_sessions": len(all_sessions_info),
            "active_sessions": session_manager.count_active_sessions(),
            "sessions": {}
        }
        
        for session_id in all_sessions_info:
            session_info = all_sessions_info[session_id]
            
            response["sessions"][session_id] = {
                "info": session_info
            }
            
        return response
    except Exception as e:
        logging.error(f"Error retrieving sessions with data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

    
@router.get("/export-csv")
async def download_csv(session_id: str):
    """Download the generated test cases as a CSV file for a specific session"""
    try:
        test_cases = session_manager.fetch_session_data(session_id, "test_cases")
        if not test_cases:
            raise HTTPException(status_code=404, detail="Test data not found for this session")
        
        additional_context = session_manager.fetch_session_data(session_id, "additional_context")
        user_input = session_manager.fetch_session_data(session_id, "user_input")
        feedback = session_manager.fetch_session_data(session_id, "feedback")
        
        logging.info(f"Exporting CSV from session {session_id}")
        
        if isinstance(test_cases, list):
            if all(isinstance(item, pd.DataFrame) for item in test_cases):
                test_cases = pd.concat(test_cases, ignore_index=True).to_dict(orient='records')
            elif not all(isinstance(item, dict) for item in test_cases) and test_cases:
                test_cases = test_cases[-1]
        
        for test in test_cases:
            test["additional_context"] = additional_context[-1] if isinstance(additional_context, list) and additional_context else additional_context
            test["user_input"] = user_input[-1] if isinstance(user_input, list) and user_input else user_input
            test["feedback"] = feedback[-1] if isinstance(feedback, list) and feedback else feedback
        
        # Generate CSV file
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"test_cases_{session_id[:8]}_{timestamp}.csv"
        filepath = os.path.join(os.path.dirname(config.CSV_FILE), filename)
        
        # Save to CSV
        df = pd.DataFrame(test_cases)
        df.to_csv(filepath, index=False)
        
        return FileResponse(
            path=filepath,
            filename=os.path.basename(filepath),
            media_type="text/csv"
        )

    except Exception as e:
        logging.error(f"CSV export error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error exporting to CSV: {str(e)}")