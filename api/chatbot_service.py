
from openai import OpenAI
import os

class PseudoBot:
    @staticmethod
    def generate_response(prompt: str, context=None):
        prompt_lower = prompt.lower()
        
        for word in ["привет", "здравствуй", "добрый день"]:
            if word in prompt_lower:
                return "Привет!!"
        for word in ["пока", "до завтра", "прощай", "до свидания"]:
            if word in prompt_lower:
                return "Прощай!!"
        return "Это тестовый скрипт"
    
    @staticmethod
    def generate_with_context(user_prompt: str):
        response = PseudoBot.generate_response(user_prompt)
        string_f = f"Ввод пользователя: {user_prompt}\nВывод бота: {response}"
        return string_f
    
class DeepSeekBot:
    def __init__(self):
        self.client = OpenAI(
            api_key=os.getenv('DEEPSEEK_API_KEY', ''),
            base_url="https://api.deepseek.com"
        )

    def generate_response(self, prompt: str, context=None):
        try:
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": "Ты полезный ассистент. Отвечай на русском языке."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip() # type: ignore
            
        except Exception as e:
            print(f"Ошибка с DeepSeek API: {e}")
            return "Извините, произошла ошибка при обработке вашего запроса."
    
    def generate_with_context(self, user_prompt: str):
        response = self.generate_response(user_prompt)
        return response


chat_bot = DeepSeekBot()