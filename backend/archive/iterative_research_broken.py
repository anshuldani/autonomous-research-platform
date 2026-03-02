"""
Iterative Research Agent
========================

Self-improving research agent that uses critique to iteratively improve.

Flow:
1. Initial research (Day 3 agent)
2. Critique quality
3. If score < threshold:
   - Generate targeted follow-up questions
   - Research those specific gaps
   - Re-synthesize with new info
   - Repeat
4. Stop when quality threshold met or max iterations reached
"""

from typing import TypedDict, List, Dict
from anthropic import Anthropic
import os
from dotenv import load_dotenv
import uuid

# Import our existing components
from research_tools import ResearchTools
from vector_store import VectorStore
from quality_scorer import score_research_quality
from critique_agent import critique_research

# Import Day 3 agents
from day3_advanced_rag_agent import (
    planning_agent,
    research_agent,
    advanced_rag_synthesis_agent,
    AdvancedResearchState
)

load_dotenv()

print("Initializing Iterative Research Agent...")
client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
tools = ResearchTools()
vector_store = VectorStore()
print("✅ All systems ready for iterative improvement!\n")


# State and functions will be added next


# ============================================================================
# ENHANCED STATE FOR ITERATION
# ============================================================================

class IterativeResearchState(TypedDict):
    """
    Extended state that tracks iterations and improvements.
    """
    # Core fields (from Day 3)
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
    current_step: str
    
    # NEW: Iteration tracking
    iteration: int
    max_iterations: int
    quality_threshold: float
    
    # NEW: Quality history
    quality_history: List[Dict]  # Track scores per iteration
    improvement_history: List[str]  # Track what was improved
    
    # NEW: Critique results
    current_critique: Dict
    needs_more_research: bool


# Iterative functions will be added next


# ============================================================================
# ITERATION 1: INITIAL RESEARCH
# ============================================================================

def run_initial_research(state: IterativeResearchState) -> IterativeResearchState:
    """
    Run initial research using Day 3 advanced RAG agent.
    """
    
    print("\n" + "="*70)
    print(f"ITERATION {state['iteration']}: INITIAL RESEARCH")
    print("="*70 + "\n")
    
    # Run planning agent
    state = planning_agent(state)
    
    # Run research agent
    state = research_agent(state)
    
    # Run synthesis agent
    state = advanced_rag_synthesis_agent(state)
    
    print(f"✅ Initial research complete (Iteration {state['iteration']})")
    
    return state


# Critique and improvement functions will be added next


# ============================================================================
# CRITIQUE & DECISION
# ============================================================================

def critique_and_decide(state: IterativeResearchState) -> IterativeResearchState:
    """
    Critique current research and decide if improvement needed.
    """
    
    print("\n" + "="*70)
    print(f"CRITIQUE: Evaluating Iteration {state['iteration']}")
    print("="*70 + "\n")
    
    # Get critique
    critique = critique_research(
        topic=state['topic'],
        questions=state['research_questions'],
        summary=state['summary'],
        sources_count=state['stored_chunks'],
        quality_threshold=state['quality_threshold']
    )
    
    # Store critique results
    state['current_critique'] = critique
    state['needs_more_research'] = critique['needs_improvement']
    
    # Track quality history
    quality_record = {
        'iteration': state['iteration'],
        'scores': critique['quality_scores'],
        'overall': critique['quality_scores']['overall_score']
    }
    state['quality_history'].append(quality_record)
    
    # Decision
    if critique['needs_improvement']:
        if state['iteration'] < state['max_iterations']:
            print(f"🔄 Quality below threshold. Proceeding to iteration {state['iteration'] + 1}")
            
            # Add follow-up questions to research
            state['research_questions'].extend(critique['followup_questions'])
            
            # Track what we're improving
            improvement_note = f"Iteration {state['iteration']+1}: {', '.join(critique['improvement_areas'])}"
            state['improvement_history'].append(improvement_note)
            
        else:
            print(f"⚠️  Max iterations ({state['max_iterations']}) reached. Stopping.")
            state['needs_more_research'] = False
            state['current_step'] = 'max_iterations_reached'
    else:
        print(f"✅ Quality threshold met! Final score: {critique['quality_scores']['overall_score']}/10")
        state['current_step'] = 'quality_achieved'
    
    return state


