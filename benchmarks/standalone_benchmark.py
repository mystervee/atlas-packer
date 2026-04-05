import timeit
import random

def build_validation_summary_original(
    images,
    atlas_size,
    border,
    padding,
):
    width, height = atlas_size
    atlas_area = width * height
    count = len(images)
    total_area = sum(img.width * img.height for img in images)

    if count > 0:
        total_area += border * 2 * (width + height)
        total_area += padding * max(0, count - 1) * min(width, height)

    fill = (total_area / atlas_area * 100.0) if atlas_area > 0 else 0.0

    warnings = []
    if fill > 100:
        warnings.append("Estimated usage exceeds atlas area. Packing will likely fail.")
    if images and max(i.width for i in images) > width - (2 * border):
        warnings.append("At least one image is wider than available atlas width.")
    if images and max(i.height for i in images) > height - (2 * border):
        warnings.append("At least one image is taller than available atlas height.")

    return total_area, fill, warnings

def build_validation_summary_optimized(
    images,
    atlas_size,
    border,
    padding,
):
    width, height = atlas_size
    atlas_area = width * height
    count = len(images)

    total_area = 0
    max_w = 0
    max_h = 0
    for img in images:
        w = img.width
        h = img.height
        total_area += w * h
        if w > max_w:
            max_w = w
        if h > max_h:
            max_h = h

    if count > 0:
        total_area += border * 2 * (width + height)
        total_area += padding * (count - 1 if count > 1 else 0) * min(width, height)

    fill = (total_area / atlas_area * 100.0) if atlas_area > 0 else 0.0

    warnings = []
    if fill > 100:
        warnings.append("Estimated usage exceeds atlas area. Packing will likely fail.")
    if count > 0 and max_w > width - (2 * border):
        warnings.append("At least one image is wider than available atlas width.")
    if count > 0 and max_h > height - (2 * border):
        warnings.append("At least one image is taller than available atlas height.")

    return total_area, fill, warnings

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

    # Verify correctness
    res_orig = build_validation_summary_original(images, atlas_size, border, padding)
    res_opt = build_validation_summary_optimized(images, atlas_size, border, padding)
    assert res_orig == res_opt, f"Results differ: {res_orig} vs {res_opt}"

    # Benchmark original
    iterations = 100
    timer_orig = timeit.timeit(lambda: build_validation_summary_original(images, atlas_size, border, padding), number=iterations)
    avg_orig = timer_orig / iterations

    # Benchmark optimized
    timer_opt = timeit.timeit(lambda: build_validation_summary_optimized(images, atlas_size, border, padding), number=iterations)
    avg_opt = timer_opt / iterations

    print(f"Original: {avg_orig:.6f}s")
    print(f"Optimized: {avg_opt:.6f}s")
    print(f"Improvement: {(avg_orig - avg_opt) / avg_orig * 100:.2f}%")

if __name__ == "__main__":
    run_benchmark()
