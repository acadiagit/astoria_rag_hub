# Path /astoria_rag_hub/app/rag_components/agent_setup.py
# Filename: agent_setup.py

import os
import logging
from langchain.agents import AgentExecutor, create_react_agent
from langchain_community.agent_toolkits import create_sql_agent
from langchain_anthropic import ChatAnthropic
from langchain_community.utilities.sql_database import SQLDatabase
from langchain.tools.retriever import create_retriever_tool
from langchain_core.prompts import ChatPromptTemplate

from app.rag_components.vector_store import get_vector_store

logger = logging.getLogger(__name__)

def create_maritime_agent() -> AgentExecutor:
    """
    Creates the main LangChain agent with access to the SQL database
    and the RAG vector store.
    """
    logger.info("Creating the maritime agent...")

    # 1. Initialize the LLM
    llm = ChatAnthropic(
        model=os.getenv("CLAUDE_MODEL", "claude-3-5-sonnet-20240620"),
        temperature=0
    )

    # --- TEMPORARY FIX: Hardcoding the DB URI to bypass .env issues ---
    # NOTE: Ensure your database password is correct here.
    db_uri = "postgresql+psycopg2://maine2025:machias@maine2025@db.cnkbkzfacepjgnvamlvn.supabase.co:5432/postgres"
    # -----------------------------------------------------------------
    
    db = SQLDatabase.from_uri(db_uri)
    sql_agent_executor = create_sql_agent(llm=llm, db=db, agent_type="tool-calling", verbose=True)
    sql_tool = sql_agent_executor.tools[0]
    sql_tool.name = "structured_database_tool"
    sql_tool.description = "Use this tool for queries about structured data such as vessel specifications, crew lists, and specific voyage details."

    # 3. Create the RAG Retriever Tool
    vector_store = get_vector_store()
    retriever = vector_store.as_retriever()
    retriever_tool = create_retriever_tool(
        retriever,
        "unstructured_vector_database_tool",
        "Use this tool for queries about historical context, descriptions, events, and interpretive questions about maritime history."
    )

    # 4. Create the Main Agent Prompt
    prompt_template = """
    Answer the following questions as best you can. You have access to the following tools:

    {tools}

    Use the following format:

    Question: the input question you must answer
    Thought: you should always think about what to do
    Action: the action to take, should be one of [{tool_names}]
    Action Input: the input to the action
    Observation: the result of the action
    ... (this Thought/Action/Action Input/Observation can repeat N times)
    Thought: I now know the final answer
    Final Answer: the final answer to the original input question

    Begin!

    Question: {input}
    Thought:{agent_scratchpad}
    """
    prompt = ChatPromptTemplate.from_template(prompt_template)

    # 5. Create the final agent with both tools
    tools = [sql_tool, retriever_tool]
    agent = create_react_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
    
    logger.info("Maritime agent created successfully.")
    return agent_executor

#end-of-file
