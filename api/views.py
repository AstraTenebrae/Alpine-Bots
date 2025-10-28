from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .serializers import BotSerializer, ScenarioSerializer, StepSerializer, ChatSerializer
from .models import Bot, Scenario, Step

from .chatbot_service import chat_bot
from .scenario_service import ScenarioEngine, ScenarioManager

from django.db import transaction
from django.db.models import Max

class BotViewSet(viewsets.ModelViewSet):
    serializer_class = BotSerializer

    def get_queryset(self):
        return Bot.objects.filter(user=self.request.user)
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'], serializer_class=ChatSerializer)
    def chat(self, request, pk=None):
        bot = self.get_object()

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True) 
        user_message = serializer.validated_data['message']

        if not user_message:
            return Response({'error': 'Сообщение пустое'}, status=status.HTTP_400_BAD_REQUEST)
        
        active_scenario = self._get_or_create_active_scenario(bot)
        conversation_context = self._get_conversation_context(active_scenario)
        bot_response_data = self._process_message(
            bot, active_scenario, user_message, conversation_context
        )
        self._save_conversation_steps(active_scenario, user_message, bot_response_data['response'])
        return Response(bot_response_data, status=status.HTTP_200_OK)

    def _get_or_create_active_scenario(self, bot):
        active_scenario = bot.scenarios.filter(is_active=True).first()
        if not active_scenario:
            active_scenario = Scenario.objects.create(
                name=f"Активный сценарий для {bot.name}",
                bot=bot,
                is_active=True,
                scenario_data=ScenarioManager.get_default_scenario()
            )
        return active_scenario

    def _get_conversation_context(self, scenario, limit=3):
        steps = scenario.steps.order_by('-order')[:limit*2]
        context_lines = []
        for step in reversed(steps):
            role = "Пользователь" if step.step_type == 'user_input' else "Бот"
            context_lines.append(f"{role}: {step.content}")
        return "\n".join(context_lines)

    def _process_message(self, bot, scenario, user_message, context):
        if scenario.scenario_data:
            scenario_engine = ScenarioEngine(scenario.scenario_data)
            return scenario_engine.process_user_input(user_message, context)
        else:
            bot_response = chat_bot.generate_response(user_message)
            return {
                'response': bot_response,
                'current_state': None,
                'is_finished': False
            }

    @transaction.atomic
    def _save_conversation_steps(self, scenario, user_message, bot_response):
        max_order = scenario.steps.aggregate(Max('order'))['order__max'] or 0
        
        Step.objects.create(
            order=max_order + 1,
            content=user_message,
            scenario=scenario,
            step_type='user_input',
        )
        Step.objects.create(
            order=max_order + 2,
            content=bot_response,
            scenario=scenario,
            step_type='bot_response',
        )

class ScenarioViewSet(viewsets.ModelViewSet):
    serializer_class = ScenarioSerializer

    def get_queryset(self):
        return Scenario.objects.filter(bot__user=self.request.user)
    
    def perform_create(self, serializer):
        scenario = serializer.save()
        if not scenario.scenario_data:
            scenario.scenario_data = ScenarioManager.get_default_scenario()
            scenario.save()
    
    @action(detail=True, methods=['get'])
    def steps(self, request, pk=None):
        scenario = self.get_object()
        steps = scenario.step_set.all()
        serializer = StepSerializer(steps, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def validate(self, request, pk=None):
        scenario = self.get_object()
        is_valid = ScenarioManager.validate_scenario_format(scenario.scenario_data)
        
        return Response({
            'is_valid': is_valid,
            'scenario_id': scenario.id,
            'scenario_name': scenario.name
        })
    
    @action(detail=True, methods=['post'])
    def set_default(self, request, pk=None):
        scenario = self.get_object()
        scenario.scenario_data = ScenarioManager.get_default_scenario()
        scenario.save()
        
        return Response({
            'status': 'default scenario set',
            'scenario_id': scenario.id
        })

class StepViewSet(viewsets.ModelViewSet):
    serializer_class = StepSerializer
    
    def get_queryset(self):
        return Step.objects.filter(scenario__bot__user=self.request.user)