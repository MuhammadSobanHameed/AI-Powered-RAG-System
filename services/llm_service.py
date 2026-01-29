"""
LLM Service
Handles interaction with Groq API for text generation
"""
from groq import Groq
from typing import Optional, List
import logging

from config import settings

logger = logging.getLogger(__name__)

class LLMService:
    """
    Service for generating responses using Groq's LLaMA models
    """
    
    def __init__(self, api_key: str = None, model: str = None):
        """
        Initialize LLM service
        
        Args:
            api_key: Groq API key
            model: Model name to use
        """
        self.api_key = api_key or settings.GROQ_API_KEY
        self.model = model or settings.LLM_MODEL
        
        if not self.api_key:
            raise ValueError("GROQ_API_KEY is not set. Please set it in .env file")
        
        self.client = Groq(api_key=self.api_key)
        logger.info(f"LLM Service initialized with model: {self.model}")
    
    def generate_response(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 1000,
        temperature: float = 0.7
    ) -> str:
        """
        Generate a response from the LLM
        
        Args:
            prompt: User prompt
            system_prompt: System prompt for context
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature
            
        Returns:
            Generated text response
        """
        try:
            messages = []
            
            if system_prompt:
                messages.append({
                    "role": "system",
                    "content": system_prompt
                })
            
            messages.append({
                "role": "user",
                "content": prompt
            })
            
            logger.info(f"Generating response with {self.model}")
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            answer = response.choices[0].message.content
            logger.info(f"Generated response: {len(answer)} characters")
            
            return answer
            
        except Exception as e:
            logger.error(f"Failed to generate LLM response: {str(e)}")
            raise
    
    def generate_answer_from_context(
        self,
        question: str,
        context: str,
        max_tokens: int = 500
    ) -> str:
        """
        Generate an answer based on provided context
        
        Args:
            question: User question
            context: Retrieved context from documents
            max_tokens: Maximum tokens in response
            
        Returns:
            Generated answer
        """
        system_prompt = """You are a question-answering system.

STRICT RULES (must follow):
1. Use ONLY the exact information explicitly present in the provided context.
2. DO NOT invent or assume lecture numbers, slide numbers, section names, or document structure.
3. DO NOT reference lectures, slides, or sections unless they are explicitly written in the context.
4. If the answer is not clearly stated in the context, respond with: "Not found in the document."
5. Do NOT add explanations, citations, or metadata that are not present verbatim in the context.

Your answer must be grounded strictly in the text."""
        
        prompt = f"""Context from documents:
{context}

Question: {question}

Answer:"""
        
        try:
            return self.generate_response(
                prompt=prompt,
                system_prompt=system_prompt,
                max_tokens=max_tokens,
                temperature=0.3  # Lower temperature for factual responses
            )
        except Exception as e:
            logger.error(f"Failed to generate answer: {str(e)}")
            return "I apologize, but I encountered an error while generating the answer."


# Global LLM service instance (initialized lazily to handle API key)
_llm_service_instance = None

def get_llm_service() -> LLMService:
    """
    Get or create the global LLM service instance
    
    Returns:
        LLM service instance
    """
    global _llm_service_instance
    if _llm_service_instance is None:
        _llm_service_instance = LLMService()
    return _llm_service_instance