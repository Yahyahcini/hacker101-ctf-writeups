# Model E1337 - Rolling Code Lock
# PRNG Solver using Z3
# Usage: python3 solve_prng.py
# Replace code1 and code2 with your two consecutive expected codes from the lab

from z3 import *

# =============================================
# REPLACE THESE WITH YOUR ACTUAL CODES
code1 = 00000000   # First expected code
code2 = 00000000   # Second expected code
# =============================================

def setup(seed):
    state = 0
    for _ in range(16):
        cur = seed & 3
        seed >>= 2
        state = (state << 4) | ((state & 3) ^ cur)
        state |= cur << 2
    return state

seed = BitVec("seed", 32)
solver = Solver()
solver.add(seed >= 0, seed <= 0xFFFFFFFF)

# Symbolic setup
state = 0
seed_copy = seed
for _ in range(16):
    cur = seed_copy & 3
    seed_copy >>= 2
    state = (state << 4) | ((state & 3) ^ cur)
    state |= cur << 2

# First code (26 bits)
val1 = 0
for _ in range(26):
    val1 <<= 1
    val1 |= state & 1
    state = (state << 1) ^ LShR(state, 61)
    state &= 0xFFFFFFFFFFFFFFFF
    state ^= 0xFFFFFFFFFFFFFFFF
    for j in range(0, 64, 4):
        cur = (state >> j) & 0xF
        cur = (LShR(cur, 3)) | ((LShR(cur, 2)) & 2) | ((cur << 3) & 8) | ((cur << 2) & 4)
        state ^= cur << j
solver.add(val1 == code1)

# Second code (26 bits)
val2 = 0
for _ in range(26):
    val2 <<= 1
    val2 |= state & 1
    state = (state << 1) ^ LShR(state, 61)
    state &= 0xFFFFFFFFFFFFFFFF
    state ^= 0xFFFFFFFFFFFFFFFF
    for j in range(0, 64, 4):
        cur = (state >> j) & 0xF
        cur = (LShR(cur, 3)) | ((LShR(cur, 2)) & 2) | ((cur << 3) & 8) | ((cur << 2) & 4)
        state ^= cur << j
solver.add(val2 == code2)

if solver.check() == sat:
    found_seed = solver.model()[seed].as_long()
    print(f"Seed found: {found_seed}")

    # Compute third code (the unlock code)
    state = setup(found_seed)
    for _ in range(2):
        val = 0
        for _ in range(26):
            val <<= 1
            val |= state & 1
            state = (state << 1) ^ (state >> 61)
            state &= 0xFFFFFFFFFFFFFFFF
            state ^= 0xFFFFFFFFFFFFFFFF
            for j in range(0, 64, 4):
                cur = (state >> j) & 0xF
                cur = (cur >> 3) | ((cur >> 2) & 2) | ((cur << 3) & 8) | ((cur << 2) & 4)
                state ^= cur << j

    unlock = 0
    for _ in range(26):
        unlock <<= 1
        unlock |= state & 1
        state = (state << 1) ^ (state >> 61)
        state &= 0xFFFFFFFFFFFFFFFF
        state ^= 0xFFFFFFFFFFFFFFFF
        for j in range(0, 64, 4):
            cur = (state >> j) & 0xF
            cur = (cur >> 3) | ((cur >> 2) & 2) | ((cur << 3) & 8) | ((cur << 2) & 4)
            state ^= cur << j

    print(f"Unlock code: {unlock}")
else:
    print("No seed found — check your codes or restart the instance and get fresh codes")
