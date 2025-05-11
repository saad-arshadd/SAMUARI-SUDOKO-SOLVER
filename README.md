# SAMUARI-SUDOKO-SOLVER


# LINKS OF GOOGLE DRIVE FOR THE DEMO , REPORT AND PROPOSAL OF THE PROJECT :

[AI Demo](https://drive.google.com/file/d/1AOOnAwsXBZhKfHmLX2GiFxpx1E-I8Gi7/view?usp=drive_link)



[AI Report ](https://docs.google.com/document/d/1cmCErP-glEZZZpm3p6dVQJK72Dq7qpcu/edit?usp=sharing&ouid=111427032532477399145&rtpof=true&sd=true)


[AI Project Proposal](https://docs.google.com/document/d/1xPrirZTzq3olpq1LbbAXajiIfRaATitF/edit?usp=drive_link&ouid=111427032532477399145&rtpof=true&sd=true)


# Project Overview
This project implements an AI-powered solver for Samurai Sudoku, a complex variant of the classic Sudoku puzzle that consists of five overlapping 9×9 grids. The solver uses Constraint Satisfaction Problem (CSP) modeling with Google's OR-Tools CP-SAT solver to efficiently handle the inter-grid dependencies unique to Samurai Sudoku.

# Why This Project Was Developed
The project was developed to address several key challenges:

Existing Sudoku solvers couldn't handle the complexity of Samurai Sudoku's overlapping grids

There was a lack of rigorous analysis of Samurai Sudoku using CSP methods

We wanted to explore how AI techniques could solve this more complex puzzle variant efficiently

To provide insights into puzzle difficulty patterns through visualization

# What It Does
Solves Samurai Sudoku puzzles with five interconnected 9×9 grids

Validates solutions to ensure all constraints are satisfied

Generates random Samurai Sudoku puzzles for testing

Provides visualization tools to analyze puzzle patterns

Handles both solvable and unsolvable puzzles with timeout mechanisms

# How It Works
The solver uses these key components:

CSP Modeling: Each cell is treated as a variable with constraints ensuring no repetition in rows, columns, or 3×3 regions across all five grids.

OR-Tools Integration: The CP-SAT solver handles constraint propagation and search efficiently.

Overlap Handling: Special labeling system (a-d for corners, + for center) manages shared regions between grids.

Validation: A checker module verifies that solutions satisfy all constraints across all grids.

# Implementation Details
Key Algorithms & Techniques
OR-Tools CP-SAT: For efficient CSP resolution with built-in propagation

Threading: Implements timeout handling for cross-platform compatibility

Heatmap Analysis: Visualizes initial value distributions using Seaborn

Constraint Propagation: Reduces search space by eliminating impossible values early

# Code Structure
samurai.py: Main solver implementation for Samurai Sudoku

sudoku.py: Base Sudoku solver (used as reference)

checker.py: Solution validation module

analyse.py: Puzzle generation and analysis tools

imaging.py: Visualization using Seaborn heatmaps

# How to Run the Program


Required libraries: ortools, seaborn, numpy, pandas

python samurai.py
Then enter the path to your puzzle file when prompted.

To generate and analyze random puzzles:

bash
python analyse.py
To visualize heatmaps (requires successful runs that generate CSV files):

bash
python imaging.py path_to_csv_file.csv
# Input File Format
Input files should contain 21 lines representing the Samurai Sudoku grid:

Lines 1-9: Top-left and top-right grids (separated by "...")

Lines 10-12: Middle grid (centered with padding)

Lines 13-21: Bottom-left and bottom-right grids (separated by "...")

Use '0' or '.' for empty cells.

# Project Outcomes
Achieved 92% solve rate for valid puzzles

Average solve time of 1.8 seconds for 17-clue puzzles

Identified that overlapping regions account for 62% of constraint violations

Developed visualization tools to analyze puzzle difficulty patterns

# Team Contributions
Ayesha Nasir (22k-4387): OR-Tools integration, CSP modeling

Saad Arshad (22k-4141): Threading implementation, visualization

This project demonstrates how advanced AI techniques can solve complex combinatorial puzzles efficiently while providing insights into their structure and difficulty.
