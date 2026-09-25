from langchain_community.vectorstores import Chroma
from langchain_community.chat_models import ChatOllama
from langchain_community.embeddings import FastEmbedEmbeddings
from langchain_core.documents.base import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema.output_parser import StrOutputParser
from langchain.schema.runnable import RunnablePassthrough, Runnable
from langchain.prompts import PromptTemplate
from langchain.vectorstores.utils import filter_complex_metadata
from langchain_core.callbacks import BaseCallbackHandler


class ChatNews:
    vector_store = None
    retriever = None
    chain = None
    saved_doc_categories = []

    def __init__(self):
        self.model = ChatOllama(model="llama3.2")
        self.text_splitter = RecursiveCharacterTextSplitter(chunk_size=1024, chunk_overlap=100)
        self.prompt = PromptTemplate.from_template(
            """
            <s> [INST] You are an assistant for question-answering tasks.
            Use the following pieces of retrieved context to answer the question.
            If you don't know the answer, just say that you don't know.
            Use three sentences maximum and keep the answer concise.  [/INST] </s>
            [INST] Question: {question}
            Context: {context}
            Answer: [/INST]
            """
        )
        self.doc_handler = ContextHandler()

    def ingest(self, docs: Document, category: str):
        self.saved_doc_categories.append(category)
        chunks = self.text_splitter.split_documents(docs)
        chunks = filter_complex_metadata(chunks)

        vector_store = Chroma.from_documents(documents=chunks, embedding=FastEmbedEmbeddings())
        self.retriever = vector_store.as_retriever(
            search_type="similarity_score_threshold",
            search_kwargs={
                "k": 3,
                "score_threshold": 0.5,
            },
        )

        self.chain = ({"context": self.retriever, "question": RunnablePassthrough()}
                      | self.prompt
                      | self.model
                      | StrOutputParser()
                      | FinalOutputGenerator()
                      )

    def ask(self, query: str):
        return self.chain.invoke(query, config={"callbacks": [self.doc_handler]})

    def clear(self):
        self.vector_store = None
        self.retriever = None
        self.chain = None
        self.saved_doc_categories = []

    
class ContextHandler(BaseCallbackHandler):
    def on_retriever_end(self, documents, run_id, parent_run_id, **kwargs):
        self.context = documents
        print(self.context)

    # def on_chain_end(self, outputs, run_id, parent_run_id, **kwargs):
    #     print("on chain end")
    #     print(outputs)

class FinalOutputGenerator(Runnable):
    def invoke(self, input, config, **kwargs):
        handler = config["callbacks"].handlers[0]
        response = f"{input} \n Data Source: \n"
        for i, doc in enumerate(handler.context):
            src = f"{i + 1}. {doc.metadata["title"]}: {doc.metadata["link"]} \n"
            response += src
        return response