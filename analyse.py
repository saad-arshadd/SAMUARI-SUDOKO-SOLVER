import samurai
import math
import csv
import time
import random
from collections import Counter
from ortools.sat.python import cp_model
import sys
import threading

# Import the required components from samurai
from samurai import cross, digits, rows, cols, square_a, square_b, square_c, square_d, square_mid, all_squares, \
    all_unitlists, grid_values

# Define squares for standard sudoku (used in puzzle generation)
squares = cross(rows, cols)
unitlist = ([cross(rows, c) for c in cols] +
            [cross(r, cols) for r in rows] +
            [cross(rs, cs) for rs in ('ABC', 'DEF', 'GHI') for cs in ('123', '456', '789')])
units = dict((s, [u for u in unitlist if s in u]) for s in squares)
peers = dict((s, set(sum(units[s], [])) - set([s])) for s in squares)

overlapping_squares = ['A1', 'A2', 'A3', 'A7', 'A8', 'A9',
                       'B1', 'B2', 'B3', 'B7', 'B8', 'B9',
                       'C1', 'C2', 'C3', 'C7', 'C8', 'C9',
                       'G1', 'G2', 'G3', 'G7', 'G8', 'G9',
                       'H1', 'H2', 'H3', 'H7', 'H8', 'H9',
                       'I1', 'I2', 'I3', 'I7', 'I8', 'I9']

square_indices_map = {}
index_squares_map = {}


def grid_index(square):
    if square not in square_indices_map:
        square_indices_map[square] = ((ord(square[0]) - ord('A')) * 9 + (int(square[1]) - 1))
    return square_indices_map[square]


def index_to_square(index):
    if index not in index_squares_map:
        index_squares_map[index] = chr(math.floor(index / 9) + ord('A')) + str(index % 9 + 1)
    return index_squares_map[index]


def assign(values, s, d):
    """Eliminate all the other values (except d) from values[s]."""
    other_values = values[s].replace(d, '')
    if all(eliminate(values, s, d2) for d2 in other_values):
        return values
    else:
        return False


def eliminate(values, s, d):
    """Eliminate d from values[s]; propagate when values or places <= 2."""
    if d not in values[s]:
        return values
    values[s] = values[s].replace(d, '')
    if len(values[s]) == 0:
        return False
    elif len(values[s]) == 1:
        d2 = values[s]
        if not all(eliminate(values, s2, d2) for s2 in peers[s]):
            return False
    for u in units[s]:
        dplaces = [s for s in u if d in values[s]]
        if len(dplaces) == 0:
            return False
        elif len(dplaces) == 1:
            if not assign(values, dplaces[0], d):
                return False
    return values


def shuffled(seq):
    """Return a randomly shuffled copy of the input sequence."""
    seq = list(seq)
    random.shuffle(seq)
    return seq


def random_puzzle(N=17):
    values = dict((s, digits) for s in squares)
    for s in shuffled(squares):
        if not assign(values, s, random.choice(values[s])):
            break
        ds = [values[s] for s in squares if len(values[s]) == 1]
        if len(ds) >= N and len(set(ds)) >= 8:
            return ''.join(values[s] if len(values[s]) == 1 else '.' for s in squares)
    return random_puzzle(N)


def random_middle_puzzle(N=17, grid='.' * 81):
    values = dict((s, digits) for s in squares)
    for s in overlapping_squares:
        if grid[grid_index(s)] != '.':
            assign(values, s, grid[grid_index(s)])
    for s in shuffled(list(set(squares) - set(overlapping_squares))):
        if not assign(values, s, random.choice(values[s])):
            break
        ds = [values[s] for s in squares if len(values[s]) == 1]
        if len(ds) >= N and len(set(ds)) >= 8:
            return ''.join(values[s] if len(values[s]) == 1 else '.' for s in squares)
    return random_middle_puzzle(N, grid)


