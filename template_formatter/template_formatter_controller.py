"""Module for building output templates based on the language"""

import os
import jinja2
import random
from utils import log

class TemplateSelector:
    """A class for selecting the templates based on language."""

    def __init__(self) -> None:
        """Initialize the TemplateSelector."""
        # Load the templates in the environment
        self.env = jinja2.Environment(loader=jinja2.FileSystemLoader('template_formatter/templates'))
    
    def select_template(self, data: dict = None) -> str:
        """Select a template based on the provided language, render it, and return the output.

        Args:
            language (str): The language code (e.g., 'en', 'es').
            data (dict, optional): Data to be passed to the template. Defaults to None.

        Returns:
            str or None: The rendered template output, or None if no template is found.
        """
        if data is None:
            data = {}

        template_prefix = "en_"
        template_files = os.listdir('template_formatter/templates')
 
        possible_templates = [template_file for template_file in template_files if template_file.startswith(template_prefix)]

        if not possible_templates:
            log.info(f"No templates found.",classname=__class__.__name__)
            return None

        random_template = random.choice(possible_templates)
        try:
            log.info("Finding template for the greeting mesage...",classname=__class__.__name__)
            template = self.env.get_template(random_template)
            rendered_output = template.render(data)
            return rendered_output
        except jinja2.exceptions.TemplateNotFound:
            log.info(f"Template '{random_template}' not found.",classname=__class__.__name__)
            return None
