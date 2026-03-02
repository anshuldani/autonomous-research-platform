"""
Iterative Research Agent
========================

Strategy: Incremental improvement via self-critique loop.
"""

from typing import TypedDict, List, Dict
from anthropic import Anthropic
import os
from dotenv import load_dotenv
import uuid
import time

from research_tools import ResearchTools
from vector_store import VectorStore
from quality_scorer import score_research_quality
from critique_agent import critique_research
from day3_advanced_rag_agent import planning_agent, AdvancedResearchState

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
        print(f"🔍 Retrieving context for {len(new_questions)} NEW questions...")
    else:
        new_questions = state['research_questions']
        print(f"📚 Retrieving context for {len(new_questions)} questions...")

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

    new_context = "\n".join(context_parts) if context_parts else "No new context."

    if not is_improvement:
        prompt = f"""Write a comprehensive research report on: {state['topic']}

Research findings:
{new_context}

Create a well-structured report (500+ words) with:
- Clear introduction
- Detailed key findings with SPECIFIC data (numbers, trial names, percentages)
- Analysis of patterns
- Conclusion

Be thorough and include quantitative details. NO bullet points."""

    else:
        weaknesses = state['current_critique']['quality_scores'].get('weaknesses', [])
        suggestions = state['current_critique']['quality_scores'].get('suggestions', [])

        weakness_text = "\n".join(f"{i+1}. {w}" for i, w in enumerate(weaknesses[:3]))
        suggestion_text = "\n".join(f"{i+1}. {s}" for i, s in enumerate(suggestions[:3]))

        prompt = f"""ENHANCE this research report by addressing specific weaknesses.

ORIGINAL REPORT (Iteration {state['iteration']-1}):
{state['previous_summary']}

IDENTIFIED WEAKNESSES:
{weakness_text}

SUGGESTIONS:
{suggestion_text}

NEW RESEARCH to address gaps:
{new_context}

TASK: Write an IMPROVED version that:
1. KEEPS all the good parts from the original
2. ADDS the missing details identified in weaknesses
3. INCORPORATES the new research findings
4. FOLLOWS the suggestions (add specific numbers, trial names, comparisons)

The improved report should be MORE DETAILED (600+ words) and address EVERY weakness.
NO bullet points."""

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=3500,
        temperature=0.3,
        messages=[{"role": "user", "content": prompt}]
    )

    state['summary'] = message.content[0].text

    return state


def run_initial_research(state):
    """Initial research."""

    print(f"\n{'='*70}")
    print(f"ITERATION 1: INITIAL RESEARCH")
    print('='*70 + '\n')

    state = planning_agent(state)
    state = research_with_delay(state, state['research_questions'])
    state = smart_synthesis(state, is_improvement=False)

    return state


def critique_and_decide(state):
    """Critique current work."""

    print(f"\n{'='*70}")
    print(f"CRITIQUE: Iteration {state['iteration']}")
    print('='*70 + '\n')

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

    if critique['needs_improvement']:
        if state['iteration'] < state['max_iterations']:
            print(f"🔄 Score: {critique['quality_scores']['overall_score']:.1f}/10")
            print(f"   Target: {state['quality_threshold']}/10")
            print(f"   → Proceeding to iteration {state['iteration'] + 1}\n")

            state['research_questions'].extend(critique['followup_questions'])

            improvement = ', '.join(critique['improvement_areas'][:2])
            state['improvement_history'].append(f"Iteration {state['iteration']+1}: {improvement}")
        else:
            print(f"⚠️  Max iterations reached\n")
            state['needs_more_research'] = False
    else:
        print(f"✅ Threshold met: {critique['quality_scores']['overall_score']:.1f}/10\n")

    return state


def run_improvement_iteration(state):
    """Run improvement iteration."""

    state['previous_summary'] = state['summary']
    state['iteration'] += 1

    print(f"\n{'='*70}")
    print(f"ITERATION {state['iteration']}: TARGETED IMPROVEMENT")
    print('='*70 + '\n')

    new_questions = state['current_critique']['followup_questions']

    print("🎯 Addressing gaps:")
    for i, q in enumerate(new_questions, 1):
        print(f"  {i}. {q[:70]}...")
    print()

    state = research_with_delay(state, new_questions)
    state = smart_synthesis(state, is_improvement=True)

    return state


def run_iterative_research(
    topic: str,
    quality_threshold: float = 7.5,
    max_iterations: int = 3
):
    """Main loop."""

    print(f"\n{'='*70}")
    print("🚀 ITERATIVE RESEARCH (SMART INCREMENTAL)")
    print('='*70)
    print(f"Topic: {topic}")
    print(f"Threshold: {quality_threshold}/10")
    print(f"Max Iterations: {max_iterations}")
    print('='*70 + '\n')

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

    print(f"\n{'='*70}")
    print("🏁 COMPLETE")
    print('='*70)
    print(f"\nTotal Iterations: {state['iteration']}")
    print(f"Final Score: {state['quality_history'][-1]['overall']:.1f}/10")
    print(f"Status: {'✅ Met' if not state['needs_more_research'] else '⚠️ Max'}\n")

    print("📊 Quality Progression:")
    for i, record in enumerate(state['quality_history']):
        delta = ""
        if i > 0:
            change = record['overall'] - state['quality_history'][i-1]['overall']
            delta = f" ({change:+.1f})"

        status = "✅" if record['overall'] >= quality_threshold else "🔄"
        print(f"  {status} Iteration {record['iteration']}: {record['overall']:.1f}/10{delta}")

    total_improvement = state['quality_history'][-1]['overall'] - state['quality_history'][0]['overall']
    print(f"\nTotal Improvement: {total_improvement:+.1f} points")
    print('='*70 + '\n')

    return state


if __name__ == "__main__":
    result = run_iterative_research(
        topic="CRISPR applications in medicine",
        quality_threshold=7.5,
        max_iterations=3
    )

    print("\n" + "="*70)
    print("FINAL SUMMARY (first 400 chars):")
    print("="*70)
    print(result['summary'][:400] + "...\n")
