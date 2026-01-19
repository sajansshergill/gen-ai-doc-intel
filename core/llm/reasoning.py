"""
LLM reasoning layer for generating structured answers from retrieved context.
Supports OpenAI, Gemini, and local LLaMA models.
"""
from typing import List, Dict, Any, Optional
import json
import os


class LLMReasoner:
    """
    LLM reasoning layer that takes retrieved chunks and generates structured answers.
    """
    
    def __init__(self, provider: str = "openai", model: Optional[str] = None):
        """
        Initialize LLM reasoner.
        
        Args:
            provider: "openai", "gemini", or "llama"
            model: Model name (e.g., "gpt-4", "gpt-3.5-turbo", "gemini-pro")
        """
        self.provider = provider
        self.model = model or self._get_default_model(provider)
        self.client = self._init_client(provider)
    
    def _get_default_model(self, provider: str) -> str:
        """Get default model for provider."""
        defaults = {
            "openai": "gpt-3.5-turbo",
            "gemini": "gemini-pro",
            "llama": "llama-2-7b"
        }
        return defaults.get(provider, "gpt-3.5-turbo")
    
    def _init_client(self, provider: str):
        """Initialize the LLM client."""
        if provider == "openai":
            try:
                import openai
                api_key = os.getenv("OPENAI_API_KEY")
                if not api_key:
                    raise ValueError("OPENAI_API_KEY environment variable not set")
                return openai.OpenAI(api_key=api_key)
            except ImportError:
                raise ImportError("openai package not installed. Run: pip install openai")
        
        elif provider == "gemini":
            try:
                import google.generativeai as genai
                api_key = os.getenv("GEMINI_API_KEY")
                if not api_key:
                    raise ValueError("GEMINI_API_KEY environment variable not set")
                genai.configure(api_key=api_key)
                return genai
            except ImportError:
                raise ImportError("google-generativeai package not installed")
        
        else:
            # For local models, return None (to be implemented)
            return None
    
    def generate_answer(
        self,
        question: str,
        context_chunks: List[Dict[str, Any]],
        response_schema: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate structured answer from question and context.
        
        Args:
            question: User's question
            context_chunks: List of retrieved chunks with text, page, doc_id, etc.
            response_schema: Optional JSON schema for structured output
        
        Returns:
            Dict with answer, citations, and metadata
        """
        # Build context from chunks
        context_text = self._build_context(context_chunks)
        
        # Build prompt
        prompt = self._build_prompt(question, context_text, response_schema)
        
        # Generate response
        if self.provider == "openai":
            return self._generate_openai(prompt, response_schema)
        elif self.provider == "gemini":
            return self._generate_gemini(prompt, response_schema)
        else:
            # Fallback: return simple concatenation
            return {
                "answer": context_text[:1000],
                "citations": [{"page": c.get("page"), "doc_id": c.get("doc_id")} for c in context_chunks[:3]],
                "model": "fallback"
            }
    
    def _build_context(self, chunks: List[Dict[str, Any]]) -> str:
        """Build context string from chunks."""
        context_parts = []
        for chunk in chunks:
            page = chunk.get("page", "?")
            text = chunk.get("text", "")
            context_parts.append(f"[Page {page}]\n{text}\n")
        return "\n---\n".join(context_parts)
    
    def _build_prompt(self, question: str, context: str, schema: Optional[Dict] = None) -> str:
        """Build prompt for LLM."""
        base_prompt = f"""You are a helpful AI assistant that answers questions based on provided document context.

Question: {question}

Context from documents:
{context}

Please provide a clear, accurate answer based on the context above. If the answer cannot be found in the context, say so.
"""
        
        if schema:
            base_prompt += f"\n\nFormat your response according to this schema:\n{json.dumps(schema, indent=2)}"
        
        return base_prompt
    
    def _generate_openai(self, prompt: str, schema: Optional[Dict] = None) -> Dict[str, Any]:
        """Generate response using OpenAI."""
        try:
            messages = [{"role": "user", "content": prompt}]
            
            # Use structured output if schema provided
            if schema:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    response_format={"type": "json_object"} if schema else None
                )
            else:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages
                )
            
            answer_text = response.choices[0].message.content
            
            # Try to parse as JSON if schema provided
            if schema:
                try:
                    answer_data = json.loads(answer_text)
                    return {
                        "answer": answer_data,
                        "raw_text": answer_text,
                        "model": self.model,
                        "provider": "openai"
                    }
                except json.JSONDecodeError:
                    return {
                        "answer": answer_text,
                        "raw_text": answer_text,
                        "model": self.model,
                        "provider": "openai",
                        "warning": "Response not valid JSON"
                    }
            
            return {
                "answer": answer_text,
                "model": self.model,
                "provider": "openai"
            }
        except Exception as e:
            return {
                "error": str(e),
                "answer": "[Error generating response]",
                "provider": "openai"
            }
    
    def _generate_gemini(self, prompt: str, schema: Optional[Dict] = None) -> Dict[str, Any]:
        """Generate response using Gemini."""
        try:
            model = self.client.GenerativeModel(self.model)
            response = model.generate_content(prompt)
            
            answer_text = response.text
            
            return {
                "answer": answer_text,
                "model": self.model,
                "provider": "gemini"
            }
        except Exception as e:
            return {
                "error": str(e),
                "answer": "[Error generating response]",
                "provider": "gemini"
            }
