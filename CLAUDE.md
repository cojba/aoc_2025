# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is an Advent of Code 2025 solutions repository. Advent of Code (AoC) is an annual programming challenge event with daily puzzles released in December. This repository contains solutions, typically implemented in Python, with a focus on clean, readable code and algorithmic problem-solving.

## Design Philosophy

- Write clear, readable, and well-documented solutions
- Prioritize correctness first, then optimize for performance
- Include explanation comments for complex algorithms
- Provide test cases with example inputs
- Document time and space complexity for algorithms
- Each day's solution should be self-contained and runnable

## Repository Structure

Recommended structure for organizing solutions:

```
aoc_2025/
├── day01/
│   ├── solution.py       # Main solution code
│   ├── input.txt         # Puzzle input
│   ├── example.txt       # Example input from problem description
│   ├── test_solution.py  # Unit tests (optional)
│   └── README.md         # Problem description and notes (optional)
├── day02/
│   ├── solution.py
│   ├── input.txt
│   └── ...
├── utils/                # Shared utilities
│   ├── __init__.py
│   ├── input_parser.py   # Common input parsing functions
│   └── algorithms.py     # Reusable algorithms (BFS, DFS, etc.)
├── requirements.txt      # Python dependencies
├── .gitignore           # Ignore input files if desired
└── README.md            # Repository overview
```

## Coding Standards

### Solution Structure

Each solution should follow this template:

```python
"""
Advent of Code 2025 - Day X: [Problem Title]

Problem description:
[Brief description of the problem]

Solution approach:
[Explanation of the algorithm/approach used]

Time complexity: O(?)
Space complexity: O(?)
"""

def parse_input(filename: str) -> list:
    """Parse the input file and return structured data."""
    with open(filename) as f:
        # Parse and return data
        pass

def part1(data: list) -> int:
    """Solve part 1 of the puzzle."""
    # Solution for part 1
    pass

def part2(data: list) -> int:
    """Solve part 2 of the puzzle."""
    # Solution for part 2
    pass

def main():
    """Run the solution with puzzle input."""
    # Test with example input
    example_data = parse_input("example.txt")
    print(f"Part 1 (example): {part1(example_data)}")
    print(f"Part 2 (example): {part2(example_data)}")
    
    # Run with actual input
    data = parse_input("input.txt")
    print(f"Part 1: {part1(data)}")
    print(f"Part 2: {part2(data)}")

if __name__ == "__main__":
    main()
```

### Python Style Guidelines

1. **Type Hints**
   - Use type hints for function parameters and return values
   - Use `list`, `dict`, `set`, `tuple` from built-in types (Python 3.9+)
   - For complex types, import from `typing`: `Optional`, `Union`, `Callable`

2. **Naming Conventions**
   - Use `snake_case` for functions and variables
   - Use `UPPER_CASE` for constants
   - Use descriptive names that explain intent
   - Avoid single-letter names except for loop indices

3. **Documentation**
   - Include module-level docstring with problem description
   - Document complex algorithms with comments
   - Explain non-obvious logic
   - Include examples in docstrings for utility functions

4. **Code Organization**
   - Keep functions small and focused (one responsibility)
   - Extract reusable logic into utility functions
   - Separate parsing from solving
   - Group related helper functions together

### Algorithm Documentation

For each solution, document:
- **Approach**: High-level strategy
- **Algorithm**: Specific technique used (BFS, DP, greedy, etc.)
- **Time complexity**: Big-O notation
- **Space complexity**: Big-O notation
- **Edge cases**: Special cases handled

Example:
```python
"""
Approach: Use dynamic programming to find shortest path
Algorithm: Dijkstra with priority queue
Time complexity: O(V + E log V) where V=vertices, E=edges
Space complexity: O(V) for distance and visited arrays
Edge cases: Disconnected graphs, negative weights
"""
```

## Common Patterns

### Input Parsing

```python
# Read all lines
def read_lines(filename: str) -> list[str]:
    with open(filename) as f:
        return [line.strip() for line in f]

# Read as integers
def read_ints(filename: str) -> list[int]:
    with open(filename) as f:
        return [int(line.strip()) for line in f]

# Read as grid
def read_grid(filename: str) -> list[list[str]]:
    with open(filename) as f:
        return [list(line.strip()) for line in f]

# Read comma-separated values
def read_csv(filename: str) -> list[int]:
    with open(filename) as f:
        return [int(x) for x in f.read().strip().split(",")]
```

### Common Algorithms

Maintain reusable algorithms in `utils/algorithms.py`:

```python
# BFS template
def bfs(start, goal, get_neighbors):
    from collections import deque
    queue = deque([start])
    visited = {start}
    
    while queue:
        current = queue.popleft()
        if current == goal:
            return True
        
        for neighbor in get_neighbors(current):
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)
    return False

# DFS template
def dfs(node, visited, get_neighbors):
    visited.add(node)
    for neighbor in get_neighbors(node):
        if neighbor not in visited:
            dfs(neighbor, visited, get_neighbors)

# Grid directions (4-way)
DIRECTIONS_4 = [(0, 1), (1, 0), (0, -1), (-1, 0)]

# Grid directions (8-way)
DIRECTIONS_8 = [
    (-1, -1), (-1, 0), (-1, 1),
    (0, -1),           (0, 1),
    (1, -1),  (1, 0),  (1, 1)
]
```

