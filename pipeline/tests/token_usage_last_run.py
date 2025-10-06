#!/usr/bin/env python3
"""
Token usage estimator for the most recent pipeline run.

Purpose:
- Estimate total LLM input and output tokens across all LLM-using steps
  for the last run directory: pipeline/data/<run_id>/

Notes:
- This uses a heuristic of ~4 characters per token (common approximation)
- It inspects actual artifacts written by each step to estimate I/O size
- Steps covered: llm_quality_scoring, article_prioritization, summarization,
  github_trending_processing (ranking + repo description), newsletter_generation (minimal)

Outputs:
- Human-readable summary
- JSON breakdown (printed at the end)
"""

from __future__ import annotations

import json
import math
import os
from pathlib import Path
from typing import Any, Dict, List, Tuple


def approx_tokens_from_text(text: str) -> int:
    if not text:
        return 0
    # Heuristic: ~4 characters ≈ 1 token
    return math.ceil(len(text) / 4)


def read_json(path: Path) -> Any:
    try:
        with path.open('r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return None


def find_last_run_dir(base: Path) -> Path | None:
    if not base.exists():
        return None
    run_dirs = [p for p in base.iterdir() if p.is_dir()]
    if not run_dirs:
        return None
    # Choose most recent by mtime
    return max(run_dirs, key=lambda p: p.stat().st_mtime)


def estimate_llm_quality_scoring(processed_dir: Path) -> Dict[str, Any]:
    """Estimate tokens for LLM quality scoring step.
    Inputs: prompt includes title + truncated content; Outputs: llm_analysis JSON.
    We approximate inputs from available article fields; outputs from llm_analysis size.
    """
    path = processed_dir / 'quality_scored_content.json'
    data = read_json(path)
    if not data:
        return {'step': 'llm_quality_scoring', 'input_tokens': 0, 'output_tokens': 0, 'items': 0, 'assumptions': 'file_missing'}

    articles = data.get('articles', [])  # passed articles only
    quality_results = data.get('quality_results', [])
    stats = data.get('statistics', {})
    total_processed = stats.get('articles_input', len(articles))

    # Input estimate: for processed items, use title + (content if present)
    input_tokens = 0
    # Use all available articles (passed). For missed ones, extrapolate using average
    sample_inputs = 0
    for art in articles:
        title = str(art.get('title', ''))
        content = str(art.get('content', ''))
        sample_inputs += 1
        input_tokens += approx_tokens_from_text(title + ' ' + content)

    avg_input = (input_tokens / sample_inputs) if sample_inputs else 0
    if total_processed > sample_inputs:
        # Extrapolate for filtered articles not present in 'articles'
        input_tokens = math.ceil(avg_input * total_processed)

    # Output estimate: sum llm_analysis JSON size for quality_results
    output_tokens = 0
    for qr in quality_results:
        analysis = qr.get('llm_analysis', {})
        try:
            analysis_str = json.dumps(analysis, ensure_ascii=False)
        except Exception:
            analysis_str = str(analysis)
        output_tokens += approx_tokens_from_text(analysis_str)

    return {
        'step': 'llm_quality_scoring',
        'input_tokens': int(input_tokens),
        'output_tokens': int(output_tokens),
        'items': int(total_processed),
        'assumptions': '4-chars/token; extrapolated inputs for filtered items'
    }


def estimate_article_prioritization(processed_dir: Path) -> Dict[str, Any]:
    """Estimate tokens for article prioritization step.
    Inputs: prompt includes per-article previews and metadata; Outputs: categorization + optional reasoning.
    We approximate inputs using a fixed-per-article preview estimate when content is not directly available.
    """
    path = processed_dir / 'prioritized_content.json'
    data = read_json(path)
    if not data:
        return {'step': 'article_prioritization', 'input_tokens': 0, 'output_tokens': 0, 'items': 0, 'assumptions': 'file_missing'}

    meta = data.get('metadata', {})
    articles_processed = meta.get('articles_processed', 0)

    # Input estimate: per the pipeline, a preview (title + snippet) per article was sent to the LLM.
    # Assume ~120 tokens/article of input (title + preview + coverage metadata), conservative.
    input_tokens = int(articles_processed * 120)

    # Output estimate: reasoning text if present + small categorization JSON
    reasoning = data.get('llm_reasoning', {})
    try:
        reasoning_str = json.dumps(reasoning, ensure_ascii=False)
    except Exception:
        reasoning_str = str(reasoning)
    output_tokens = approx_tokens_from_text(reasoning_str) + int(articles_processed * 5)  # small overhead

    return {
        'step': 'article_prioritization',
        'input_tokens': input_tokens,
        'output_tokens': int(output_tokens),
        'items': int(articles_processed),
        'assumptions': '120 input tokens/article; categorization overhead ~5/article'
    }


def estimate_summarization(processed_dir: Path) -> Dict[str, Any]:
    """Estimate tokens for summarization step.
    Inputs: title + content/summary per article; Outputs: generated title/summary per article.
    """
    path = processed_dir / 'summarized_content.json'
    data = read_json(path)
    if not data:
        return {'step': 'summarization', 'input_tokens': 0, 'output_tokens': 0, 'items': 0, 'assumptions': 'file_missing'}

    summaries = data.get('summaries', {})
    all_items: List[Dict[str, Any]] = []
    for k in ('headlines', 'secondary', 'optional'):
        all_items.extend(summaries.get(k, []))

    stats = data.get('statistics', {})
    total = stats.get('total_articles', len(all_items))

    input_tokens = 0
    output_tokens = 0
    for item in all_items:
        # Input estimate: best effort using available fields
        title = str(item.get('original_title', ''))
        # We may not have the exact content used; if present, use original_summary
        original_summary = str(item.get('original_summary', ''))
        input_tokens += approx_tokens_from_text(title + ' ' + original_summary)

        # Output estimate: generated title + summary
        gen_title = str(item.get('title', ''))
        gen_summary = str(item.get('summary', ''))
        output_tokens += approx_tokens_from_text(gen_title + ' ' + gen_summary)

    return {
        'step': 'summarization',
        'input_tokens': int(input_tokens),
        'output_tokens': int(output_tokens),
        'items': int(total),
        'assumptions': 'Inputs use original_title+original_summary when available'
    }


def estimate_github_trending(raw_dir: Path, processed_dir: Path) -> Dict[str, Any]:
    """Estimate tokens for GitHub trending processing.
    - Ranking prompt may use top 10 repos. Use metadata.ranking_source to detect LLM usage.
    - Description generation for top repos: use repo description + optional readme_preview as inputs; summary text as outputs.
    """
    raw_file = raw_dir / 'github_trending.json'
    proc_file = processed_dir / 'github_trending.json'
    raw = read_json(raw_file)
    proc = read_json(proc_file)
    if not proc:
        return {'step': 'github_trending_processing', 'input_tokens': 0, 'output_tokens': 0, 'items': 0, 'assumptions': 'file_missing'}

    input_tokens = 0
    output_tokens = 0
    items = 0
    assumptions: List[str] = []

    # Ranking
    meta = proc.get('metadata', {})
    ranking_source = meta.get('ranking_source', 'API')
    if ranking_source == 'LLM' and raw:
        # Build prompt from top 10 repos fields (name, language, stars, description, readme_preview if present)
        rows = raw.get('repositories', [])[:10]
        prompt_parts = []
        for r in rows:
            prompt_parts.append(
                f"{r.get('repo_name','')} ({r.get('primary_language','')}) - {r.get('stars','')} stars\n"
                f"Description: {r.get('description','')}\n"
                f"README: {str(r.get('readme_preview',''))[:500]}\n"
            )
        prompt_text = "\n".join(prompt_parts)
        input_tokens += approx_tokens_from_text(prompt_text)
        # Output estimate: rankings JSON short; add small overhead
        output_tokens += 500  # conservative fixed estimate
        assumptions.append('LLM ranking used; prompt from top 10 repos; fixed 500 output tokens')
    else:
        assumptions.append('Ranking by API; no LLM cost')

    # Description generation (per repo summary)
    repos = proc.get('repositories', [])
    for repo in repos:
        if repo.get('status') == 'success':
            # Input: name + original_description
            raw_desc = f"{repo.get('repo_name','')} {repo.get('original_description','')}"
            input_tokens += approx_tokens_from_text(raw_desc)
            # Output: summary text
            output_tokens += approx_tokens_from_text(str(repo.get('summary', '')))
            items += 1

    return {
        'step': 'github_trending_processing',
        'input_tokens': int(input_tokens),
        'output_tokens': int(output_tokens),
        'items': int(items),
        'assumptions': '; '.join(assumptions) if assumptions else 'none'
    }


def estimate_newsletter_generation(processed_dir: Path) -> Dict[str, Any]:
    """Newsletter generation is largely deterministic JSON assembly; assume no LLM cost here."""
    return {
        'step': 'newsletter_generation',
        'input_tokens': 0,
        'output_tokens': 0,
        'items': 1,
        'assumptions': 'no LLM usage in this step'
    }


def main() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    data_root = repo_root / 'pipeline' / 'data'
    last_run = find_last_run_dir(data_root)
    if not last_run:
        print('No run directories found under pipeline/data/.')
        return

    raw_dir = last_run / 'raw'
    processed_dir = last_run / 'processed'
    output_dir = last_run / 'output'

    breakdown: List[Dict[str, Any]] = []

    # Steps
    breakdown.append(estimate_llm_quality_scoring(processed_dir))
    breakdown.append(estimate_article_prioritization(processed_dir))
    breakdown.append(estimate_summarization(processed_dir))
    breakdown.append(estimate_github_trending(raw_dir, processed_dir))
    breakdown.append(estimate_newsletter_generation(processed_dir))

    total_input = sum(it.get('input_tokens', 0) for it in breakdown)
    total_output = sum(it.get('output_tokens', 0) for it in breakdown)

    # Human-readable summary
    print(f"Analyzed last run: {last_run}")
    print("\nPer-step estimated token usage (input/output):")
    for it in breakdown:
        print(f"- {it['step']}: {it['input_tokens']:,} input / {it['output_tokens']:,} output tokens"
              f" | items={it.get('items', 0)}")

    print("\nTotals:")
    print(f"- Total input tokens:  {total_input:,}")
    print(f"- Total output tokens: {total_output:,}")
    print(f"- Estimated total tokens: {total_input + total_output:,}")

    print("\nAssumptions per step:")
    for it in breakdown:
        print(f"- {it['step']}: {it.get('assumptions', 'none')}")

    result = {
        'run_dir': str(last_run),
        'totals': {
            'input_tokens': int(total_input),
            'output_tokens': int(total_output),
            'total_tokens': int(total_input + total_output)
        },
        'steps': breakdown
    }

    print("\nJSON summary:")
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()