def random_samurai_puzzle(N_a=17, N_b=17, N_c=17, N_d=17, N_plus=17):
    grid_a = random_puzzle(N_a)
    grid_b = random_puzzle(N_b)
    grid_c = random_puzzle(N_c)
    grid_d = random_puzzle(N_d)

    grid_plus = (grid_a[grid_index('G7'):grid_index('G9') + 1] + '...' + grid_b[grid_index('G1'):grid_index('G3') + 1] +
                 grid_a[grid_index('H7'):grid_index('H9') + 1] + '...' + grid_b[grid_index('H1'):grid_index('H3') + 1] +
                 grid_a[grid_index('I7'):grid_index('I9') + 1] + '...' + grid_b[grid_index('I1'):grid_index('I3') + 1] +
                 '.' * 9 * 3 +
                 grid_c[grid_index('A7'):grid_index('A9') + 1] + '...' + grid_d[grid_index('A1'):grid_index('A3') + 1] +
                 grid_c[grid_index('B7'):grid_index('B9') + 1] + '...' + grid_d[grid_index('B1'):grid_index('B3') + 1] +
                 grid_c[grid_index('C7'):grid_index('C9') + 1] + '...' + grid_d[grid_index('C1'):grid_index('C3') + 1])

    if not check_middle_puzzle(grid_plus):
        return random_samurai_puzzle(N_a, N_b, N_c, N_d, N_plus)
    grid_plus = random_middle_puzzle(N_plus, grid_plus)

    samurai_grid = [
        grid_a.replace('.', '0')[grid_index('A1'):grid_index('A9') + 1] + '...' + grid_b.replace('.', '0')[
                                                                                  grid_index('A1'):grid_index(
                                                                                      'A9') + 1],
        grid_a.replace('.', '0')[grid_index('B1'):grid_index('B9') + 1] + '...' + grid_b.replace('.', '0')[
                                                                                  grid_index('B1'):grid_index(
                                                                                      'B9') + 1],
        grid_a.replace('.', '0')[grid_index('C1'):grid_index('C9') + 1] + '...' + grid_b.replace('.', '0')[
                                                                                  grid_index('C1'):grid_index(
                                                                                      'C9') + 1],
        grid_a.replace('.', '0')[grid_index('D1'):grid_index('D9') + 1] + '...' + grid_b.replace('.', '0')[
                                                                                  grid_index('D1'):grid_index(
                                                                                      'D9') + 1],
        grid_a.replace('.', '0')[grid_index('E1'):grid_index('E9') + 1] + '...' + grid_b.replace('.', '0')[
                                                                                  grid_index('E1'):grid_index(
                                                                                      'E9') + 1],
        grid_a.replace('.', '0')[grid_index('F1'):grid_index('F9') + 1] + '...' + grid_b.replace('.', '0')[
                                                                                  grid_index('F1'):grid_index(
                                                                                      'F9') + 1],
        grid_a.replace('.', '0')[grid_index('G1'):grid_index('G9') + 1] + grid_plus.replace('.', '0')[
                                                                          grid_index('A4'):grid_index(
                                                                              'A6') + 1] + grid_b.replace('.', '0')[
                                                                                           grid_index('G1'):grid_index(
                                                                                               'G9') + 1],
        grid_a.replace('.', '0')[grid_index('H1'):grid_index('H9') + 1] + grid_plus.replace('.', '0')[
                                                                          grid_index('B4'):grid_index(
                                                                              'B6') + 1] + grid_b.replace('.', '0')[
                                                                                           grid_index('H1'):grid_index(
                                                                                               'H9') + 1],
        grid_a.replace('.', '0')[grid_index('I1'):grid_index('I9') + 1] + grid_plus.replace('.', '0')[
                                                                          grid_index('C4'):grid_index(
                                                                              'C6') + 1] + grid_b.replace('.', '0')[
                                                                                           grid_index('I1'):grid_index(
                                                                                               'I9') + 1],
        '......' + grid_plus.replace('.', '0')[grid_index('D1'):grid_index('D9') + 1] + '......',
        '......' + grid_plus.replace('.', '0')[grid_index('E1'):grid_index('E9') + 1] + '......',
        '......' + grid_plus.replace('.', '0')[grid_index('F1'):grid_index('F9') + 1] + '......',
        grid_c.replace('.', '0')[grid_index('A1'):grid_index('A9') + 1] + grid_plus.replace('.', '0')[
                                                                          grid_index('G4'):grid_index(
                                                                              'G6') + 1] + grid_d.replace('.', '0')[
                                                                                           grid_index('A1'):grid_index(
                                                                                               'A9') + 1],
        grid_c.replace('.', '0')[grid_index('B1'):grid_index('B9') + 1] + grid_plus.replace('.', '0')[
                                                                          grid_index('H4'):grid_index(
                                                                              'H6') + 1] + grid_d.replace('.', '0')[
                                                                                           grid_index('B1'):grid_index(
                                                                                               'B9') + 1],
        grid_c.replace('.', '0')[grid_index('C1'):grid_index('C9') + 1] + grid_plus.replace('.', '0')[
                                                                          grid_index('I4'):grid_index(
                                                                              'I6') + 1] + grid_d.replace('.', '0')[
                                                                                           grid_index('C1'):grid_index(
                                                                                               'C9') + 1],
        grid_c.replace('.', '0')[grid_index('D1'):grid_index('D9') + 1] + '...' + grid_d.replace('.', '0')[
                                                                                  grid_index('D1'):grid_index(
                                                                                      'D9') + 1],
        grid_c.replace('.', '0')[grid_index('E1'):grid_index('E9') + 1] + '...' + grid_d.replace('.', '0')[
                                                                                  grid_index('E1'):grid_index(
                                                                                      'E9') + 1],
        grid_c.replace('.', '0')[grid_index('F1'):grid_index('F9') + 1] + '...' + grid_d.replace('.', '0')[
                                                                                  grid_index('F1'):grid_index(
                                                                                      'F9') + 1],
        grid_c.replace('.', '0')[grid_index('G1'):grid_index('G9') + 1] + '...' + grid_d.replace('.', '0')[
                                                                                  grid_index('G1'):grid_index(
                                                                                      'G9') + 1],
        grid_c.replace('.', '0')[grid_index('H1'):grid_index('H9') + 1] + '...' + grid_d.replace('.', '0')[
                                                                                  grid_index('H1'):grid_index(
                                                                                      'H9') + 1],
        grid_c.replace('.', '0')[grid_index('I1'):grid_index('I9') + 1] + '...' + grid_d.replace('.', '0')[
                                                                                  grid_index('I1'):grid_index('I9') + 1]
    ]

    counts = {}
    counts['a'] = Counter()
    counts['b'] = Counter()
    counts['c'] = Counter()
    counts['d'] = Counter()
    counts['+'] = Counter()

    return samurai_grid, counts