# Improvement iteration function will be added next


# ============================================================================
# IMPROVEMENT ITERATION
# ============================================================================

def run_improvement_iteration(state: IterativeResearchState) -> IterativeResearchState:
    """
    Run targeted research to address identified weaknesses.
    """
    
    state['iteration'] += 1
    
    print("\n" + "="*70)
    print(f"ITERATION {state['iteration']}: TARGETED IMPROVEMENT")
    print("="*70 + "\n")
    
    # Get the new follow-up questions (already added to state)
    new_questions = state['current_critique']['followup_questions']
    
    print(f"🎯 Researching specific gaps:")
    for i, q in enumerate(new_questions, 1):
        print(f"  {i}. {q}")
    print()
    
    # Research ONLY the new questions (not all questions again)
    print("�� Gathering additional sources...")
    
    all_texts = []
    all_metadata = []
    
    for question in new_questions:
        # Search web
        results = tools.search_web(query=question, max_results=2)
        
        for result in results:
            all_texts.append(result['content'])
            all_metadata.append({
                'title': result['title'],
                'url': result['url'],
                'question': question,
                'score': result['score'],
                'source_type': 'improvement_research',
                'iteration': state['iteration']
            })
    
    # Store new sources in vector DB
    if all_texts:
        print(f"💾 Storing {len(all_texts)} additional sources...")
        vector_store.store_documents(
            texts=all_texts,
            metadata=all_metadata,
            research_id=state['research_id'],
            auto_chunk=True
        )
        
        state['stored_chunks'] += len(all_texts)
    
    # Re-synthesize with ALL stored knowledge (original + new)
    print(f"✨ Re-synthesizing with expanded knowledge base...")
    
    state = advanced_rag_synthesis_agent(state)
    
    print(f"✅ Improvement iteration {state['iteration']} complete")
    
    return state


# Main loop will be added next


# ============================================================================
# MAIN ITERATIVE LOOP
# ============================================================================

def run_iterative_research(
    topic: str,
    quality_threshold: float = 8.0,
    max_iterations: int = 3
) -> IterativeResearchState:
    """
    Run self-improving research workflow.
    
    The agent will:
    1. Conduct initial research
    2. Critique the quality
    3. If below threshold and iterations remain:
       - Identify gaps
       - Research those specific areas
       - Re-synthesize with new knowledge
       - Repeat
    4. Stop when quality threshold met or max iterations reached
    
    Args:
        topic: Research topic
        quality_threshold: Minimum acceptable score (0-10)
        max_iterations: Maximum improvement iterations
    
    Returns:
        Final state with complete research and quality history
    """
    
    print("\n" + "="*70)
    print("🚀 ITERATIVE SELF-IMPROVING RESEARCH AGENT")
    print("="*70)
    print(f"Topic: {topic}")
    print(f"Quality Threshold: {quality_threshold}/10")
    print(f"Max Iterations: {max_iterations}")
    print("="*70 + "\n")
    
    # Initialize state
    research_id = f"iterative_{uuid.uuid4().hex[:8]}"
    
    state: IterativeResearchState = {
        # Core fields
        'topic': topic,
        'research_id': research_id,
        'research_questions': [],
        'search_results': {},
        'stored_chunks': 0,
        'retrieval_method': '',
        'rag_context': '',
        'rerank_scores': [],
        'quality_metrics': {},
        'summary': '',
        'current_step': 'initialized',
        
        # Iteration fields
        'iteration': 1,
        'max_iterations': max_iterations,
        'quality_threshold': quality_threshold,
        'quality_history': [],
        'improvement_history': [],
        'current_critique': {},
        'needs_more_research': True
    }
    
    # ITERATION 1: Initial research
    state = run_initial_research(state)
    
    # Critique iteration 1
    state = critique_and_decide(state)
    
    # ITERATIONS 2+: Improvement loop
    while state['needs_more_research'] and state['iteration'] < max_iterations:
        state = run_improvement_iteration(state)
        state = critique_and_decide(state)
    
    # Final summary
    print("\n" + "="*70)
    print("🏁 ITERATIVE RESEARCH COMPLETE")
    print("="*70)
    
    print(f"\nFinal Results:")
    print(f"  Total Iterations: {state['iteration']}")
    print(f"  Final Quality Score: {state['quality_history'][-1]['overall']}/10")
    print(f"  Quality Threshold: {quality_threshold}/10")
    print(f"  Status: {'✅ Threshold Met' if not state['needs_more_research'] else '⚠️ Max Iterations'}")
    
    print(f"\n📊 Quality Progression:")
    for record in state['quality_history']:
        status = "✅" if record['overall'] >= quality_threshold else "🔄"
        print(f"  {status} Iteration {record['iteration']}: {record['overall']}/10")
    
    if state['improvement_history']:
        print(f"\n🎯 Improvements Made:")
        for improvement in state['improvement_history']:
            print(f"  • {improvement}")
    
    print("\n" + "="*70 + "\n")
    
    return state


