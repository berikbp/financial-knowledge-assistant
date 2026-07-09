import os

from dotenv import load_dotenv
from openai import OpenAI

from src.retrieval.hybrid_retriever import HybridResult
from src.generation.context_formatter import format_context


class AnswerGenerator:
    def __init__(self, model: str | None = None):
        load_dotenv()

        api_key = os.getenv("OPENAI_API_KEY")

        if not api_key:
            raise ValueError("OPENAI_API_KEY is missing. Add it to your .env file.")

        self.client = OpenAI(api_key=api_key)
        self.model = model or os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    def generate_answer(
        self,
        query: str,
        results: list[HybridResult],
    ) -> str:
        context = format_context(results)

        prompt = f"""
You are a strict financial knowledge assistant.

Answer the user's question using ONLY the retrieved context.


Rules:
- Extract only statements that are explicitly present in the context.
- Do not rewrite a weak relation as a strong causal claim.
- Do not combine two different source statements into one new conclusion.
- Do not use outside knowledge.
- You do not need to use every source.
- Preserve the meaning of the source exactly.
- Do not replace "economic growth", "GDP", "economy", or "economic slowdown" with "inflation".
- If a sentence says something affected GDP or economic growth, do not report it as an inflation factor.
- For inflation questions, ignore retrieved chunks that mainly discuss GDP/economic growth unless they directly mention inflation, prices, price pressure, or inflation expectations.
- Be careful with pronouns and nearby sentences. If a phrase like "замедление" refers to economic growth, GDP, or the economy, do not rewrite it as "замедление инфляции".
- For inflation-factor questions, ignore statements about GDP, economic growth, oil-sector production, or economic slowdown unless the same sentence explicitly connects them to inflation, prices, inflation expectations, or inflation pressure.
- If a retrieved source contains both inflation and GDP information, only extract the inflation-related sentences.
Question relevance rules:
- Prefer information that directly answers the user's question over related background facts.
- Prefer chunks that contain direct wording from the user's question.
- If the question asks about inflation factors, prefer statements containing words like:
  "инфляция", "инфляционные ожидания", "инфляционное давление",
  "продовольственная инфляция", "цены", "дезинфляционный фактор".
- If the question asks about inflation factors, do NOT include GDP growth, economic slowdown,
  oil-sector output, or general macroeconomic background unless the context directly says it affected
  inflation, price pressure, inflation expectations, or inflation dynamics.
- If the question asks about line items, list the line items directly from the statement.
- If the question asks about measures, list measures/actions directly from the context.

Completeness rules:
- When the question asks for factors, measures, reasons, or line items, include up to 5 well-supported items if they are present in the context.
- If one source contains several directly relevant items, extract several items from that source.
- Do not stop at 3 items if more directly supported items are available.
- Prefer complete coverage of the main directly relevant concepts over shortness.

Citation rules:
- Every answer point must include a citation.
- Citation format must be exactly [1], [2], [3].
- Do not write [DOCUMENT 1], (Source 1), "Source 1", or any other citation format.
- Do NOT create a Sources section.

Language rules:
- Use the same language as the user's question.

Output format:
1. <directly supported answer point> [source number]
2. <directly supported answer point> [source number]
3. <directly supported answer point> [source number]
4. <directly supported answer point, if supported> [source number]
5. <directly supported answer point, if supported> [source number]

User question:
{query}

Retrieved context:
{context}

Answer:
""".strip()

        response = self.client.responses.create(
            model=self.model,
            input=prompt,
            temperature=0.1,
        )

        return response.output_text





















'''
The problem was **LLM faithfulness**.

Not retrieval. Not Qdrant. Not BM25. Not reranker.

The system retrieved relevant chunks, but the LLM was taking those chunks and **over-interpreting** them.

## What was happening

We gave the LLM retrieved context and asked:

```text
Answer the question using the context.
```

That sounds safe, but in practice the model did this:

```text
context fact A + context fact B + its own reasoning
→ new causal claim
```

Example:

The retrieved chunk said something like:

```text
Oil-sector limitations slowed GDP growth in Q1 2026.
```

The model answered:

```text
Oil-sector problems affected inflation expectations.
```

That is not directly stated. It is an inference.

So the issue was:

```text
The answer sounded reasonable, but it was not fully grounded in the retrieved evidence.
```

That is dangerous in financial RAG.

## Why it happened

LLMs are trained to be helpful and explanatory. So when the context contains related facts, the model tries to connect them.

It sees:

```text
oil sector
GDP slowdown
inflation
macroeconomic conditions
```

and tries to create a smooth answer.

But in RAG, especially financial RAG, we do **not** want smooth unsupported reasoning. We want:

```text
Only what the documents explicitly support.
```

That is why we rewrote the prompt several times.

## What the first prompt did wrong

The first prompt said:

```text
Answer using only the provided context.
Use citations.
```

That was not enough.

Because “using context” does not prevent the model from doing this:

```text
The context says X.
The model infers Y.
Then writes Y with citation.
```

The citation looked valid, but the cited chunk did not directly support the exact claim.

That is called a **citation faithfulness problem**.

## What we changed

We progressively made the prompt stricter.

First, we added:

```text
Do not invent facts.
Do not infer causal relationships.
Every claim must be directly supported.
```

That reduced some hallucination, but the model still over-explained.

Then we added:

```text
Do not use every source.
Ignore weak chunks.
Do not create unsupported causal links.
If a chunk talks about GDP but not inflation, don't present it as an inflation factor.
```

That helped.

Then we removed LLM-generated sources because it duplicated and mismatched sources:

```text
[4] chunk 28
[5] chunk 28
```

So we decided:

```text
LLM writes answer only.
Python prints sources separately.
```

That was a good engineering fix.

Finally, we changed the answer style from free-form summary to **extractive format**:

```text
factor — what the context explicitly says [citation]
```

That solved most of the issue.

## What we actually solved

We solved three separate problems:

### 1. Over-inference

Before:

```text
The model created causal links not directly stated.
```

After:

```text
The model mostly lists only factors directly supported by retrieved chunks.
```

### 2. Bad source formatting

Before:

```text
The model generated messy Sources section.
```

After:

```text
Python prints the source list separately and reliably.
```

### 3. Too much context noise

Before:

```text
Top 5 chunks included some noisy/table-heavy chunks.
```

After:

```text
We used fewer top chunks and stricter prompting, so the model had less room to hallucinate.
```

## The core lesson

Retrieval answers two questions:

```text
Did we find relevant evidence?
```

Generation answers another question:

```text
Can the LLM use that evidence without adding unsupported claims?
```

We had solved retrieval, but generation was still too free.

So the prompt rewrites were about moving from:

```text
"Write a helpful answer from these chunks"
```

to:

```text
"Extract only explicitly supported claims from these chunks"
```

That is the key.

## Final state

Now the answer is not perfect, but it is much safer:

```text
Shorter
more extractive
uses citations
does not create its own Sources section
less likely to invent causal links
```

The remaining issue is that the LLM can still occasionally phrase something too strongly. That is why the next serious step is evaluation/faithfulness checking.
'''