from itertools import combinations, product
from ortools.sat.python import cp_model
import streamlit as st

def generate_pairwise_combinations(parameters):
    param_keys = sorted(parameters.keys())  # Sort keys lexicographically
    all_pairs = set()

    # Generate all pairs of parameters in lex order
    for p1, p2 in combinations(param_keys, 2):
        for v1 in parameters[p1]:
            for v2 in parameters[p2]:
                all_pairs.add(((p1, v1), (p2, v2)))

    return list(all_pairs)

def find_minimum_test_suite(parameters):
    if not isinstance(parameters, dict):
        raise TypeError("Parameters must be a dictionary")
    if not parameters:
        raise ValueError("Parameters dictionary cannot be empty")
    if not all(isinstance(v, list) for v in parameters.values()):
        raise TypeError("All parameter values must be lists")
    
    all_pairs = generate_pairwise_combinations(parameters)
    param_keys = list(parameters.keys())
    all_values = list(product(*parameters.values()))

    model = cp_model.CpModel()
    test_case_vars = [model.NewBoolVar(f"tc_{i}") for i in range(len(all_values))]
    pair_covered = {}

    for i, pair in enumerate(all_pairs):
        pair_covered[i] = model.NewBoolVar(f"pair_{i}")
        model.AddMaxEquality(pair_covered[i], [
            test_case_vars[j] for j, test in enumerate(all_values)
            if (pair[0] in zip(param_keys, test)) and (pair[1] in zip(param_keys, test))
        ])

    model.Add(sum(pair_covered.values()) == len(all_pairs))
    model.Minimize(sum(test_case_vars))

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 300  # Add timeout
    status = solver.Solve(model)

    if status == cp_model.OPTIMAL:
        optimal_suite = [all_values[i] for i in range(len(all_values)) if solver.Value(test_case_vars[i])]
        return optimal_suite, all_pairs
    elif status == cp_model.FEASIBLE:
        st.warning("Found a solution, but it may not be optimal")
        optimal_suite = [all_values[i] for i in range(len(all_values)) if solver.Value(test_case_vars[i])]
        return optimal_suite, all_pairs
    else:
        return None, None

def count_unique_pairs(test_cases, all_pairs, parameters):
    covered_pairs = set()
    test_case_pairs = []
    new_unique_counts = []

    for test in test_cases:
        current_covered = len(covered_pairs)
        test_pairs = set()
        for p1, p2 in combinations(zip(parameters.keys(), test), 2):
            pair = tuple(sorted([p1, p2]))
            if pair in all_pairs:
                test_pairs.add(pair)
        covered_pairs.update(test_pairs)
        test_case_pairs.append(test_pairs)
        new_unique = len(covered_pairs) - current_covered
        new_unique_counts.append(new_unique)

    return covered_pairs, test_case_pairs, new_unique_counts

# Parameter setup
parameters = {
  'Display Mode': ['Full Graph', 'Text Only', 'Limited-Bandwidth'],
  'Language': ['English', 'French', 'Spanish', 'Turkish'],
  'Fonts': ['Minimal', 'Standard', 'Document-loaded'],
  'Color': ['Monochrome', 'Colormap', '16-bit', 'True Color'],
  'Screen Size': ['Hand-held', 'laptop', 'fullsize']
}

# Run the optimization
optimal_tests, all_pairs = find_minimum_test_suite(parameters)

if optimal_tests:
    covered_pairs, test_case_pairs, new_unique_counts = count_unique_pairs(optimal_tests, all_pairs, parameters)
    print(f"Total unique pairs: {len(all_pairs)}")
    print(f"Total test cases: {len(optimal_tests)}")
    for i, test in enumerate(optimal_tests, 1):
        print(f"Test case {i}: {test} ({new_unique_counts[i-1]} new unique pairs)")
else:
    print("No optimal test suite found.")