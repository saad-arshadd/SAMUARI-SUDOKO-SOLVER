## Solve Samurai Sudoku with OR-Tools

import os
from checker import checker
from ortools.sat.python import cp_model


def cross(A, B, c=''):
    "Cross product of elements in A and elements in B."
    return [a + b + c for a in A for b in B]


digits = '123456789'
rows = 'ABCDEFGHI'
cols = digits

# Define all squares and units for each sudoku grid
id_var = 'a'  # top left
square_a = cross(rows, cols, id_var)
unitlist_a = ([cross(rows, c, id_var) for c in cols] +
              [cross(r, cols, id_var) for r in rows] +
              [cross(rs, cs, id_var) for rs in ('ABC', 'DEF', 'GHI') for cs in ('123', '456', '789')])

id_var = 'b'  # top right
square_b = cross(rows, cols, id_var)
unitlist_b = ([cross(rows, c, id_var) for c in cols] +
              [cross(r, cols, id_var) for r in rows] +
              [cross(rs, cs, id_var) for rs in ('ABC', 'DEF', 'GHI') for cs in ('123', '456', '789')])

id_var = 'c'  # bottom left
square_c = cross(rows, cols, id_var)
unitlist_c = ([cross(rows, c, id_var) for c in cols] +
              [cross(r, cols, id_var) for r in rows] +
              [cross(rs, cs, id_var) for rs in ('ABC', 'DEF', 'GHI') for cs in ('123', '456', '789')])

id_var = 'd'  # bottom right
square_d = cross(rows, cols, id_var)
unitlist_d = ([cross(rows, c, id_var) for c in cols] +
              [cross(r, cols, id_var) for r in rows] +
              [cross(rs, cs, id_var) for rs in ('ABC', 'DEF', 'GHI') for cs in ('123', '456', '789')])


def repl(c):
    a = b = 0
    s = ""
    if c[0] in 'ABCGHI' and c[1] in '123789':
        if c[0] in 'ABC':
            s += chr(ord(c[0]) + 6)
            a = 1
        elif c[0] in 'GHI':
            s += chr(ord(c[0]) - 6)
            a = 2
        if c[1] in '123':
            s += chr(ord(c[1]) + 6)
            b = 1
        elif c[1] in '789':
            s += chr(ord(c[1]) - 6)
            b = 2
    else:
        return c
    if a == 1 and b == 1:
        s += 'a'
    elif a == 1 and b == 2:
        s += 'b'
    elif a == 2 and b == 1:
        s += 'c'
    elif a == 2 and b == 2:
        s += 'd'
    return s


id_var = '+'
square_mid = [repl(x) for x in cross(rows, cols, id_var)]
unitlist_mid = ([square_mid[x * 9:x * 9 + 9] for x in range(0, 9)] +
                [square_mid[x::9] for x in range(0, 9)] +
                [cross(rs, cs, id_var) for rs in ('ABC', 'DEF', 'GHI')
                 for cs in ('123', '456', '789')
                 if not (rs in 'ABCGHI' and cs in '123789')])

all_squares = set(square_a + square_b + square_c + square_d + square_mid)
all_unitlists = unitlist_a + unitlist_b + unitlist_c + unitlist_d + unitlist_mid


def grid_values(grid):
    "Convert grid into a dict of {square: char} with '0' or '.' for empties."
    a = [x[:9] for x in grid[:9]]
    b = [x[12:] for x in grid[:9]]
    c = [x[:9] for x in grid[12:]]
    d = [x[12:] for x in grid[12:]]
    mid = [x[6:15] for x in grid[6:15]]

    chars = ([item for sublist in a for item in sublist] +
             [item for sublist in b for item in sublist] +
             [item for sublist in c for item in sublist] +
             [item for sublist in d for item in sublist] +
             [item for sublist in mid for item in sublist])

    sqrs = square_a + square_b + square_c + square_d + square_mid
    assert len(chars) == 405
    return dict(zip(sqrs, chars))


def solve(grid):
    """Solve the Samurai Sudoku using OR-Tools CP-SAT solver."""
    model = cp_model.CpModel()

    # Create variables
    cell_vars = {}
    for s in all_squares:
        cell_vars[s] = model.NewIntVar(1, 9, s)

    # Add constraints for all units
    for unit in all_unitlists:
        model.AddAllDifferent([cell_vars[s] for s in unit])

    # Add initial values from the grid
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
        for s in all_squares:
            solution[s] = str(solver.Value(cell_vars[s]))
        return solution
    return False


def display(values, sqr):
    """Display sudoku in a 2-D grid."""
    if not values:
        print("No solution to display")
        return

    width = 1 + max(len(values[s]) for s in sqr)
    line = '+'.join(['-' * (width * 3)] * 3)
    for r in rows:
        print(''.join(values[sqr[(ord(r) - 65) * 9 + int(c) - 1]]
                      .center(width) + ('|' if c in '36' else '') for c in cols))
        if r in 'CF': print(line)
    print()


def display_samurai(vals):
    """Print all five sudoku grids."""
    if not vals:
        print("Solution not found, please check if test is valid.")
        return
    print("Top left:")
    display(vals, square_a)
    print("Top right:")
    display(vals, square_b)
    print("Bottom left:")
    display(vals, square_c)
    print("Bottom right:")
    display(vals, square_d)
    print("Middle:")
    display(vals, square_mid)
    checker(vals, [square_a, square_b, square_c, square_d, square_mid])


if __name__ == '__main__':
    while True:
        try:
            txt = input("Insert file path containing the Samurai Sudoku: ")
            with open(txt, 'r') as f:
                samurai_grid = [line.strip() for line in f if line.strip()]
                break
        except FileNotFoundError:
            print(f"File not found: {txt}")
            print("Example test cases can be found in the 'tests' directory")

    ans = solve(samurai_grid)
    display_samurai(ans)