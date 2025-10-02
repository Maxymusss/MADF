# DSPy - Commonly Used Modules

**Library**: dspy-ai
**Type**: Direct Python Library
**Purpose**: Programming framework for LMs (not prompting)
**Documentation**: https://dspy.ai/
**GitHub**: https://github.com/stanfordnlp/dspy

---

## Core Concept

DSPy shifts from prompting to **programming** language models:
- **Signatures**: Task definitions (input → output)
- **Modules**: Reusable LM components
- **Optimizers**: Self-improvement and compilation

**Key Insight**: All DSPy modules are built using `dspy.Predict` as foundation

---

## Installation & Setup

```python
import dspy

# Configure LM
lm = dspy.LM('openai/gpt-4')
dspy.configure(lm=lm)

# Or with specific settings
dspy.configure(
    lm=lm,
    temperature=0.0,
    max_tokens=1000
)
```

---

## Core Modules

### 1. dspy.Predict

**Purpose**: Basic predictor module (foundation for all others)

**Signature**:
```python
Predict(signature: str | Signature)
```

**Parameters**:
- `signature`: Task definition (e.g., "question -> answer")

**Features**:
- Handles key forms of learning
- Stores instructions, demonstrations, updates
- Does not modify signature
- Base for all other modules

**Usage Priority**: HIGH - Foundational module

**Example**:
```python
# Define signature
generate_answer = dspy.Predict('question -> answer')

# Use it
response = generate_answer(question="What is LangGraph?")
print(response.answer)

# With structured signature
class QA(dspy.Signature):
    """Answer questions with context"""
    context = dspy.InputField()
    question = dspy.InputField()
    answer = dspy.OutputField()

qa = dspy.Predict(QA)
response = qa(context="...", question="...")
```

---

### 2. dspy.ChainOfThought

**Purpose**: Step-by-step reasoning before response

**Signature**:
```python
ChainOfThought(signature: str | Signature, n: int = None)
```

**Parameters**:
- `signature`: Task definition
- `n`: Number of completions to generate (optional)

**Features**:
- Adds intermediate reasoning steps
- Adds `reasoning` field to output
- Often improves quality vs `Predict`
- Simple drop-in replacement for `Predict`

**Usage Priority**: HIGH - Quality improvement

**Example**:
```python
# Basic usage
qa_cot = dspy.ChainOfThought('question -> answer')
response = qa_cot(question="Why is DSPy better than prompting?")
print(response.reasoning)  # Step-by-step thought process
print(response.answer)     # Final answer

# Multiple completions
qa_multi = dspy.ChainOfThought('question -> answer', n=5)
responses = qa_multi(question="...")
# Returns 5 different reasoning chains

# Often just swap ChainOfThought for Predict
# OLD: qa = dspy.Predict('question -> answer')
# NEW: qa = dspy.ChainOfThought('question -> answer')
```

---

### 3. dspy.ReAct

**Purpose**: Agent module that can use tools

**Signature**:
```python
ReAct(signature: str | Signature, tools: list = None)
```

**Parameters**:
- `signature`: Task definition
- `tools`: List of callable tools

**Features**:
- Combines reasoning + acting
- Iterative tool use
- Observation-action loops

**Usage Priority**: MEDIUM - Agent workflows

**Example**:
```python
# Define tools
def search_web(query: str) -> str:
    """Search the web for information"""
    return f"Results for {query}..."

def python_repl(code: str) -> str:
    """Execute Python code"""
    return eval(code)

# Create ReAct agent
agent = dspy.ReAct(
    signature='task -> result',
    tools=[search_web, python_repl]
)

# Use agent
response = agent(task="Find and calculate the average population of top 5 cities")
print(response.result)
```

---

### 4. dspy.ProgramOfThought

**Purpose**: Generates and executes code to solve task

**Signature**:
```python
ProgramOfThought(signature: str | Signature)
```

**Features**:
- Generates code from task
- Executes code
- Returns execution result

**Usage Priority**: LOW - Specialized code generation

**Example**:
```python
# Math problem solving
math_solver = dspy.ProgramOfThought('problem -> solution')
response = math_solver(problem="Calculate factorial of 10")
```

---

### 5. dspy.MultiChainComparison

**Purpose**: Compare multiple ChainOfThought outputs

**Signature**:
```python
MultiChainComparison(signature: str | Signature, M: int = 3)
```

