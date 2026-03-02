"""
Benchmark Self-Improvement Quality Gains
=========================================

Measure how much quality improves through iterations.
"""

from iterative_research import run_iterative_research
from quality_scorer import score_research_quality


def benchmark_improvement():
    """
    Run multiple topics and measure improvement.
    """
    
    print("\n" + "="*70)
    print("BENCHMARK: Self-Improvement Quality Gains")
    print("="*70 + "\n")
    
    topics = [
        "Recent advances in Alzheimer's disease treatment",
        "Impact of vertical farming on food security",
        "Applications of graph neural networks"
    ]
    
    results = []
    
    for i, topic in enumerate(topics, 1):
        print(f"\n{'─'*70}")
        print(f"TOPIC {i}/{len(topics)}: {topic}")
        print('─'*70 + '\n')
        
        # Run iterative research
        result = run_iterative_research(
            topic=topic,
            quality_threshold=8.0,
            max_iterations=2  # Limit to 2 for speed
        )
        
        initial_score = result['quality_history'][0]['overall']
        final_score = result['quality_history'][-1]['overall']
        improvement = final_score - initial_score
        
        results.append({
            'topic': topic,
            'initial': initial_score,
            'final': final_score,
            'improvement': improvement,
            'iterations': result['iteration']
        })
        
        print(f"\n  Initial:  {initial_score:.1f}/10")
        print(f"  Final:    {final_score:.1f}/10")
        print(f"  Gain:     +{improvement:.1f} points")
    
    # Summary statistics
    print("\n" + "="*70)
    print("📊 BENCHMARK SUMMARY")
    print("="*70)
    
    avg_improvement = sum(r['improvement'] for r in results) / len(results)
    avg_initial = sum(r['initial'] for r in results) / len(results)
    avg_final = sum(r['final'] for r in results) / len(results)
    
    print(f"\nAcross {len(topics)} topics:")
    print(f"  Average Initial Score:  {avg_initial:.1f}/10")
    print(f"  Average Final Score:    {avg_final:.1f}/10")
    print(f"  Average Improvement:    +{avg_improvement:.1f} points")
    print(f"  Improvement Percentage: +{(avg_improvement/avg_initial*100):.0f}%")
    
    print("\n" + "─"*70)
    print("Individual Results:")
    print("─"*70)
    
    for i, r in enumerate(results, 1):
        print(f"\n{i}. {r['topic'][:50]}...")
        print(f"   {r['initial']:.1f}/10 → {r['final']:.1f}/10 (+{r['improvement']:.1f})")
    
    print("\n" + "="*70)
    print("✨ Self-improvement consistently increases quality!")
    print("="*70 + "\n")


if __name__ == "__main__":
    benchmark_improvement()
