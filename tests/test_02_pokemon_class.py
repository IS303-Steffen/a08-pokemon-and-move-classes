max_score = 15  # This value is pulled by yml_generator.py to assign a score to this test.
from conftest import load_student_code, format_error_message, exception_message_for_students, normalize_text, prettify_dictionary
#from test_cases_classes_final import class_test_cases
from collections.abc import Iterable
import pytest

def test_02_pokemon_class(current_test_name, input_test_cases, class_test_cases):
    try:
        # Ensure test_cases is valid and iterable
        if not isinstance(input_test_cases, list):
            input_test_case = {"id_input_test_case": None}
            exception_message_for_students(ValueError("input_test_cases should be a list of dictionaries. Contact your professor."), input_test_case, current_test_name) 
            return  # Technically not needed, as exception_message_for_students throws a pytest.fail Error, but included for clarity that this ends the test.

        # Use the appropriate test case
        input_test_case = input_test_cases[0]
        inputs = input_test_case["inputs"]

        # Name of the class being tested:
        class_name = "Pokemon"
        class_test_cases_payload = {'class_name': class_name}
        class_test_cases_payload['class_test_cases'] = class_test_cases.get(class_name)
        class_test_cases_payload['test_type'] = 'class_test'

        # Load the student's code and test classes
        manager_payload = load_student_code(current_test_name, inputs, input_test_case, class_tests=class_test_cases_payload)

        # first check if there was an error trying to run the code
        if manager_payload.get('class_results').get('CLASS ERROR') is not None:
            custom_message = f"{manager_payload.get('class_results').get('CLASS ERROR').get('message')}\n\n"
            formatted_message = format_error_message(
                                    custom_message=custom_message, 
                                    input_test_case=input_test_case,
                                    current_test_name=current_test_name)
            pytest.fail(formatted_message)

        class_results_list = manager_payload.get('class_results').get('class_test_cases')

        # loop through each class test case
        for class_result in class_results_list:
            # check if each expected value is present in the class

            for expected_var_name, expected_var_value in class_result['init_expected_values'].items():
                        
                # Checks for a match among the variable names (normalized) and values (normalized)
                expected_value_found = False
                for actual_var_name, actual_var_value in class_result['actual_object'].items():
                    # check the variable names
                    normalized_expected_name = normalize_text(expected_var_name)
                    normalized_actual_name = normalize_text(actual_var_name)
                    expected_name_match = normalized_expected_name == normalized_actual_name

                    # check the variable values
                    normalized_expected_value = normalize_text(expected_var_value)
                    normalized_actual_value = normalize_text(actual_var_value)
                    expected_value_match = normalized_expected_value == normalized_actual_value

                    if expected_name_match and expected_value_match:
                        expected_value_found = True
                        break

                # if the test is going to fail, prep all the error message strings:    
                if not expected_value_found:

                    # Get the initial arguments for the object
                    init_args = class_result['init_args']
                    init_args_str = '\n'.join([f"{parameter}: {argument}" for parameter, argument in init_args.items()])
                    
                    # Because I serialize custom objects into dictionaries, I need to overwrite the default datatype in
                    # the error message for variables that should be holding custom objects to make the error messages clearer.
                    types = {} # if the object should have other custom objects inside it, list the variable names and their class name here.
                    type_str = types.get(expected_var_name, type(expected_var_value).__name__)
                    
                    normalized_expected_value = prettify_dictionary(normalized_expected_value)

                    actual_obj_values_normalized = normalize_text(class_result['actual_object'])
                    actual_obj_values_normalized.pop('methods', None)
                    actual_obj_values_normalized = prettify_dictionary(actual_obj_values_normalized)

                    for original, replacement in [('soccerteam', '__'), ('sponsoredteam', '__')]:
                        normalized_expected_name = normalized_expected_name.replace(original, replacement)
                        normalized_expected_value = str(normalized_expected_value).replace(original, replacement)
                        actual_obj_values_normalized = actual_obj_values_normalized.replace(original, replacement)

                assert expected_value_found, format_error_message(
                    custom_message=(f"When creating an object from your {class_name} class with the following arguments passed into your constructor:\n\n"
                                    f"{init_args_str}\n\n"
                                    f"The created object was expected to have a variable with this name and value (ignoring punctuation / capitalization):\n\n"
                                    f"EXPECTED VARIABLE NAME:\n"
                                    f"-----------------------\n"
                                    f"{normalized_expected_name}\n\n"
                                    f"EXPECTED DATA TYPE:\n"
                                    f"-------------------\n"
                                    f"{type_str}\n\n"
                                    f"EXPECTED VALUE:\n"
                                    f"---------------\n"
                                    f"{normalized_expected_value}\n\n"
                                    f"But no variable was found in your object with a matching variable name and value. "
                                    f"Below are all the variables contained in your {class_name} object, ignoring punctuation / capitalization for both the variable name and value:\n\n"
                                    f"YOUR ACTUAL OBJECT:\n"
                                    f"---------------\n"
                                    f"{actual_obj_values_normalized}\n\n"),
                    current_test_name=current_test_name,
                    input_test_case=input_test_case,
                )
        
    except AssertionError:
        raise
    except Exception as e:
        exception_message_for_students(e, input_test_case, current_test_name)
