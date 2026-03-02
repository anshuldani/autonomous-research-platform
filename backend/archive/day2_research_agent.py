"""
DAY 2: Research Agent with Web Search
======================================

WHAT WE'RE BUILDING:
A 3-agent workflow that actually searches the web

AGENTS:
1. Planning Agent: Generates research questions
2. Research Agent: Searches web for each question (NEW!)
3. Synthesis Agent: Summarizes findings from real sources

FLOW:
Planning → Research → Synthesis → Complete
"""

# Core libraries
from anthropic import Anthropic
from typing import TypedDict, List, Dict
from langgraph.graph import StateGraph, END
import os
from dotenv import load_dotenv
import json

# Our custom module
from research_tools import ResearchTools

# Load environment variables
load_dotenv()

# Initialize clients
print("Initializing clients...")
client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
tools = ResearchTools()
print("✅ All clients ready\n")


# ============================================================================
# STATE DEFINITION
# ============================================================================

class ResearchState(TypedDict):
    """
    State that flows through the agent workflow.
    
    This is extended from Day 1 to include web search results.
    
    Fields:
        topic: User's research topic
        research_questions: Generated questions from planning agent
        search_results: Web search results mapped by question (NEW!)
        summary: Final synthesis from all sources
        current_step: Progress tracking
    """
    topic: str
    research_questions: List[str]
    search_results: Dict[str, List[Dict]]  # Question -> List of sources
    summary: str
    current_step: str


# ============================================================================
# AGENT 1: PLANNING AGENT
# ============================================================================

def planning_agent(state: ResearchState) -> ResearchState:
    """
    Generate focused research questions for the topic.
    
    This agent uses Claude to break down the research topic into
    3 specific, answerable questions that will guide web search.
    
    Args:
        state: Current workflow state with 'topic' filled
    
    Returns:
        Updated state with 'research_questions' populated
    """
    print("\n" + "="*60)
    print("STEP 1: PLANNING")
    print("="*60)
    print(f"Topic: {state['topic']}\n")
    
    # Call Claude to generate questions
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

Return ONLY a JSON array, nothing else:
["Question 1?", "Question 2?", "Question 3?"]"""
        }]
    )
    
    # Parse JSON response
    response_text = message.content[0].text
    
    # Handle potential markdown code blocks
    if "```json" in response_text:
        response_text = response_text.split("```json")[1].split("```")[0]
    elif "```" in response_text:
        response_text = response_text.split("```")[1].split("```")[0]
    
    questions = json.loads(response_text.strip())
    
    # Display generated questions
    print("Generated research questions:")
    for i, q in enumerate(questions, 1):
        print(f"  {i}. {q}")
    print()
    
    # Update state
    state['research_questions'] = questions
    state['current_step'] = 'questions_generated'
    
    return state


# ============================================================================
# AGENT 2: RESEARCH AGENT (NEW!)
# ============================================================================

def research_agent(state: ResearchState) -> ResearchState:
    """
    Search the web for each research question.
    
    This is the core innovation of Day 2. For each question generated
    by the planning agent, we perform actual web searches and gather
    real sources from the internet.
    
    The agent loops through all questions, searches the web using Tavily,
    and stores results mapped by their originating question.
    
    Args:
        state: Current workflow state with 'research_questions' filled
    
    Returns:
        Updated state with 'search_results' populated
        
    Example state transformation:
        Input:
            research_questions: ["What is X?", "How does Y work?"]
            
        Output:
            search_results: {
                "What is X?": [
                    {title: "Article 1", url: "...", content: "...", score: 0.95},
                    {title: "Article 2", url: "...", content: "...", score: 0.87}
                ],
                "How does Y work?": [...]
            }
    """
    print("\n" + "="*60)
    print("STEP 2: WEB RESEARCH")
    print("="*60 + "\n")
    
    # Dictionary to store results: {question: [sources]}
    all_results = {}
    
    # Search for each question
    for i, question in enumerate(state['research_questions'], 1):
        print(f"Question {i}/{len(state['research_questions'])}: {question}")
        
        # Use ResearchTools to search the web
        results = tools.search_web(
            query=question,
            max_results=3  # Get top 3 results per question
        )
        
        # Store results for this question
        all_results[question] = results
        
        # Display what we found
        print(f"  Found {len(results)} sources:")
        for result in results:
            # Show truncated title
            title = result['title'][:60]
            print(f"    - {title}{'...' if len(result['title']) > 60 else ''}")
        print()
    
    # Update state
    state['search_results'] = all_results
    state['current_step'] = 'research_complete'
    
    # Summary statistics
    total_sources = sum(len(sources) for sources in all_results.values())
    print(f"✅ Research complete!")
    print(f"   Questions researched: {len(all_results)}")
    print(f"   Total sources gathered: {total_sources}")
    print()
    
    return state


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def format_sources_for_claude(search_results: Dict[str, List[Dict]]) -> str:
    """
    Format search results into a readable context for Claude.
    
    Takes the dictionary of search results and formats them into
    a structured text that Claude can easily parse and synthesize.
    
    Args:
        search_results: Dictionary mapping questions to their sources
    
    Returns:
        Formatted string with all sources organized by question
    """
    formatted_sections = []
    
    for question, results in search_results.items():
        # Add question header
        formatted_sections.append(f"\n## Research Question: {question}\n")
        
        # Add each source
        for i, result in enumerate(results, 1):
            formatted_sections.append(f"### Source {i}: {result['title']}")
            formatted_sections.append(f"URL: {result['url']}")
            formatted_sections.append(f"Relevance Score: {result['score']:.2f}")
            # Include first 400 characters of content
            content_preview = result['content'][:400]
            formatted_sections.append(f"{content_preview}...\n")
    
    return "\n".join(formatted_sections)


# ============================================================================
# AGENT 3: SYNTHESIS AGENT
# ============================================================================

def synthesis_agent(state: ResearchState) -> ResearchState:
    """
    Synthesize findings from all web sources into a coherent summary.
    
    This agent takes all the search results gathered by the research agent
    and uses Claude to create an intelligent, comprehensive summary that
    synthesizes information across multiple sources.
    
    Args:
        state: Current workflow state with 'search_results' filled
    
    Returns:
        Updated state with 'summary' populated
    """
    print("\n" + "="*60)
    print("STEP 3: SYNTHESIS")
    print("="*60 + "\n")
    
    print("Formatting sources for synthesis...")
    
    # Format all research for Claude
    context_text = format_sources_for_claude(state['search_results'])
    
    print(f"Synthesizing findings from {len(state['search_results'])} questions...")
    
    # Call Claude to synthesize
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2048,  # Longer response for comprehensive summary
        messages=[{
            "role": "user",
            "content": f"""You are a research synthesizer. Create a comprehensive 
