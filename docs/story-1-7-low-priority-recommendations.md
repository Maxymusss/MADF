# Story 1.7 - Low Priority Recommendations Explained

This document explains each LOW PRIORITY recommendation from the implementation review, including rationale, implementation approach, and trade-offs.

---

## LOW PRIORITY #1: Add Enforcement Wrapper for process_task()

### Problem Statement
Currently, there's no programmatic enforcement that agents call `clarify_task()` before executing `process_task()`. This relies on developers remembering to add the clarification check in each agent implementation.

**Risk**: Developers might forget to add clarification logic, undermining the BMAD inquiry protocol.

### Current Pattern (Manual)
```python
class AnalystAgent(BaseAgent):
    def process_task(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        # Developer must remember to add this:
        clarification = self.clarify_task(task, context)
        if not clarification["clear"]:
            return {
                "status": "needs_clarification",
                "questions": clarification["questions"]
            }

        # Actual task processing
        return {"result": "analysis complete"}
```

**Issues**:
- Easy to forget clarification check
- Inconsistent implementation across agents
- No compile-time or runtime enforcement

### Proposed Solution: Template Method Pattern

Implement a non-abstract `process_task()` in `BaseAgent` that enforces clarification, then call abstract `_execute_task()`:

```python
class BaseAgent(ABC):
    def process_task(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process task with automatic clarification enforcement (Template Method Pattern)

        This method is final - agents should implement _execute_task() instead
        """
        # Step 1: Clarify task (automatic)
        clarification = self.clarify_task(task, context)

        if not clarification["clear"]:
            # Return questions without executing
            return {
                "status": "needs_clarification",
                "questions": clarification["questions"],
                "capability": clarification.get("capability"),
                "alternatives": clarification.get("alternatives"),
                "agent": self.name
            }

        # Step 2: Execute task (delegated to subclass)
        try:
            result = self._execute_task(task, context, clarification)
            result["agent"] = self.name
            result["capability_used"] = clarification["capability"]
            return result
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "agent": self.name
            }

    @abstractmethod
    def _execute_task(
        self,
        task: str,
        context: Dict[str, Any],
        clarification: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute task after clarification is complete

        Args:
            task: Task description
            context: Task context
            clarification: Clarification result from clarify_task()

        Returns:
            Dict with execution results
        """
        pass
```

**Agent Implementation Changes**:
```python
class AnalystAgent(BaseAgent):
    # Old way (manual clarification):
    # def process_task(self, task, context):
    #     clarification = self.clarify_task(task, context)
    #     if not clarification["clear"]:
    #         return {"status": "needs_clarification", ...}
    #     return {"result": "done"}

    # New way (automatic clarification):
    def _execute_task(self, task, context, clarification):
        # Clarification already handled by BaseAgent.process_task()
        # Just implement the actual logic
        return {"result": "analysis complete"}
```

### Benefits
✅ **Guaranteed Clarification**: Every agent MUST go through clarification phase
✅ **Consistency**: All agents follow same pattern
✅ **Less Boilerplate**: Agents don't repeat clarification logic
✅ **Easier Testing**: Can test clarification enforcement once in BaseAgent

### Trade-offs
⚠️ **Breaking Change**: Existing agent implementations must be refactored
⚠️ **Less Flexibility**: Agents can't bypass clarification (but this is desired)
⚠️ **Slightly More Complex**: Template Method Pattern adds indirection

### Implementation Effort
- **Effort**: Medium (2-3 hours)
- **Files Changed**:
  - `src/agents/base_agent.py` (add enforcement wrapper)
  - All 5 agent files (rename `process_task` → `_execute_task`)
  - Tests (update to use new pattern)
- **Risk**: Medium (breaking change to existing agents)

### Recommendation
**Implement if**: You want strong guarantees that inquiry protocol is always followed
**Skip if**: You trust developers to manually add clarification checks, or prefer flexibility

---

## LOW PRIORITY #2: Add NLP-Based Context Matching

### Problem Statement
Current keyword extraction uses simple heuristics:
- Pattern: "What are the user requirements?"
- Keywords: Extracted via hardcoded mappings (`user` → `["user", "users", "target_user"]`)
- Context check: Simple `if keyword in context` lookup

**Limitations**:
- Misses semantic equivalents (e.g., "stakeholder" vs "user")
- Can't handle synonyms or related concepts
- No understanding of question semantics

### Current Implementation (HIGH PRIORITY FIX)
```python
class ContextKeywordExtractor:
    DOMAIN_MAPPINGS = {
        "user": ["user", "users", "target_user", "target_users", "audience"],
        "requirement": ["requirement", "requirements", "criteria", "acceptance_criteria"],
        # ...
    }

    @classmethod
    def extract_keywords(cls, pattern: str) -> Set[str]:
        # Clean pattern, extract words, apply domain mappings
        # Returns: set of potential context keys
```

