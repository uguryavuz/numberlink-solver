# numberlink-solver [![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/) [![python-3.7](https://img.shields.io/badge/python-3.7-blue)](https://www.python.org/downloads/release/python-370/)
Ugur Yavuz, August 2019

Numberlink-Solver is, as its name suggests, a [Numberlink puzzle](https://en.wikipedia.org/wiki/Numberlink) solver. This is achieved by converting the puzzle into a [Boolean satisfiability (SAT) problem](https://en.wikipedia.org/wiki/Boolean_satisfiability_problem), and then using Google's [OR-Tools](https://developers.google.com/optimization/) library to solve this problem. The [pygame](https://www.pygame.org) library provides a visual interface for the creation of the puzzle.  

## How to run?
* Clone or download this repository.
* In the repository's directory, run setup.py in Terminal to install the necessary libraries.
* Run solve_numberlink.py in Terminal. Input the puzzle's width, height and how many numbers there are.
* In the graphic interface that shows up, select the numbers' locations in order.
* Click 'Solve'. If no solution is found, the puzzle will be colored in the red tint. If a solution is found, it will be displayed.
* If a solution is found, you can click 'Save as .JPG' to save a screenshot of the solution in the directory where solve_numberlink.py is situated.
* Close the window, or press any combination out of ESC, Command + Q, ALT + F4, to terminate the program.

## Notes
* The solver assumes that the puzzles have a unique solution, following the convention for traditional Numberlink puzzles.

### Future

* Create and load from .CNF files.
* Add my --educational solver (I had initially written a SAT solver myself, which turned out to be much slower than the one provided by OR-Tools).
* Using a better suited graphics library than pygame.
* Remove the unique solution assumption. Although the solver can currently solve such puzzles, it may end up creating free-standing loops. A constraint that doesn't allow solutions to contain free-standing loops must be added.
