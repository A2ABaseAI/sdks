#!/usr/bin/env python3
"""
Run all examples in the examples directory.
"""
import asyncio
import os
import subprocess
import sys
from pathlib import Path

def run_example(example_file: Path, api_key: str):
    """Run a single example file."""
    example_name = example_file.name
    print(f"\n{'='*80}")
    print(f"Running: {example_name}")
    print(f"{'='*80}")
    
    env = os.environ.copy()
    env['BASEAI_API_KEY'] = api_key
    # Add parent directory to PYTHONPATH so we can import a2abase
    pythonpath = env.get('PYTHONPATH', '')
    if pythonpath:
        env['PYTHONPATH'] = f"{str(example_file.parent.parent)}:{pythonpath}"
    else:
        env['PYTHONPATH'] = str(example_file.parent.parent)
    
    try:
        result = subprocess.run(
            [sys.executable, str(example_file)],
            env=env,
            cwd=str(example_file.parent.parent),
            timeout=120,  # 2 minute timeout per example
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print(f"✅ {example_name}: SUCCESS")
            # Show last few lines of output
            if result.stdout:
                lines = result.stdout.strip().split('\n')
                print(f"Output (last 5 lines):")
                for line in lines[-5:]:
                    print(f"  {line}")
        else:
            print(f"❌ {example_name}: FAILED")
            if result.stderr:
                error_lines = result.stderr.strip().split('\n')
                print(f"Error (last 5 lines):")
                for line in error_lines[-5:]:
                    print(f"  {line}")
            elif result.stdout:
                output_lines = result.stdout.strip().split('\n')
                print(f"Output (last 5 lines):")
                for line in output_lines[-5:]:
                    print(f"  {line}")
        
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        print(f"⏱️  {example_name}: TIMEOUT (exceeded 2 minutes)")
        return False
    except Exception as e:
        print(f"❌ {example_name}: ERROR - {e}")
        return False

def main():
    """Run all examples."""
    api_key = os.getenv("BASEAI_API_KEY")
    if not api_key:
        print("❌ BASEAI_API_KEY environment variable not set")
        print("Please set it with: export BASEAI_API_KEY='pk_xxx:sk_xxx'")
        return 1
    
    example_dir = Path(__file__).parent
    examples = sorted([
        f for f in example_dir.glob("*.py")
        if f.name != "__init__.py"
        and f.name != "run_all_examples.py"
        and f.name != "mcp_server.py"
        and f.name != "kv.py"
    ])
    
    print(f"Found {len(examples)} examples to run")
    print(f"API Key: {api_key[:20]}...")
    
    results = {}
    for example_file in examples:
        success = run_example(example_file, api_key)
        results[example_file.name] = success
    
    # Summary
    print(f"\n{'='*80}")
    print("SUMMARY")
    print(f"{'='*80}")
    successful = sum(1 for s in results.values() if s)
    total = len(results)
    print(f"Total: {total}")
    print(f"✅ Successful: {successful}")
    print(f"❌ Failed: {total - successful}")
    
    if successful < total:
        print("\nFailed examples:")
        for name, success in results.items():
            if not success:
                print(f"  ❌ {name}")
    
    return 0 if successful == total else 1

if __name__ == "__main__":
    sys.exit(main())

