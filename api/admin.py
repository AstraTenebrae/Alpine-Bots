from django.contrib import admin
from .models import Bot, Scenario, Step
from django import forms
import json


class ScenarioForm(forms.ModelForm):
    class Meta:
        model = Scenario
        fields = '__all__'
        widgets = {
            'scenario_data': forms.Textarea(attrs={'rows': 20, 'cols': 80}),
        }

    def clean_scenario_data(self):
        data = self.cleaned_data['scenario_data']
        try:
            if isinstance(data, str):
                json.loads(data)
            return data
        except json.JSONDecodeError as e:
            raise forms.ValidationError(f"Невалидный JSON: {e}")

@admin.register(Bot)
class BotAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'created_at', 'updated_at']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(Scenario)
class ScenarioAdmin(admin.ModelAdmin):
    list_display = ['name', 'bot', 'created_at', 'updated_at']
    list_filter = ['bot', 'created_at', 'updated_at']
    search_fields = ['bot', 'name', 'description']
    readonly_fields = ['created_at', 'updated_at']
    
    def scenario_preview(self, obj):
        if obj.scenario_data:
            states = obj.scenario_data.get('states', {})
            return f"{len(states)} состояний"
        return "Пустой сценарий"

@admin.register(Step)
class StepAdmin(admin.ModelAdmin):
    list_display = ['order', 'step_type', 'scenario', 'created_at']
    list_filter = ['step_type', 'scenario']
    search_fields = ['content']
    readonly_fields = ['created_at']    
