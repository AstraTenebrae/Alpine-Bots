from rest_framework import serializers

from models import Bot, Scenario, Step

class StepSerializer(serializers.ModelSerializer):
    class Meta:
        model = Step
        fields = '__all__'

class ScenarioSerializer(serializers.ModelSerializer):
    steps = StepSerializer(many=True, )
    class Meta:
        model = Scenario
        fields = '__all__'

class BotSerializer(serializers.ModelSerializer):
    scenarios = Scenario
    class Meta:
        model = Bot
        fields = '__all__'