from rest_framework import serializers

from .models import Bot, Scenario, Step

from .scenario_service import ScenarioManager

class StepSerializer(serializers.ModelSerializer):
    class Meta:
        model = Step
        fields = '__all__'

class ScenarioSerializer(serializers.ModelSerializer):
    steps = StepSerializer(many=True, read_only=True)
    class Meta:
        model = Scenario
        fields = '__all__'

    def validate_scenario_data(self, value):
        if value and not ScenarioManager.validate_scenario_format(value):
            raise serializers.ValidationError("Невалидный формат сценария")
        return value

class BotSerializer(serializers.ModelSerializer):
    scenarios = ScenarioSerializer(many=True, read_only=True)
    class Meta:
        model = Bot
        fields = '__all__'

class ChatSerializer(serializers.Serializer):
    message = serializers.CharField(
        required=True, 
        min_length=1,
        max_length=1000,
        help_text="Сообщение для бота"
    )