summary about: {state['topic']}

Based on this research from multiple web sources:
{context_text}

Write a well-structured summary with:
1. An introductory paragraph setting context (2-3 sentences)
2. Key findings synthesized from the sources (3-4 paragraphs)
3. Notable patterns, trends, or insights discovered (1-2 paragraphs)
4. A concluding paragraph with implications (2-3 sentences)

Requirements:
- Synthesize information across sources, don't just list facts
- Be analytical and identify connections between findings
- Write in clear, professional prose
- Aim for 400-500 words total
- Do NOT use bullet points or lists"""
        }]
    )
    
    summary = message.content[0].text
    
    print("✅ Synthesis complete!\n")
    
    # Update state
    state['summary'] = summary
    state['current_step'] = 'complete'
    
    return state


# Workflow builder will be added next


# ============================================================================
# WORKFLOW BUILDER
# ============================================================================

def create_research_workflow():
    """
    Build the complete 3-agent research workflow.
    
    Workflow:
        Planning Agent → Research Agent → Synthesis Agent → END
    
    Each agent processes the state and passes it to the next agent.
    The final state contains the complete research report.
    
    Returns:
        Compiled LangGraph application ready to execute
    """
    print("🏗️  Building research workflow...")
    
    # Initialize graph with state type
    workflow = StateGraph(ResearchState)
    
    # Add all three agents as nodes
    workflow.add_node("planner", planning_agent)
    workflow.add_node("researcher", research_agent)
    workflow.add_node("synthesizer", synthesis_agent)
    
    # Set entry point
    workflow.set_entry_point("planner")
    
    # Chain agents together
    workflow.add_edge("planner", "researcher")      # Plan → Research
    workflow.add_edge("researcher", "synthesizer")  # Research → Synthesize
    workflow.add_edge("synthesizer", END)          # Synthesize → Done
    
    # Compile into runnable application
    app = workflow.compile()
    
    print("✅ Workflow compiled (3 agents)")
    print("   Flow: Planning → Research → Synthesis → Complete\n")
    
    return app


# Run function will be added next


def run_research(topic: str):
    """
    Execute the complete research workflow.
    
    This is the main entry point for running research. It:
    1. Creates initial state with the topic
    2. Builds and executes the workflow
    3. Returns the final state with complete research
    
    Args:
        topic: Research topic to investigate
    
    Returns:
        Final state dictionary with all research results
    """
    print("\n" + "="*60)
    print("🚀 STARTING 3-AGENT RESEARCH WORKFLOW")
    print("="*60)
    
    # Create initial state
    initial_state = {
        "topic": topic,
        "research_questions": [],
        "search_results": {},
        "summary": "",
        "current_step": "initialized"
    }
    
    # Build workflow
    app = create_research_workflow()
    
    # Execute workflow (this runs all agents in sequence)
    final_state = app.invoke(initial_state)
    
    return final_state


# Testing section will be added next


# ============================================================================
# TESTING & EXECUTION
# ============================================================================

if __name__ == "__main__":
    """
    Test the complete workflow with a sample topic.
    
    This runs when you execute: python day2_research_agent.py
    """
    
    # Test topic
    test_topic = "Recent breakthroughs in quantum computing"
    
    print("="*60)
    print("TESTING DAY 2 RESEARCH AGENT")
    print("="*60)
    print(f"Test topic: {test_topic}\n")
    
    # Run workflow
    result = run_research(test_topic)
    
    # Display results
    print("\n" + "="*60)
    print("📄 FINAL RESEARCH REPORT")
    print("="*60)
    print(f"\nTopic: {result['topic']}")
    print(f"Status: {result['current_step']}")
    
    print(f"\n{'─'*60}")
    print("RESEARCH QUESTIONS:")
    print('─'*60)
    for i, q in enumerate(result['research_questions'], 1):
        print(f"{i}. {q}")
    
    print(f"\n{'─'*60}")
    print("SOURCES GATHERED:")
    print('─'*60)
    total_sources = sum(len(sources) for sources in result['search_results'].values())
    print(f"Total sources: {total_sources}")
    
    print(f"\n{'─'*60}")
    print("SYNTHESIZED SUMMARY:")
    print('─'*60)
    print(result['summary'])
    print()
