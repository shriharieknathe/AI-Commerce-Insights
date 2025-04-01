from langchain_openai import ChatOpenAI
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_core.messages import HumanMessage
from langchain_core.messages import SystemMessage
from langgraph.prebuilt import create_react_agent
from flask import Flask, request, jsonify
from flask_cors import CORS
from langchain_core.messages import HumanMessage
import langchain
from intent_entity.intent_entity import IntentEntity
from template_formatter.template_formatter_controller import TemplateSelector


langchain.verbose = True
app = Flask(__name__)
CORS(app)


username = 'root'
password = 'mindstix'
host = 'localhost'  # or your database host
port = '3306'       # default MySQL port
database = 'edb3'
table_name = 'amazon_sale_report'
sql_string = f'mysql+mysqlconnector://{username}:{password}@{host}:{port}/{database}'

db = SQLDatabase.from_uri(sql_string)
llm = ChatOpenAI(model="gpt-4o")
mini_llm = ChatOpenAI(model="gpt-4o-mini", max_tokens=10000)


intent_entity = IntentEntity()
template_selector = TemplateSelector()
toolkit = SQLDatabaseToolkit(db=db, llm=mini_llm)

tools = toolkit.get_tools()

with open('mysql_prompt.txt', 'r') as file:
    _mysql_prompt = file.read()
system_message = SystemMessage(content=_mysql_prompt)

with open('primary_kpis_system_message.txt', 'r') as file:
    primary_kpis_prompt = file.read()
primary_kpis_system_message = SystemMessage(content=primary_kpis_prompt)

# with open('secondary_kpis_system_message.txt', 'r') as file:
#     secondary_kpis_prompt = file.read()
# secondary_kpis_system_message = SystemMessage(content=secondary_kpis_prompt)

agent_executor = create_react_agent(mini_llm, tools, messages_modifier=system_message)
primary_kpis_agent_executor = create_react_agent(llm, tools, messages_modifier=primary_kpis_system_message)
secondary_kpis_agent_executor = create_react_agent(llm, tools, messages_modifier=system_message)



@app.route("/qna", methods=["POST"])
def get_response():
    try:
        if "question" in request.form:
            question = request.form["question"].strip()

        intent_name = intent_entity.find_intent_entity(question=question, intents = 'general_intents')
        print("Intent name:",intent_name)

        agent_response = None

        if intent_name == "greeting":
            result = template_selector.select_template()

        elif intent_name == 'simple_sales_analysis':
            agent_response = agent_executor.invoke(input={"messages": [HumanMessage(content=question)]})

        elif intent_name == 'complex_sales_analysis':
            kpi_intent = intent_entity.find_intent_entity(question=question, intents = 'kpis_classifier')

            if kpi_intent == 'primary_kpis':
                print("kpi_intent:",kpi_intent)
                agent_response = primary_kpis_agent_executor.invoke(input={"messages": [HumanMessage(content=question)]})

            else:
                print("kpi_intent:",'secondary_kpis')
                agent_response = secondary_kpis_agent_executor.invoke(input={"messages": [HumanMessage(content=question)]})
        if agent_response:
            result = agent_response['messages'][-1].content
            print(agent_response)

        response = {'answer': result}
        print(result)
        
        return jsonify(response), 200

    except Exception as e:

        error_response = {"error": "An error occurred, please try again.", "details": str(e)}
        print(error_response)
        return jsonify(error_response), 500  # 500 for internal server error

if __name__ == "__main__":
    app.run(debug=False)
