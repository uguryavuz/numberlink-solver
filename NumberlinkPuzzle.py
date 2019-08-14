# Author: Ugur Yavuz
# August 2019
# NumberlinkPuzzle.py: A Numberlink puzzle class that takes the puzzle width,
#                      height, and the locations of the colors (numbers) at initialization.
#                      Contains a conjunctive normal form (CNF) generator and solver(s).

from itertools import product, combinations           # Easier inter- and intra-array operations.
from ortools.sat.python import cp_model               # The OR-Tools SAT solver.


class NumberlinkPuzzle:
    """
    A Numberlink puzzle class that takes the puzzle width, height, and the locations of the colors
    (numbers) at initialization. Contains a conjunctive normal form (CNF) generator and solver
    methods.
    """

    def __init__(self, width, height, color_locs):
        """
        :param width: Width of the puzzle.
        :param height: Height of the puzzle.
        :param color_locs: Array containing the x, y coordinates (0, 0 at top-left) of the numbers.
        color_locs[0] and color_locs[1] are the coordinates of 1, etc.
        """
        self.width = width
        self.height = height
        self.color_count = len(color_locs) // 2       # Defined for convenience.
        self.color_locs = color_locs

    def generate_cnf(self):
        """
        Returns an array of CNF clauses, where the literals preceded by '-' are negated, and each
        literal in a clause is separated by whitespace.
        Clauses:
        - v.x.y = True if the cell at (x, y) is connected to the cell at (x, y+1)
        - h.x.y = True if the cell at (x, y) is connected to the cell at (x+1, y)
        - c.x.y.N = True if the cell at (x, y) has N as its number (color)
        :return: cnf_clauses
        """
        cnf_clauses = []
        for x in range(self.width):
            for y in range(self.height):

                # All vertical and horizontal lines attached to current cell.
                lines = []
                if x != self.width - 1:
                    lines.append(f'h.{x}.{y}')
                if y != self.height - 1:
                    lines.append(f'v.{x}.{y}')
                if x != 0:
                    lines.append(f'h.{x - 1}.{y}')
                if y != 0:
                    lines.append(f'v.{x}.{y - 1}')

                # Every color cell has only 1 line going in/out, every non-color cell
                # has 2 lines going in/out. Denoting corresponding logic in CNF.
                # (1 or 2 True out of 2, 3 or 4 literals).
                if (x, y) in self.color_locs:
                    # 1 true out of 2 lines.
                    if len(lines) == 2:
                        cnf_clauses.append('{} {}'.format(*lines))
                        cnf_clauses.append('-{} -{}'.format(*lines))
                    # 1 true out of 3 lines.
                    elif len(lines) == 3:
                        for (a, b) in combinations(lines, 2):
                            cnf_clauses.append(f'-{a} -{b}')
                        cnf_clauses.append('{} {} {}'.format(*lines))
                    # 1 true out of 4 lines.
                    else:
                        for (a, b) in combinations(lines, 2):
                            cnf_clauses.append(f'-{a} -{b}')
                        cnf_clauses.append('{} {} {} {}'.format(*lines))
                else:
                    # 2 true out of 2 lines.
                    if len(lines) == 2:
                        for l in lines:
                            cnf_clauses.append(l)
                    # 2 true out of 3 lines.
                    elif len(lines) == 3:
                        for (a, b) in combinations(lines, 2):
                            cnf_clauses.append(f'{a} {b}')
                        cnf_clauses.append('-{} -{} -{}'.format(*lines))
                    # 2 true out of 4 lines.
                    else:
                        for (a, b, c) in combinations(lines, 3):
                            cnf_clauses.append(f'{a} {b} {c}')
                            cnf_clauses.append(f'-{a} -{b} -{c}')

                # Colors variables for current cell. Only 1 is True. We essentially create a
                # CNF XOR-gate.
                color_vars = [f'c.{x}.{y}.{color}' for color in range(1, self.color_count + 1)]
                for (a, b) in combinations(color_vars, 2):
                    cnf_clauses.append(f'-{a} -{b}')
                cnf_clauses.append(' '.join(color_vars))

                # Vertical/horizontal line implies color shared with adjacent cell.
                if f'h.{x}.{y}' in lines:
                    cur_colors = [(f'c.{x}.{y}.{color}', f'c.{x + 1}.{y}.{color}') for color
                                  in range(1, self.color_count + 1)]
                    for double in product(*cur_colors):
                        cnf_clauses.append(f'-h.{x}.{y} ' + ' '.join(double))
                if f'v.{x}.{y}' in lines:
                    cur_colors = [(f'c.{x}.{y}.{color}', f'c.{x}.{y + 1}.{color}') for color
                                  in range(1, self.color_count + 1)]
                    for double in product(*cur_colors):
                        cnf_clauses.append(f'-v.{x}.{y} ' + ' '.join(double))

        # Add respective colors/numbers to given color locations.
        for i in range(self.color_count):
            cnf_clauses.append(f'c.{self.color_locs[2 * i][0]}.{self.color_locs[2 * i][1]}.{i + 1}')
            cnf_clauses.append(f'c.{self.color_locs[2 * i + 1][0]}.{self.color_locs[2 * i + 1][1]}.{i + 1}')

        return cnf_clauses

    def solve(self, cnf_clauses):
        """
        Finds truth value assignments for given cnf_clauses. Returns a list of all literals, which
        are preceded by '-' if they are assigned a False value.
        :param cnf_clauses:
        :return: assignments array. None if the problem is not solvable.
        """
        assignments = []
        
        # Initialize model. Keep track of literals in the bool_vars dictionary.
        model = cp_model.CpModel()
        bool_vars = {}

        # Add each clause to the model, add each individual bool_var to the dictionary, where it
        # is associated to its definition in the model.
        for line in cnf_clauses:
            signed_vars, bare_vars, signs = line.split(), [], []

            for var in signed_vars:
                sign = -1 if var[0] == '-' else 1
                bare_var = var[1:] if sign == -1 else var
                bare_vars.append(bare_var)
                signs.append(sign)
                if bare_var not in bool_vars:
                    bool_vars[bare_var] = model.NewBoolVar(bare_var)

            model.AddBoolOr([bool_vars[bare_vars[i]] if signs[i] == 1 else
                             bool_vars[bare_vars[i]].Not()
                             for i in range(len(bare_vars))])

        # Initialize and run solver.
        solver = cp_model.CpSolver()
        status = solver.Solve(model)
        print(f"Solution is {solver.StatusName(status)}")

        # 2 means that the solution is feasible.
        # Create assignments array in the format specified above.
        if status == 2:
            colors = sorted([key for key in bool_vars if key[0] == 'c' and
                             solver.Value(bool_vars[key]) > 0])
            for color in colors:
                rel_vertical = 'v.' + '.'.join(color.split('.')[1:-1])
                if rel_vertical in bool_vars:
                    rel_vertical = '-' + rel_vertical if solver.Value(
                        bool_vars[rel_vertical]) < 1 else rel_vertical
                else:
                    rel_vertical = ''
                rel_horizontal = 'h.' + '.'.join(color.split('.')[1:-1])
                if rel_horizontal in bool_vars:
                    rel_horizontal = '-' + rel_horizontal if solver.Value(
                        bool_vars[rel_horizontal]) < 1 else rel_horizontal
                else:
                    rel_horizontal = ''
                assignments.append(' '.join([elt for elt in [color, rel_vertical,
                                                             rel_horizontal] if len(elt) > 0]))
            return assignments
        else:
            return None
