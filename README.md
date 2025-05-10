# Pairwise Test Case Generator

This project provides a Streamlit web application for generating pairwise (also known as all-pairs) test suites. Pairwise testing is a black-box test design technique that aims to test all possible discrete combinations of pairs of input parameters. This tool helps in creating an efficient set of test cases that cover all pairwise interactions, significantly reducing the number of test cases compared to an exhaustive approach while maintaining high defect detection rates.

The application allows users to define parameters and their respective values, choose between two different algorithms (CP-SAT and Greedy), and then generate a test suite.

## Features

*   **Dynamic Parameter Management:** Add, update, and delete parameters and their values through the web interface.
*   **Two Algorithm Options:**
    *   **CP-SAT (Constraint Programming - Satisfiability):** Utilizes Google's OR-Tools to find an optimal (minimum) set of test cases. This method guarantees the smallest possible test suite but can be slower for very large parameter sets.
    *   **Greedy Algorithm:** A faster heuristic approach that iteratively selects the test case covering the most new pairs. It may not always produce the absolute minimum number of test cases but is efficient for larger inputs.
*   **Interactive UI:** Built with Streamlit for an easy-to-use web interface.
*   **Input Validation:** Includes validation for parameter names and values to prevent errors.
*   **Results Display:** Shows the total number of unique pairs, the total number of generated test cases, and a detailed table of the test cases with the number of new unique pairs covered by each.

## How it Works

The core idea is to ensure that every possible pair of values across any two parameters is covered by at least one test case.

1.  **Parameter Definition:** The user defines a set of parameters and the possible values for each parameter. For example:
    *   `Operating System`: `Windows`, `Linux`, `macOS`
    *   `Browser`: `Chrome`, `Firefox`, `Safari`
2.  **Pair Generation:** The application first generates all unique pairs of (parameter value, parameter value) combinations.
3.  **Test Suite Generation:**
    *   **CP-SAT Algorithm (`algo.py`):**
        *   Models the problem as a constraint satisfaction problem.
        *   Creates boolean variables for each possible test case and each pair.
        *   Defines constraints to ensure all pairs are covered.
        *   Minimizes the total number of selected test cases.
        *   Uses the `ortools.sat.python.cp_model` library.
    *   **Greedy Algorithm (`greedyalgo.py`):**
        *   Starts with an empty test suite and a list of all uncovered pairs.
        *   In each step, it iterates through all possible test cases and selects the one that covers the maximum number of currently uncovered pairs.
        *   The selected test case is added to the suite, and the pairs it covers are marked as covered.
        *   This process repeats until all pairs are covered.
4.  **Display Results:** The generated test suite is displayed, along with metrics like the number of test cases and the pairs covered.

## File Structure

*   `main.py`: The main Streamlit application file. It handles the UI, user input, parameter management, and calls the appropriate algorithm.
*   `algo.py`: Implements the pairwise test case generation using the CP-SAT solver from Google OR-Tools.
*   `greedyalgo.py`: Implements the greedy algorithm for pairwise test case generation.
*   `requirements.txt` (Recommended): To list project dependencies.

## Setup and Usage

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/Pairwise-Test-Case-Generator.git
    cd Pairwise-Test-Case-Generator
    ```

2.  **Create a virtual environment (recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3.  **Install dependencies:**
    You will need to create a `requirements.txt` file. Based on your code, it should contain:
    ```
    streamlit
    ortools
    pandas
    ```
    Then install them:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Run the Streamlit application:**
    ```bash
    streamlit run main.py
    ```
    This will open the application in your web browser.

5.  **Using the Application:**
    *   The application will start with a default set of parameters.
    *   **Algorithm Selection:** Choose between 'CP-SAT' (default, optimal) or 'Greedy' (faster, potentially more test cases).
    *   **Parameter Management:**
        *   **Add:** Enter a "New Parameter Name" and its "Values (comma-separated)" and click "Add Parameter".
        *   **Update:** Modify the comma-separated values for an existing parameter and click its "📝 Update" button.
        *   **Delete:** Click the "🗑️ Delete" button next to a parameter to remove it.
        *   **Clear All:** Removes all defined parameters.
    *   **Generate Test Cases:** Once parameters are set up (at least two parameters, each with at least two values), click the "Generate Test Cases" button.
    *   **View Results:** The application will display:
        *   Total unique pairs possible.
        *   Total test cases in the generated suite.
        *   A table listing each test case, its parameter values, and the number of new unique pairs it covers.

## Code Overview

### `main.py`

*   Handles the Streamlit UI components (input fields, buttons, tables).
*   Manages session state for parameters and algorithm selection.
*   Includes validation functions for parameter names (`validate_parameter_name`) and values (`validate_parameter_values`).
*   Calls the selected algorithm (`algo.find_minimum_test_suite` or `greedyalgo.find_minimum_test_suite`) upon user request.
*   Formats and displays the results.

### `algo.py` (CP-SAT Algorithm)

*   `generate_pairwise_combinations(parameters)`: Generates all unique pairs of (parameter, value) combinations from the input parameters. Ensures lexicographical order of parameter keys for consistent pair generation.
*   `find_minimum_test_suite(parameters)`:
    *   Sets up the CP-SAT model.
    *   Creates boolean variables for each potential test case (all possible combinations of parameter values) and each pair.
    *   `model.AddMaxEquality`: Links test case variables to pair coverage. A pair is covered if at least one test case that includes that pair is selected.
    *   `model.Add(sum(pair_covered.values()) == len(all_pairs))`: Ensures all generated pairs are covered.
    *   `model.Minimize(sum(test_case_vars))`: The objective is to minimize the number of test cases selected.
    *   Includes a timeout for the solver.
    *   Returns the optimal test suite if found.
*   `count_unique_pairs(test_cases, all_pairs, parameters)`: Calculates how many new unique pairs each test case in the generated suite covers.

### `greedyalgo.py` (Greedy Algorithm)

*   `generate_pairwise_combinations(parameters)`: Similar to the one in `algo.py`, generates all unique pairs.
*   `get_pairs_in_test(test, param_keys)`: Given a single test case (a list of values), determines all pairs covered by it.
*   `find_minimum_test_suite(parameters)`:
    *   Initializes an empty test suite and a set of uncovered pairs.
    *   Iteratively selects the test case from `all_values` (all possible product combinations) that covers the most *new* pairs.
    *   Adds the best test to the suite and updates the set of covered pairs.
    *   Continues until all pairs are covered or no more pairs can be covered.
    *   Includes a `MAX_COMBINATIONS` limit to prevent excessive computation for very large parameter spaces.
*   `count_unique_pairs(test_cases, all_pairs, parameters)`: Similar to the one in `algo.py`, calculates new unique pairs covered per test case.

## Potential Improvements

*   **Export Results:** Add functionality to export the generated test cases (e.g., to CSV or Excel).
*   **Performance for Greedy:** For very large inputs, the `product(*parameters.values())` in the greedy algorithm can still be very large. Optimizations like sampling or more advanced greedy heuristics could be explored.
*   **Error Handling:** Enhance error handling for edge cases or unexpected solver statuses.
*   **Progress Indication:** For the CP-SAT solver, provide more feedback on the solving process if it takes a long time.
*   **Advanced Constraints:** Allow users to specify constraints (e.g., "if Parameter A is Value X, then Parameter B cannot be Value Y").

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request or open an Issue.

---

This README provides a comprehensive overview. Let me know if you'd like any part adjusted!
