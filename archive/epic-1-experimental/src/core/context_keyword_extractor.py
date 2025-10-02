"""
Context Keyword Extractor for Inquiry Pattern Matching

HIGH PRIORITY FIX: More sophisticated keyword extraction from inquiry patterns
Extracts meaningful keywords/phrases from questions to match against context dicts.
"""

import re
from typing import List, Set


class ContextKeywordExtractor:
    """
    Extracts context keywords from inquiry patterns

    Example:
        Pattern: "What are the user requirements?"
        Keywords: ["user", "requirements", "user_requirements"]

        Pattern: "What scope to analyze? (file/module/system)"
        Keywords: ["scope", "analyze", "analysis", "file", "module", "system"]
    """

    # Common question words to filter out
    QUESTION_WORDS = {
        "what", "which", "who", "where", "when", "why", "how",
        "is", "are", "does", "do", "can", "should", "would", "could",
        "the", "a", "an", "to", "of", "for", "in", "on", "at", "by"
    }

    # Domain-specific keyword mappings
    DOMAIN_MAPPINGS = {
        "user": ["user", "users", "target_user", "target_users", "audience"],
        "requirement": ["requirement", "requirements", "criteria", "acceptance_criteria"],
        "scope": ["scope", "boundary", "boundaries", "coverage"],
        "depth": ["depth", "level", "detail", "granularity"],
        "risk": ["risk", "risks", "risk_level", "probability", "impact"],
        "test": ["test", "tests", "testing", "test_coverage"],
        "architecture": ["architecture", "design", "system_design"],
        "performance": ["performance", "speed", "latency", "throughput"],
        "security": ["security", "auth", "authentication", "authorization"],
    }

    @classmethod
    def extract_keywords(cls, pattern: str) -> Set[str]:
        """
        Extract context keywords from inquiry pattern

        Args:
            pattern: Inquiry pattern (question string)

        Returns:
            Set of potential context keys to check

        Example:
            extract_keywords("What are the user requirements?")
            → {"user", "users", "requirement", "requirements", "criteria", "acceptance_criteria"}
        """
        keywords = set()

        # Clean pattern: lowercase, remove punctuation
        clean_pattern = pattern.lower()
        clean_pattern = re.sub(r'[?!.,;:]', '', clean_pattern)

        # Remove parenthetical hints like "(file/module/system)"
        clean_pattern = re.sub(r'\([^)]*\)', '', clean_pattern)

        # Split into words
        words = clean_pattern.split()

        # Extract meaningful words (filter out question words)
        meaningful_words = [
            word for word in words
            if word not in cls.QUESTION_WORDS and len(word) > 2
        ]

        # Add base words
        keywords.update(meaningful_words)

        # Add domain-specific mappings
        for word in meaningful_words:
            # Check if word is in domain mappings
            for domain_key, domain_values in cls.DOMAIN_MAPPINGS.items():
                if word in domain_key or domain_key in word:
                    keywords.update(domain_values)

        # Add compound keywords (e.g., "user requirements" → "user_requirements")
        if len(meaningful_words) >= 2:
            # Create bigrams
            for i in range(len(meaningful_words) - 1):
                compound = f"{meaningful_words[i]}_{meaningful_words[i+1]}"
                keywords.add(compound)

        return keywords

    @classmethod
    def has_context_for_pattern(cls, pattern: str, context: dict) -> bool:
        """
        Check if context dict has information addressing inquiry pattern

        Args:
            pattern: Inquiry pattern (question)
            context: Context dictionary

        Returns:
            True if context addresses pattern, False otherwise

        Example:
            pattern = "What are the user requirements?"
            context = {"requirements": {"user_stories": [...]}}
            → True (found "requirements")

            context = {"scope": "module"}
            → False (no user/requirement keywords)
        """
        if not context:
            return False

        # Extract keywords from pattern
        keywords = cls.extract_keywords(pattern)

        # Check if any keyword exists in context with non-empty value
        for key in keywords:
            if key in context:
                value = context[key]
                # Check if value is non-empty
                if value is not None and value != "" and value != []:
                    return True

        return False


# Convenience function
def has_context_for_pattern(pattern: str, context: dict) -> bool:
    """
    Convenience wrapper for ContextKeywordExtractor.has_context_for_pattern

    Args:
        pattern: Inquiry pattern
        context: Context dict

    Returns:
        True if context addresses pattern
    """
    return ContextKeywordExtractor.has_context_for_pattern(pattern, context)
