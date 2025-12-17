from dataclasses import dataclass

from rich.console import Console
from rich.text import Text

console = Console()


@dataclass
class BFFState:
    tape: bytearray
    head0: int
    head1: int
    ip: int


@dataclass
class Instructions:
    head0_left: int
    head0_right: int
    head1_left: int
    head1_right: int
    incr: int
    decr: int
    copy_head0: int
    copy_head1: int
    jump_fwd: int
    jump_back: int


INSTR = Instructions(
    head0_left=ord('<'),
    head0_right=ord('>'),
    head1_left=ord('{'),
    head1_right=ord('}'),
    incr=ord('+'),
    decr=ord('-'),
    copy_head0=ord('.'),
    copy_head1=ord(','),
    jump_fwd=ord('['),
    jump_back=ord(']')
)


PROGRAM_LENGTH: int = 64


def print_state(state: BFFState) -> None:
    # Build tape display
    tape_text = Text()
    for i, byte in enumerate(state.tape):
        char = chr(byte) if 32 <= byte < 127 else '·'

        style = ""
        if i == state.ip:
            style = "bold white on green"
        elif i == state.head0 and i == state.head1:
            style = "bold white on magenta"
        elif i == state.head0:
            style = "bold white on blue"
        elif i == state.head1:
            style = "bold white on red"

        tape_text.append(f" {char} ", style=style)

    console.print(tape_text)
    console.print(
        f"[green]IP={state.ip}[/green]  "
        f"[blue]head0={state.head0}[/blue]  "
        f"[red]head1={state.head1}[/red]"
    )
    console.print()


def create_state(program: bytes) -> BFFState:
    return BFFState(tape = bytearray(program), head0=0, head1=0, ip=0)


def find_matching_bracket(tape: bytearray, pos: int, direction: int) -> int | None:
    """
    Find the matching bracket starting from pos, searching in direction.
    direction: +1 for forward, -1 for backward
    Returns the index of the matching bracket, or None if not found.
    """
    counter: int = 0
    cur_instr: int = tape[pos]
    matching_instr: int = INSTR.jump_back if cur_instr == INSTR.jump_fwd else INSTR.jump_fwd
    pos += direction
    while pos < len(tape) and pos >= 0:
        if tape[pos] == cur_instr:
            counter += 1
        elif tape[pos] == matching_instr:
            if counter == 0:
                return pos
            else:
                counter -= 1
        pos += direction

    return None


def step(state: BFFState) -> bool:
    """Execute one instruction. Return False if execution should stop."""
    if state.ip < 0 or state.ip >= len(state.tape):
        return False
    instruction: int = state.tape[state.ip]
    match instruction:
        case INSTR.head0_left:
            state.head0 = (state.head0 - 1) % len(state.tape)
            state.ip += 1
        case INSTR.head0_right:
            state.head0 = (state.head0 + 1) % len(state.tape)
            state.ip += 1
        case INSTR.head1_left:
            state.head1 = (state.head1 - 1) % len(state.tape)
            state.ip += 1
        case INSTR.head1_right:
            state.head1 = (state.head1 + 1) % len(state.tape)
            state.ip += 1
        case INSTR.decr:
            state.tape[state.head0] = (state.tape[state.head0] - 1) % 256
            state.ip += 1
        case INSTR.incr:
            state.tape[state.head0] = (state.tape[state.head0] + 1) % 256
            state.ip += 1
        case INSTR.copy_head0:
            state.tape[state.head1] = state.tape[state.head0]
            state.ip += 1
        case INSTR.copy_head1:
            state.tape[state.head0] = state.tape[state.head1]
            state.ip += 1
        case INSTR.jump_fwd:
            if state.tape[state.head0] == 0:
                next_pos: int | None = find_matching_bracket(state.tape, state.ip, direction=1)
                if next_pos is None:
                    return False
                state.ip = next_pos
            state.ip += 1
        case INSTR.jump_back:
            if state.tape[state.head0] != 0:
                next_pos: int | None = find_matching_bracket(state.tape, state.ip, direction=-1)
                if next_pos is None:
                    return False
                state.ip = next_pos
            state.ip += 1
        case _:
            state.ip += 1
    return True


def run(state: BFFState, max_steps: int = 8192) -> int:
    """Run until termination. Return number of steps executed."""
    num_steps: int = 0
    while step(state):
        num_steps += 1
        if num_steps >= max_steps:
            break
    return num_steps


def main():
    program = bytearray([
        ord('['), ord('-'), ord(']'),  # code at positions 0,1,2
        2,                              # data at position 3
        0, 0, 0, 0                      # padding
    ])
    state = BFFState(tape=program, head0=3, head1=0, ip=0)

    steps = run(state)
    print(f"{steps=}")

    program_copy = bytearray([
        ord('#'), ord('.'), ord('*'), ord('3')
    ])
    state = BFFState(tape=program_copy, head0=2, head1=0, ip=0)
    print_state(state)
    run(state)
    print_state(state)


if __name__ == "__main__":
    main()
