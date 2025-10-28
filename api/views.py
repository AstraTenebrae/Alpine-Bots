from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .serializers import BotSerializer, ScenarioSerializer, StepSerializer, ChatSerializer
from .models import Bot, Scenario, Step

from .chatbot_service import chat_bot
from .scenario_service import ScenarioEngine, ScenarioManager

class BotViewSet(viewsets.ModelViewSet):
    serializer_class = BotSerializer

    def get_queryset(self):
        return Bot.objects.filter(user=self.request.user)
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['get','post'], serializer_class=ChatSerializer)
    def chat(self, request, pk=None):
        bot = self.get_object()

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True) 
        user_message = serializer.validated_data['message']

        if not user_message:
            return Response({'error': 'no user message found'}, status=status.HTTP_400_BAD_REQUEST)
        active_scenario = bot.scenario_set.first()        
        if active_scenario and active_scenario.scenario_data:
            scenario_engine = ScenarioEngine(active_scenario.scenario_data)
            result = scenario_engine.process_user_input(user_message)
            bot_response = result['response']
        else:
            bot_response = chat_bot.generate_with_context(user_message)
        
        try:
            scenario = bot.scenario_set.first()
            if not scenario:
                scenario = Scenario.objects.create(
                    name=f"Default Scenario for {bot.name}",
                    bot=bot
                )
            last_step = scenario.step_set.order_by('-order').first()
            if last_step:
                next_order = last_step.order + 1
            else:
                next_order = 1
            user_step = Step.objects.create(
                order=next_order,
                content=user_message,
                scenario=scenario,
                step_type='user_input',
            )
            bot_step = Step.objects.create(
                order=next_order + 1,
                content=bot_response,
                scenario=scenario,
                step_type='bot_response',
            )
        except Exception as e:
            print(f"Ошибка при сохранении шагов: {e}")
        response_data = {
            'bot_response': bot_response,
        }
        if active_scenario and active_scenario.scenario_data:
            response_data.update({
                'current_state': result.get('current_state'),
                'is_finished': result.get('is_finished', False)
            })            
        return Response(response_data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def reset_scenario(self, request, pk=None):
        return Response({'status': 'scenario reset'})    

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