config = {
    "provider": "Azure",
    "prompt_builder": {
        "retriever_qa":{
            "template":"""Use the following context for answering - 
            {context}
            -------------------------------------------------------------------------------------------------
            Create the output based on context above as truthfully as possible.
                
            For Final Answer:
            1. Most importantly the answer should not be more than 100 words
            2. User is not knowing the observations which you get, so generate the output with clarity.
            3. Tone: friendly + professional.
            4. Add the product url at the end of the answer(Note: Give the product url only when a valid product url is present).
                

            Question: {query}
            Output: Let's think step by step:
            """,
            "input_variables":["context", "query"]
        },
        "retriever_qa_program":{
            "template":"""Use the following context for answering - 
            {context}
            -------------------------------------------------------------------------------------------------
            Create the output based on context above as truthfully as possible.
                
            For Final Answer:
            1. Most importantly the answer should not be more than 100 words
            2. User is not knowing the observations which you get, so generate the output with clarity.
            3. Tone: friendly + professional.
            4. If the user has asked for any suggestions generate the answer as program specific.
            5. Make sure that the answer contains the name of the program and the program image url. 
                

            Question: {query}
            Output: Let's think step by step:
            """,
            "input_variables":["context", "query"]
        },
        "intent_entity": {
            "template": """
                You are an expert having 10 years of experience in classifying questions based on intents.

                Note: The output intent should be strictly from the following intents

                Here are the list of intents with there description.
                {intents}

                Here are some examples:
                {few_shot_examples}


                Note: You have to just return the name of the intent nothing else.

                Input: {input} 
                Intent:
                """,
            "input_variables": [
                "intents",
                "few_shot_examples",
                "input",
            ],
        },    
    },
    "intent_entity": {
        "general_intents": [
            {
                "intent_name": "simple_sales_analysis",
                "description": "The Simple Sales Analysis intent addresses straightforward queries about sales performance. It provides quick insights on sales values, performance by category, channel, and state, and percentages of total sales.",
                "few_shot_examples": [
                    "What are the latest sales values?",
                    "What is the change in sales over the last 2 months?",
                    "Which category has the highest sales?",
                    "What percentage of total sales comes from the top 3 performing categories?"
                ]
            },  
            {
                "intent_name": "complex_sales_analysis",
                "description": "The Complex Sales Analysis intent addresses detailed queries related to sales trends, root cause analysis, and performance factors. It helps to identify trends, reasons for sales fluctuations, and comparisons across different categories, channels, and states.",
                "few_shot_examples": [
                    "Why are sales down compared to previous months?",
                    "What are the factors affecting the decline in sales for June 2022?",
                    "Which category is preferred the most by each state?",
                    "Which channel is performing better and how is it impacting sales?",
                    "Which category has the highest return rate?"
                ]
            },
            {
                "intent_name": "greeting",
                "description": "The Greeting intent encompasses queries that express greetings, such as 'hello', 'hi' , 'good morning', 'good afternoon', etc. Users can use these types of queries to start a conversation or establish a friendly interaction. This attempt is responsible for recognizing and responding appropriately to greetings.",
                "few_shot_examples": [
                    "Hi",
                    "Hey",
                    "Hello",
                    "Hello how are you?",
                    "Good morning, can you help me?",
                    "Good afternoon, is there anything I can help you with?",
                    "Hello! How can you help you today?",
                ]
            },
        ],
        'kpis_classifier': [
            {
                "intent_name": "primary_kpis",
                "description": "The Primary KPIs intent tracks and reports changes in Sales Amount and Sales Quantity across Category, Size, State, and Channel. It identifies significant shifts in these KPIs and highlights any emerging trends.",
                "few_shot_examples": [
                    "Track the change in Sales Amount by Category.",
                    "What is the percentage change in Sales Quantity by State?",
                    "Has any Channel contributing to the sales shown a significant change?",
                    "Report any new trends in sales by Size."
                ]
            }, 
            {
                "intent_name": "secondary_kpis",
                "description": "The Secondary KPIs intent monitors and reports changes in Fill Rate, Average Order Value, Return Rate, Damage Rate, and Shipment Error Rate by Category, Size, State, and Channel, and the impact it has created on the sales. It identifies significant changes and emerging trends in these secondary metrics. It intends to do root cause analysis and find the reasons behind any change and checks other KPIs for the fluctuations.",
                "few_shot_examples": [
                    "Track the change in Fill Rate by Channel.",
                    "What is the percentage change in Average Order Value by State?",
                    "Has any Category shown a significant shift in Return Rate?",
                    "Report any new trends in Damage Rate by Size.",
                    "Why there is change in sales?",
                    "What are the factors affecting Fill Rate?",
                    "Which category is creating the most influence on sales?",
                    "Which state has poor shipping score?"
                ]
            },
        ]
    },
    "genai_safety": {
        "input_cleaner": {
            "model": {
                "model_id": "gpt-4o-mini_chat_models",
                "model_name": "gpt-4o-mini",
                "model_parameters": {
                    "temperature": 0,
                    "max_tokens": 256,
                },
                "model_kwargs": {},
            },
            "ontopic_path": "utils/ontopic_fd.json",
            "offtopic_path": "utils/offtopic_fd.json",
            "business_metric_path": "utils/business_metric.json",
            "avg_word_length": 333,
            "toxicity_threshold": 0.2,
            "jailbreak_threshold": 0.45,
            "injection_threshold": 0.45,
            "sentiment_threshold": -0.45,
            "ontopic_threshold": 0.35,
            "offtopic_threshold": 0.4,
        },
        "output_evaluator": {
            "relevance_to_prompt": 0.6,
            "flesch_reading_ease": 80,
            "automated_readability_index": 12,
            "toxicity_threshold": 0.4,
            "difficult_words": 10,
            "sentiment_threshold": -0.4,
        },
        "moderation_rails": {
            "nvidia_nemo_path": "utils/nvidia_nemo",
            "model": {
                "model_id": "gpt-4o-mini_chat_models",
                "model_name": "gpt-4o-mini",
                "model_parameters": {
                    "temperature": 0.0
                },
                "model_kwargs": {},
            },
        },
    },
    "template_selector": {
        "model": {
            "model_id": "text-embedding-3-large_embedding_models",
            "model_name": "text-embedding-3-large",
            "model_parameters": {},
            "model_kwargs": {},
        },
        "file_path": "embeddings.npy",
    },
    "template_formatter": {
        "templates": [
            {
                "channel": "whatsapp",
                "intent": "greeting",
                "template_name": "whatsapp_greeting",
            },
            {
                "channel": "chatbot",
                "intent": "greeting",
                "template_name": "chatbot_greeting",
            },
            {
                "channel": "whatsapp",
                "intent": "product_discovery",
                "template_name": "whatsapp_product_discovery",
            },
            {
                "channel": "chatbot",
                "intent": "product_discovery",
                "template_name": "chatbot_product_discovery",
            },
        ]
    },
    "logger": {
        "level": "INFO",
        "format": "%(asctime)s %(levelname)s %(username)s %(classname)s %(methodname)s %(message)s",
        "handlers": {"streamhandler": False},
    },
    "hash_user_id": False,
}