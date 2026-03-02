# Usage Guide

## Quick Start
```bash
# Run with default example
python day2_research_agent.py
```

## Custom Topics

### Programmatic Usage
```python
from day2_research_agent import run_research

# Research any topic
result = run_research("Impact of climate change on coral reefs")

# Access results
print(f"Questions: {result['research_questions']}")
print(f"Sources: {len(result['search_results'])}")
print(f"Summary: {result['summary']}")
```

### Command Line
```python
# Edit day2_research_agent.py, change test_topic:
if __name__ == "__main__":
    test_topic = "YOUR TOPIC HERE"
    result = run_research(test_topic)
```

## Advanced Usage

### Adjust Search Depth
```python
# In research_agent function, modify:
results = tools.search_web(
    query=question,
    max_results=5  # Change from 3 to 5 for more sources
)
```

### Custom Synthesis Prompt
```python
# In synthesis_agent function, modify the prompt:
content = f"""Create a technical analysis of: {state['topic']}
- Focus on recent developments
- Include quantitative data
- Cite specific studies
...
"""
```

### Access Individual Agents
```python
from day2_research_agent import planning_agent, research_agent, synthesis_agent

# Create initial state
state = {
    'topic': 'Quantum computing',
    'research_questions': [],
    'search_results': {},
    'summary': '',
    'current_step': 'init'
}

# Run agents individually
state = planning_agent(state)
print(state['research_questions'])

state = research_agent(state)
print(state['search_results'].keys())

state = synthesis_agent(state)
print(state['summary'])
```

## Example Topics

### Technology
- "Latest developments in large language models"
- "State of autonomous vehicle technology 2024"
- "Breakthrough in quantum error correction"

### Science
- "CRISPR gene editing recent clinical trials"
- "James Webb Space Telescope discoveries"
- "Progress in fusion energy research"

### Business
- "Impact of AI on software development productivity"
- "Trends in renewable energy investment"
- "Evolution of remote work post-pandemic"

### Health
- "Advances in Alzheimer's disease treatment"
- "Mental health interventions using AI"
- "Personalized medicine using genomics"

## Output Structure
```python
{
    'topic': str,
    'research_questions': [str, str, str],
    'search_results': {
        'question': [
            {
                'title': str,
                'url': str,
                'content': str,
                'score': float
            },
            ...
        ],
        ...
    },
    'summary': str,
    'current_step': 'complete'
}
```

## Tips for Best Results

### Topic Selection
✅ **Good:** Specific, time-bound, searchable  
- "Recent breakthroughs in mRNA vaccines"
- "2024 developments in solar panel efficiency"

❌ **Bad:** Too broad or philosophical  
- "Everything about technology"
- "The meaning of consciousness"

### Question Quality
- Planning agent generates better questions with specific topics
- Narrow topics → focused questions → relevant sources

### Source Quality
- Tavily's relevance score indicates quality (0-1)
- Scores >0.85 typically indicate highly relevant sources
- Low scores might indicate off-topic results

## Troubleshooting

### No Results Found
- Try more general search terms
- Check API key configuration
- Verify internet connection

### Summary Too Short
- Increase `max_tokens` in synthesis_agent
- Add more sources per question (increase `max_results`)

### Questions Off-Topic
- Refine your topic to be more specific
- Check planning agent prompt engineering

### API Errors
- Verify API keys in .env
- Check rate limits
- Ensure venv is activated
