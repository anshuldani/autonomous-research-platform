"""
Iterative Self-Improving Research Agent
"""

from typing import TypedDict, List, Dict
from anthropic import Anthropic
import os
from dotenv import load_dotenv
import uuid
import time
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.research import ResearchTools
from retrieval.vector_store import VectorStore
from agents.quality import score_research_quality
from agents.critique import critique_research

load_dotenv()

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
tools = ResearchTools()
vector_store = VectorStore()


class IterativeResearchState(TypedDict):
    topic: str
    research_id: str
    research_questions: List[str]
    search_results: Dict[str, List[Dict]]
    stored_chunks: int
    retrieval_method: str
    rag_context: str
    rerank_scores: List[float]
    quality_metrics: Dict
    summary: str
    previous_summary: str
    current_step: str
    iteration: int
    max_iterations: int
    quality_threshold: float
    quality_history: List[Dict]
    improvement_history: List[str]
    current_critique: Dict
    needs_more_research: bool


def research_with_delay(state, questions):
    """Research and store with indexing delay."""
    all_texts = []
    all_metadata = []
    
    for question in questions:
        results = tools.search_web(query=question, max_results=2)
        for result in results:
            all_texts.append(result['content'])
            all_metadata.append({
                'title': result['title'],
                'url': result['url'],
                'question': question,
                'iteration': state['iteration']
            })
    
    if all_texts:
        print(f"💾 Storing {len(all_texts)} sources...")
        vector_store.store_documents(
            texts=all_texts,
            metadata=all_metadata,
            research_id=state['research_id'],
            auto_chunk=True
        )
        state['stored_chunks'] += len(all_texts)
        print("⏳ Indexing delay (3s)...")
        time.sleep(3)
    
    return state


def smart_synthesis(state, is_improvement=False):
    """Smart synthesis that builds on previous work."""
    if is_improvement:
        new_questions = state['current_critique']['followup_questions']
    else:
        new_questions = state['research_questions']
    
    context_parts = []
    for question in new_questions:
        results = vector_store.hybrid_search(
            query=question,
            research_id=state['research_id'],
            top_k=2,
            alpha=0.7
        )
        if results:
            context_parts.append(f"\nQuestion: {question}\n")
            for r in results:
                context_parts.append(f"Source: {r['metadata'].get('title', 'N/A')}")
                context_parts.append(f"{r['text']}\n")
    
    new_context = "\n".join(context_parts) if context_parts else "No context."
    
    if not is_improvement:
        prompt = f"""Write a comprehensive research report on: {state['topic']}

Research findings:
{new_context}

Create a well-structured report (500+ words) with detailed findings and quantitative data."""
    else:
        weaknesses = state['current_critique']['quality_scores'].get('weaknesses', [])
        weakness_text = "\n".join(f"{i+1}. {w}" for i, w in enumerate(weaknesses[:3]))
        
        prompt = f"""ENHANCE this research report.

ORIGINAL REPORT:
{state['previous_summary']}

WEAKNESSES TO FIX:
{weakness_text}

NEW RESEARCH:
{new_context}

Write an IMPROVED version that keeps good parts and adds missing details (600+ words)."""
    
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=3500,
        temperature=0.3,
        messages=[{"role": "user", "content": prompt}]
    )
    
    state['summary'] = message.content[0].text
    return state


def planning_agent(state):
    """Generate research questions."""
    prompt = f"""Generate 3 focused research questions about: {state['topic']}

Return as JSON array: ["question 1?", "question 2?", "question 3?"]"""
    
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}]
    )
    
    import json
    text = message.content[0].text
    if "```" in text:
        text = text.split("```")[1].replace("json", "").strip()
    questions = json.loads(text)
    state['research_questions'] = questions
    return state


def run_initial_research(state):
    """Initial research iteration."""
    print(f"\n{'='*70}\nITERATION 1: INITIAL RESEARCH\n{'='*70}\n")
    state = planning_agent(state)
    state = research_with_delay(state, state['research_questions'])
    state = smart_synthesis(state, is_improvement=False)
    return state


def critique_and_decide(state):
    """Critique and decide if improvement needed."""
    critique = critique_research(
        topic=state['topic'],
        questions=state['research_questions'],
        summary=state['summary'],
        sources_count=state['stored_chunks'],
        quality_threshold=state['quality_threshold']
    )
    
    state['current_critique'] = critique
    state['needs_more_research'] = critique['needs_improvement']
    
    quality_record = {
        'iteration': state['iteration'],
        'scores': critique['quality_scores'],
        'overall': critique['quality_scores']['overall_score']
    }
    state['quality_history'].append(quality_record)
    
    if critique['needs_improvement'] and state['iteration'] < state['max_iterations']:
        state['research_questions'].extend(critique['followup_questions'])
    else:
        state['needs_more_research'] = False
    
    return state


def run_improvement_iteration(state):
    """Improvement iteration."""
    state['previous_summary'] = state['summary']
    state['iteration'] += 1
    
    print(f"\n{'='*70}\nITERATION {state['iteration']}: IMPROVEMENT\n{'='*70}\n")
    
    new_questions = state['current_critique']['followup_questions']
    state = research_with_delay(state, new_questions)
    state = smart_synthesis(state, is_improvement=True)
    return state


def run_iterative_research(topic: str, quality_threshold: float = 7.5, max_iterations: int = 3):
    """Main iterative research function."""
    print(f"\n🚀 ITERATIVE RESEARCH\nTopic: {topic}\n")
    
    state: IterativeResearchState = {
        'topic': topic,
        'research_id': f"iter_{uuid.uuid4().hex[:8]}",
        'research_questions': [],
        'search_results': {},
        'stored_chunks': 0,
        'retrieval_method': 'hybrid',
        'rag_context': '',
        'rerank_scores': [],
        'quality_metrics': {},
        'summary': '',
        'previous_summary': '',
        'current_step': 'init',
        'iteration': 1,
        'max_iterations': max_iterations,
        'quality_threshold': quality_threshold,
        'quality_history': [],
        'improvement_history': [],
        'current_critique': {},
        'needs_more_research': True
    }
    
    state = run_initial_research(state)
    state = critique_and_decide(state)
    
    while state['needs_more_research'] and state['iteration'] < max_iterations:
        state = run_improvement_iteration(state)
        state = critique_and_decide(state)
    
    print(f"\n✅ COMPLETE - Score: {state['quality_history'][-1]['overall']:.1f}/10\n")
    return state


if __name__ == "__main__":
    result = run_iterative_research("CRISPR in medicine", quality_threshold=7.5, max_iterations=3)
    print(result['summary'][:400])
