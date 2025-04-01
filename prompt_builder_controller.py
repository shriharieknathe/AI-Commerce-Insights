from langchain_core.prompts import ChatPromptTemplate
from config import config

class PromptBuilder:
    """
    Example to use this class:

    prompt_version = PromptBuilder()  # initialize class 

    prompt = prompt_version.get_prompt(module_name="intent_entity")  # get prompt object

    input_variables = prompt_version.get_input_variable()  # get input_variables as list
    

    """

    def __init__(self):
        self.template_dict = config["prompt_builder"]

    def get_prompt(self, module_name, intent_name=None, entity_name=None):

        if intent_name and entity_name:
            self.repo = f"{module_name}_{intent_name}_{entity_name}"
        elif intent_name:
            self.repo = f"{module_name}_{intent_name}"
        else:
            self.repo = f"{module_name}"

        prompt = ChatPromptTemplate.from_template(self.template_dict[self.repo]["template"])

        return prompt
    
    def get_prompt_template(self):

        template = self.template_dict[self.repo]["template"]

        return template
    
    def get_input_variable(self):

        input_variables = self.template_dict[self.repo]["input_variables"]

        return input_variables