**Example**:
- Pattern: "What are the user requirements?"
- Extracted: `{"user", "users", "requirement", "requirements", "criteria"}`
- Context: `{"stakeholder_needs": [...]}` ← **MISS** (doesn't match "user")

### Proposed Solution: spaCy NLP Integration

Use spaCy for semantic understanding:

```python
import spacy

class NLPContextMatcher:
    """NLP-based context matching using spaCy"""

    def __init__(self):
        # Load small English model (12MB)
        self.nlp = spacy.load("en_core_web_sm")

        # Define semantic similarity thresholds
        self.similarity_threshold = 0.6  # Tunable

    def extract_semantic_keywords(self, pattern: str) -> Set[str]:
        """
        Extract keywords with semantic understanding

        Uses spaCy's:
        - Part-of-speech tagging (extract nouns)
        - Lemmatization (normalize word forms)
        - Word vectors (semantic similarity)
        """
        doc = self.nlp(pattern.lower())

        keywords = set()

        # Extract meaningful nouns and verbs
        for token in doc:
            if token.pos_ in ["NOUN", "VERB"] and not token.is_stop:
                keywords.add(token.lemma_)  # Normalized form

        return keywords

    def has_semantic_match(self, pattern: str, context: dict) -> bool:
        """
        Check if context semantically addresses pattern

        Uses word vector similarity to match related concepts
        """
        pattern_keywords = self.extract_semantic_keywords(pattern)
        pattern_doc = self.nlp(" ".join(pattern_keywords))

        # Check each context key for semantic similarity
        for key in context.keys():
            key_doc = self.nlp(key)

            # Calculate semantic similarity
            similarity = pattern_doc.similarity(key_doc)

            if similarity >= self.similarity_threshold:
                # Check if value is non-empty
                if context[key] and context[key] != "" and context[key] != []:
                    return True

        return False
```

**Example with NLP**:
- Pattern: "What are the user requirements?"
- Extracted: `{"user", "requirement"}` (lemmatized)
- Context: `{"stakeholder_needs": [...]}`
- Similarity: `similarity("user", "stakeholder")` = 0.65 ✅ **MATCH**

### Benefits
✅ **Semantic Understanding**: Matches related concepts (user/stakeholder, requirement/need)
✅ **Better Accuracy**: Reduces false negatives from strict keyword matching
✅ **Handles Synonyms**: Automatically understands word relationships
✅ **Lemmatization**: Normalizes word forms (requirements → requirement)

### Trade-offs
⚠️ **Dependency**: Adds spaCy (~50MB with model)
⚠️ **Performance**: Slower than keyword matching (~10-50ms per pattern)
⚠️ **Complexity**: Requires tuning similarity threshold
⚠️ **Overkill**: Current keyword approach might be "good enough"

### Implementation Effort
- **Effort**: Medium-High (4-6 hours including testing/tuning)
- **Dependencies**: `spacy`, `en_core_web_sm` model
- **Files Changed**:
  - `src/core/nlp_context_matcher.py` (new file)
  - `src/agents/base_agent.py` (optional: add NLP mode flag)
  - `pyproject.toml` (add spacy dependency)
- **Risk**: Low (additive feature, doesn't break existing functionality)

### Recommendation
**Implement if**:
- High-stakes use cases requiring accurate context matching
- Users use varied terminology (technical vs business language)
- You have budget for ~50MB dependency

**Skip if**:
- Current keyword matching works well enough
- Performance is critical (keyword matching is ~100x faster)
- Want to minimize dependencies

### Hybrid Approach (Best of Both Worlds)
Make NLP optional:
```python
class BaseAgent:
    def __init__(self, ..., use_nlp: bool = False):
        self.use_nlp = use_nlp
        if use_nlp:
            self.nlp_matcher = NLPContextMatcher()

    def _has_context_for_pattern(self, pattern, context):
        if self.use_nlp:
            return self.nlp_matcher.has_semantic_match(pattern, context)
        else:
            return ContextKeywordExtractor.has_context_for_pattern(pattern, context)
```

**Benefits**: Fast keyword matching by default, NLP when needed

---

## Summary: Low Priority Recommendations

| Recommendation | Effort | Impact | Risk | Implement When |
|----------------|--------|--------|------|----------------|
| **#1: Enforcement Wrapper** | Medium | High (guarantees clarification) | Medium (breaking change) | Want strong clarification guarantees |
| **#2: NLP Context Matching** | Medium-High | Medium (better accuracy) | Low (additive) | High-stakes use cases with varied terminology |

### Suggested Implementation Order (If Pursuing Low Priority Items)
1. **Start with #1 (Enforcement Wrapper)** - Higher impact, ensures inquiry protocol is always followed
2. **Add #2 (NLP) as optional enhancement** - Use hybrid approach (keyword by default, NLP flag for advanced use)

### Current Status Assessment
**Current implementation is PRODUCTION-READY without LOW priority items**:
- HIGH priority fixes ensure robust keyword matching
- MEDIUM priority fixes ensure validation and proper error handling
- LOW priority items are optimizations, not requirements

**Proceed with agent implementations and testing as-is**, revisit LOW priority items based on real-world usage feedback.
