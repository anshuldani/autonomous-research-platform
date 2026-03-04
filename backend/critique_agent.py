"""
Critique Agent
==============

Agent that critiques research and suggests improvements.

This agent:
1. Evaluates research quality
2. Identifies specific weaknesses
3. Generates targeted follow-up questions
4. Enables iterative improvement
"""

from typing import Dict, List, TypedDict
from anthropic import Anthropic
import os
import re
from dotenv import load_dotenv
import json
from quality_scorer import score_research_quality, _extract_json

load_dotenv()

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


class CritiqueResult(TypedDict):
    """Result from critique agent"""
    quality_scores: Dict
    needs_improvement: bool
    followup_questions: List[str]
    improvement_areas: List[str]


# Critique function will be added next


def critique_research(
    topic: str,
    questions: List[str],
    summary: str,
    sources_count: int,
    quality_threshold: float = 8.0
) -> CritiqueResult:
    """
    Critique research and suggest improvements.
    
    Args:
        topic: Research topic
        questions: Original questions
        summary: Generated summary
        sources_count: Number of sources used
        quality_threshold: Minimum acceptable score (default: 8.0)
    
    Returns:
        CritiqueResult with scores, improvement needs, and suggestions
    """
    
    print("\n" + "="*60)
    print("🔍 CRITIQUE AGENT")
    print("="*60 + "\n")
    
    # Step 1: Score quality
    scores = score_research_quality(topic, questions, summary, sources_count)
    
    overall_score = scores['overall_score']
    needs_improvement = overall_score < quality_threshold
    
    # Step 2: If needs improvement, generate follow-up questions
    followup_questions = []
    improvement_areas = []
    
    if needs_improvement:
        print(f"⚠️  Score {overall_score}/10 is below threshold ({quality_threshold})")
        print("   Generating improvement suggestions...\n")
        
        # Generate targeted follow-up questions
        critique_prompt = f"""Based on this research critique, generate 2-3 targeted follow-up 
research questions that would address the weaknesses.

ORIGINAL TOPIC: {topic}

WEAKNESSES:
{chr(10).join(f"- {w}" for w in scores.get('weaknesses', []))}

SUGGESTIONS:
{chr(10).join(f"- {s}" for s in scores.get('suggestions', []))}

Generate specific, searchable questions that would fill these gaps.

Return ONLY a JSON object:
{{
  "followup_questions": ["Question 1?", "Question 2?"],
  "improvement_areas": ["Area 1", "Area 2"]
}}"""
        
        message = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1024,
            messages=[{
                "role": "user",
                "content": critique_prompt
            }]
        )
        
        improvements = _extract_json(message.content[0].text)
        
        followup_questions = improvements.get('followup_questions', [])
        improvement_areas = improvements.get('improvement_areas', [])
        
        print("📝 Follow-up Questions:")
        for i, q in enumerate(followup_questions, 1):
            print(f"  {i}. {q}")
        
        print(f"\n🎯 Areas to Improve:")
        for area in improvement_areas:
            print(f"  • {area}")
        
    else:
        print(f"✅ Score {overall_score}/10 meets threshold ({quality_threshold})")
        print("   No improvement needed!")
    
    print("\n" + "="*60 + "\n")
    
    return {
        'quality_scores': scores,
        'needs_improvement': needs_improvement,
        'followup_questions': followup_questions,
        'improvement_areas': improvement_areas
    }
