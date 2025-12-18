import os
import random

from primordial_byte.interpreter import BFFState, run
from primordial_byte.metrics import high_order_entropy


def create_soup(n_programs: int, program_size: int = 64) -> list[bytearray]:
    """Create n_programs random programs of program_size bytes each."""
    return [bytearray(os.urandom(program_size)) for _ in range(n_programs)]


def mutate(soup: list[bytearray], mutation_rate: float = 0.00024) -> None:
    """Apply random mutations in-place."""
    if not soup:
        return

    n_programs = len(soup)
    program_size = len(soup[0])
    total_bytes = n_programs * program_size

    # Expected number of mutations per epoch
    n_mutations = int(total_bytes * mutation_rate + 0.5)

    for _ in range(n_mutations):
        prog_idx = random.randint(0, n_programs - 1)
        byte_idx = random.randint(0, program_size - 1)
        soup[prog_idx][byte_idx] = random.randint(0, 255)


def run_epoch(soup: list[bytearray], program_size: int = 64) -> None:
    """Run one epoch: pair programs, execute, split back. Modifies soup in-place."""
    random.shuffle(soup)
    for index in range(0, len(soup), 2):
        invert: bool = random.random() < 0.5
        prog_a = soup[index]
        prog_b = soup[index+1]
        if invert:
            prog = prog_a + prog_b
        else:
            prog = prog_b + prog_a
        state = BFFState(prog, head0=0, head1=0, ip=0)
        run(state)
        first_half = state.tape[:program_size]
        second_half = state.tape[program_size:]
        if invert:  # prog was A+B
            soup[index] = first_half      # modified A
            soup[index+1] = second_half   # modified B
        else:       # prog was B+A
            soup[index] = second_half     # modified A
            soup[index+1] = first_half    # modified B


def run_simulation(
    n_programs: int = 4096,
    program_size: int = 64,
    n_epochs: int = 16000,
    mutation_rate: float = 0.00024,
    measure_every: int = 100,
) -> list[float]:
    """
    Run full simulation. Return list of high-order entropy measurements.
    """
    measurements: list[float] = []
    soup = create_soup(n_programs, program_size=program_size)
    for epoch in range(n_epochs):
        run_epoch(soup, program_size=program_size)
        mutate(soup, mutation_rate=mutation_rate)
        if epoch % measure_every == 0:
            complexity = high_order_entropy(b"".join(soup))
            measurements.append(complexity)
            print(complexity)

    return measurements


def count_replicators(soup: list[bytearray], pattern: bytes) -> int:
    return sum(1 for prog in soup if pattern in bytes(prog))


def run_seeded_simulation(
    n_programs: int = 4096,
    program_size: int = 64,
    n_epochs: int = 16_000,
    mutation_rate: float = 0.00024,
    measure_every: int = 100,
) -> list[float]:
    """Seed soup with one known replicator, see if it takes over."""
    measurements: list[float] = []
    soup = create_soup(n_programs, program_size=program_size)
    replicator_code = b"[[{.>]-]]-]>.{[["  # 16 bytes, no space in middle
    replicator_bytes = replicator_code + bytes(48)  # pad with zeros

    soup[0] = bytearray(replicator_bytes)
    soup[1] = bytearray(replicator_bytes)
    replicator = b"[[{.>]-]]-]>.{[["
    for epoch in range(n_epochs):
        run_epoch(soup, program_size=program_size)
        count = count_replicators(soup, replicator)
        complexity = high_order_entropy(b"".join(soup))
        mutate(soup, mutation_rate=mutation_rate)
        if epoch % measure_every == 0:
            complexity = high_order_entropy(b"".join(soup))
            measurements.append(complexity)
            print(f"epoch={epoch}, complexity={complexity:.3f}, replicators={count}")

    return measurements



def main():
    run_seeded_simulation()


if __name__ == "__main__":
    main()
