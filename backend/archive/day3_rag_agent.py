"""
DAY 3: RAG-Enhanced Research Agent
===================================

WHAT'S NEW:
- Stores web search results in vector database
- Uses semantic search to find most relevant chunks
- Synthesizes from retrieved context (not all sources)

ARCHITECTURE:
Planning Agent → Research Agent → Store in VectorDB → RAG Synthesis → Report

KEY IMPROVEMENT:
Instead of giving Claude ALL sources, we:
1. Store sources in vector DB
2. Semantically search for MOST relevant chunks
3. Give Claude only the best context
"""

# Core libraries
from anthropic import Anthropic
from typing import TypedDict, List, Dict
from langgraph.graph import StateGraph, END
import os
from dotenv import load_dotenv
import json
import uuid

# Our modules
from research_tools import ResearchTools
from vector_store import VectorStore

# Load environment
load_dotenv()

# Initialize clients
print("Initializing Day 3 RAG Agent...")
client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
tools = ResearchTools()
vector_store = VectorStore()  # NEW: Vector database
print("✅ All clients ready (including VectorStore!)\n")

# State and agents will be added next


# ============================================================================
# STATE DEFINITION
# ============================================================================

class ResearchState(TypedDict):
    """
    Enhanced state for RAG-powered research.
    
    New fields compared to Day 2:
    - research_id: Unique ID for grouping vectors
    - stored_chunks: Count of chunks stored in vector DB
    
    Fields:
        topic: User's research topic
        research_id: Unique identifier for this research session
        research_questions: Generated questions
        search_results: Raw web search results
        stored_chunks: Number of chunks stored in vector DB (NEW)
        rag_context: Retrieved context from vector search (NEW)
        summary: Final synthesized report
        current_step: Progress tracking
    """
    topic: str
    research_id: str  # NEW: Unique ID
    research_questions: List[str]
    search_results: Dict[str, List[Dict]]
    stored_chunks: int  # NEW: Track storage
    rag_context: str  # NEW: Retrieved chunks
    summary: str
    current_step: str


# Agents will be added next


# ============================================================================
# AGENT 1: PLANNING AGENT (Same as Day 2)
# ============================================================================

def planning_agent(state: ResearchState) -> ResearchState:
    """
    Generate focused research questions.
    
    This agent is unchanged from Day 2.
    """
    print("\n" + "="*60)
    print("STEP 1: PLANNING")
    print("="*60)
    print(f"Topic: {state['topic']}\n")
    
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        messages=[{
            "role": "user",
            "content": f"""Generate 3 specific, focused research questions for: {state['topic']}

Requirements:
- Questions should be answerable via web search
- Each question should cover a different aspect
- Be specific, not overly broad

Return ONLY a JSON array:
["Question 1?", "Question 2?", "Question 3?"]"""
        }]
    )
    
    response_text = message.content[0].text
    
    # Handle markdown code blocks
    if "```json" in response_text:
        response_text = response_text.split("```json")[1].split("```")[0]
    elif "```" in response_text:
        response_text = response_text.split("```")[1].split("```")[0]
    
    questions = json.loads(response_text.strip())
    
    print("Generated research questions:")
    for i, q in enumerate(questions, 1):
        print(f"  {i}. {q}")
    print()
    
    state['research_questions'] = questions
    state['current_step'] = 'questions_generated'
    
    return state


# Research agent will be added next


# ============================================================================
# AGENT 2: ENHANCED RESEARCH AGENT (NEW: Stores in VectorDB)
# ============================================================================

