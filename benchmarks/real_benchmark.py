import sys
from unittest.mock import MagicMock

# Mock PIL.Image before importing anything that might use it
mock_pil = MagicMock()
sys.modules["PIL"] = mock_pil
sys.modules["PIL.Image"] = mock_pil

import timeit
import random
from utils.validation import build_validation_summary

class MockImage:
    def __init__(self, w, h):
        self.width = w
        self.height = h

def run_benchmark():
    num_images = 100000
    images = [MockImage(random.randint(1, 100), random.randint(1, 100)) for _ in range(num_images)]
    atlas_size = (1024, 1024)
    border = 2
    padding = 2

    def test_func():
        build_validation_summary(images, atlas_size, border, padding)

    # Warmup
    test_func()

    # Benchmark
    iterations = 100
    total_time = timeit.timeit(test_func, number=iterations)
    avg_time = total_time / iterations

    print(f"Average time: {avg_time:.6f} seconds")

if __name__ == "__main__":
    run_benchmark()
