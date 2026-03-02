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
from dotenv import load_dotenv
import json

load_dotenv()

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


# Scoring function will be added next


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
    prompt = f"""You are a research quality evaluator. Score this research on a 0-10 scale.

TOPIC: {topic}

RESEARCH QUESTIONS:
{chr(10).join(f"{i+1}. {q}" for i, q in enumerate(questions))}

SUMMARY:
{summary}

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
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        messages=[{
            "role": "user",
            "content": prompt
        }]
    )
    
    # Parse response
    response_text = message.content[0].text
    
    # Handle markdown code blocks
    if "```json" in response_text:
        response_text = response_text.split("```json")[1].split("```")[0]
    elif "```" in response_text:
        response_text = response_text.split("```")[1].split("```")[0]
    
    scores = json.loads(response_text.strip())
    
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
    """Test the quality scorer"""
    
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
