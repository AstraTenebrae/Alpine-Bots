from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from serializers import BotSerializer, ScenarioSerializer, StepSerializer
from models import Bot, Scenario, Step

class BotViewSet(viewsets.ModelViewSet):
    serializer_class = BotSerializer

    def get_queryset(self):
        return Bot.objects.filter(user=self.request.user)
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class ScenarioViewSet(viewsets.ModelViewSet):
    serializer_class = ScenarioSerializer

    def get_queryset(self):
        return Scenario.objects.filter(bot__user=self.request.user)
    
    @action(detail=True, methods=['get'])
    def steps(self, request, pk=None):
        scenario = self.get_object()
        steps = scenario.steps.all()
        serializer = StepSerializer(steps, many=True)
        return Response(serializer.data)
    
class StepViewSet(viewsets.ModelViewSet):
    serializer_class = StepSerializer
    
    def get_queryset(self):
        return Step.objects.filter(scenario__bot__user=self.request.user)