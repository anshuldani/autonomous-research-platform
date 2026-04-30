"""
Advanced RAG Research Agent
============================

Production-grade RAG with hybrid search, Cohere reranking, and
LangGraph workflow orchestration.
"""

from anthropic import Anthropic
from typing import TypedDict, List, Dict
from langgraph.graph import StateGraph, END
import os
from dotenv import load_dotenv
import json
import uuid

from research_tools import ResearchTools
from vector_store import VectorStore

load_dotenv()

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
tools = ResearchTools()
vector_store = VectorStore()


# ============================================================================
# ENHANCED STATE
# ============================================================================

class AdvancedResearchState(TypedDict):
    """
    State with quality metrics and advanced retrieval info.
    
    New fields:
    - retrieval_method: Track which method was used
    - rerank_scores: Quality scores from reranking
    - quality_metrics: Overall quality assessment
    """
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


# ============================================================================
# AGENT 1: PLANNING AGENT
# ============================================================================

def planning_agent(state: AdvancedResearchState) -> AdvancedResearchState:
    """Generate research questions (unchanged)"""
    
    print("\n" + "="*60)
    print("STEP 1: PLANNING")
    print("="*60)
    print(f"Topic: {state['topic']}\n")
    
    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1024,
        messages=[{
            "role": "user",
            "content": f"""Generate 3 specific research questions for: {state['topic']}

Return ONLY a JSON array:
["Question 1?", "Question 2?", "Question 3?"]"""
        }]
    )
    
    response_text = message.content[0].text
    
    if "```json" in response_text:
        response_text = response_text.split("```json")[1].split("```")[0]
    elif "```" in response_text:
        response_text = response_text.split("```")[1].split("```")[0]
    
    questions = json.loads(response_text.strip())
    
    print("Generated questions:")
    for i, q in enumerate(questions, 1):
        print(f"  {i}. {q}")
    print()
    
    state['research_questions'] = questions
    state['current_step'] = 'questions_generated'
    
    return state


# ============================================================================
# AGENT 2: RESEARCH AGENT (with storage)
# ============================================================================

def research_agent(state: AdvancedResearchState) -> AdvancedResearchState:
    """Search web and store in vector DB"""
    
    print("\n" + "="*60)
    print("STEP 2: WEB RESEARCH + VECTOR STORAGE")
    print("="*60 + "\n")
    
    all_results = {}
    all_texts = []
    all_metadata = []
    
    for i, question in enumerate(state['research_questions'], 1):
        print(f"Question {i}/{len(state['research_questions'])}: {question}")
        
        results = tools.search_web(query=question, max_results=3)
        all_results[question] = results
        
        print(f"  Found {len(results)} sources:")
        for result in results:
            title = result['title'][:60]
            print(f"    - {title}{'...' if len(result['title']) > 60 else ''}")
            
            all_texts.append(result['content'])
            all_metadata.append({
                'title': result['title'],
                'url': result['url'],
                'question': question,
                'score': result['score'],
                'source_type': 'web_search'
            })
        
        print()
    
    # Store in vector DB
    print(f"💾 Storing {len(all_texts)} sources in vector database...")
    vector_store.store_documents(
        texts=all_texts,
        metadata=all_metadata,
        research_id=state['research_id'],
        auto_chunk=True
    )
    
    state['search_results'] = all_results
    state['stored_chunks'] = len(all_texts)
    state['current_step'] = 'research_complete'
    
    total_sources = sum(len(s) for s in all_results.values())
    print(f"✅ Research complete: {total_sources} sources, stored in VectorDB")
    print()
    
    return state



# ============================================================================
# AGENT 3: ADVANCED RAG SYNTHESIS
# ============================================================================

