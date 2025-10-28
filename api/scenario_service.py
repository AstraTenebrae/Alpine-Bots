import json
from typing import Dict, Any, Optional
from .chatbot_service import chat_bot

class ScenarioEngine:
    def __init__(self, scenario_data: Dict[str, Any]):
        self.scenario_data = scenario_data
        self.current_state = scenario_data.get('initial_state', 'start')
        self.conversation_history = []
    
    def get_current_state(self) -> Optional[Dict[str, Any]]:
        return self.scenario_data.get('states', {}).get(self.current_state)
    
    def process_user_input(self, user_input: str) -> Dict[str, Any]:
        current_state = self.get_current_state()
        if not current_state:
            return {
                'response': "Извините, произошла ошибка в сценарии.",
                'current_state': self.current_state,
                'is_finished': True
            }
        
        self.conversation_history.append(f"Пользователь: {user_input}")
        
        prompt_template = current_state.get('prompt', '')
        
        context = "\n".join(self.conversation_history[-6:])
        full_prompt = f"{prompt_template}\n\nКонтекст диалога:\n{context}\n\nТекущий ввод пользователя: {user_input}"
        
        try:
            bot_response = chat_bot.generate_response(full_prompt)            
            self.conversation_history.append(f"Бот: {bot_response}")
            next_state = self._determine_next_state(user_input, current_state)
            self.current_state = next_state
            is_finished = self.current_state == 'end' or not self.scenario_data.get('states', {}).get(self.current_state)
            
            return {
                'response': bot_response,
                'current_state': self.current_state,
                'next_state': next_state,
                'is_finished': is_finished
            }
            
        except Exception as e:
            fallback_state = current_state.get('fallback_state', 'error')
            self.current_state = fallback_state
            
            return {
                'response': "Извините, произошла ошибка при обработке вашего запроса.",
                'current_state': self.current_state,
                'is_finished': False,
                'error': str(e)
            }
    
    def _determine_next_state(self, user_input: str, current_state: Dict[str, Any]) -> str:
        user_input_lower = user_input.lower()
        transitions = current_state.get('transitions', {})
        for keyword, next_state in transitions.items():
            if keyword.lower() in user_input_lower:
                return next_state
        return current_state.get('default_next_state', self.current_state)
    
    def reset(self):
        self.current_state = self.scenario_data.get('initial_state', 'start')
        self.conversation_history = []


class ScenarioManager:
    @staticmethod
    def validate_scenario_format(scenario_data: Dict[str, Any]) -> bool:
        try:
            if 'initial_state' not in scenario_data:
                return False
            
            states = scenario_data.get('states', {})
            if not states:
                return False
            if scenario_data['initial_state'] not in states:
                return False
            for state_name, state_data in states.items():
                if 'prompt' not in state_data:
                    return False
            return True
        except Exception:
            return False
    
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