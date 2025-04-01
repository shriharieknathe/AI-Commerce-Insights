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

langchain.verbose = True
app = Flask(__name__)
CORS(app)


username = 'root'
password = 'mindstix'
host = 'localhost'  # or your database host
port = '3306'       # default MySQL port
database = 'edb2'
table_name = 'amazon_sale_report'
sql_string = f'mysql+mysqlconnector://{username}:{password}@{host}:{port}/{database}'

db = SQLDatabase.from_uri(sql_string)
llm = ChatOpenAI(model="gpt-4o-mini", max_tokens=10000)


toolkit = SQLDatabaseToolkit(db=db, llm=llm)

tools = toolkit.get_tools()

with open('mysql_prompt.txt', 'r') as file:
    _mysql_prompt = file.read()

system_message = SystemMessage(content=_mysql_prompt)

agent_executor = create_react_agent(llm, tools, messages_modifier=system_message)


@app.route("/qna", methods=["POST"])
def get_response():
    try:
        if "question" in request.form:
            question = request.form["question"].strip()

        agent_response = agent_executor.invoke(input={"messages": [HumanMessage(content=question)]})
        result = agent_response['messages'][-1].content

        response = {'answer': result, 'agent_response': str(agent_response)}
        print(response)
        return jsonify(response), 200

    except Exception as e:

        error_response = {"error": "An error occurred, please try again.", "details": str(e)}
        return jsonify(error_response), 500  # 500 for internal server error

if __name__ == "__main__":
    app.run(debug=False)
