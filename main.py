import streamlit as st
import algo
import greedyalgo
from ast import literal_eval

def initialize_session_state():
    if 'parameters' not in st.session_state:
        st.session_state.parameters = {
            'Display Mode': ['Full Graph', 'Text Only', 'Limited-Bandwidth'],
            'Language': ['English', 'French', 'Spanish', 'Turkish'],
            'Fonts': ['Minimal', 'Standard', 'Document-loaded'],
            'Color': ['Monochrome', 'Colormap', '16-bit', 'True Color'],
            'Screen Size': ['Hand-held', 'laptop', 'fullsize']
        }
    
    # Add version tracking
    if 'version' not in st.session_state:
        st.session_state.version = "1.0"

def initialize_algorithm_state():
    if 'algorithm' not in st.session_state:
        st.session_state.algorithm = 'CP-SAT'

def validate_parameter_name(name):
    """Validate parameter name"""
    if not name or not name.strip():
        return False, "Parameter name cannot be empty"
    
    # Add character validation
    if not all(c.isalnum() or c in [' ', '_', '-'] for c in name):
        return False, "Parameter names can only contain letters, numbers, spaces, underscores, and hyphens"
    
    # Add length validation
    if len(name) > 50:
        return False, "Parameter name too long (max 50 characters)"
    
    if name.strip() in st.session_state.parameters:
        return False, "Parameter name already exists"
    
    return True, ""

def validate_parameter_values(values, current_param=None):
    """Validate and clean parameter values"""
    MAX_VALUE_LENGTH = 100
    MAX_VALUES = 50
    
    if not values or not values.strip():
        return False, [], "Values cannot be empty"
    
    # Split and clean values
    values_list = [v.strip() for v in values.split(',') if v.strip()]
    
    # Check maximum number of values
    if len(values_list) > MAX_VALUES:
        return False, [], f"Maximum {MAX_VALUES} values allowed per parameter"
    
    # Check value length
    long_values = [v for v in values_list if len(v) > MAX_VALUE_LENGTH]
    if long_values:
        return False, [], f"Values exceeding {MAX_VALUE_LENGTH} characters: {', '.join(long_values)}"
    
    # Check for duplicates within this parameter
    if len(values_list) != len(set(values_list)):
        return False, [], "Duplicate values are not allowed within a parameter"
    
    # Check for duplicates across all parameters
    all_other_values = set()
    for param, param_values in st.session_state.parameters.items():
        if param != current_param:  # Skip the current parameter when updating
            all_other_values.update(param_values)
    
    duplicates = set(values_list) & all_other_values
    if duplicates:
        return False, [], f"Values {', '.join(duplicates)} already exist in other parameters"
    
    # Check minimum number of values
    if len(values_list) < 2:
        return False, [], "At least 2 values are required for each parameter"
        
    return True, values_list, ""