def research_agent(state: ResearchState) -> ResearchState:
    """
    Search web AND store in vector database.
    
    NEW in Day 3:
    - After searching, chunks and stores in Pinecone
    - Tracks number of chunks stored
    - Enables semantic search later
    """
    print("\n" + "="*60)
    print("STEP 2: WEB RESEARCH + VECTOR STORAGE")
    print("="*60 + "\n")
    
    all_results = {}
    
    # Collect all texts and metadata for batch storage
    all_texts = []
    all_metadata = []
    
    # Search for each question
    for i, question in enumerate(state['research_questions'], 1):
        print(f"Question {i}/{len(state['research_questions'])}: {question}")
        
        # Web search
        results = tools.search_web(query=question, max_results=3)
        all_results[question] = results
        
        print(f"  Found {len(results)} sources:")
        for result in results:
            title = result['title'][:60]
            print(f"    - {title}{'...' if len(result['title']) > 60 else ''}")
            
            # Collect for vector storage
            all_texts.append(result['content'])
            all_metadata.append({
                'title': result['title'],
                'url': result['url'],
                'question': question,
                'score': result['score'],
                'source_type': 'web_search'
            })
        
        print()
    
    # NEW: Store all sources in vector database
    print(f"💾 Storing {len(all_texts)} sources in vector database...")
    vector_store.store_documents(
        texts=all_texts,
        metadata=all_metadata,
        research_id=state['research_id'],
        auto_chunk=True  # Automatically chunk long articles
    )
    
    # Update state
    state['search_results'] = all_results
    state['stored_chunks'] = len(all_texts)  # Track chunks stored
    state['current_step'] = 'research_complete'
    
    total_sources = sum(len(sources) for sources in all_results.values())
    print(f"✅ Research complete!")
    print(f"   Questions researched: {len(all_results)}")
    print(f"   Total sources gathered: {total_sources}")
    print(f"   Stored in vector DB: ✅")
    print()
    
    return state


# RAG synthesis will be added next


# ============================================================================
# AGENT 3: RAG-ENHANCED SYNTHESIS AGENT (NEW: Uses Semantic Search)
# ============================================================================

def rag_synthesis_agent(state: ResearchState) -> ResearchState:
    """
    Synthesize using RAG retrieval.
    
    NEW in Day 3:
    - Instead of using ALL sources, semantically search vector DB
    - Retrieve only most relevant chunks for each question
    - Much better context quality for Claude
    """
    print("\n" + "="*60)
    print("STEP 3: RAG-ENHANCED SYNTHESIS")
    print("="*60 + "\n")
    
    # For each question, retrieve most relevant chunks
    rag_chunks = []
    
    for question in state['research_questions']:
        print(f"🔍 RAG search for: {question}")
        
        # Semantic search in vector DB
        relevant_chunks = vector_store.search(
            query=question,
            research_id=state['research_id'],
            top_k=3  # Get top 3 most relevant chunks per question
        )
        
        # Format retrieved chunks
        rag_chunks.append(f"\n## Question: {question}\n")
        for i, chunk in enumerate(relevant_chunks, 1):
            rag_chunks.append(
                f"### Relevant Source {i} (score: {chunk['score']:.3f})"
            )
            rag_chunks.append(f"Title: {chunk['metadata'].get('title', 'N/A')}")
            rag_chunks.append(f"{chunk['text']}\n")
            
            print(f"   Retrieved: {chunk['metadata'].get('title', 'N/A')[:50]}... "
                  f"(score: {chunk['score']:.3f})")
        print()
    
    # Join all RAG context
    rag_context = "\n".join(rag_chunks)
    state['rag_context'] = rag_context
    
    print(f"Synthesizing from {len(state['research_questions']) * 3} retrieved chunks...")
    
    # Call Claude with RAG context
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2048,
        messages=[{
            "role": "user",
            "content": f"""Create a comprehensive research report on: {state['topic']}

Based on these semantically retrieved sources:
{rag_context}

Write a well-structured summary with:
1. An introductory paragraph (2-3 sentences)
2. Key findings synthesized from sources (3-4 paragraphs)
3. Notable patterns and insights (1-2 paragraphs)
4. Concluding implications (2-3 sentences)

Requirements:
- Synthesize across sources, don't just list facts
- Be analytical and identify connections
- Write in clear, professional prose
- Aim for 400-500 words
- Do NOT use bullet points"""
        }]
    )
    
    summary = message.content[0].text
    
    print("✅ RAG synthesis complete!\n")
    
    state['summary'] = summary
    state['current_step'] = 'complete'
    
    return state


# Workflow builder will be added next


# ============================================================================
# WORKFLOW BUILDER
# ============================================================================

