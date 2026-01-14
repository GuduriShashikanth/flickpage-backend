"""
Memory usage checker for CineLibre backend
Helps verify we stay under 512MB RAM limit
"""
import psutil
import os
import sys

def get_process_memory():
    """Get current process memory usage in MB"""
    process = psutil.Process(os.getpid())
    mem_info = process.memory_info()
    return mem_info.rss / 1024 / 1024  # Convert to MB

def check_system_memory():
    """Check system memory availability"""
    mem = psutil.virtual_memory()
    print("=" * 60)
    print("System Memory Status")
    print("=" * 60)
    print(f"Total RAM: {mem.total / 1024 / 1024:.0f} MB")
    print(f"Available: {mem.available / 1024 / 1024:.0f} MB")
    print(f"Used: {mem.used / 1024 / 1024:.0f} MB ({mem.percent}%)")
    print(f"Free: {mem.free / 1024 / 1024:.0f} MB")
    print()

def test_model_loading():
    """Test memory usage when loading the ML model"""
    print("=" * 60)
    print("Testing Model Loading Memory Impact")
    print("=" * 60)
    
    # Baseline
    baseline = get_process_memory()
    print(f"Baseline (Python + imports): {baseline:.1f} MB")
    
    # Set memory limits
    os.environ["OMP_NUM_THREADS"] = "1"
    os.environ["MKL_NUM_THREADS"] = "1"
    os.environ["ONNXRUNTIME_ENABLE_TELEMETRY"] = "0"
    
    # Load FastEmbed
    print("\nLoading FastEmbed model...")
    try:
        from fastembed import TextEmbedding
        model = TextEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2")
        after_model = get_process_memory()
        model_size = after_model - baseline
        print(f"After model load: {after_model:.1f} MB")
        print(f"Model size: {model_size:.1f} MB")
        
        # Test embedding generation
        print("\nGenerating test embedding...")
        list(model.embed(["test query"]))
        after_embed = get_process_memory()
        embed_overhead = after_embed - after_model
        print(f"After embedding: {after_embed:.1f} MB")
        print(f"Embedding overhead: {embed_overhead:.1f} MB")
        
        # Total
        total = after_embed
        print(f"\n{'=' * 60}")
        print(f"TOTAL MEMORY USAGE: {total:.1f} MB")
        print(f"{'=' * 60}")
        
        # Check against limit
        KOYEB_LIMIT = 512
        remaining = KOYEB_LIMIT - total
        print(f"\nKoyeb Nano Limit: {KOYEB_LIMIT} MB")
        print(f"Remaining headroom: {remaining:.1f} MB ({remaining/KOYEB_LIMIT*100:.1f}%)")
        
        if remaining < 100:
            print("\n⚠️  WARNING: Less than 100MB headroom!")
            print("Consider further optimizations.")
        elif remaining < 200:
            print("\n✅ Acceptable headroom for production")
        else:
            print("\n✅ Excellent headroom for production")
        
        return total
        
    except Exception as e:
        print(f"❌ Error loading model: {e}")
        return None

def main():
    check_system_memory()
    total = test_model_loading()
    
    if total and total > 512:
        print("\n❌ CRITICAL: Memory usage exceeds 512MB limit!")
        print("This will cause crashes on Koyeb Nano instances.")
        sys.exit(1)
    else:
        print("\n✅ Memory usage is within acceptable limits")

if __name__ == "__main__":
    main()