### Testing

Include test cases with example inputs:

```python
def test_part1():
    example_data = parse_input("example.txt")
    assert part1(example_data) == 42, "Part 1 failed on example"

def test_part2():
    example_data = parse_input("example.txt")
    assert part2(example_data) == 123, "Part 2 failed on example"

if __name__ == "__main__":
    test_part1()
    test_part2()
    main()
```

## Development Workflow

### Starting a New Day

1. **Create directory structure**
   ```bash
   mkdir -p dayXX
   cd dayXX
   ```

2. **Create solution file from template**
   ```bash
   cp ../template.py solution.py
   ```

3. **Add input files**
   - Download puzzle input to `input.txt`
   - Copy example from problem to `example.txt`

4. **Implement solution**
   - Start with `parse_input()` to handle input format
   - Implement `part1()` first
   - Test with example input
   - Run with actual input
   - Implement `part2()` (often builds on part 1)

5. **Verify and optimize**
   - Check correctness with examples
   - Analyze time/space complexity
   - Optimize if needed (but don't over-optimize)

### Testing Approach

- **Test with examples first**: Always verify solution works with provided examples
- **Edge cases**: Consider empty inputs, single elements, maximum values
- **Incremental development**: Test each function independently
- **Print debug info**: Use print statements liberally during development
- **Verify results**: Double-check answer before submitting to AoC website

### Version Control

When committing solutions:

```bash
# Commit pattern for each day
git add dayXX/
git commit -m "Add solution for Day XX: [Problem Title]

Part 1: [Brief description of approach]
Part 2: [Brief description of approach]

Time complexity: O(?)
Space complexity: O(?)"
```

**What to commit**:
- ✅ Solution code (`solution.py`)
- ✅ Example inputs (`example.txt`)
- ✅ Tests if created
- ✅ Utility functions
- ⚠️  Puzzle inputs (`input.txt`) - optional, AoC discourages sharing

**Git ignore recommendations**:
```gitignore
# Python
__pycache__/
*.pyc
.pytest_cache/

# Optional: Personal puzzle inputs
# input.txt

# IDE
.vscode/
.idea/
*.swp
```

## Optimization Tips

### When to Optimize

1. **Don't optimize prematurely**: Get working solution first
2. **Measure before optimizing**: Use `time` or `cProfile`
3. **Optimize bottlenecks only**: Focus on the slowest parts
4. **Know your data structures**: Choose appropriate collections

### Common Optimizations

**Use appropriate data structures**:
- `set` for membership testing (O(1) vs O(n) for list)
- `deque` for queue operations (O(1) vs O(n) for list)
- `dict` for lookups and counting
- `heapq` for priority queues

**Memoization**:
```python
from functools import lru_cache

@lru_cache(maxsize=None)
def expensive_function(n):
    # Recursive or expensive computation
    pass
```

**Generator expressions** for memory efficiency:
```python
# Instead of: sum([x**2 for x in range(1000000)])
result = sum(x**2 for x in range(1000000))
```

**NumPy** for numerical operations on large datasets:
```python
import numpy as np
# Fast array operations
arr = np.array(data)
result = np.sum(arr)
```

## Debugging Strategies

### Print Debugging
```python
# Visualize grids
def print_grid(grid):
    for row in grid:
        print("".join(row))

# Debug state
def debug_state(step, value):
    print(f"Step {step}: {value}")
    
# Trace execution
import sys
print(..., file=sys.stderr)  # Won't interfere with output parsing
```

### Interactive Debugging
```python
# Insert breakpoint
import pdb; pdb.set_trace()

# Or use Python 3.7+ built-in
breakpoint()
```

### Assertion Checking
```python
# Verify invariants
assert len(data) > 0, "Input cannot be empty"
assert all(x >= 0 for x in values), "All values must be non-negative"
```

## Common Pitfalls

1. **Off-by-one errors**: Carefully check loop bounds and indices
2. **Integer overflow**: Python handles big integers, but be aware in other languages
3. **Mutating shared state**: Be careful with default mutable arguments
4. **String concatenation**: Use `"".join()` for building large strings
5. **Floating point precision**: Use `math.isclose()` for comparisons
6. **Deep vs shallow copy**: Use `copy.deepcopy()` when needed
7. **Grid indexing**: Remember `grid[row][col]` vs `grid[y][x]`

## Quick Reference

### Useful Python Libraries
```python
# Standard library
import re                 # Regular expressions
import math              # Mathematical functions
import itertools         # Combinatorial generators
import collections       # deque, Counter, defaultdict
import heapq             # Priority queue
import functools         # lru_cache, reduce
from typing import *     # Type hints

# Optional external
import numpy as np       # Numerical computing
import networkx as nx    # Graph algorithms
```

### Running Solutions
```bash
# Run solution for specific day
cd dayXX
python solution.py

# Run with timing
time python solution.py

# Profile performance
python -m cProfile -s cumtime solution.py
```

## Additional Resources

- **Advent of Code**: https://adventofcode.com/
- **Python Docs**: https://docs.python.org/3/
- **Algorithm Visualizations**: https://visualgo.net/
- **Big-O Cheat Sheet**: https://www.bigocheatsheet.com/
