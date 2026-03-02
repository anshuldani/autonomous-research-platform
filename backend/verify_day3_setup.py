"""
Day 3 Setup Verification
========================

Verify all APIs and dependencies are configured correctly.
"""

import os
from dotenv import load_dotenv

load_dotenv()


def verify_environment():
    """Check all environment variables."""
    
    print("\n" + "="*60)
    print("DAY 3 SETUP VERIFICATION")
    print("="*60)
    
    required_keys = {
        'ANTHROPIC_API_KEY': 'Claude (required)',
        'TAVILY_API_KEY': 'Web search (required)',
        'PINECONE_API_KEY': 'Vector DB (required)',
        'VOYAGE_API_KEY': 'Embeddings (required)',
        'COHERE_API_KEY': 'Reranking (optional)'
    }
    
    print("\n📋 Environment Variables:")
    print("─"*60)
    
    all_good = True
    
    for key, description in required_keys.items():
        value = os.getenv(key)
        
        if value:
            masked = value[:8] + "..." if len(value) > 8 else "***"
            status = "✅"
            print(f"{status} {key:<25} {masked:<20} {description}")
        else:
            status = "❌" if "required" in description else "⚠️"
            all_good = False if "required" in description else all_good
            print(f"{status} {key:<25} {'NOT SET':<20} {description}")
    
    # Test imports
    print("\n📦 Package Imports:")
    print("─"*60)
    
    packages = [
        ('anthropic', 'Claude API'),
        ('langgraph', 'Agent framework'),
        ('tavily', 'Web search'),
        ('pinecone', 'Vector database'),
        ('voyageai', 'Embeddings'),
        ('cohere', 'Reranking (optional)')
    ]
    
    for package, description in packages:
        try:
            __import__(package)
            print(f"✅ {package:<20} {description}")
        except ImportError:
            print(f"❌ {package:<20} NOT INSTALLED - {description}")
            if package != 'cohere':
                all_good = False
    
    # Test connections
    print("\n🔌 API Connections:")
    print("─"*60)
    
    # Test Pinecone
    try:
        from pinecone import Pinecone
        pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
        indexes = list(pc.list_indexes())
        print(f"✅ Pinecone connected ({len(indexes)} indexes)")
    except Exception as e:
        print(f"❌ Pinecone connection failed: {e}")
        all_good = False
    
    # Test Voyage
    try:
        import voyageai
        voyage = voyageai.Client(api_key=os.getenv("VOYAGE_API_KEY"))
        # Small test
        result = voyage.embed(["test"], model="voyage-3", input_type="document")
        print(f"✅ Voyage AI connected (dimension: {len(result.embeddings[0])})")
    except Exception as e:
        print(f"❌ Voyage AI failed: {e}")
        all_good = False
    
    # Test VectorStore
    print("\n🗄️  VectorStore Test:")
    print("─"*60)
    
    try:
        from vector_store import VectorStore
        store = VectorStore()
        print(f"✅ VectorStore initialized")
        print(f"   Index: {store.index_name}")
        print(f"   Dimension: {store.dimension}")
    except Exception as e:
        print(f"❌ VectorStore failed: {e}")
        all_good = False
    
    # Final summary
    print("\n" + "="*60)
    if all_good:
        print("✅ ALL CHECKS PASSED!")
        print("="*60)
        print("\nYou're ready to run Day 3 agents:")
        print("  python day3_rag_agent.py")
        print("  python day3_advanced_rag_agent.py")
    else:
        print("❌ SOME CHECKS FAILED")
        print("="*60)
        print("\nPlease fix the issues above:")
        print("  1. Add missing API keys to .env")
        print("  2. Install missing packages: pip install -r requirements.txt")
        print("  3. Verify API keys are valid")
    
    print()


if __name__ == "__main__":
    verify_environment()
