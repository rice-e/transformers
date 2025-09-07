# Proposal: Safe Generation Mode for Hugging Face Transformers

## Motivation
Recent incidents have highlighted the risks of large language models (LLMs) producing unsafe outputs. In one highly publicized case, individuals engaged in self-harm after following harmful suggestions from an AI assistant. These tragic outcomes demonstrate that safety failures are not abstract—they can have **serious real-world consequences**.

At the same time, open source LLMs are rapidly becoming more powerful and accessible. Tools for running models locally (e.g., via Hugging Face, LM Studio, Ollama) are lowering barriers for non-technical users to adopt them. Unlike proprietary models, these deployments may lack built-in safety layers. This means users could interact directly with raw model outputs without the guardrails that commercial providers typically add.

Given this context, it is no longer sufficient to rely on the assumption that safety checks will be added at the application level. **Safety should be available as an integrated, optional feature within the core library itself**, so developers (and eventually end users) can easily enable safeguards when generating text.

## Vision
The proposed feature is an optional **Safe Generation mode** within Hugging Face Transformers. It allows users to activate a safety layer during text generation, ensuring outputs are filtered, re-ranked, or annotated for harmful or biased content.

Key design principles:
- **Opt-in, not enforced:** Default behavior remains unchanged. Safety is available when explicitly enabled.
- **Pluggable safety checkers:** Users can choose their own models or functions for safety evaluation (e.g., toxicity detection, bias classifiers, PII filters).
- **Flexible actions:** Unsafe outputs can be blocked, revised, reranked, or simply annotated with metadata.
- **Lightweight and non-disruptive:** Integrates with existing pipelines without heavy new dependencies.

## User Experience
Example usage might look like:
```python
from transformers import pipeline
pipe = pipeline(
  "safe-text-generation",
  model="gpt2",
  safety_checker="unitary/unbiased-toxic-roberta",
  safety_config={"threshold": 0.5}
)
pipe("Write a joke about ...")
```

Alternatively, a flag within `generate()` could activate safety mode with user-provided checkers:
```python
outputs = model.generate(
  **inputs,
  safe_generate=True,
  safety_checker=my_checker
)
```

## Benefits
- **Developer empowerment:** Lowers the barrier to responsible deployment of LLMs.
- **Consistency with ecosystem:** Mirrors how Hugging Face Diffusers provides a `SafetyChecker` for image generation.
- **Support for diverse safety goals:** Toxicity, bias, PII, and hallucination checks can all be layered in.
- **High visibility and impact:** Widely adopted by researchers and developers, ensuring broad downstream benefit.

## Alignment with Broader Concerns
This proposal responds to a growing societal need: as open source models proliferate, **safety should not be left as an afterthought**. Many non-technical users may turn to local LLMs as free alternatives to commercial APIs. Without integrated safety tools, they may unknowingly expose themselves to harmful outputs. Providing an accessible Safe Generation feature within Transformers is a proactive way to mitigate these risks.

## Conclusion
By offering an opt-in Safe Generation mode, Hugging Face can take a meaningful step toward reducing harm from open source LLMs while preserving user freedom and modularity. The feature would support safer use cases in education, healthcare, legal assistance, and everyday interactions—domains where the stakes of unsafe outputs are highest. This aligns with the broader mission of building open, responsible, and human-centered AI.

