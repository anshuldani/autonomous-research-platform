"""
Compare Single-Pass vs Iterative Research
==========================================

Demonstrate quality improvement from self-critique.
"""

from day3_advanced_rag_agent import run_advanced_research
from iterative_research import run_iterative_research
import time


def compare_approaches(topic: str):
    """
    Compare single-pass vs iterative research quality.
    """
    
    print("\n" + "="*70)
    print("COMPARISON: Single-Pass vs Iterative Self-Improvement")
    print("="*70)
    print(f"Topic: {topic}\n")
    
    # ========================================================================
    # Approach 1: Single-Pass (Day 3)
    # ========================================================================
    
    print("─"*70)
    print("APPROACH 1: Single-Pass Research (Day 3)")
    print("─"*70)
    
    start = time.time()
    single_result = run_advanced_research(topic)
    single_time = time.time() - start
    
    # Score the single-pass result
    from quality_scorer import score_research_quality
    
    single_scores = score_research_quality(
        topic=topic,
        questions=single_result['research_questions'],
        summary=single_result['summary'],
        sources_count=single_result['stored_chunks']
    )
    
    print(f"✅ Single-pass complete in {single_time:.1f}s")
    print(f"Quality Score: {single_scores['overall_score']}/10")
    
    # ========================================================================
    # Approach 2: Iterative Self-Improvement (Day 4)
    # ========================================================================
    
    print("\n" + "─"*70)
    print("APPROACH 2: Iterative Self-Improving Research (Day 4)")
    print("─"*70)
    
    start = time.time()
    iterative_result = run_iterative_research(
        topic=topic,
        quality_threshold=8.0,
        max_iterations=3
    )
    iterative_time = time.time() - start
    
    final_score = iterative_result['quality_history'][-1]['overall']
    
    print(f"✅ Iterative research complete in {iterative_time:.1f}s")
    print(f"Final Quality Score: {final_score}/10")
    
    # ========================================================================
    # Comparison
    # ========================================================================
    
    print("\n" + "="*70)
    print("📊 COMPARISON RESULTS")
    print("="*70)
    
    print(f"\n{'Metric':<30} {'Single-Pass':<20} {'Iterative'}")
    print("─"*70)
    print(f"{'Quality Score':<30} {single_scores['overall_score']:<20.1f} {final_score:.1f}")
    print(f"{'Iterations':<30} {'1':<20} {iterative_result['iteration']}")
    print(f"{'Total Sources':<30} {single_result['stored_chunks']:<20} {iterative_result['stored_chunks']}")
    print(f"{'Time (seconds)':<30} {single_time:<20.1f} {iterative_time:.1f}")
    
    improvement = final_score - single_scores['overall_score']
    
    print("\n" + "="*70)
    print("🎯 KEY INSIGHTS")
    print("="*70)
    
    if improvement > 0:
        print(f"\n✨ Iterative approach improved quality by {improvement:.1f} points!")
        print(f"   {single_scores['overall_score']}/10 → {final_score}/10")
        print(f"\n   Quality improvement: +{(improvement/single_scores['overall_score']*100):.0f}%")
    else:
        print(f"\n✅ Both approaches achieved similar quality")
    
    print(f"\n📈 Iteration Progression:")
    for i, record in enumerate(iterative_result['quality_history'], 1):
        arrow = " → " if i < len(iterative_result['quality_history']) else ""
        print(f"   Iteration {i}: {record['overall']:.1f}/10{arrow}", end="")
    print()
    
    print("\n" + "="*70)
    print("SUMMARIES COMPARISON")
    print("="*70)
    
    print("\n📄 Single-Pass Summary (first 200 chars):")
    print("─"*70)
    print(single_result['summary'][:200] + "...\n")
    
    print("📄 Iterative Summary (first 200 chars):")
    print("─"*70)
    print(iterative_result['summary'][:200] + "...\n")
    
    print("="*70)
    print("💡 The iterative approach identifies weaknesses and")
    print("   researches targeted areas to improve quality!")
    print("="*70 + "\n")


if __name__ == "__main__":
    compare_approaches("Impact of microplastics on ocean ecosystems")
