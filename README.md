# Numberlink-Solver [![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/) [![python-3.7](https://img.shields.io/badge/python-3.7-blue)](https://www.python.org/downloads/release/python-370/)
Ugur Yavuz, August 2019

Numberlink-Solver is, as its name suggests, a [Numberlink puzzle](https://en.wikipedia.org/wiki/Numberlink) solver. This is achieved by converting the puzzle into a [Boolean satisfiability (SAT) problem](https://en.wikipedia.org/wiki/Boolean_satisfiability_problem), and then using Google's [OR-Tools]() library to solve this problem. The [pygame](https://www.pygame.org) library provides a visual interface for the creation of the puzzle.  

### To-do list

* Load from CNF option (in command line)
* --educational solver (in command line)
* Save as CNF / Solve options (after next's)
    * Load from CNF would take you here
* Red overlay if no solution (X)
* Save image (after solution) (X)
* setup.py (pip install pygame, pygbutton, ortools) (X?)
* Comments in code (X?)
* README.md
