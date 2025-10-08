from langgraph.graph import StateGraph, END
from langchain_core.runnables import RunnableLambda
from typing import TypedDict, List
from retriever import get_retriever
from generator import generate_answer
from langchain.schema import Document
from csv_interpreter import run_csv_interpreter_agent

retriever = get_retriever()
#retriever.search_kwargs['k'] = 10

def build_graph(retriever):
    class GraphState(TypedDict):
        query: str
        documents: List[Document]
        answer: str

    def retrieve_docs(state: GraphState) -> GraphState:
        docs = retriever(state["query"], k=10)
        return {"query": state["query"], "documents": docs}

    def csv_agent_node(state: GraphState) -> GraphState:
        processed_docs = run_csv_interpreter_agent(state["documents"])
        return {**state, "documents": processed_docs}

    def generate_node(state: GraphState) -> GraphState:
        answer, prompt = generate_answer(state["query"], state["documents"])
        return {**state, "answer": answer}

    graph = StateGraph(GraphState)
    graph.add_node("retriever", RunnableLambda(retrieve_docs))
    graph.add_node("csv_agent", RunnableLambda(csv_agent_node))
    graph.add_node("generate", RunnableLambda(generate_node))

    graph.set_entry_point("retriever")
    graph.add_edge("retriever", "csv_agent")
    graph.add_edge("csv_agent", "generate")
    graph.add_edge("generate", END)

    return graph.compile()



