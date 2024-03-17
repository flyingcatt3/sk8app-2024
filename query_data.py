import argparse
from time import sleep
import sys
import os
from dotenv import load_dotenv
from langchain.vectorstores.chroma import Chroma
from langchain_community.embeddings import CohereEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate

CHROMA_PATH = "chroma"
DATA_PATH = "data/redbull"
embeddings = CohereEmbeddings(model="embed-multilingual-v3.0",cohere_api_key="0X7IQsghxQVYwVdnC4C2nMgpX5xx4i2yGeYsuIN6")
PROMPT_TEMPLATE = """
請扮演一位人工智慧助理，你的任務是回答滑板相關的問題。
---
Context:
{context}
Context僅做為參考，回答一般問題時無須考慮到Context是否提到與問題相關的資訊，需運用自己對於問題的理解回答。
但如果是與滑板相關的問題，盡可能運用Context提供的資訊回答。

回答問題: {question}
---
"""

load_dotenv()
api_key = os.getenv('GOOGLE_API_KEY')

def main():
    # Create CLI.
    parser = argparse.ArgumentParser()
    parser.add_argument("query_text", type=str, help="The query text.")
    args = parser.parse_args()
    query_text = args.query_text
    print(f"Query text: {query_text}")

    # Prepare the DB.
    #embedding_function = OpenAIEmbeddings()
    embedding_function = CohereEmbeddings(model="embed-multilingual-v3.0",cohere_api_key="0X7IQsghxQVYwVdnC4C2nMgpX5xx4i2yGeYsuIN6")
    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)

    #retriever_mmr = db.as_retriever(search_type="mmr",k=5)

    #docs_mmr = retriever_mmr.get_relevant_documents(query_text)

    # Search the DB.
    results = db.similarity_search_with_relevance_scores(query_text, k=3)
    
    if len(results) == 0 or results[0][1] < 0.6:
        #print(str(results[0][1]))
        print("INFO: [RAG]Unable to find matching results.")
        #return

    context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in results])
    prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    prompt = prompt_template.format(context=context_text, question=query_text)
    #print(f"Prompt: {prompt}")

    model = ChatGoogleGenerativeAI(model="gemini-pro",google_api_key=api_key,temperature=0.7)
    
    for chunk in model.stream(prompt):
        for char in chunk.content:
            sys.stdout.write(char)
            sys.stdout.flush()
            sleep(0.05)
        
    '''
    response_text = model.predict(prompt)
    
    sources = [doc.metadata.get("source", None) for doc, _score in results]
    formatted_response = f"Response: {response_text}\nSources: {sources}"
    print(formatted_response)
    '''


if __name__ == "__main__":
    main()
