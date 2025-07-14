# chat.py - Fixed version
import json
from typing import Dict, List
import openai

class ChatManager:
    def __init__(self, embedding_manager):  # Removed type hint to fix error
        self.embedding_manager = embedding_manager
        self.client = openai.OpenAI()
    
    async def process_query(self, question: str, max_results: int = 5) -> Dict:
        """Process user query and generate response"""
        
        # Retrieve relevant context
        context_results = await self.embedding_manager.search_similar(
            question, 
            max_results=max_results
        )
        
        if not context_results:
            return {
                "answer": "I don't have information about that topic in my knowledge base.",
                "sources": [],
                "confidence": 0.0
            }
        
        # Build context for LLM
        context_text = "\n\n".join([
            f"Source: {result['metadata']['source_url']}\n{result['text']}"
            for result in context_results
        ])
        
        # Generate response using LLM
        system_prompt = """You are a helpful sales assistant for this company's website. 
        Answer questions based ONLY on the provided context from the company's website or data.
        Focus on sales, pricing, and product features information.
        If the information is not in the context, clearly say you say that my current information is limited.
        Keep responses polite, concise and helpful.
        Always mention when you're referencing specific product or pricing information."""
        
        user_prompt = f"""Context from company website:
        {context_text}
        
        Question: {question}
        
        Please provide a helpful answer based on the context above."""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1,
                max_tokens=500
            )
            
            answer = response.choices[0].message.content
            
            # Calculate confidence based on relevance scores
            avg_confidence = sum(result['score'] for result in context_results) / len(context_results)
            
            # Format sources
            sources = [
                {
                    "url": result['metadata']['source_url'],
                    "title": result['metadata']['title'],
                    "relevance_score": round(result['score'], 3)
                }
                for result in context_results
            ]
            
            return {
                "answer": answer,
                "sources": sources,
                "confidence": round(avg_confidence, 3)
            }
            
        except Exception as e:
            print(f"Error generating response: {e}")
            return {
                "answer": "I encountered an error processing your question. Please try again.",
                "sources": [],
                "confidence": 0.0
            }