def advanced_rag_synthesis_agent(state: AdvancedResearchState) -> AdvancedResearchState:
    """
    Advanced synthesis using:
    1. Hybrid search (semantic + keyword)
    2. Reranking with Cohere
    3. Quality metrics tracking
    """
    
    print("\n" + "="*60)
    print("STEP 3: ADVANCED RAG SYNTHESIS")
    print("="*60 + "\n")
    
    all_retrieved_chunks = []
    all_rerank_scores = []
    
    for question in state['research_questions']:
        print(f"🔍 Advanced retrieval for: {question}")
        
        # Step 1: Hybrid search (get more candidates)
        print(f"   → Hybrid search (semantic + keyword)...")
        candidates = vector_store.hybrid_search(
            query=question,
            research_id=state['research_id'],
            top_k=10,  # Get 10 candidates
            alpha=0.7  # 70% semantic, 30% keyword
        )
        
        # Step 2: Rerank with Cohere
        print(f"   → Reranking {len(candidates)} candidates...")
        try:
            reranked = vector_store.rerank_results(
                query=question,
                results=candidates,
                top_n=3  # Keep top 3 after reranking
            )
            
            # Track rerank scores
            for r in reranked:
                all_rerank_scores.append(r.get('rerank_score', 0))
            
            retrieved = reranked
            
        except Exception as e:
            print(f"   ⚠️  Reranking unavailable: {e}")
            print(f"   → Using top 3 from hybrid search")
            retrieved = candidates[:3]
        
        # Add to context
        all_retrieved_chunks.append(f"\n## Question: {question}\n")
        
        for i, chunk in enumerate(retrieved, 1):
            score_info = f"rerank: {chunk.get('rerank_score', 0):.3f}" if 'rerank_score' in chunk else f"hybrid: {chunk.get('hybrid_score', chunk['score']):.3f}"
            
            all_retrieved_chunks.append(
                f"### Source {i} ({score_info})"
            )
            all_retrieved_chunks.append(f"Title: {chunk['metadata'].get('title', 'N/A')}")
            all_retrieved_chunks.append(f"{chunk['text']}\n")
            
            print(f"   ✓ {chunk['metadata'].get('title', 'N/A')[:50]}... ({score_info})")
        
        print()
    
    # Join context
    rag_context = "\n".join(all_retrieved_chunks)
    state['rag_context'] = rag_context
    state['retrieval_method'] = "hybrid+rerank"
    state['rerank_scores'] = all_rerank_scores
    
    # Quality metrics
    avg_score = sum(all_rerank_scores) / len(all_rerank_scores) if all_rerank_scores else 0
    state['quality_metrics'] = {
        'avg_rerank_score': avg_score,
        'total_chunks_retrieved': len(state['research_questions']) * 3,
        'retrieval_method': state['retrieval_method']
    }
    
    print(f"📊 Quality metrics:")
    print(f"   Avg rerank score: {avg_score:.3f}")
    print(f"   Chunks retrieved: {state['quality_metrics']['total_chunks_retrieved']}")
    print()
    
    # Synthesize with Claude
    print(f"Synthesizing from {state['quality_metrics']['total_chunks_retrieved']} high-quality chunks...")
    
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2048,
        messages=[{
            "role": "user",
            "content": f"""Create a comprehensive research report on: {state['topic']}

Based on these carefully retrieved and reranked sources:
{rag_context}

Write a well-structured summary with:
1. Introduction (2-3 sentences)
2. Key findings (3-4 paragraphs)
3. Patterns and insights (1-2 paragraphs)
4. Conclusion (2-3 sentences)

Requirements:
- Synthesize across sources
- Be analytical
- Professional prose
- 400-500 words
- NO bullet points"""
        }]
    )
    
    summary = message.content[0].text
    
    print("✅ Advanced RAG synthesis complete!")
    print()
    
    state['summary'] = summary
    state['current_step'] = 'complete'
    
    return state



# ============================================================================
# WORKFLOW
# ============================================================================

def create_advanced_rag_workflow():
    """Build advanced RAG workflow with quality tracking"""
    
    print("🏗️  Building advanced RAG workflow...")
    
    workflow = StateGraph(AdvancedResearchState)
    
    workflow.add_node("planner", planning_agent)
    workflow.add_node("researcher", research_agent)
    workflow.add_node("advanced_synthesizer", advanced_rag_synthesis_agent)
    
    workflow.set_entry_point("planner")
    workflow.add_edge("planner", "researcher")
    workflow.add_edge("researcher", "advanced_synthesizer")
    workflow.add_edge("advanced_synthesizer", END)
    
    app = workflow.compile()
    
    print("✅ Advanced RAG workflow compiled")
    print("   Flow: Planning → Research+Storage → Hybrid+Rerank → Synthesis\n")
    
    return app


def run_advanced_research(topic: str):
    """Execute advanced RAG research"""
    
    print("\n" + "="*60)
    print("🚀 ADVANCED RAG RESEARCH WORKFLOW")
    print("="*60)
    
    research_id = f"advanced_{uuid.uuid4().hex[:8]}"
    
    initial_state = {
        "topic": topic,
        "research_id": research_id,
        "research_questions": [],
        "search_results": {},
        "stored_chunks": 0,
        "retrieval_method": "",
        "rag_context": "",
        "rerank_scores": [],
        "quality_metrics": {},
        "summary": "",
        "current_step": "initialized"
    }
    
    app = create_advanced_rag_workflow()
    final_state = app.invoke(initial_state)
    
    return final_state


# Testing
if __name__ == "__main__":
    test_topic = "Recent breakthroughs in renewable energy storage"
    
    print("="*60)
    print("TESTING: ADVANCED RAG AGENT")
    print("="*60)
    print(f"Topic: {test_topic}\n")
    
    result = run_advanced_research(test_topic)
    
    print("\n" + "="*60)
    print("📄 ADVANCED RAG RESEARCH REPORT")
    print("="*60)
    print(f"\nResearch ID: {result['research_id']}")
    print(f"Topic: {result['topic']}")
    
    print(f"\n{'─'*60}")
    print("QUESTIONS:")
    print('─'*60)
    for i, q in enumerate(result['research_questions'], 1):
        print(f"{i}. {q}")
    
    print(f"\n{'─'*60}")
    print("RETRIEVAL QUALITY:")
    print('─'*60)
    print(f"Method: {result['retrieval_method']}")
    print(f"Chunks retrieved: {result['quality_metrics']['total_chunks_retrieved']}")
    print(f"Avg rerank score: {result['quality_metrics']['avg_rerank_score']:.3f}")
    
    if result['rerank_scores']:
        print(f"Best score: {max(result['rerank_scores']):.3f}")
        print(f"Worst score: {min(result['rerank_scores']):.3f}")
    
    print(f"\n{'─'*60}")
    print("SUMMARY:")
    print('─'*60)
    print(result['summary'])
    
    print("\n" + "="*60)
    print("✨ ADVANCED RAG FEATURES DEMONSTRATED!")
    print("="*60)
    print("\n✅ Hybrid search (semantic + keyword)")
    print("✅ Cohere reranking for precision")
    print("✅ Quality metrics tracking")
    print("✅ Production-grade retrieval\n")
