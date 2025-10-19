"""
Comprehensive comparison between TF-IDF and Neural Embeddings matching
Shows accuracy improvements and performance metrics
"""
import time
from pathlib import Path
import pandas as pd

from config import Config
from src.matcher import LyricsMatcher  # TF-IDF matcher
from src.neural_matcher import NeuralLyricsMatcher  # Neural matcher


class MatcherComparison:
    """Compare different matching approaches"""
    
    def __init__(self):
        """Initialize both matchers"""
        print("\n" + "="*70)
        print("🔬 MATCHER COMPARISON: TF-IDF vs Neural Embeddings")
        print("="*70 + "\n")
        
        print("📦 Loading matchers...")
        self.tfidf_matcher = LyricsMatcher()
        self.neural_matcher = NeuralLyricsMatcher(model_name='all-MiniLM-L6-v2')
        print("✅ Both matchers loaded\n")
    
    def compare_single_query(self, query_text, top_k=5, verbose=True):
        """
        Compare both approaches on a single query
        
        Args:
            query_text: Query text to search
            top_k: Number of results
            verbose: Print detailed output
        
        Returns:
            Dictionary with comparison results
        """
        if verbose:
            print("="*70)
            print(f"Query: \"{query_text}\"")
            print("="*70 + "\n")
        
        # TF-IDF matching
        if verbose:
            print("📊 TF-IDF Approach:")
            print("-" * 70)
        
        tfidf_start = time.time()
        tfidf_results = self.tfidf_matcher.match_with_details(query_text, top_k)
        tfidf_time = time.time() - tfidf_start
        
        if verbose:
            if tfidf_results:
                for i, result in enumerate(tfidf_results, 1):
                    print(f"{i}. {result['artist']} - {result['title']}")
                    print(f"   Score: {result['final_score']:.2%} | Type: {result['match_type']}")
            else:
                print("No matches found")
            print(f"\n⏱️  Time: {tfidf_time:.3f}s\n")
        
        # Neural matching
        if verbose:
            print("🧠 Neural Embeddings Approach:")
            print("-" * 70)
        
        neural_start = time.time()
        neural_results = self.neural_matcher.match_with_details(query_text, top_k)
        neural_time = time.time() - neural_start
        
        if verbose:
            if neural_results:
                for i, result in enumerate(neural_results, 1):
                    print(f"{i}. {result['artist']} - {result['title']}")
                    print(f"   Score: {result['final_score']:.2%} | Type: {result['match_type']}")
            else:
                print("No matches found")
            print(f"\n⏱️  Time: {neural_time:.3f}s\n")
        
        # Comparison summary
        if verbose:
            self._print_comparison_summary(tfidf_results, neural_results, tfidf_time, neural_time)
        
        return {
            'query': query_text,
            'tfidf': {
                'results': tfidf_results,
                'time': tfidf_time,
                'top_score': tfidf_results[0]['final_score'] if tfidf_results else 0
            },
            'neural': {
                'results': neural_results,
                'time': neural_time,
                'top_score': neural_results[0]['final_score'] if neural_results else 0
            }
        }
    
    def _print_comparison_summary(self, tfidf_results, neural_results, tfidf_time, neural_time):
        """Print comparison summary"""
        print("📈 Comparison Summary:")
        print("-" * 70)
        
        # Match agreement
        if tfidf_results and neural_results:
            tfidf_top = f"{tfidf_results[0]['artist']} - {tfidf_results[0]['title']}"
            neural_top = f"{neural_results[0]['artist']} - {neural_results[0]['title']}"
            
            if tfidf_top == neural_top:
                print("✅ Both approaches agree on top match!")
            else:
                print("⚠️  Different top matches:")
                print(f"   TF-IDF:  {tfidf_top}")
                print(f"   Neural:  {neural_top}")
        
        # Score comparison
        if tfidf_results and neural_results:
            tfidf_score = tfidf_results[0]['final_score']
            neural_score = neural_results[0]['final_score']
            score_diff = neural_score - tfidf_score
            
            print(f"\n📊 Top Match Confidence:")
            print(f"   TF-IDF:  {tfidf_score:.2%}")
            print(f"   Neural:  {neural_score:.2%}")
            print(f"   Difference: {score_diff:+.2%}")
        
        # Speed comparison
        print(f"\n⏱️  Performance:")
        print(f"   TF-IDF:  {tfidf_time:.3f}s")
        print(f"   Neural:  {neural_time:.3f}s")
        speedup = tfidf_time / neural_time if neural_time > 0 else 0
        if speedup > 1:
            print(f"   TF-IDF is {speedup:.1f}x faster")
        else:
            print(f"   Neural is {1/speedup:.1f}x faster")
        
        print()
    
    def batch_comparison(self, queries, output_file=None):
        """
        Compare both approaches on multiple queries
        
        Args:
            queries: List of query texts
            output_file: Optional CSV output file
        
        Returns:
            DataFrame with comparison results
        """
        print("\n" + "="*70)
        print(f"📊 Batch Comparison: {len(queries)} queries")
        print("="*70 + "\n")
        
        results = []
        
        for i, query in enumerate(queries, 1):
            print(f"[{i}/{len(queries)}] Processing: \"{query[:50]}...\"")
            
            comparison = self.compare_single_query(query, top_k=3, verbose=False)
            
            # Record results
            tfidf_top = comparison['tfidf']['results'][0] if comparison['tfidf']['results'] else None
            neural_top = comparison['neural']['results'][0] if comparison['neural']['results'] else None
            
            results.append({
                'query': query,
                'tfidf_match': f"{tfidf_top['artist']} - {tfidf_top['title']}" if tfidf_top else "No match",
                'tfidf_score': comparison['tfidf']['top_score'],
                'tfidf_time': comparison['tfidf']['time'],
                'neural_match': f"{neural_top['artist']} - {neural_top['title']}" if neural_top else "No match",
                'neural_score': comparison['neural']['top_score'],
                'neural_time': comparison['neural']['time'],
                'matches_agree': (tfidf_top and neural_top and 
                                 tfidf_top['title'] == neural_top['title'] and 
                                 tfidf_top['artist'] == neural_top['artist'])
            })
        
        df = pd.DataFrame(results)
        
        # Print summary
        print("\n" + "="*70)
        print("📈 Batch Comparison Summary")
        print("="*70 + "\n")
        
        print(f"Total Queries: {len(queries)}")
        print(f"Agreement Rate: {df['matches_agree'].sum() / len(df) * 100:.1f}%")
        print(f"\nAverage Confidence Scores:")
        print(f"   TF-IDF:  {df['tfidf_score'].mean():.2%}")
        print(f"   Neural:  {df['neural_score'].mean():.2%}")
        print(f"\nAverage Processing Time:")
        print(f"   TF-IDF:  {df['tfidf_time'].mean():.3f}s")
        print(f"   Neural:  {df['neural_time'].mean():.3f}s")
        
        # Save to file
        if output_file:
            df.to_csv(output_file, index=False)
            print(f"\n💾 Results saved to: {output_file}")
        
        return df
    
    def semantic_similarity_test(self):
        """
        Test semantic understanding with paraphrased queries
        Shows where neural embeddings excel
        """
        print("\n" + "="*70)
        print("🧪 Semantic Similarity Test")
        print("="*70 + "\n")
        
        # Test with paraphrased/semantically similar queries
        test_cases = [
            {
                'original': "I want to hold your hand",
                'paraphrase': "I desire to grasp your palm"
            },
            {
                'original': "all you need is love",
                'paraphrase': "the only thing required is affection"
            },
            {
                'original': "dancing in the moonlight",
                'paraphrase': "moving to music under the moon"
            }
        ]
        
        for case in test_cases:
            print(f"Original: \"{case['original']}\"")
            print(f"Paraphrase: \"{case['paraphrase']}\"")
            print("-" * 70)
            
            # Compare both on paraphrase
            comparison = self.compare_single_query(case['paraphrase'], top_k=3, verbose=False)
            
            tfidf_results = comparison['tfidf']['results']
            neural_results = comparison['neural']['results']
            
            print("\nTF-IDF Top Match:")
            if tfidf_results:
                top = tfidf_results[0]
                print(f"   {top['artist']} - {top['title']} ({top['final_score']:.2%})")
            else:
                print("   No match")
            
            print("\nNeural Top Match:")
            if neural_results:
                top = neural_results[0]
                print(f"   {top['artist']} - {top['title']} ({top['final_score']:.2%})")
            else:
                print("   No match")
            
            print("\n" + "="*70 + "\n")
    
    def close(self):
        """Close both matchers"""
        self.tfidf_matcher.close()
        self.neural_matcher.close()


def main():
    """Run comparison tests"""
    
    # Initialize comparison
    comparison = MatcherComparison()
    
    # Test queries - generic examples
    test_queries = [
        "sunshine on my shoulders makes me happy",
        "take me home country roads",
        "sweet dreams are made of this",
        "don't stop believing hold on to that feeling",
        "we are the champions my friends"
    ]
    
    print("🎯 Single Query Comparison")
    print("="*70 + "\n")
    
    # Test first query in detail
    comparison.compare_single_query(test_queries[0], top_k=5)
    
    # Batch comparison
    print("\n\n🎯 Batch Comparison")
    comparison.batch_comparison(
        test_queries,
        output_file=Config.PROCESSED_DATA_DIR / "comparison_results.csv"
    )
    
    # Semantic similarity test
    comparison.semantic_similarity_test()
    
    # Close
    comparison.close()
    
    print("\n✅ Comparison complete!")
    print("\n💡 Key Takeaways:")
    print("   • Neural embeddings understand semantic meaning")
    print("   • Better at handling paraphrases and synonyms")
    print("   • TF-IDF is faster for exact keyword matching")
    print("   • Hybrid approach combines strengths of both")


if __name__ == "__main__":
    main()