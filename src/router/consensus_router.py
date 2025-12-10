"""
Multi-Model Consensus and Verification Router for Legal AI.

This module implements a robust multi-model system where:
1. Primary models generate responses
2. Verification models check for errors
3. Consensus analysis produces final output with confidence scores

Designed for high-stakes legal applications where accuracy is critical.
"""

import asyncio
from enum import Enum
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import logging
from collections import Counter

logger = logging.getLogger(__name__)


class ModelRole(Enum):
    """Role of a model in the consensus system."""
    PRIMARY = "primary"  # Generates initial responses
    VERIFIER = "verifier"  # Checks and validates responses
    FACT_CHECKER = "fact_checker"  # Validates facts and citations


@dataclass
class ModelResponse:
    """Response from a single model."""
    model_name: str
    response: str
    confidence: float  # 0.0 to 1.0
    citations: List[str]
    metadata: Dict[str, Any]
    role: ModelRole


@dataclass
class ConsensusResult:
    """Final consensus result with verification."""
    final_response: str
    confidence_score: float  # 0.0 to 1.0
    agreement_level: str  # 'unanimous', 'strong', 'moderate', 'weak', 'conflicting'
    model_responses: List[ModelResponse]
    verification_notes: List[str]
    discrepancies: List[str]
    requires_human_review: bool
    citations: List[str]