# ============================================================================
# TESTING
# ============================================================================

if __name__ == "__main__":
    """
    Test iterative research with self-improvement.
    """
    
    # Test topic
    test_topic = "Applications of CRISPR gene editing in medicine"
    
    print("\n" + "="*70)
    print("TESTING: ITERATIVE SELF-IMPROVING AGENT")
    print("="*70)
    print(f"Topic: {test_topic}")
    print(f"Threshold: 8.0/10")
    print(f"Max Iterations: 3")
    print("="*70 + "\n")
    
    input("Press Enter to start iterative research...\n")
    
    # Run iterative research
    result = run_iterative_research(
        topic=test_topic,
        quality_threshold=8.0,
        max_iterations=3
    )
    
    # Display detailed results
    print("\n" + "="*70)
    print("📄 DETAILED RESULTS")
    print("="*70)
    
    print(f"\nResearch ID: {result['research_id']}")
    print(f"Topic: {result['topic']}")
    
    print(f"\n{'─'*70}")
    print("RESEARCH QUESTIONS (ALL ITERATIONS):")
    print('─'*70)
    for i, q in enumerate(result['research_questions'], 1):
        print(f"{i}. {q}")
    
    print(f"\n{'─'*70}")
    print("QUALITY EVOLUTION:")
    print('─'*70)
    for record in result['quality_history']:
        print(f"\nIteration {record['iteration']}:")
        print(f"  Overall:   {record['scores']['overall_score']}/10")
        print(f"  Depth:     {record['scores']['depth_score']}/10")
        print(f"  Relevance: {record['scores']['relevance_score']}/10")
        print(f"  Clarity:   {record['scores']['clarity_score']}/10")
        print(f"  Coverage:  {record['scores']['coverage_score']}/10")
    
    print(f"\n{'─'*70}")
    print("FINAL SUMMARY:")
    print('─'*70)
    print(result['summary'])
    
    print("\n" + "="*70)
    print("✨ SELF-IMPROVEMENT DEMONSTRATED!")
    print("="*70)
    
    improvement = result['quality_history'][-1]['overall'] - result['quality_history'][0]['overall']
    print(f"\nQuality Improvement: +{improvement:.1f} points")
    print(f"Initial:  {result['quality_history'][0]['overall']}/10")
    print(f"Final:    {result['quality_history'][-1]['overall']}/10")
    print()
