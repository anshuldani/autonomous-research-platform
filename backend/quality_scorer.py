"""
Quality Scoring System
======================

Evaluates research quality on a 0-10 scale.

Criteria:
- Depth: How thorough is the coverage?
- Relevance: How well does it answer the questions?
- Clarity: How well-written is the summary?
- Sources: Are sources authoritative and diverse?
"""

from typing import Dict, List
from anthropic import Anthropic
import os
import re
from dotenv import load_dotenv
import json

load_dotenv()

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


def _extract_json(text: str) -> dict:
    """
    Robustly extract a JSON object from a Claude response.

    Handles:
    - Markdown code fences (```json ... ```)
    - Extra prose before/after the JSON block
    - Literal newlines embedded inside string values (invalid JSON)
    """
    # Strip code fences
    if "```json" in text:
        text = text.split("```json")[1].split("```")[0]
    elif "```" in text:
        text = text.split("```")[1].split("```")[0]

    # Find the outermost { ... } via brace counting
    start = text.find("{")
    if start == -1:
        raise ValueError("No JSON object found in response")

    depth = 0
    end = start
    for i, ch in enumerate(text[start:], start):
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                end = i
                break

    raw = text[start : end + 1]

    # First attempt: parse as-is
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        pass

    # Second attempt: replace unescaped newlines inside string values
    # This collapses multi-line strings into single-line strings.
    sanitized = re.sub(r'(?<!\\)\n', ' ', raw)
    sanitized = re.sub(r'\s{2,}', ' ', sanitized)
    try:
        return json.loads(sanitized)
    except json.JSONDecodeError:
        pass

    # Fallback: return neutral scores so the pipeline keeps running
    print("⚠️  JSON parse failed — using fallback scores")
    return {
        "overall_score": 5.0,
        "depth_score": 5.0,
        "relevance_score": 5.0,
        "clarity_score": 5.0,
        "coverage_score": 5.0,
        "weaknesses": ["Could not parse quality assessment"],
        "suggestions": ["Re-run scoring"],
    }


def score_research_quality(
    topic: str,
    questions: List[str],
    summary: str,
    sources_count: int
) -> Dict:
    """
    Score research quality using Claude as a critic.
    
    Returns scores for:
    - Overall (0-10)
    - Depth (0-10)
    - Relevance (0-10)
    - Clarity (0-10)
    - Coverage (0-10)
    
    Plus: Specific feedback on weaknesses
    """
    
    print(f"📊 Scoring research quality...")
    
    # Create scoring prompt
    # Truncate summary to keep prompt within safe token limits
    summary_trunc = summary[:3000] + ("…" if len(summary) > 3000 else "")

    prompt = f"""You are a research quality evaluator. Score this research on a 0-10 scale.

TOPIC: {topic}

RESEARCH QUESTIONS:
{chr(10).join(f"{i+1}. {q}" for i, q in enumerate(questions))}

SUMMARY:
{summary_trunc}

METADATA:
- Sources used: {sources_count}
- Summary length: {len(summary.split())} words

Evaluate on these criteria (0-10 each):
1. DEPTH: How thorough is the coverage?
2. RELEVANCE: How well does it answer the questions?
3. CLARITY: How well-written and clear is it?
4. COVERAGE: Are all questions adequately addressed?

Provide:
1. Scores for each criterion
2. Overall score (average)
3. Specific weaknesses (what's missing or unclear)
4. Suggestions for improvement

Return ONLY a JSON object:
{{
  "overall_score": 7.5,
  "depth_score": 8.0,
  "relevance_score": 7.0,
  "clarity_score": 8.0,
  "coverage_score": 7.0,
  "weaknesses": ["Missing X", "Unclear about Y"],
  "suggestions": ["Research more about X", "Clarify Y with specific examples"]
}}"""
    
    # Call Claude
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        messages=[{
            "role": "user",
            "content": prompt
        }]
    )
    
    scores = _extract_json(message.content[0].text)
    
    # Display results
    print(f"\n{'='*60}")
    print("QUALITY ASSESSMENT")
    print('='*60)
    print(f"Overall Score: {scores['overall_score']}/10")
    print(f"\nDetailed Scores:")
    print(f"  Depth:     {scores['depth_score']}/10")
    print(f"  Relevance: {scores['relevance_score']}/10")
    print(f"  Clarity:   {scores['clarity_score']}/10")
    print(f"  Coverage:  {scores['coverage_score']}/10")
    
    if scores.get('weaknesses'):
        print(f"\nWeaknesses:")
        for w in scores['weaknesses']:
            print(f"  ❌ {w}")
    
    if scores.get('suggestions'):
        print(f"\nSuggestions for Improvement:")
        for s in scores['suggestions']:
            print(f"  💡 {s}")
    
    print('='*60 + '\n')
    
    return scores


if __name__ == "__main__":
    print("\n" + "="*60)
    print("TESTING QUALITY SCORER")
    print("="*60 + "\n")
    
    # Mock research data
    test_topic = "Quantum computing applications"
    test_questions = [
        "What are practical applications of quantum computing?",
        "How does quantum computing compare to classical computing?"
    ]
    test_summary = """Quantum computing shows promise in cryptography 
    and drug discovery. It uses quantum bits which can be in superposition."""
    
    # Score it
    scores = score_research_quality(
        topic=test_topic,
        questions=test_questions,
        summary=test_summary,
        sources_count=5
    )
    
    print(f"✅ Scoring complete!")
    print(f"Overall: {scores['overall_score']}/10")