def main():
    st.set_page_config(layout="wide")
    st.title("Pairwise Test Case Generator")
    initialize_session_state()
    initialize_algorithm_state()
    
    if 'clear_fields' in st.session_state and st.session_state.clear_fields:
        # Reset the clear_fields flag
        st.session_state.clear_fields = False
        # Initialize empty input fields
        st.session_state.new_param = ""
        st.session_state.new_values = ""

    st.markdown("""
    ### Instructions
    1. The exmaples are given as default values for the parameters.
    2. Choose algorithm from the selection box, CP-SAT will be the default and any performance and accruacy tests should be done with CP-SAT.
    3. Add, edit, or delete parameters and their values using the controls below
    4. Click 'Generate Test Cases' to create an optimal test suite
    5. The results will be displayed in the table below
    """)

    # Make algorithm selection more prominent
    st.markdown("---")
    st.subheader("Algorithm Selection")
    
    # Add explanation columns
    col1, col2 = st.columns(2)
    with col1:
        st.radio(
            "Select Algorithm",
            ['CP-SAT', 'Greedy'],
            key='algorithm',
            horizontal=True,
        )
    with col2:
        if st.session_state.algorithm == 'CP-SAT':
            st.info("🎯 CP-SAT: Generates optimal (minimum) test cases but may be slower for large parameter sets")
        else:
            st.info("⚡ Greedy: Faster execution but may generate more test cases than necessary")

    st.markdown("---")
    # Parameter management section
    st.subheader("Parameter Management")
    
    # Add Clear All button and new parameter controls in the same row
    with st.container():
        col1, col2, col3, col4 = st.columns([1, 2, 0.7, 0.3])
        with col1:
            new_param = st.text_input("New Parameter Name", key="new_param")
        with col2:
            new_values = st.text_input("Values (comma-separated)", key="new_values")
        with col3:
            if st.button("Add Parameter", use_container_width=True):
                name_valid, name_error = validate_parameter_name(new_param)
                if name_valid:
                    values_valid, values_list, values_error = validate_parameter_values(new_values)
                    if values_valid:
                        st.session_state.parameters[new_param.strip()] = values_list
                        st.success(f"Added {new_param}")
                        st.session_state.clear_fields = True
                        st.rerun()
                    else:
                        st.error(values_error)
                else:
                    st.error(name_error)
        with col4:
            if st.button("Clear All", type="secondary", use_container_width=True):
                st.session_state.parameters = {}
                st.session_state.clear_fields = True
                st.success("All parameters cleared")
                st.rerun()

    # Edit existing parameters
    st.subheader("Current Parameters")
    
    # Create a container for parameters with custom styling
    with st.container():
        for param in list(st.session_state.parameters.keys()):
            # Add a visual separator between parameters
            st.markdown("---")
            
            # Create three columns with better proportions
            col1, col2, col3, col4 = st.columns([1, 2, 0.5, 0.5])
            
            with col1:
                st.markdown(f"**{param}**")
            
            with col2:
                values = st.text_input(
                    "Values",
                    value=", ".join(st.session_state.parameters[param]),
                    key=f"input_{param}",
                    label_visibility="collapsed"
                )
            
            with col3:
                if st.button("📝 Update", key=f"update_{param}", use_container_width=True):
                    values_valid, values_list, values_error = validate_parameter_values(values, current_param=param)
                    if not values_valid:
                        st.error(values_error)
                    else:
                        st.session_state.parameters[param] = values_list
                        st.success(f"Updated {param}")
            
            with col4:
                if st.button("🗑️ Delete", key=f"delete_{param}", use_container_width=True):
                    del st.session_state.parameters[param]
                    if len(st.session_state.parameters) == 1:
                        st.warning("Only 1 parameter remaining. Add more parameters to generate test cases.")
                    else:
                        st.success(f"Deleted {param}")
                    st.rerun()

    # Generate test cases section
    st.markdown("---")
    st.subheader("Generate Test Cases")
    
    # Center the generate button
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        generate_button = st.button("Generate Test Cases", use_container_width=True)
    
    if generate_button:
        # Validate the entire parameter set
        invalid_params = []
        for param, values in st.session_state.parameters.items():
            if len(values) < 2:
                invalid_params.append(param)
        
        if invalid_params:
            st.error(f"The following parameters need at least 2 values: {', '.join(invalid_params)}")
            return
        
        if len(st.session_state.parameters) < 2:
            st.error("Please add at least 2 parameters")
            return
            
        with st.spinner("Generating optimal test suite..."):
            if st.session_state.algorithm == 'CP-SAT':
                optimal_tests, all_pairs = algo.find_minimum_test_suite(st.session_state.parameters)
                if optimal_tests:
                    covered_pairs, test_case_pairs, new_unique_counts = algo.count_unique_pairs(
                        optimal_tests, all_pairs, st.session_state.parameters
                    )
            else:  # Greedy algorithm
                optimal_tests, all_pairs = greedyalgo.find_minimum_test_suite(st.session_state.parameters)
                if optimal_tests:
                    covered_pairs, test_case_pairs, new_unique_counts = greedyalgo.count_unique_pairs(
                        optimal_tests, all_pairs, st.session_state.parameters
                    )

            if optimal_tests:
                # Display results
                st.success("Test suite generated successfully!")
                
                # Metrics in a container with better spacing
                with st.container():
                    col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
                    with col2:
                        st.metric("Total Unique Pairs", len(all_pairs))
                    with col3:
                        st.metric("Total Test Cases", len(optimal_tests))

                # Create a table of test cases
                st.subheader("Test Cases")
                
                # Prepare data for the table
                table_data = []
                headers = ["Test Case #"] + list(st.session_state.parameters.keys()) + ["New Unique Pairs"]
                
                for i, test in enumerate(optimal_tests, 1):
                    row = [f"Test {i}"] + list(test) + [new_unique_counts[i-1]]
                    table_data.append(row)
                
                # Display as a DataFrame with improved styling
                import pandas as pd
                df = pd.DataFrame(table_data, columns=headers)
                st.dataframe(
                    df,
                    use_container_width=True,
                    hide_index=True
                )

            else:
                st.error("No optimal test suite found.")

if __name__ == "__main__":
    main() 