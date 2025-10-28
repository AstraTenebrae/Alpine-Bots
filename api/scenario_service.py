from typing import Dict, Any, Optional
from .chatbot_service import chat_bot

class ScenarioEngine:
    def __init__(self, scenario_data: Dict[str, Any]):
        self.scenario_data = scenario_data
        self.current_state = scenario_data.get('initial_state', 'start')
    
    def get_current_state_config(self) -> Optional[Dict[str, Any]]:
        return self.scenario_data.get('states', {}).get(self.current_state)
    
    def _create_success_response(self, response: str, next_state: str) -> Dict[str, Any]:
        return {
            'response': response,
            'current_state': self.current_state,
            'next_state': next_state,
            'is_finished': next_state == 'end',
            'error': None
        }
    
    def _create_error_response(self, error_msg: str) -> Dict[str, Any]:
        return {
            'response': "Извините, произошла ошибка.",
            'current_state': self.current_state,
            'next_state': self.current_state,
            'is_finished': False,
            'error': error_msg
        }
    
    def _build_prompt(self, prompt_template: str, user_input: str, context: str) -> str:
        if context:
            return f"{prompt_template}\n\nКонтекст диалога:\n{context}\n\nТекущий ввод: {user_input}"
        return f"{prompt_template}\n\nВвод пользователя: {user_input}"
    
    def _determine_next_state(self, user_input: str, current_state: Dict[str, Any]) -> str:
        user_input_lower = user_input.lower()
        transitions = current_state.get('transitions', {})
        
        for keyword, next_state in transitions.items():
            if keyword.lower() in user_input_lower:
                return next_state
        
        return current_state.get('default_next_state', 'end')
    
    def process_user_input(self, user_input: str, conversation_context: str = "") -> Dict[str, Any]:
        current_state_config = self.get_current_state_config()
        if not current_state_config:
            return self._create_error_response("Состояние сценария не найдено")

        try:
            prompt_template = current_state_config.get('prompt', '')
            full_prompt = self._build_prompt(prompt_template, user_input, conversation_context)
            
            bot_response = chat_bot.generate_response(full_prompt)
            next_state = self._determine_next_state(user_input, current_state_config)
            self.current_state = next_state
            
            return self._create_success_response(bot_response, next_state)
            
        except Exception as e:
            print(f"Ошибка обработки сценария: {e}")
            return self._create_error_response(str(e))
    

class ScenarioManager:
    @staticmethod
    def validate_scenario_format(scenario_data: Dict[str, Any]) -> bool:
        required_keys = {'initial_state', 'states'}
        if not all(key in scenario_data for key in required_keys):
            return False
        
        states = scenario_data['states']
        if not states or scenario_data['initial_state'] not in states:
            return False
        
        for state_name, state_config in states.items():
            if not isinstance(state_config, dict):
                return False
        return True
    
    @staticmethod
    def get_default_scenario() -> Dict[str, Any]:
        return {
            "initial_state": "welcome",
            "states": {
                "welcome": {
                    "prompt": "Ты приветственный бот. Поприветствуй пользователя и спроси, чем ты можешь помочь.",
                    "transitions": {
                        "помощь": "help",
                        "услуги": "services",
                        "контакты": "contacts"
                    },
                    "default_next_state": "help",
                    "fallback_state": "welcome"
                },
                "help": {
                    "prompt": "Ты помощник. Опиши, какие услуги ты предоставляешь. Будь дружелюбным и полезным.",
                    "transitions": {
                        "контакты": "contacts",
                        "назад": "welcome"
                    },
                    "default_next_state": "help",
                    "fallback_state": "welcome"
                },
                "services": {
                    "prompt": "Расскажи о конкретных услугах компании. Упомяни консультации, поддержку и другие услуги.",
                    "transitions": {
                        "контакты": "contacts",
                        "помощь": "help"
                    },
                    "default_next_state": "services",
                    "fallback_state": "welcome"
                },
                "contacts": {
                    "prompt": "Предоставь контактную информацию: телефон, email, адрес. Заверши разговор вежливо.",
                    "transitions": {
                        "спасибо": "end",
                        "пока": "end"
                    },
                    "default_next_state": "end",
                    "fallback_state": "welcome"
                },
                "end": {
                    "prompt": "Попрощайся с пользователем и пожелай хорошего дня.",
                    "transitions": {},
                    "default_next_state": "end"
                }
            }
        }