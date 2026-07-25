WEEK 2 — Prompt Engineering for Production
Objective: Student writes prompts that survive production. Not "10 prompts to 10x your life" Twitter trash — actual reliability patterns.

Interview questions: "How do you reduce hallucinations?", "What is chain-of-thought?", "How do you evaluate a prompt?", "What is few-shot vs zero-shot?"

Episode 2.1 — The Anatomy of a Production Prompt
Runtime: 15 min
Cover: System prompt structure, role assignment, constraints, output format specification, why prompts break in production, XML tags vs markdown
Assignment: Rewrite 3 broken ChatGPT prompts into production-grade versions
Episode 2.2 — Few-Shot, Chain-of-Thought, and ReAct
Runtime: 15 min
Cover: When each pattern helps, when it hurts, how to pick examples, self-consistency
Interview relevance: Direct interview question at product companies
Episode 2.3 — Prompt Chaining & Meta-Prompting
Runtime: 12 min
Cover: Breaking complex tasks into chained calls, using LLMs to generate prompts, prompt caching (Anthropic + OpenAI)
Episode 2.4 — Failure Modes & Defensive Prompting
Runtime: 15 min
Cover: Prompt injection basics, jailbreak resistance, output validation, retry-on-invalid patterns
Deliverable this week: Production extraction pipeline that pulls structured data from messy PDFs/emails with 90%+ reliability. GitHub.
Resume line unlocked: "Designed prompt engineering pipeline with structured output validation reducing hallucination rate from 18% to under 3% on internal test set."