**Parameters**:
- `signature`: Task definition
- `M`: Number of chains to generate and compare

**Features**:
- Generates M reasoning chains
- Compares and selects best
- Higher quality but slower

**Usage Priority**: LOW - Quality-critical tasks

**Example**:
```python
# Generate and compare 5 reasoning chains
qa_compare = dspy.MultiChainComparison('question -> answer', M=5)
response = qa_compare(question="Complex question requiring analysis")
```

---

## Signatures (Task Definitions)

### String Signatures

**Simple format**: `"input_field -> output_field"`

```python
# Single input, single output
classify = dspy.Predict('text -> sentiment')

# Multiple inputs
qa = dspy.Predict('context, question -> answer')

# Multiple outputs
analyze = dspy.Predict('text -> sentiment, confidence')
```

### Structured Signatures

**Class-based**: More control and documentation

```python
class Summarize(dspy.Signature):
    """Summarize long text into concise summary"""
    document = dspy.InputField(desc="Long document to summarize")
    max_words = dspy.InputField(desc="Maximum words in summary")
    summary = dspy.OutputField(desc="Concise summary")

summarizer = dspy.ChainOfThought(Summarize)
result = summarizer(document="...", max_words=50)
```

---

## Optimizers (Self-Improvement)

### 1. dspy.BootstrapFewShot

**Purpose**: Generate few-shot examples automatically

```python
from dspy.teleprompt import BootstrapFewShot

# Define metric
def accuracy_metric(example, pred, trace=None):
    return example.answer == pred.answer

# Optimize
optimizer = BootstrapFewShot(metric=accuracy_metric)
optimized_qa = optimizer.compile(
    student=dspy.ChainOfThought('question -> answer'),
    trainset=training_data
)
```

**Usage Priority**: MEDIUM - Quality improvement

---

### 2. dspy.MIPRO

**Purpose**: Advanced optimizer using instructions + demonstrations

```python
from dspy.teleprompt import MIPRO

optimizer = MIPRO(metric=accuracy_metric)
optimized = optimizer.compile(
    student=module,
    trainset=train_data,
    valset=val_data
)
```

**Usage Priority**: LOW - Advanced optimization

---

## Module Composition

**Modules are composable** - build complex workflows:

```python
class RAGPipeline(dspy.Module):
    def __init__(self):
        super().__init__()
        self.retrieve = dspy.Retrieve(k=5)
        self.generate = dspy.ChainOfThought('context, question -> answer')

    def forward(self, question):
        context = self.retrieve(question)
        return self.generate(context=context, question=question)

# Use pipeline
pipeline = RAGPipeline()
response = pipeline(question="What is DSPy?")
```

---

## Tool Count Summary

**Total DSPy Modules**: 20+ modules/optimizers
**Commonly Used**: 5 modules (80% of use cases)

**Priority Breakdown**:
- **HIGH (2 modules)**: dspy.Predict, dspy.ChainOfThought
- **MEDIUM (2 modules)**: dspy.ReAct, BootstrapFewShot
- **LOW (3 modules)**: dspy.ProgramOfThought, dspy.MultiChainComparison, MIPRO

---

## Performance Characteristics

- **Speed**:
  - `Predict`: Fast (single LM call)
  - `ChainOfThought`: Medium (reasoning overhead)
  - `ReAct`: Slow (iterative tool calls)
  - `MultiChainComparison`: Very slow (M × ChainOfThought)
- **Quality**:
  - `Predict` < `ChainOfThought` < `MultiChainComparison`
- **Cost**: Proportional to LM calls

---

## Testing Priority

**HIGH Priority** (must test):
1. `dspy.Predict` - Foundation module
2. `dspy.ChainOfThought` - Quality improvement
3. Signature definition (string vs. class)
4. Module composition

**MEDIUM Priority**:
1. `dspy.ReAct` - Tool-using agents
2. `BootstrapFewShot` - Optimization

**LOW Priority**:
1. `dspy.ProgramOfThought` - Code generation
2. `dspy.MultiChainComparison` - Advanced comparison
3. Advanced optimizers (MIPRO)

---

## Comparison: DSPy vs Traditional Prompting

