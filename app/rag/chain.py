from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import Document
from typing import List, Dict, Any
from app.core.config import settings
from app.services.embeddings import embedding_service
from app.services.vector_store import vector_store


class RAGChain:
    """RAG chain for question answering with document retrieval."""
    
    def __init__(self):
        self.llm = ChatOpenAI(
            api_key=settings.openai_api_key,
            model="gpt-3.5-turbo",
            temperature=0.1
        )
        
        self.prompt_template = ChatPromptTemplate.from_template("""
You are a helpful AI assistant that answers questions about synthesizer manuals and technical documentation. 
Use the following context to answer the user's question. If you cannot answer the question based on the context, 
say so clearly.

Context:
{context}

Question: {question}

Answer the question based on the context provided. Be accurate and cite specific information from the context.
If the context doesn't contain enough information to answer the question, say "I don't have enough information to answer this question based on the available documentation."

Answer:
""")
    
    def retrieve_relevant_chunks(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Retrieve relevant document chunks for a query."""
        # Generate query embedding
        query_embedding = embedding_service.get_embedding(query)
        
        # Search for similar chunks
        results = vector_store.search_similar(query_embedding, limit=limit)
        
        return results
    
    def generate_response(self, query: str, context_chunks: List[Dict[str, Any]]) -> str:
        """Generate a response using the LLM with retrieved context."""
        # Prepare context from chunks
        context_text = "\n\n".join([
            f"Chunk {i+1} (Page {chunk['payload'].get('page_number', 'Unknown')}): {chunk['payload'].get('content', '')}"
            for i, chunk in enumerate(context_chunks)
        ])
        
        # Create the prompt
        prompt = self.prompt_template.format(
            context=context_text,
            question=query
        )
        
        # Generate response
        response = self.llm.invoke(prompt)
        
        return response.content
    
    def process_query(self, query: str, limit: int = 5) -> Dict[str, Any]:
        """Process a query through the complete RAG pipeline."""
        # Retrieve relevant chunks
        relevant_chunks = self.retrieve_relevant_chunks(query, limit)
        
        # Generate response
        response = self.generate_response(query, relevant_chunks)
        
        return {
            "response": response,
            "relevant_chunks": relevant_chunks
        }


# Global RAG chain instance
rag_chain = RAGChain() 