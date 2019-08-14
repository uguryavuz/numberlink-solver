from itertools import product, combinations
from ortools.sat.python import cp_model

class NumberlinkPuzzle():

    def __init__(self, width, height, color_locs):
        self.width = width
        self.height = height
        self.color_count = len(color_locs) // 2
        self.color_locs = color_locs

    def generate_cnf(self):
        
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

                # Every color cell has only 1 line, every non-color cell has 2 lines.
                # Denote corresponding logic in CNF. (1 or 2 True out of 2, 3 or 4).
                if (x, y) in self.color_locs:
                    if len(lines) == 2:
                        cnf_clauses.append('{} {}'.format(*lines))
                        cnf_clauses.append('-{} -{}'.format(*lines))
                    elif len(lines) == 3:
                        for (a, b) in combinations(lines, 2):
                            cnf_clauses.append(f'-{a} -{b}')
                        cnf_clauses.append('{} {} {}'.format(*lines))
                    else:
                        for (a, b) in combinations(lines, 2):
                            cnf_clauses.append(f'-{a} -{b}')
                        cnf_clauses.append('{} {} {} {}'.format(*lines))
                else:
                    if len(lines) == 2:
                        for l in lines:
                            cnf_clauses.append(l)
                    elif len(lines) == 3:
                        for (a, b) in combinations(lines, 2):
                            cnf_clauses.append(f'{a} {b}')
                        cnf_clauses.append('-{} -{} -{}'.format(*lines))
                    else:
                        for (a, b, c) in combinations(lines, 3):
                            cnf_clauses.append(f'{a} {b} {c}')
                            cnf_clauses.append(f'-{a} -{b} -{c}')

                # Colors variables for current cell. Only 1 is True. We essentially create a CNF XOR-gate.
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

        for i in range(self.color_count):
            cnf_clauses.append(f'c.{self.color_locs[2 * i][0]}.{self.color_locs[2 * i][1]}.{i + 1}')
            cnf_clauses.append(f'c.{self.color_locs[2 * i + 1][0]}.{self.color_locs[2 * i + 1][1]}.{i + 1}')

        return cnf_clauses

    def solve(self, cnf_clauses):

        assignments = []

        model = cp_model.CpModel()
        boolVars = {}

        for line in cnf_clauses:
            signed_vars, bare_vars, signs = line.split(), [], []

            for var in signed_vars:
                sign = -1 if var[0] == '-' else 1
                bare_var = var[1:] if sign == -1 else var
                bare_vars.append(bare_var)
                signs.append(sign)
                if bare_var not in boolVars:
                    boolVars[bare_var] = model.NewBoolVar(bare_var)

            model.AddBoolOr([boolVars[bare_vars[i]] if signs[i] == 1 else boolVars[bare_vars[i]].Not()
                             for i in range(len(bare_vars))])

        solver = cp_model.CpSolver()
        status = solver.Solve(model)
        print(f"Solution is {solver.StatusName(status)}")

        if status == 2:
            colors = sorted([key for key in boolVars if key[0] == 'c' and solver.Value(boolVars[key]) > 0])
            for color in colors:
                rel_vertical = 'v.' + '.'.join(color.split('.')[1:-1])
                if rel_vertical in boolVars:
                    rel_vertical = '-' + rel_vertical if solver.Value(
                        boolVars[rel_vertical]) < 1 else rel_vertical
                else:
                    rel_vertical = ''

                rel_horizontal = 'h.' + '.'.join(color.split('.')[1:-1])
                if rel_horizontal in boolVars:
                    rel_horizontal = '-' + rel_horizontal if solver.Value(
                        boolVars[rel_horizontal]) < 1 else rel_horizontal
                else:
                    rel_horizontal = ''

                assignments.append(' '.join([elt for elt in [color, rel_vertical, rel_horizontal] if len(elt) > 0]))

            return assignments
        else:
            return None