def create_rag_workflow():
    """
    Build RAG-enhanced research workflow.
    
    Flow:
        Planning → Research (+ VectorDB Storage) → RAG Synthesis → END
    
    Key difference from Day 2:
    - Research agent stores in VectorDB
    - Synthesis uses semantic search instead of all sources
    
    Returns:
        Compiled LangGraph application
    """
    print("🏗️  Building RAG workflow...")
    
    workflow = StateGraph(ResearchState)
    
    # Add all agents
    workflow.add_node("planner", planning_agent)
    workflow.add_node("researcher", research_agent)
    workflow.add_node("rag_synthesizer", rag_synthesis_agent)
    
    # Set entry point
    workflow.set_entry_point("planner")
    
    # Chain agents
    workflow.add_edge("planner", "researcher")
    workflow.add_edge("researcher", "rag_synthesizer")
    workflow.add_edge("rag_synthesizer", END)
    
    app = workflow.compile()
    
    print("✅ RAG workflow compiled (3 agents)")
    print("   Flow: Planning → Research+Storage → RAG Synthesis → Complete\n")
    
    return app


# Run function will be added next


def run_research(topic: str):
    """
    Execute RAG-enhanced research workflow.
    
    Args:
        topic: Research topic to investigate
    
    Returns:
        Final state with RAG-synthesized report
    """
    print("\n" + "="*60)
    print("🚀 STARTING RAG-ENHANCED RESEARCH WORKFLOW")
    print("="*60)
    
    # Generate unique research ID
    research_id = f"research_{uuid.uuid4().hex[:8]}"
    
    # Create initial state
    initial_state = {
        "topic": topic,
        "research_id": research_id,
        "research_questions": [],
        "search_results": {},
        "stored_chunks": 0,
        "rag_context": "",
        "summary": "",
        "current_step": "initialized"
    }
    
    # Build and execute workflow
    app = create_rag_workflow()
    final_state = app.invoke(initial_state)
    
    return final_state


# Testing section will be added next


# ============================================================================
# TESTING & EXECUTION
# ============================================================================

if __name__ == "__main__":
    """
    Test RAG-enhanced research agent
    """
    
    # Test topic
    test_topic = "Recent breakthroughs in CRISPR gene editing"
    
    print("="*60)
    print("TESTING DAY 3: RAG-ENHANCED RESEARCH AGENT")
    print("="*60)
    print(f"Test topic: {test_topic}\n")
    
    # Run workflow
    result = run_research(test_topic)
    
    # Display results
    print("\n" + "="*60)
    print("📄 FINAL RAG RESEARCH REPORT")
    print("="*60)
    print(f"\nResearch ID: {result['research_id']}")
    print(f"Topic: {result['topic']}")
    print(f"Status: {result['current_step']}")
    
    print(f"\n{'─'*60}")
    print("RESEARCH QUESTIONS:")
    print('─'*60)
    for i, q in enumerate(result['research_questions'], 1):
        print(f"{i}. {q}")
    
    print(f"\n{'─'*60}")
    print("VECTOR STORAGE:")
    print('─'*60)
    print(f"Documents stored: {result['stored_chunks']}")
    print(f"Research ID: {result['research_id']}")
    
    print(f"\n{'─'*60}")
    print("RAG RETRIEVAL:")
    print('─'*60)
    total_sources = sum(len(sources) for sources in result['search_results'].values())
    retrieved_chunks = result['research_questions'] and len(result['research_questions']) * 3
    print(f"Total sources gathered: {total_sources}")
    print(f"Chunks retrieved for synthesis: {retrieved_chunks}")
    print(f"Retrieval efficiency: Using {retrieved_chunks}/{result['stored_chunks']} chunks")
    
    print(f"\n{'─'*60}")
    print("SYNTHESIZED SUMMARY:")
    print('─'*60)
    print(result['summary'])
    print()
    
    print("="*60)
    print("✨ RAG WORKFLOW COMPLETE!")
    print("="*60)
    print("\nKey improvements over Day 2:")
    print("  ✅ Stored sources in vector database")
    print("  ✅ Used semantic search for relevant chunks")
    print("  ✅ Better context quality for synthesis")
    print("  ✅ Can query stored knowledge later")
    print()
