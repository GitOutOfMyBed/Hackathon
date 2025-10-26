"""
Verification script to confirm we're using REAL data, not fake samples.
"""
import json
import os


def verify_fever_data():
    """Check if FEVER data is real or synthetic"""
    print("="*70)
    print("VERIFYING FEVER DATA")
    print("="*70)
    
    filepath = 'datasets/fever/train.jsonl'
    if not os.path.exists(filepath):
        print(f"\n✗ ERROR: {filepath} not found!")
        return False
    
    # Check file size
    file_size = os.path.getsize(filepath)
    print(f"\nFile size: {file_size:,} bytes ({file_size / 1024 / 1024:.1f} MB)")
    
    if file_size < 1_000_000:  # Less than 1 MB is suspicious
        print("  ⚠️  WARNING: File is very small - likely synthetic data")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        first_line = f.readline()
        data = json.loads(first_line)
    
    # Check for signs of REAL FEVER data
    checks = {
        'Has claim field': 'claim' in data,
        'Has label field': 'label' in data,
        'Has evidence field': 'evidence' in data,
        'Has id field': 'id' in data,
        'ID is numeric': isinstance(data.get('id'), int),
    }
    
    print("\nFEVER Data Checks:")
    for check, passed in checks.items():
        status = "✓" if passed else "✗"
        print(f"  {status} {check}")
    
    # Check if evidence has proper structure
    evidence = data.get('evidence', [])
    if evidence and len(evidence) > 0:
        first_ev = evidence[0]
        print(f"\n  Evidence structure: {type(first_ev)}")
        print(f"  Evidence sample: {str(evidence)[:100]}...")
    
    # Print first claim to verify it's real
    claim = data.get('claim', 'N/A')
    print(f"\n  First claim: {claim}")
    
    # RED FLAG CHECK: If claim is one of our known synthetic samples
    synthetic_claims = [
        "The Earth is flat and not spherical",
        "The Great Wall of China is visible from the Moon",
        "Water boils at 50 degrees Celsius"
    ]
    
    is_synthetic = any(syn in claim for syn in synthetic_claims)
    
    if is_synthetic:
        print("\n  ✗ WARNING: This looks like SYNTHETIC data!")
        print("  ✗ You're still using the sample data generator!")
        return False
    else:
        print("\n  ✓ This appears to be REAL FEVER data")
        return True


def verify_squad_data():
    """Check if SQuAD data is real or synthetic"""
    print("\n" + "="*70)
    print("VERIFYING SQUAD DATA")
    print("="*70)
    
    filepath = 'datasets/squad/train.jsonl'
    if not os.path.exists(filepath):
        print(f"\n✗ ERROR: {filepath} not found!")
        return False
    
    # Check file size
    file_size = os.path.getsize(filepath)
    print(f"\nFile size: {file_size:,} bytes ({file_size / 1024 / 1024:.1f} MB)")
    
    if file_size < 1_000_000:  # Less than 1 MB is suspicious
        print("  ⚠️  WARNING: File is very small - likely synthetic data")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        first_line = f.readline()
        data = json.loads(first_line)
    
    checks = {
        'Has question field': 'question' in data,
        'Has answers field': 'answers' in data,
        'Has context field': 'context' in data,
        'Has title field': 'title' in data,
        'Context is long': len(data.get('context', '')) > 100,
    }
    
    print("\nSQuAD Data Checks:")
    for check, passed in checks.items():
        status = "✓" if passed else "✗"
        print(f"  {status} {check}")
    
    # Print sample
    question = data.get('question', 'N/A')
    answers = data.get('answers', [])
    if isinstance(answers, list) and len(answers) > 0:
        answer = answers[0].get('text', 'N/A')
    else:
        answer = 'N/A'
    context = data.get('context', 'N/A')
    
    print(f"\n  Question: {question}")
    print(f"  Answer: {answer}")
    print(f"  Context preview: {context[:80]}...")
    
    # RED FLAG CHECK: If question is one of our known synthetic samples
    synthetic_questions = [
        "What is the capital of the United Kingdom?",
        "Where was Albert Einstein born?",
        "How many planets are in the Solar System?"
    ]
    
    is_synthetic = any(syn in question for syn in synthetic_questions)
    
    if is_synthetic:
        print("\n  ✗ WARNING: This looks like SYNTHETIC data!")
        print("  ✗ You're still using the sample data generator!")
        return False
    else:
        print("\n  ✓ This appears to be REAL SQuAD data")
        return True


