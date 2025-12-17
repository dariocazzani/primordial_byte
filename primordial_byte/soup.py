import os
import random

from primordial_byte.interpreter import BFFState, run
from primordial_byte.metrics import high_order_entropy


def create_soup(n_programs: int, program_size: int = 64) -> list[bytearray]:
    """Create n_programs random programs of program_size bytes each."""
    return [bytearray(os.urandom(program_size)) for _ in range(n_programs)]


# TODO: very inefficient --> speed this up
def mutate(soup: list[bytearray], mutation_rate: float = 0.00024) -> None:
    """Apply random mutations in-place. Default rate is 0.024% per byte per epoch."""
    for program in soup:
        for index in range(len(program)):
            if random.random() < mutation_rate:
                program[index] = random.randint(0, 255)


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


def main():
    run_simulation()


if __name__ == "__main__":
    main()
