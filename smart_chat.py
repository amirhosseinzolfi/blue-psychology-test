from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_ollama import OllamaEmbeddings
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage
from typing import TypedDict, Annotated
import operator

# --- Initialize LLM and Embeddings ---
llm = ChatOpenAI(
    base_url="http://141.98.210.15:15203/v1",
    model_name="gpt-4o-mini",
    temperature=0.5,
    api_key="324"
)

def get_embeddings():
    return OllamaEmbeddings(model="nomic-embed-text")

# --- Define Agent State ---
class AgentState(TypedDict):
    messages: Annotated[list, operator.add]

# --- RAG Setup ---
vectorstore = None
retriever = None

# --- Create Agent ---
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a helpful assistant. Respond to the user's questions. Do not ask questions. Use the retrieved context to answer the questions."),
        MessagesPlaceholder(variable_name="messages"),
    ]
)

# --- Define Graph ---
graph = StateGraph(AgentState)
graph.add_node("agent", lambda x: x) # Placeholder
graph.set_entry_point("agent")
graph.add_edge("agent", END)

# --- Build App ---
memory = SqliteSaver.from_conn_string("bot.db")
app = graph.compile(checkpointer=memory)

# --- History Management ---
def summarize_messages(messages):
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "You are an expert in summarizing conversations. Create a concise summary of the following messages."),
            MessagesPlaceholder(variable_name="messages"),
        ]
    )
    summarizer = prompt | llm
    summary = summarizer.invoke({"messages": messages})
    return [summary]

def manage_history(config):
    thread_id = config["configurable"]["thread_id"]
    history = memory.get(thread_id)
    if history and len(history["messages"]) > 10:
        # Summarize and update history
        summarized_history = summarize_messages(history["messages"])
        memory.put(thread_id, {"messages": summarized_history})
        return summarized_history
    elif history:
        return history["messages"]
    return []

# --- Update Vector Store ---
def update_vector_store(user_id, message):
    # This is a simple in-memory vector store. For a real application,
    # you would want to persist this.
    vectorstore.add_texts([message])

# --- Main Chat Function ---
def run_chat(user_id, message):
    global vectorstore, retriever
    if vectorstore is None:
        embeddings = get_embeddings()
        vectorstore = FAISS.from_texts(["You are a helpful assistant."], embedding=embeddings)
        retriever = vectorstore.as_retriever()

    agent_runnable = create_react_agent(llm, [retriever], prompt)
    agent_with_history = RunnableWithMessageHistory(
        agent_runnable,
        manage_history,
        input_messages_key="messages",
        history_messages_key="history",
    )

    graph = StateGraph(AgentState)
    graph.add_node("agent", agent_with_history)
    graph.set_entry_point("agent")
    graph.add_edge("agent", END)

    app = graph.compile(checkpointer=memory)

    config = {"configurable": {"thread_id": str(user_id)}}

    # Update vector store with the new message
    update_vector_store(user_id, message)

    # The agent will now have access to the retriever and history
    response = app.invoke({"messages": [HumanMessage(content=message)]}, config=config)
    # After invoking, the state is updated in the checkpointer.
    # We can retrieve the latest state to get the full history.
    latest_state = app.get_state(config)
    return latest_state.values()['messages'][-1].content

if __name__ == '__main__':
    # Example usage
    user_id = "12345"
    while True:
        user_input = input("You: ")
        if user_input.lower() == "exit":
            break
        response = run_chat(user_id, user_input)
        print(f"AI: {response}")
