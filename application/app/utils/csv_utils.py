import json
import pandas as pd
from utils.logger import logging

from core.config import *

def json_to_dataframe(test_cases_json):
    """Convert validated test case data to pandas DataFrame"""
    try:
        # Parse the JSON string if it's a string
        if isinstance(test_cases_json, str):
            test_cases_json = test_cases_json.strip('"').replace('\\"', '"')
            data = json.loads(test_cases_json)
        else:
            data = test_cases_json
            
        # Extract test cases list
        if isinstance(data, dict) and "test_cases" in data:
            test_cases = data["test_cases"]
        else:
            test_cases = data
            
        records = []
        for test_case in test_cases:
            # Handle steps formatting based on type
            if isinstance(test_case["test_scenarios"]["steps"], list):
                steps = " | ".join(test_case["test_scenarios"]["steps"])
            elif isinstance(test_case["test_scenarios"]["steps"], dict):
                steps = " | ".join([f"{k}: {v}" for k, v in test_case["test_scenarios"]["steps"].items()])
            else:
                steps = str(test_case["test_scenarios"]["steps"])
                
            # Handle input formatting based on type
            if isinstance(test_case["test_scenarios"]["input"], dict):
                input_data = str(test_case["test_scenarios"]["input"])
            else:
                input_data = test_case["test_scenarios"]["input"]
                
            records.append({
                "BRD Scope": test_case["brd_scope"],
                "BRD FR No": test_case["brd_fr_no"],
                "Acceptance Criteria No": test_case["acceptance_criteria_no"],
                "Acceptance Criteria Summary": test_case["acceptance_criteria_summary"],
                "Test Scenario ID": test_case["test_scenario_id"],
                "Test Scenario Input": input_data,
                "Test Scenario Steps": steps,
                "Expected Result": test_case["expected_result"],
                "Reference Document": test_case["reference_document"],
                "Status": test_case["status"],
                "Defect Comment": test_case.get("defect_comment", ""),
                "Label": test_case["label"],
                "Component": test_case["component"]
            })
        return pd.DataFrame(records)
    except Exception as e:
        logging.error(f"Error converting JSON to DataFrame: {e}")
        raise

def save_to_csv(test_cases_data, filename=Config.CSV_FILE):
    """Save DataFrame to CSV file"""
    df = json_to_dataframe(test_cases_data)
    df.to_csv(filename, index=False)
    return filename