# Paper Evidence Pack — OctoTools

## Metadata
- **Title:** OctoTools: A Multi-Agent Framework with Extensible Tools for Complex Reasoning
- **Authors:** Pan Lu*, Bowen Chen*, Sheng Liu*, Rahul Thapa, Joseph Boen, James Zou (Stanford University)
- **Venue/ID:** arXiv:2502.11271v2 [cs.LG], v2 dated 13 Apr 2026
- **Website:** https://octotools.github.io

## Problem & why it matters
Complex reasoning tasks mix visual understanding, domain knowledge retrieval, numerical
calculation, and multi-step reasoning. Plain LLM prompting fails to orchestrate these varied
processes into a coherent chain. Existing tool-augmented methods either require training on
curated data, are locked to one specialized domain, support only limited tool types, or cannot
do multi-step problem solving — hindering general use.

## Method summary
OctoTools is a **training-free, extensible multi-agent framework** with three parts (Figure 2):
1. **Tool cards** — standardized wrappers encapsulating each tool's metadata (name, I/O types,
   demo commands, usage constraints like "limitations" and "best practices"). New tools plug in
   with lightweight natural-language metadata — no framework change, no retraining.
2. **Planner agent** — does high-level planning (a tentative global plan from the query) and
   low-level planning (an action per step: sub-goal + selected tool + context). A **context
   verifier** checks after every step whether the problem is solved; a **solution summarizer**
   compiles the final answer from the full trajectory.
3. **Executor agent** — a **command generator** turns the planner's text action into an
   executable Python command, and a **command executor** runs it, appending
   (action, command, result) to the trajectory. Separating planning from command generation
   avoids overloading one model.
Plus a **task-specific toolset optimization** algorithm: greedy search (O(n) instead of O(2^n))
that picks a beneficial tool subset per task from a small validation set.

## Experiment setup
- 16 benchmarks spanning 2 modalities (text/vision), 5 domains (general, mathematical,
  scientific, medical, agentic), 4 reasoning types (visual understanding, numerical calculation,
  knowledge retrieval, multi-step reasoning). Includes MathVista, MMLU-Pro, MedQA, GPQA,
  GAIA-Text, Game of 24, PathCLS.
- Base model gpt-4o-2024-08-06. Baselines: zero-shot, CoT, OctoTools_base (base tool only).
- Framework comparison: AutoGen, GPT-Functions, LangChain with the **same GPT-4o backbone, same
  toolset, same 10-step / 300s budget** — differences attributable to agent architecture.

## Key results
- **58.5% average accuracy** across 16 tasks: **+9.3%** over zero-shot GPT-4o, **+7.7%** over CoT (Table 1, Figure 1).
- Beats agent frameworks with identical tools: **+10.6% vs AutoGen, +7.5% vs GPT-Functions, +7.3% vs LangChain** (Table 2).
- Largest gains on tool-hungry tasks: Game of 24 +22.5, PathCLS +22.2, PathVQA +17.2, CLEVR-Math +14.5, GAIA-Text +9.7 (vs zero-shot).
- Toolset strategies: base tool 53.9% → full toolset 57.4% → optimized toolset 58.9% (Figure 7).
- Accuracy increases with step budget (Figure 6); avg executed steps only 2.56 (GPT-4o) — verifier stops early on easy queries. Cost ≈ $0.05/query GPT-4o, <$0.01 GPT-4o-mini (Table 5).
- Generalizes across backbones: +5.8–8.4% on Claude 3.5 Haiku, Gemini 2.5 Pro, Grok-2 Vision, Qwen2.5-VL-72B (Figure 9); +7.1% avg with GPT-4o-mini; +13.6%/+6.3% on compact Qwen2.5-3B/7B (Table 3).
- Robust to noise: with tool-failure probability up to p=0.4, average drop ≤1.6% on 10 tasks (Table 4).
- Failure analysis (200 cases, Table 6): weak tools 65.0%, imperfect low-level plan 45.0%, imperfect high-level plan 32.5%; core framework errors (invalid command generation) only 1.5%.
- Human-facing demo: 22.9K visits, 3.6K queries, 69% of sampled feedback positive, praising step-by-step transparency.

## Limitations
- Performance tied to base LLM's reasoning/coding quality (hallucinated tool metadata hurts).
- Errors dominated by tool limitations and imperfect planning, not the framework — improving
  tool quality and planner reasoning is future work.

## Figures used as evidence
- **Main figure:** Figure 2, page 2 — "The framework of OctoTools": tool cards → planner
  (query analyzer, action predictor, context verifier, solution summarizer) → executor (command
  generator, command executor), with task-specific toolset optimization.
  Crop: `input/assets/main_figure.png` (graphic-region v3; header-zone flag visually reviewed
  and accepted — diagram only, no title/author text).
- **Result figure:** Figure 1, page 1 — bar chart, average accuracy on 16 tasks: GPT-4o 49.2,
  GPT-4o (CoT) 50.8, AutoGen 47.9, GPT-Functions 51.0, LangChain 51.2, **OctoTools 58.5**.
  Crop: `input/assets/result_figure.png` (axes and tick labels included).

## Key factual claims (with evidence)
1. OctoTools is training-free — no model weight updates required. (Abstract; §2.1)
2. Tool cards encapsulate tool metadata so new tools are added "without modifying the underlying framework or agent logic". (§2.2)
3. The planner does both high-level planning (global tentative plan) and low-level planning (per-step action = sub-goal + tool + context). (§2.3)
4. A dedicated command generator converts text actions to executable Python, because one model doing both planning and coding "can overload the model and lead to errors". (§2.4)
5. The context verifier decides CONTINUE vs STOP after each step; a solution summarizer compiles the final answer from the trajectory. (§2.3, Figure 3)
6. Toolset optimization uses greedy search, reducing O(2^n) subset search to O(n). (§2.5)
7. OctoTools reaches 58.5% average accuracy on 16 benchmarks: +9.3% over zero-shot GPT-4o, +7.7% over CoT. (Table 1)
8. With the same tools, model, and budgets, OctoTools beats AutoGen by 10.6%, GPT-Functions by 7.5%, LangChain by 7.3%. (Table 2, §3.3)
9. Optimized toolset 58.9% vs full toolset 57.4% vs base tool 53.9%. (Figure 7)
10. Despite a 10-step budget, average executed steps are 2.56 (GPT-4o) — early stopping by the verifier; ~$0.05 per query. (Table 5)
11. Under injected tool failures up to p=0.4, average accuracy drops at most 1.6% (Qwen2.5-7B, 10 tasks). (Table 4)
12. In 200 failure cases, 65% trace to weak tools and only 1.5% to invalid command generation — the framework core is robust. (Table 6)
