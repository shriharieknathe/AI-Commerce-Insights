"""Module for classifying the intent"""

from langchain.chains.llm import LLMChain
from config import config
from langchain_openai import ChatOpenAI
from prompt_builder_controller import PromptBuilder

class IntentEntity:

    def __init__(
            self
        ) -> None:
        model = ChatOpenAI(model="gpt-4o-mini", max_tokens=1000)

        prompt_builder = PromptBuilder()
        prompt = prompt_builder.get_prompt(module_name="intent_entity")
        self.__input_variables = prompt_builder.get_input_variable()
        self.__llm_chain = LLMChain(
            prompt=prompt, 
            llm=model
        )
        return
    
    def find_intent_entity(
            self,
            question,
            intents,
        ):
        all_intents = config["intent_entity"][intents]
        
        filtered_intents = self.__filter_item(
                items = all_intents,
                condition = self.__intent_filter_condition
            )
        
        prompt_variables_dict = {}
        input_variables_values = []


        # Initialize an empty string to store intent descriptions
        intents = ""

        few_shot_examples = ""

        # Loop through each intent in intents_list and generate its description
        for index, intent in enumerate(filtered_intents, start=1):
            intents += f"{index}.Intent: {intent.get('intent_name', '')}\n"
            intents += f"   Description: {intent.get('description', '')}\n"
            intents += "   ...\n"
            for few_shot_example_index, few_shot_example_question in  enumerate(intent.get('few_shot_examples',[])):
                few_shot_examples += f"Input: {few_shot_example_question}\n"
                few_shot_examples += f"Intent: {intent.get('intent_name','')}\n"
                few_shot_examples += "\n"

        input_variables_values.append(intents)
        input_variables_values.append(few_shot_examples)
        input_variables_values.append(question)

        for input_variables, input_variables_values in zip(self.__input_variables, input_variables_values):
            prompt_variables_dict[input_variables] = input_variables_values

        response_answer = self.__llm_chain.run(
            prompt_variables_dict
        )

        # Split the response by newline to separate intent and entities
        response_lines = response_answer.strip().split('\n')
        
        # Extract intent name from the first line
        intent_name = response_lines[0].lower()

        # Extract entities from subsequent lines
        self.__entities = ""#[line.strip('- ') for line in response_lines[2:]]

        self.__selected_intents = self.__filter_item(
                items = filtered_intents,
                condition = lambda intent: intent.get('intent_name', '') == intent_name
            )

        intent_name = self.__selected_intents[0].get('intent_name', '')

        return intent_name
    
    def __filter_item(
            self,
            items,
            condition
        ) -> any:
        return [item for item in items if condition(item)]
    
    def __intent_filter_condition(
            self,
            intent
        ) -> bool:
        return True#(intent.is_image_supported == self.__is_image_supported & intent.is_ocr_supported == self.__is_ocr_supported)
        
    def get_entities(
            self
        ):
        return self.__entities
    