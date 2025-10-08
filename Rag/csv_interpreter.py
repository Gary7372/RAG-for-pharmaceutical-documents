import re
from typing import List
from langchain.schema import Document, HumanMessage
from langchain_aws import ChatBedrock

# Initialize the LLM client
llm = ChatBedrock(
    model_id="mistral.mistral-7b-instruct-v0:2",
    client=None,
    model_kwargs={"temperature": 0.3, "max_tokens": 1024},
)

def llm_summarize_or_pass_through(chunk_text: str) -> str:
    prompt = f"""
You are an expert in interpreting pharmacokinetic (PK) data from CSV files structured with multi-level column headers and PK parameters as row labels. Each cell represents a single data point (numeric value), optionally accompanied by a unit.

Your task:
Write one clear, natural, and complete English sentence for each cell in the table. In each sentence, combine the following elements:

The row label (e.g., a pharmacokinetic parameter such as Cmax, Tmax, AUC₀–∞, etc.).

The full column header, including all header levels (e.g., Treatment A – Day 1 – Mean).

The cell value, exactly as shown (preserve all numeric precision).

The unit, but only if it is explicitly present in the data.

Style and rules:
Write one sentence per cell, no exceptions.

Make each sentence natural-sounding, clear, and scientifically accurate.

Do not summarize, interpret, or compare data—just describe the value as a standalone fact.

If a unit is present, include it exactly as written.

If no unit is provided, omit it without assuming or adding one.

Always include full context from the column headers in each sentence.

✅ Example:
If the value is 15.8 ng/mL under column Treatment A – Day 1 – Mean for the row Cmax, write:

The Cmax under Treatment A on Day 1 (Mean) was 15.8 ng/mL.

If the value is 5.2 with no unit:

The Cmax under Treatment A on Day 1 (Mean) was 5.2.

Also keep the source of the table

Now, using the table below, write one sentence for every cell, following these rules:
Table:


{chunk_text}


"""
    response = llm.invoke([HumanMessage(content=prompt)])
    return response.content.strip()

def run_csv_interpreter_agent(documents: List[Document]) -> List[Document]:
    updated_docs = []

    for doc in documents:
        content = doc.page_content.strip()

        # Only interpret chunks that contain the phrase "this is a csv"
        if "this is a csv" in content.lower():
            result = llm_summarize_or_pass_through(content)

            if result == content:
                doc.metadata["csv_processed"] = False
            else:
                doc.page_content = result
                doc.metadata["csv_processed"] = True
        else:
            # Return other chunks as they are
            doc.metadata["csv_processed"] = False

        updated_docs.append(doc)

    return updated_docs

