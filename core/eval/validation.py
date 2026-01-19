"""
Evaluation and validation tooling.
Includes hallucination checks, schema validation, and faithfulness metrics.
"""
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, ValidationError


class FaithfulnessChecker:
    """
    Checks if answers are faithful to source documents.
    Requires citations and verifies claim coverage.
    """
    
    def check_faithfulness(
        self,
        answer: str,
        evidence_chunks: List[Dict[str, Any]],
        citations: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Check if answer is faithful to evidence.
        
        Args:
            answer: Generated answer text
            evidence_chunks: Retrieved chunks used
            citations: Citations provided in answer
        
        Returns:
            Dict with faithfulness metrics
        """
        # Check citation coverage
        cited_chunk_ids = {c.get("chunk_id") for c in citations if c.get("chunk_id")}
        evidence_chunk_ids = {c.get("chunk_id") for c in evidence_chunks if c.get("chunk_id")}
        
        citation_coverage = len(cited_chunk_ids) / max(len(evidence_chunk_ids), 1)
        
        # Check if answer requires citations (has specific claims)
        answer_has_claims = len(answer.split(".")) > 2  # Multiple sentences
        
        # Check citation requirement compliance
        requires_citations = answer_has_claims and len(citations) > 0
        
        # Quote overlap check (simplified)
        evidence_text = " ".join([c.get("text", "") for c in evidence_chunks]).lower()
        answer_lower = answer.lower()
        
        # Simple word overlap metric
        answer_words = set(answer_lower.split())
        evidence_words = set(evidence_text.split())
        word_overlap = len(answer_words & evidence_words) / max(len(answer_words), 1)
        
        return {
            "citation_coverage": citation_coverage,
            "requires_citations": requires_citations,
            "has_citations": len(citations) > 0,
            "word_overlap": word_overlap,
            "faithfulness_score": (citation_coverage * 0.5 + word_overlap * 0.5),
            "passed": citation_coverage >= 0.5 and (not answer_has_claims or len(citations) > 0)
        }


class HallucinationChecker:
    """
    Simple hallucination checker that verifies answer claims
    against retrieved context.
    """
    
    def check(self, answer: str, context_chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Check if answer contains information not present in context.
        
        Returns:
            Dict with hallucination_score (0-1, lower is better) and flagged_claims
        """
        context_text = " ".join([c.get("text", "") for c in context_chunks]).lower()
        answer_lower = answer.lower()
        
        # Simple heuristic: check if answer contains specific claims
        # In production, use more sophisticated NLP methods
        answer_sentences = [s.strip() for s in answer_lower.split(".") if len(s.strip()) > 20]
        
        flagged_claims = []
        for sentence in answer_sentences:
            # Check if sentence contains specific entities/numbers not in context
            # This is a simplified check
            if len(sentence) > 50:  # Only check substantial claims
                # Extract potential entities (numbers, capitalized words)
                words = sentence.split()
                # Simple check: if sentence has many unique terms not in context
                unique_terms = set(words) - set(context_text.split())
                if len(unique_terms) > len(words) * 0.3:  # More than 30% unique
                    flagged_claims.append(sentence)
        
        hallucination_score = len(flagged_claims) / max(len(answer_sentences), 1)
        
        return {
            "hallucination_score": min(hallucination_score, 1.0),
            "flagged_claims": flagged_claims,
            "context_coverage": len(context_text) / max(len(answer), 1)
        }


class SchemaValidator:
    """
    Validates that LLM outputs conform to expected schemas.
    """
    
    def validate(self, data: Dict[str, Any], schema: BaseModel) -> Dict[str, Any]:
        """
        Validate data against a Pydantic schema.
        
        Returns:
            Dict with is_valid, errors (if any), and validated_data
        """
        try:
            validated = schema(**data)
            return {
                "is_valid": True,
                "errors": [],
                "validated_data": validated.dict()
            }
        except ValidationError as e:
            return {
                "is_valid": False,
                "errors": [str(err) for err in e.errors()],
                "validated_data": None
            }
    
    def validate_response(self, response: Dict[str, Any], required_fields: List[str]) -> Dict[str, Any]:
        """
        Validate response has required fields and types.
        
        Args:
            response: Response dict to validate
            required_fields: List of required field names
        
        Returns:
            Validation result
        """
        missing_fields = [field for field in required_fields if field not in response]
        
        # Check evidence/citations requirement
        has_evidence = "evidence" in response or "citations" in response
        
        return {
            "is_valid": len(missing_fields) == 0,
            "missing_fields": missing_fields,
            "has_evidence": has_evidence,
            "passed": len(missing_fields) == 0 and has_evidence
        }


class EvaluationHarness:
    """
    Complete evaluation harness for document intelligence system.
    """
    
    def __init__(self):
        self.faithfulness_checker = FaithfulnessChecker()
        self.hallucination_checker = HallucinationChecker()
        self.schema_validator = SchemaValidator()
    
    def evaluate_response(
        self,
        response: Dict[str, Any],
        evidence_chunks: List[Dict[str, Any]],
        expected_schema: Optional[BaseModel] = None
    ) -> Dict[str, Any]:
        """
        Comprehensive evaluation of a query response.
        
        Returns:
            Dict with all evaluation metrics
        """
        answer = response.get("answer", "")
        citations = response.get("citations", [])
        
        # Faithfulness check
        faithfulness = self.faithfulness_checker.check_faithfulness(
            answer, evidence_chunks, citations
        )
        
        # Hallucination check
        hallucination = self.hallucination_checker.check(answer, evidence_chunks)
        
        # Schema validation
        schema_result = None
        if expected_schema:
            schema_result = self.schema_validator.validate(response, expected_schema)
        else:
            # Basic validation
            schema_result = self.schema_validator.validate_response(
                response,
                ["answer", "citations"]
            )
        
        # Overall pass/fail
        passed = (
            faithfulness.get("passed", False) and
            hallucination.get("hallucination_score", 1.0) < 0.5 and
            schema_result.get("is_valid", False) if schema_result else True
        )
        
        return {
            "passed": passed,
            "faithfulness": faithfulness,
            "hallucination": hallucination,
            "schema_validation": schema_result,
            "overall_score": (
                faithfulness.get("faithfulness_score", 0) * 0.4 +
                (1 - hallucination.get("hallucination_score", 1)) * 0.3 +
                (1.0 if schema_result.get("is_valid", False) else 0.0) * 0.3
            )
        }

    """
    Validates that LLM outputs conform to expected schemas.
    """
    
    def validate(self, data: Dict[str, Any], schema: BaseModel) -> Dict[str, Any]:
        """
        Validate data against a Pydantic schema.
        
        Returns:
            Dict with is_valid, errors (if any), and validated_data
        """
        try:
            validated = schema(**data)
            return {
                "is_valid": True,
                "errors": [],
                "validated_data": validated.dict()
            }
        except ValidationError as e:
            return {
                "is_valid": False,
                "errors": [str(err) for err in e.errors()],
                "validated_data": None
            }