import math
import os
from collections import Counter

from brotli import compress


def shannon_entropy(data: bytes) -> float:
    """Compute Shannon entropy in bits per byte."""
    if len(data) == 0:
        return 0.0
    bytes_count = Counter(data)
    probabilities: list[float] = [count / len(data) for count in bytes_count.values()]
    entropy: float = -sum(prob * math.log2(prob) for prob in probabilities)
    return entropy


def high_order_entropy(data: bytes) -> float:
    """
    Compute high-order entropy: Shannon entropy minus normalized Kolmogorov complexity.
    Uses brotli compression as an approximation for Kolmogorov complexity.
    """
    shortest_program = len(compress(data, quality=11)) # see paper
    normalized_kolmogorov = shortest_program / len(data) * 8
    return shannon_entropy(data) - normalized_kolmogorov


def main():
    # Truly random data
    random_data = os.urandom(1024)

    # Structured repetition
    repetitive_data = b"ABCD" * 256

    print(f"Random:     {high_order_entropy(random_data):.3f}")
    print(f"Repetitive: {high_order_entropy(repetitive_data):.3f}")


if __name__ == "__main__":
    main()
