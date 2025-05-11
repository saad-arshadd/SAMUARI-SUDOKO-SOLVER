## Solve Every Sudoku Puzzle with OR-Tools

from ortools.sat.python import cp_model


def cross(A, B):
    "Cross product of elements in A and elements in B."
    return [a + b for a in A for b in B]


digits = '123456789'
rows = 'ABCDEFGHI'
cols = digits
squares = cross(rows, cols)
unitlist = ([cross(rows, c) for c in cols] +
            [cross(r, cols) for r in rows] +
            [cross(rs, cs) for rs in ('ABC', 'DEF', 'GHI') for cs in ('123', '456', '789')])
units = dict((s, [u for u in unitlist if s in u])
             for s in squares)
peers = dict((s, set(sum(units[s], [])) - set([s]))
             for s in squares)


################ Unit Tests ################

def test():
    "A set of tests that must pass."
    assert len(squares) == 81
    assert len(unitlist) == 27
    assert all(len(units[s]) == 3 for s in squares)
    assert all(len(peers[s]) == 20 for s in squares)
    assert units['C2'] == [['A2', 'B2', 'C2', 'D2', 'E2', 'F2', 'G2', 'H2', 'I2'],
                           ['C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'C7', 'C8', 'C9'],
                           ['A1', 'A2', 'A3', 'B1', 'B2', 'B3', 'C1', 'C2', 'C3']]
    assert peers['C2'] == set(['A2', 'B2', 'D2', 'E2', 'F2', 'G2', 'H2', 'I2',
                               'C1', 'C3', 'C4', 'C5', 'C6', 'C7', 'C8', 'C9',
                               'A1', 'A3', 'B1', 'B3'])
    print('All tests pass.')


################ Parse a Grid ################

def grid_values(grid):
    "Convert grid into a dict of {square: char} with '0' or '.' for empties."
    chars = [c for c in grid if c in digits or c in '0.']
    assert len(chars) == 81
    return dict(zip(squares, chars))


################ Display as 2-D grid ################

def display(values):
    "Display these values as a 2-D grid."
    width = 1 + max(len(values[s]) for s in squares)
    line = '+'.join(['-' * (width * 3)] * 3)
    for r in rows:
        print(''.join(values[r + c].center(width) + ('|' if c in '36' else '') for c in cols))
        if r in 'CF': print(line)
    print()


################ OR-Tools Solver ################

def solve(grid):
    """Solve the Sudoku puzzle using OR-Tools CP-SAT solver."""
    # Create the model
    model = cp_model.CpModel()

    # Create variables
    cell_vars = {}
    for s in squares:
        cell_vars[s] = model.NewIntVar(1, 9, s)

    # Add constraints
    # 1. AllDifferent for rows, columns, and boxes
    for unit in unitlist:
        model.AddAllDifferent([cell_vars[s] for s in unit])

    # 2. Initial values from the grid
    grid_vals = grid_values(grid)
    for s, val in grid_vals.items():
        if val in digits:
            model.Add(cell_vars[s] == int(val))

    # Solve
    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    # Extract solution if found
    if status in [cp_model.FEASIBLE, cp_model.OPTIMAL]:
        solution = {}
        for s in squares:
            solution[s] = str(solver.Value(cell_vars[s]))
        return solution
    return False


################ System test ################

import time, random


def solve_all(grids, name='', showif=0.0):
    """Attempt to solve a sequence of grids. Report results."""

    def time_solve(grid):
        start = time.time()
        values = solve(grid)
        t = time.time() - start
        if showif is not None and t > showif:
            display(grid_values(grid))
            if values: display(values)
            print('(%.2f seconds)\n' % t)
        return (t, solved(values))

    times, results = zip(*[time_solve(grid) for grid in grids])
    N = len(grids)
    if N > 1:
        print("Solved %d of %d %s puzzles (avg %.2f secs (%d Hz), max %.2f secs)." %
              (sum(results), N, name, sum(times) / N, N / sum(times), max(times)))


def solved(values):
    "A puzzle is solved if each unit is a permutation of the digits 1 to 9."

    def unitsolved(unit): return set(values[s] for s in unit) == set(digits)

    return values is not False and all(unitsolved(unit) for unit in unitlist)


def random_puzzle(N=17):
    """Make a random puzzle with N or more assignments."""
    values = dict((s, digits) for s in squares)
    for s in shuffled(squares):
        if not assign(values, s, random.choice(values[s])):
            break
        ds = [values[s] for s in squares if len(values[s]) == 1]
        if len(ds) >= N and len(set(ds)) >= 8:
            return ''.join(values[s] if len(values[s]) == 1 else '.' for s in squares)
    return random_puzzle(N)


if __name__ == '__main__':
    test()
    solve_all(from_file("easy50.txt", '========'), "easy", None)
    solve_all(from_file("top95.txt"), "hard", None)
    solve_all(from_file("hardest.txt"), "hardest", None)
    solve_all([random_puzzle() for _ in range(99)], "random", 100.0)