def check_middle_puzzle(grid='.' * 81):
    values = dict((s, digits) for s in squares)
    for s in squares:
        if grid[grid_index(s)] != '.':
            if not assign(values, s, grid[grid_index(s)]):
                return False
    return True


def write_counter_to_database(name, counter):
    with open(name, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Y-Axis', 'X-Axis', 'Number of Hits'])
        for key, value in counter.items():
            writer.writerow([key[0], key[1], value])


class TimeoutException(Exception):
    pass


def solve_with_timeout(samurai_grid, timeout=10):
    """Solve with timeout using threading."""
    result = [None]

    def worker():
        try:
            # Solve using OR-Tools
            model = cp_model.CpModel()
            cells = {}
            for s in all_squares:
                cells[s] = model.NewIntVar(1, 9, s)

            for unit in all_unitlists:
                model.AddAllDifferent([cells[s] for s in unit])

            grid_vals = grid_values(samurai_grid)
            for s, val in grid_vals.items():
                if val in digits:
                    model.Add(cells[s] == int(val))

            solver = cp_model.CpSolver()
            status = solver.Solve(model)

            if status in [cp_model.FEASIBLE, cp_model.OPTIMAL]:
                solution = {}
                for s in all_squares:
                    solution[s] = str(solver.Value(cells[s]))
                result[0] = solution
            else:
                result[0] = False
        except Exception as e:
            result[0] = False

    thread = threading.Thread(target=worker)
    thread.start()
    thread.join(timeout=timeout)

    if thread.is_alive():
        return False  # Timed out
    return result[0]


if __name__ == '__main__':
    success_counter = 0
    timeout_counter = 0
    num_loops = 100

    a = Counter()
    b = Counter()
    c = Counter()
    d = Counter()
    plus = Counter()

    for i in range(num_loops):
        try:
            samurai_grid, counts = random_samurai_puzzle(17, 17, 17, 17, 17)
            ans = solve_with_timeout(samurai_grid, timeout=10)

            if ans is False:
                print(f"Puzzle {i}: Timeout or unsolvable")
                timeout_counter += 1
            else:
                success_counter += 1
                a.update(counts['a'])
                b.update(counts['b'])
                c.update(counts['c'])
                d.update(counts['d'])
                plus.update(counts['+'])
                print(f"Puzzle {i}: Solved successfully")
        except Exception as e:
            print(f"Puzzle {i}: Error - {str(e)}")
            timeout_counter += 1

    write_counter_to_database('grid_a_success_hits.csv', a)
    write_counter_to_database('grid_b_success_hits.csv', b)
    write_counter_to_database('grid_c_success_hits.csv', c)
    write_counter_to_database('grid_d_success_hits.csv', d)
    write_counter_to_database('grid_plus_success_hits.csv', plus)

    print('#' * 100)
    print("Number of Initial Squares Filled in each Grid Quadrant:")
    print("Top Left: 17, Top Right: 17, Bottom Left: 17, Bottom Right: 17, Centre: 17")
    print("Successes:", success_counter)
    print("Failures:", num_loops - success_counter)
    print("Success Ratio:", success_counter / num_loops)
    print("Timeouts:", timeout_counter)
    print("Timeout Ratio:", timeout_counter / num_loops)
    print('#' * 100)