class ConsensusRouter:
    """
    Routes queries to multiple models and produces consensus with verification.

    Architecture:
    - 3 Primary models generate responses in parallel
    - 2 Verification models check the primary responses
    - Consensus analysis produces final output with confidence
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the consensus router.

        Args:
            config: Configuration for models and consensus settings
        """
        self.config = config or {}

        # Define model assignments
        self.primary_models = [
            {"name": "gpt-4", "provider": "openai", "weight": 1.2},
            {"name": "claude-opus", "provider": "anthropic", "weight": 1.2},
            {"name": "gemini-pro", "provider": "google", "weight": 1.0},
        ]

        self.verification_models = [
            {"name": "llama-3-70b", "provider": "groq", "purpose": "error_detection"},
            {"name": "mixtral-8x7b", "provider": "huggingface", "purpose": "fact_checking"},
        ]

        # Consensus thresholds
        self.unanimous_threshold = 1.0  # All models agree
        self.strong_threshold = 0.8     # 80%+ agreement
        self.moderate_threshold = 0.6   # 60%+ agreement
        self.weak_threshold = 0.4       # 40%+ agreement

        # When to require human review
        self.human_review_threshold = 0.6  # Below 60% confidence

    async def get_consensus(
        self,
        query: str,
        context: Optional[str] = None,
        use_verification: bool = True,
        min_confidence: float = 0.6
    ) -> ConsensusResult:
        """
        Get consensus response from multiple models with verification.

        Args:
            query: Legal query to process
            context: Optional context (RAG results, case law, etc.)
            use_verification: Whether to use verification models
            min_confidence: Minimum confidence threshold (0.0 to 1.0)

        Returns:
            ConsensusResult with final response and metadata
        """
        logger.info(f"Processing query with consensus: {query[:100]}...")

        # Step 1: Get responses from primary models (parallel)
        primary_responses = await self._get_primary_responses(query, context)

        # Step 2: Analyze consensus among primary models
        consensus_analysis = self._analyze_consensus(primary_responses)

        # Step 3: Run verification if enabled
        verification_notes = []
        if use_verification and len(primary_responses) > 0:
            verification_notes = await self._verify_responses(
                query,
                primary_responses,
                consensus_analysis
            )

        # Step 4: Generate final response
        final_response = self._generate_final_response(
            primary_responses,
            consensus_analysis,
            verification_notes
        )

        # Step 5: Calculate overall confidence
        confidence_score = self._calculate_confidence(
            primary_responses,
            consensus_analysis,
            verification_notes
        )

        # Step 6: Identify discrepancies
        discrepancies = self._identify_discrepancies(primary_responses)

        # Step 7: Determine if human review needed
        requires_review = (
            confidence_score < self.human_review_threshold or
            consensus_analysis['agreement_level'] == 'conflicting' or
            len(discrepancies) > 2
        )

        # Collect all citations
        all_citations = []
        for resp in primary_responses:
            all_citations.extend(resp.citations)
        all_citations = list(set(all_citations))  # Deduplicate

        return ConsensusResult(
            final_response=final_response,
            confidence_score=confidence_score,
            agreement_level=consensus_analysis['agreement_level'],
            model_responses=primary_responses,
            verification_notes=verification_notes,
            discrepancies=discrepancies,
            requires_human_review=requires_review,
            citations=all_citations
        )

    async def _get_primary_responses(
        self,
        query: str,
        context: Optional[str]
    ) -> List[ModelResponse]:
        """
        Get responses from all primary models in parallel.

        Args:
            query: The query to process
            context: Optional context

        Returns:
            List of ModelResponse objects
        """
        # TODO: Implement actual API calls to each model
        # For now, return mock responses

        tasks = []
        for model in self.primary_models:
            task = self._query_model(
                model_name=model['name'],
                provider=model['provider'],
                query=query,
                context=context,
                role=ModelRole.PRIMARY
            )
            tasks.append(task)

        responses = await asyncio.gather(*tasks, return_exceptions=True)

        # Filter out failed responses
        valid_responses = [
            r for r in responses
            if isinstance(r, ModelResponse)
        ]

        if len(valid_responses) == 0:
            logger.error("All primary models failed to respond")
            raise RuntimeError("No valid responses from primary models")

        return valid_responses

    async def _verify_responses(
        self,
        query: str,
        primary_responses: List[ModelResponse],
        consensus_analysis: Dict[str, Any]
    ) -> List[str]:
        """
        Use verification models to check primary responses.

        Args:
            query: Original query
            primary_responses: Responses from primary models
            consensus_analysis: Consensus analysis results

        Returns:
            List of verification notes/issues found
        """
        verification_notes = []

        # Prepare verification prompt
        responses_text = "\n\n".join([
            f"Model {i+1} ({resp.model_name}):\n{resp.response}"
            for i, resp in enumerate(primary_responses)
        ])

        verification_prompt = f"""
You are a verification model checking legal AI responses for accuracy.

Original Query: {query}

Responses to verify:
{responses_text}

Please:
1. Check for factual errors
2. Identify contradictions between responses
3. Verify any citations mentioned
4. Flag any legal inaccuracies
5. Note areas of uncertainty

Provide a concise verification report.
"""

        # Run verification models
        verification_tasks = []
        for model in self.verification_models:
            task = self._query_model(
                model_name=model['name'],
                provider=model['provider'],
                query=verification_prompt,
                context=None,
                role=ModelRole.VERIFIER
            )
            verification_tasks.append(task)

        verification_responses = await asyncio.gather(
            *verification_tasks,
            return_exceptions=True
        )

        # Extract verification notes
        for resp in verification_responses:
            if isinstance(resp, ModelResponse):
                verification_notes.append(
                    f"[{resp.model_name}] {resp.response}"
                )

        return verification_notes

    async def _query_model(
        self,
        model_name: str,
        provider: str,
        query: str,
        context: Optional[str],
        role: ModelRole
    ) -> ModelResponse:
        """
        Query a single model.

        Args:
            model_name: Name of the model
            provider: Provider (openai, anthropic, google, groq, huggingface)
            query: Query to send
            context: Optional context
            role: Role of this model

        Returns:
            ModelResponse object
        """
        # TODO: Implement actual API calls based on provider
        # This is a stub that should be replaced with real implementations

        logger.info(f"Querying {model_name} ({provider}) for {role.value}")

        # Mock response for now
        # In production, this would call the actual API
        return ModelResponse(
            model_name=model_name,
            response=f"[Mock response from {model_name}]",
            confidence=0.8,
            citations=[],
            metadata={"provider": provider, "role": role.value},
            role=role
        )

    def _analyze_consensus(
        self,
        responses: List[ModelResponse]
    ) -> Dict[str, Any]:
        """
        Analyze consensus among responses.

        Args:
            responses: List of model responses

        Returns:
            Dictionary with consensus analysis
        """
        if len(responses) == 0:
            return {
                'agreement_level': 'none',
                'agreement_score': 0.0,
                'common_points': [],
                'conflicting_points': []
            }

        # Simple analysis based on response similarity
        # In production, use semantic similarity, fact extraction, etc.

        # Calculate average confidence
        avg_confidence = sum(r.confidence for r in responses) / len(responses)

        # Determine agreement level
        if avg_confidence >= self.unanimous_threshold:
            agreement_level = 'unanimous'
        elif avg_confidence >= self.strong_threshold:
            agreement_level = 'strong'
        elif avg_confidence >= self.moderate_threshold:
            agreement_level = 'moderate'
        elif avg_confidence >= self.weak_threshold:
            agreement_level = 'weak'
        else:
            agreement_level = 'conflicting'

        return {
            'agreement_level': agreement_level,
            'agreement_score': avg_confidence,
            'num_responses': len(responses),
            'common_points': [],  # TODO: Extract common points
            'conflicting_points': []  # TODO: Extract conflicts
        }

    def _generate_final_response(
        self,
        primary_responses: List[ModelResponse],
        consensus_analysis: Dict[str, Any],
        verification_notes: List[str]
    ) -> str:
        """
        Generate final consensus response.

        Args:
            primary_responses: Responses from primary models
            consensus_analysis: Consensus analysis
            verification_notes: Notes from verification models

        Returns:
            Final response text
        """
        if len(primary_responses) == 0:
            return "Unable to generate response - no valid model responses."

        # Strategy: Use highest-confidence response as base
        # Then incorporate points from other responses

        sorted_responses = sorted(
            primary_responses,
            key=lambda r: r.confidence,
            reverse=True
        )

        final_response = sorted_responses[0].response

        # Add agreement level note
        agreement_note = (
            f"\n\n[Consensus Level: {consensus_analysis['agreement_level'].upper()}]"
        )

        # Add verification notes if significant
        if verification_notes:
            verification_summary = "\n\n[Verification Notes]:\n" + "\n".join(
                f"- {note[:200]}" for note in verification_notes[:3]
            )
        else:
            verification_summary = ""

        return final_response + agreement_note + verification_summary

    def _calculate_confidence(
        self,
        primary_responses: List[ModelResponse],
        consensus_analysis: Dict[str, Any],
        verification_notes: List[str]
    ) -> float:
        """
        Calculate overall confidence score.

        Args:
            primary_responses: Primary model responses
            consensus_analysis: Consensus analysis
            verification_notes: Verification notes

        Returns:
            Confidence score (0.0 to 1.0)
        """
        if len(primary_responses) == 0:
            return 0.0

        # Base score: average of primary model confidences
        base_score = sum(r.confidence for r in primary_responses) / len(primary_responses)

        # Boost for high agreement
        agreement_score = consensus_analysis['agreement_score']
        consensus_boost = (agreement_score - 0.5) * 0.2  # -0.1 to +0.1

        # Penalty for verification issues
        verification_penalty = len(verification_notes) * 0.05  # -0.05 per issue

        # Final confidence
        confidence = base_score + consensus_boost - verification_penalty

        # Clamp to [0, 1]
        return max(0.0, min(1.0, confidence))

    def _identify_discrepancies(
        self,
        responses: List[ModelResponse]
    ) -> List[str]:
        """
        Identify discrepancies between model responses.

        Args:
            responses: List of model responses

        Returns:
            List of discrepancy descriptions
        """
        discrepancies = []

        # TODO: Implement semantic comparison
        # For now, return empty list

        # Example: Check if responses have very different lengths
        lengths = [len(r.response) for r in responses]
        if max(lengths) > min(lengths) * 2:
            discrepancies.append(
                "Response lengths vary significantly (may indicate different interpretations)"
            )

        return discrepancies


# Factory function
def create_consensus_router(config: Optional[Dict[str, Any]] = None) -> ConsensusRouter:
    """
    Create and configure a ConsensusRouter instance.

    Args:
        config: Optional configuration dictionary

    Returns:
        Configured ConsensusRouter
    """
    return ConsensusRouter(config)
