from itertools import combinations, product
from typing import Dict, List, Set, Tuple, Any

def generate_pairwise_combinations(parameters: Dict[str, List[str]]) -> List[Tuple[Tuple[str, str], Tuple[str, str]]]:
    param_keys = sorted(parameters.keys())
    all_pairs = set()

    for p1, p2 in combinations(param_keys, 2):
        for v1 in parameters[p1]:
            for v2 in parameters[p2]:
                all_pairs.add(((p1, v1), (p2, v2)))

    return list(all_pairs)

def get_pairs_in_test(test: List[str], param_keys: List[str]) -> Set[Tuple[Tuple[str, str], Tuple[str, str]]]:
    pairs = set()
    for (p1, p2) in combinations(range(len(param_keys)), 2):
        pair = ((param_keys[p1], test[p1]), (param_keys[p2], test[p2]))
        pairs.add(tuple(sorted(pair)))
    return pairs

def find_minimum_test_suite(parameters: Dict[str, List[str]]) -> Tuple[List[List[str]], List[Tuple[Tuple[str, str], Tuple[str, str]]]]:
    param_keys = list(parameters.keys())
    all_values = list(product(*parameters.values()))
    all_pairs = generate_pairwise_combinations(parameters)
    
    covered_pairs: Set[Tuple[Tuple[str, str], Tuple[str, str]]] = set()
    test_suite: List[List[str]] = []
    
    while len(covered_pairs) < len(all_pairs):
        best_test = None
        best_new_pairs = 0
        
        for test in all_values:
            test_pairs = get_pairs_in_test(test, param_keys)
            new_pairs = len(test_pairs - covered_pairs)
            
            if new_pairs > best_new_pairs:
                best_new_pairs = new_pairs
                best_test = test
        
        if best_test is None:
            break
            
        test_suite.append(best_test)
        covered_pairs.update(get_pairs_in_test(best_test, param_keys))
    
    return test_suite, all_pairs

def count_unique_pairs(test_cases: List[List[str]], all_pairs: List[Tuple[Tuple[str, str], Tuple[str, str]]], parameters: Dict[str, List[str]]) -> Tuple[Set[Any], List[Set[Any]], List[int]]:
    covered_pairs = set()
    test_case_pairs = []
    new_unique_counts = []
    param_keys = list(parameters.keys())

    for test in test_cases:
        current_covered = len(covered_pairs)
        test_pairs = get_pairs_in_test(test, param_keys)
        covered_pairs.update(test_pairs)
        test_case_pairs.append(test_pairs)
        new_unique = len(covered_pairs) - current_covered
        new_unique_counts.append(new_unique)

    return covered_pairs, test_case_pairs, new_unique_counts 