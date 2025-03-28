from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_ollama import OllamaEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama.llms import OllamaLLM

pdfs_directory = 'pdfs/'

embeddings = OllamaEmbeddings(model="deepseek-r1")

model = OllamaLLM(model="deepseek-r1")


template = """
you are an assistant that answers questions. Using the following retrieved information, answer the
user question. If you dont know the answer, say that you dont know. Use upto 3 sentences, keeping the
answer concise.
Question: {question}
Context: {context}
Answer:
"""

# the file when uploaded goes to pdf directory
def upload_pdf(file):
    with open(pdfs_directory + file.name, "wb") as f:
        f.write (file.getbuffer())


# used to split pdf into chunks
def create_vector_store(file_path):
# pdf is read into a variable document
    loader = PyPDFLoader(file_path)
    documents = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size = 2000,
        chunk_overlap = 300,
        add_start_index = True
    )

# documents are chunked and stored to db
    chunked_docs = text_splitter.split_documents(documents)
    db = FAISS.from_documents(chunked_docs,embeddings)

    return db


# retrive the relvent chunk from the prompt
# here k=4 means 4 relevant chunks would be returned
def retrieve_docs(db,query,k=4):
    print(db.similarity_search(query))
    return db.similarity_search(query,k)



def question_pdf(question,documents):

    #it joins all the chunks to form a context
    context = "\n\n".join([doc.page_content for doc in documents])
    prompt = ChatPromptTemplate.from_template(template)

    # here model is deepseek and promt is the template defined above
    chain = prompt | model
    
    # our template had a question that is what our client asks and the context that we defined above
    return chain.invoke({"question":question, "context":context})