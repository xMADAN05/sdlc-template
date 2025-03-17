import uuid
import pandas as pd
from datetime import datetime, timedelta
from typing import Union, Dict, Any, List

from core.config import config


class SessionManager:
    def __init__(self):
        self.session_data: Dict[str, Dict[str, List[Dict[str, Any]]]] = {}
        self.session_info: Dict[str, Dict[str, Any]] = {}
    
    def initialize_session(self):
        id = uuid.uuid4() 
        session_id = f"test_gen_{id}"
        self.session_info[session_id] = {
            'created_at': datetime.now(),
            'last_activity': datetime.now(),
            'status': 'active'
        }
        self.session_data[session_id] = {}
        return session_id
    
    def retrieve_session_info(self, session_id):
        if session_id in self.session_info:
            return self.session_info[session_id]
        return None
    
    def terminate_session(self, session_id):
        if session_id in self.session_info:
            self.session_info[session_id]["status"] = "inactive"
            return True, self.session_info[session_id]
        return False, None
    
    def save_data_to_session(self , session_id: str, key: str, data: Union[Dict[str, Any], pd.DataFrame]):
        if session_id not in self.session_data:
            return False
        
        
        if isinstance(data, pd.DataFrame):
            data = data.to_dict(orient='records')
        
        if key not in self.session_data[session_id]:
            self.session_data[session_id][key] = []
        self.session_data[session_id][key].append(data)
        self.session_data[session_id]["last_activity"] = datetime.now()
        return True
    
    def fetch_session_data(self, session_id, key = None):
        if session_id not in self.session_data:
            return None
        data = self.session_data[session_id] if key is None else self.session_data[session_id].get(key, [])
        if isinstance(data, list) and all(isinstance(d, list) for d in data) and all(isinstance(d[0], dict) for d in data if d):  # Check if list of DataFrame
            return [pd.DataFrame(d) for d in data]
        return data
    
    def remove_inactive_sessions(self):
        current_time = datetime.now()
        timeout_threshold = timedelta(seconds=config.SESSION_TIMEOUT)
        expired_sessions = [id for id, info in self.session_info.items() if current_time - info['last_activity'] > timeout_threshold]
        inactive_sessions = [id for id in self.session_info if self.session_info[id]['status'] == 'inactive']
        
        for id in expired_sessions+ inactive_sessions:
            self.session_info.pop(id, None)
            self.session_data.pop(id, None)
            
    def count_active_sessions(self):
        return sum(1 for session in self.session_info.values() if session['status'] == 'active')


session_manager = SessionManager()
