from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_experimental.text_splitter import SemanticChunker
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableParallel
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_openai import ChatOpenAI
from langfuse.callback import CallbackHandler
from langchain_postgres.vectorstores import PGVector, DistanceStrategy
from langchain_postgres.chat_message_histories import PostgresChatMessageHistory
from transformers import AutoTokenizer
# from langchain.document_loaders import TextLoader


from src.config import settings
from src.chats.prompt_templates import rag_system_prompt


class LLMService():
    @classmethod
    def init_langfuse_handler(cls):
        langfuse_handler = CallbackHandler(
            secret_key=settings.LANGFUSE_SECRET_KEY,
            public_key=settings.LANGFUSE_PUBLIC_KEY,
            host=settings.LANGFUSE_HOST,
        )
        return langfuse_handler
    
    @classmethod
    def init_llm(cls):
        llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            openai_api_base="http://localhost:8080/v1",
            temperature=0.0, # better to stay from 0.0 to 0.7
            max_tokens=4096, # -1 - unlimited
            openai_api_key="sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx", # any random string
            # frequency_penalty
            # presence_penalty
            # streaming=True
            # stop=[]
        )
        return llm

    @classmethod
    def init_embeddings(cls):
        embeddings = HuggingFaceEmbeddings(
            model_name = "./src/huggingface/bge-m3",
            model_kwargs = {'device': 'cuda'}
        )
        return embeddings
    
    @classmethod
    def init_tokenizer(cls):
        tokenizer = AutoTokenizer.from_pretrained(
            pretrained_model_name_or_path="./src/huggingface/bge-m3", # "google-bert/bert-base-multilingual-cased",
            max_length = 2048,
            truncation = True,
            # padding="max_length"
        )
        return tokenizer
    
    @classmethod
    def init_retriever(cls):
        vectorstore = PGVector(
            embeddings=cls.init_embeddings(),
            distance_strategy=DistanceStrategy.COSINE,
            collection_name="news", # TODO: choosing collection functionallity
            connection = "postgresql+psycopg://postgres:postgres@localhost:5432/postgres",
        )
        retriever = vectorstore.as_retriever(
            search_kwargs={"k": 3} # "k": 4 - TODO: choosing top n of k functionality (k = 5)
        )
        return retriever
    
    @classmethod
    def init_rag_prompt(cls):
        # TODO: chat history summury to prompt
        base_rag_prompt = ChatPromptTemplate.from_messages([
                ("system", rag_system_prompt),
                ("human", "{question}"),
        ])
        return base_rag_prompt

    @classmethod
    def init_text_splitter(cls):
        text_splitter = RecursiveCharacterTextSplitter.from_huggingface_tokenizer( # SemanticChunker
            separators=["\n\n", "\n", " ", ""], # ["\n\n", "\n"],
            tokenizer=cls.init_tokenizer(),
            chunk_size=2048,
            chunk_overlap=100,
            # is_separator_regex=False,
        )
        return text_splitter

    @classmethod
    def upload_langchain_document(cls, page_content, metadata):
        langchain_document = Document(page_content=page_content, metadata=metadata)
        document_chunks = cls.init_text_splitter().split_documents([langchain_document])
        db = PGVector.from_documents(
            embedding=cls.init_embeddings(),
            documents=document_chunks,
            collection_name="news", # collection_name=data["endpoint"], - if each html file as collection (коллекция может представлять один файл / один объект так и абстрактную группу объектов - объекты новостей)
            connection="postgresql+psycopg://postgres:postgres@localhost:5432/postgres",
            use_jsonb=True,
            pre_delete_collection=False,
        )
        # for docs in document_chunks: print(len(docs.page_content))
        return db

    @classmethod
    def init_rag_chain(cls, question_text: str):
        def format_docs(docs):
            return "\n\n".join(doc.page_content for doc in docs)
        
        #     rag_chain = (
        #         {"context": cls.init_retriever | cls.format_docs, "question": RunnablePassthrough()} #  lambda x: context_text
        #         | cls.init_rag_prompt
        #         | cls.init_llm # .bind(stop=["\nCypher query:", "\nUser input: "])
        #         | StrOutputParser()
        #     )
        #     rag_chain.invoke(input = {"question": question_text}, config={"callbacks": [cls.init_langfuse_handler()]})
        
        rag_chain_from_docs = (
            RunnablePassthrough.assign(context=(lambda x: format_docs(x["context"])))
            | cls.init_rag_prompt()
            | cls.init_llm() # .bind(stop=["\nCypher query:", "\nUser input: "])
            | StrOutputParser()
        )
        
        rag_chain_with_source = RunnableParallel(
            {"context": cls.init_retriever(), "question": RunnablePassthrough()}
        ).assign(answer = rag_chain_from_docs)
        
        output = rag_chain_with_source.invoke(input = question_text, config = {"callbacks": [cls.init_langfuse_handler()]}) # input = {"question": question_text}
        return output
