from django.db import models
from django.contrib.auth.models import User

class Bot(models.Model):
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=250, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    bot_config = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return f"Bot {self.name}"

class Scenario(models.Model):
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=250, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    bot = models.ForeignKey(Bot, on_delete=models.CASCADE)

    scenario_data = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return f"Scenario {self.name} of Bot {self.bot.name}"

class Step(models.Model):
    order = models.IntegerField()
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    scenario = models.ForeignKey(Scenario, on_delete=models.CASCADE)

    step_type = models.CharField(max_length=20, choices=[
        ('user_input', 'Ввод пользователя'),
        ('bot_response', 'Ответ бота'),
    ], default='bot_response')

    

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"Step {self.order} of Scenario {self.scenario.name}"
