from langchain_aws import ChatBedrock
from langchain.schema import Document, HumanMessage
from typing import List, Tuple
from dotenv import load_dotenv

load_dotenv()

llm = ChatBedrock(
    model_id="eu.anthropic.claude-3-5-sonnet-20240620-v1:0",
    client=None,
    model_kwargs={"temperature": 0.3, "max_tokens": 2048},
)

def generate_answer(query: str, documents: List[Document]) -> Tuple[str, str]:
    text = "\n\n".join(
        f"[Source: {doc.metadata.get('source', 'Unknown')} | Page: {doc.metadata.get('page', '?')}] {doc.page_content.strip()}"
        for doc in documents
    )

    instruction_prompt = f"""As an expert in pharmaceutical regulatory affairs, analyze the following EMA public assessment content. The content may include:

Unstructured text (e.g., assessment report excerpts)

Using only the information explicitly stated in the input text, answer the following question:

"{query}"

Your response must consist of two parts:

Answer — A clear, factual answer in one complete sentence.

If multiple items are involved, use concise bullet points or comma-separated lists.

Do not include summaries, background, or assumptions not directly supported by the text.

If the answer is not found in the provided content, reply only with: "i don’t know".

Justification — Briefly explain why this answer was given by referencing the relevant parts of the input text. For each reference, include the **exact source name and page number** using the provided metadata (e.g., Source: Netupitant_Assessment.pdf, Page: 15). If the information is missing, state that clearly.

This approach ensures strict regulatory alignment by grounding both the answer and rationale exclusively in the EMA-provided content.

Input:
"{text}"
"""

    full_prompt = f"{instruction_prompt}\n{text}"
    response = llm.invoke([HumanMessage(content=full_prompt)])
    return response.content.strip(), instruction_prompt



