import time
from typing import Dict, Any, Optional
from speedruncompy.api import SpeedrunClient
from speedruncompy.endpoints import GetGameData, PutRunSettings, PutAuthLogin
from speedruncompy.auth import get_CSRF
from speedruncompy.datatypes import RunSettings

class API:
    def __init__(self, game_id: str):
        self.api = SpeedrunClient()
        self.game_id = game_id
        self.csrf_token = None
        self.game_data = None
        
    def login(self, username: str, password: str, token: Optional[str] = None):
        return PutAuthLogin(username, password, token, _api=self.api).perform()
    
    def get_csrf_token(self) -> str:
        self.csrf_token = get_CSRF(_api=self.api)
        return self.csrf_token
    
    def fetch_game_data(self) -> Dict[str, Any]:
        self.game_data = GetGameData(gameId=self.game_id).perform()
        return self.game_data
    
    def submit_run(self, data: Dict[str, Any], time_obj: Dict[str, int]) -> Any:
        settings = {
            'levelId': data['level_id'],
            'categoryId': data['category_id'],
            'playerNames': [p.strip() for p in data['players'].split(',') if p.strip()],
            'gameId': self.game_id,
            'platformId': "8gej2n93", # pc
            'date': int(time.time()),
            'video': data['video'],
            'videoState': 0,
            'comment': data['description'],
            'time': time_obj,
        }
        
        if data.get('variable_id') and data.get('variable_value_id'):
            settings['values'] = [{
                'variableId': data['variable_id'],
                'valueId': data['variable_value_id']
            }]
        
        run_settings = RunSettings(settings)
        return PutRunSettings(
            csrfToken=self.csrf_token,
            settings=run_settings,
            autoverify=False,
            _api=self.api
        ).perform()
