import timeit
import sys
from unittest.mock import MagicMock

# Mock PIL for environment
mock_image_module = MagicMock()
sys.modules['PIL'] = MagicMock()
sys.modules['PIL.Image'] = mock_image_module
mock_image_module.Resampling.LANCZOS = 1

def fit_image_original(image, width, height):
    source = image.copy()
    source.thumbnail((width, height), 1) # Use 1 for LANCZOS
    return source

def fit_image_optimized(image, width, height):
    # Calculate aspect ratio
    img_w, img_h = image.size
    ratio = min(width / img_w, height / img_h)

    if ratio >= 1.0:
        return image.copy()

    new_size = (int(img_w * ratio), int(img_h * ratio))
    # resize returns a new image, no copy needed
    return image.resize(new_size, 1)

def benchmark():
    # Simulate large image data copy vs no copy
    # We'll use a large bytearray to represent image data
    data_size = 4000 * 4000 * 4 # 4K RGBA image ~64MB
    data = bytearray(data_size)

    def simulate_original():
        # Copy data
        copy_data = data[:]
        # Simulate thumbnail (some operation on data, but resize is usually what happens)
        # We'll just take a slice to simulate resize
        return copy_data[:data_size // 4]

    def simulate_optimized():
        # No initial copy, just resize (slice)
        return data[:data_size // 4]

    iterations = 100
    timer_orig = timeit.timeit(simulate_original, number=iterations)
    timer_opt = timeit.timeit(simulate_optimized, number=iterations)

    print(f"Simulated Original (with copy): {timer_orig/iterations:.6f}s")
    print(f"Simulated Optimized (no copy): {timer_opt/iterations:.6f}s")
    print(f"Improvement: {(timer_orig - timer_opt) / timer_orig * 100:.2f}%")

    # Verify calls using Mocks
    mock_img = MagicMock()
    mock_img.size = (2000, 1000)

    print("\nVerifying Mock calls for Original:")
    fit_image_original(mock_img, 1000, 500)
    print(f"copy() called: {mock_img.copy.called}")

    mock_img.reset_mock()

    print("\nVerifying Mock calls for Optimized:")
    fit_image_optimized(mock_img, 1000, 500)
    print(f"copy() called: {mock_img.copy.called}")
    print(f"resize() called: {mock_img.resize.called}")

if __name__ == "__main__":
    benchmark()
