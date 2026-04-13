import timeit
import random
from typing import List
from utils.validation import build_validation_summary
from tests.test_utils import MockImage

def run_benchmark():
    # Setup data
    num_images = 100000
    images = [MockImage(random.randint(1, 100), random.randint(1, 100)) for _ in range(num_images)]
    atlas_size = (1024, 1024)
    border = 2
    padding = 2

    # We need to monkeypatch LoadedImage if we want to use the actual build_validation_summary
    # Or just ensure MockImage has width/height properties as expected.

    def test_func():
        build_validation_summary(images, atlas_size, border, padding)

    # Warmup
    test_func()

    # Benchmark
    iterations = 100
    total_time = timeit.timeit(test_func, number=iterations)
    avg_time = total_time / iterations

    print(f"Average time for {num_images} images: {avg_time:.6f} seconds")

if __name__ == "__main__":
    run_benchmark()