| Aspect | DSPy | Traditional Prompting | Winner |
|--------|------|----------------------|--------|
| Approach | Programming | Prompt engineering | DSPy (systematic) |
| Reusability | High (modules) | Low (copy-paste) | DSPy |
| Optimization | Automatic | Manual | DSPy |
| Composability | Native | Hard | DSPy |
| Learning curve | Steeper | Easier | Prompting |
| Maintainability | High | Low | DSPy |
| Debugging | Structured | Ad-hoc | DSPy |

**DSPy Strengths**:
- Best for complex LM pipelines
- Automatic optimization
- Composable modules
- Systematic approach
- Quality improvements via CoT

**Traditional Prompting Strengths**:
- Best for simple one-off tasks
- Lower learning curve
- Direct control
- No framework overhead

---

## Use Case Recommendations

**Use DSPy when**:
- Building complex LM workflows
- Need automatic optimization
- Want reusable components
- Multi-step reasoning required
- Self-improving systems
- LangGraph agent enhancement

**Use Traditional Prompting when**:
- Simple single-shot tasks
- Rapid prototyping
- One-off experiments
- No optimization needed

---

## LangGraph Integration Pattern

**Story 1.4**: DSPy for self-improvement in LangGraph agents

```python
import dspy

class AgentModule(dspy.Module):
    def __init__(self):
        super().__init__()
        self.task_analyzer = dspy.ChainOfThought('task -> analysis, steps')
        self.code_generator = dspy.ChainOfThought('analysis, steps -> code')

    def forward(self, task: str):
        # Analyze task
        analysis = self.task_analyzer(task=task)

        # Generate code
        code = self.code_generator(
            analysis=analysis.analysis,
            steps=analysis.steps
        )

        return code

# Optimize with training data
from dspy.teleprompt import BootstrapFewShot

def quality_metric(example, pred, trace=None):
    # Custom metric
    return pred.code.count("def") > 0

optimizer = BootstrapFewShot(metric=quality_metric)
optimized_agent = optimizer.compile(
    student=AgentModule(),
    trainset=training_examples
)
```

---

## Best Practices

1. **Start with ChainOfThought**: Often better than Predict with minimal overhead
2. **Use structured Signatures**: Better documentation and type hints
3. **Compose modules**: Build complex pipelines from simple parts
4. **Optimize with data**: Use BootstrapFewShot when you have training examples
5. **Define clear metrics**: Essential for optimization
6. **Cache LM calls**: Use DSPy's built-in caching
7. **Use ReAct for agents**: When tools are needed
8. **Test before optimizing**: Ensure base module works
9. **Monitor costs**: LM calls add up with optimization
10. **Version signatures**: Track changes to task definitions

---

## Common Patterns

### RAG Pipeline
```python
class RAG(dspy.Module):
    def __init__(self, k=3):
        self.retrieve = dspy.Retrieve(k=k)
        self.generate = dspy.ChainOfThought('context, question -> answer')

    def forward(self, question):
        context = self.retrieve(question).passages
        return self.generate(context=context, question=question)
```

### Multi-Step Agent
```python
class MultiStepAgent(dspy.Module):
    def __init__(self):
        self.plan = dspy.ChainOfThought('task -> steps')
        self.execute = dspy.ReAct('step -> result', tools=[...])

    def forward(self, task):
        plan = self.plan(task=task)
        results = [self.execute(step=s) for s in plan.steps]
        return results
```

### Self-Correcting Module
```python
class SelfCorrect(dspy.Module):
    def __init__(self):
        self.generate = dspy.Predict('input -> output')
        self.critique = dspy.ChainOfThought('output -> critique, improved')

    def forward(self, input):
        output = self.generate(input=input)
        improved = self.critique(output=output.output)
        return improved.improved
```

---

## Error Handling

```python
import dspy

try:
    lm = dspy.LM('openai/gpt-4')
    dspy.configure(lm=lm)

    qa = dspy.ChainOfThought('question -> answer')
    response = qa(question="What is DSPy?")
except Exception as e:
    print(f"DSPy error: {e}")
```

---

## Integration with MADF

**Story 1.4 Goal**: Use DSPy for agent self-improvement

**Approach**:
1. Wrap LangGraph agents in DSPy modules
2. Define quality metrics per agent
3. Collect training data from agent execution
4. Optimize with BootstrapFewShot
5. Deploy optimized agents

**Benefits**:
- Automatic prompt improvement
- Systematic quality enhancement
- Data-driven optimization
- Composable agent components