def verify_benchmark_output():
    """Check if generated scenarios use real data"""
    print("\n" + "="*70)
    print("VERIFYING BENCHMARK OUTPUT")
    print("="*70)
    
    filepath = 'outputs/benchmark_data.jsonl'
    if not os.path.exists(filepath):
        print(f"\n✗ ERROR: {filepath} not found!")
        print("  Run 'python main.py' first to generate the benchmark")
        return False
    
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = [f.readline() for _ in range(5)]
    
    scenarios = [json.loads(line) for line in lines if line.strip()]
    
    fever_scenarios = [s for s in scenarios if s.get('source_dataset') == 'fever']
    
    if fever_scenarios:
        sample = fever_scenarios[0]
        print(f"\nSample FEVER scenario:")
        print(f"  Utterance: {sample.get('utterance', 'N/A')}")
        print(f"  Ground truth: {sample.get('ground_truth', 'N/A')}")
        print(f"  Evidence: {str(sample.get('evidence_sentences', []))[:100]}...")
        
        # Check if ground truth is a placeholder
        gt = sample.get('ground_truth', '')
        if 'See Wikipedia:' in gt and len(gt) < 50:
            print("\n  ⚠️  WARNING: Ground truth looks like a placeholder!")
            print("  ⚠️  Evidence not properly extracted from FEVER!")
            return False
    
    print("\n  ✓ Output format looks correct")
    return True


def count_lines(filepath):
    """Count lines in a file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return sum(1 for _ in f)
    except:
        return 0


if __name__ == "__main__":
    print("\n" + "="*70)
    print("DATA VERIFICATION SCRIPT")
    print("Checking if you're using REAL datasets or fake samples")
    print("="*70 + "\n")
    
    fever_ok = verify_fever_data()
    squad_ok = verify_squad_data()
    output_ok = verify_benchmark_output()
    
    print("\n" + "="*70)
    print("DATASET SIZE CHECK")
    print("="*70)
    
    fever_lines = count_lines('datasets/fever/train.jsonl')
    squad_lines = count_lines('datasets/squad/train.jsonl')
    
    print(f"\nFEVER dataset: {fever_lines:,} examples")
    if fever_lines < 1000:
        print("  ⚠️  WARNING: Too few examples - likely synthetic")
    else:
        print("  ✓ Sufficient data")
    
    print(f"\nSQuAD dataset: {squad_lines:,} examples")
    if squad_lines < 1000:
        print("  ⚠️  WARNING: Too few examples - likely synthetic")
    else:
        print("  ✓ Sufficient data")
    
    print("\n" + "="*70)
    print("FINAL VERDICT")
    print("="*70)
    
    if fever_ok and squad_ok and output_ok and fever_lines >= 1000 and squad_lines >= 1000:
        print("\n✓ SUCCESS: Using REAL FEVER and SQuAD datasets")
        print("✓ Benchmark data is legitimate and verified")
        print(f"✓ FEVER: {fever_lines:,} examples")
        print(f"✓ SQuAD: {squad_lines:,} examples")
    else:
        print("\n✗ FAILURE: Still using synthetic/sample data")
        print("✗ Follow the correction instructions to fix this")
        print("\nIssues found:")
        if not fever_ok:
            print("  - FEVER data appears synthetic")
        if not squad_ok:
            print("  - SQuAD data appears synthetic")
        if not output_ok:
            print("  - Benchmark output has issues")
        if fever_lines < 1000:
            print(f"  - FEVER has only {fever_lines} examples (need 1000+)")
        if squad_lines < 1000:
            print(f"  - SQuAD has only {squad_lines} examples (need 1000+)")
    
    print("="*70 + "\n")
