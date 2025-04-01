from intent_entity.intent_entity import IntentEntity

intent_entity = IntentEntity()
standalone_question = 'What are the influencing factors for decline in sales over time?'
intent_name = intent_entity.find_intent_entity(question=standalone_question, intents='kpis_classifier')
print(intent_name)