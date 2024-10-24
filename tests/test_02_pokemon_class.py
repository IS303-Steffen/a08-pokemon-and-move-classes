max_score = 15  # This value is pulled by yml_generator.py to assign a score to this test.
from conftest import load_student_code, format_error_message, exception_message_for_students, normalize_text, prettify_dictionary
#from test_cases_classes_final import class_test_cases
from collections.abc import Iterable
import pytest

def test_02_pokemon_class(test_cases, test_cases_classes):
    try:
        # Ensure test_cases is valid and iterable
        if not isinstance(test_cases, list):
            test_case = {"id_test_case": None}
            exception_message_for_students(ValueError("test_cases should be a list of dictionaries. Contact your professor."), test_case=test_case) 
            return  # Technically not needed, as exception_message_for_students throws a pytest.fail Error, but included for clarity that this ends the test.

        # Use the appropriate test case
        test_case = test_cases[0]
        inputs = test_case["inputs"]

        # Name of the class being tested:
        class_name = "Pokemon"
        class_test_cases = {'class_name': class_name}
        class_test_cases['class_test_cases'] = test_cases_classes.get(class_name)
        class_test_cases['test_type'] = 'class_test'

        # Load the student's code and test classes
        queue_payload = load_student_code(inputs, test_case, class_tests=class_test_cases)

        # first check if there was an error trying to run the code
        if queue_payload.get('class_results').get('CLASS ERROR') is not None:
            pytest.fail(f"{format_error_message(
                custom_message=(f"{queue_payload.get('class_results').get('CLASS ERROR')}\n\n"), 
                test_case=test_case,
                )}")

        class_results_list = queue_payload.get('class_results').get('class_test_cases')

        # loop through each class test case
        for class_result in class_results_list:
            # check if each expected value is present in the class

            init_args = class_result['init_args']
            init_args_str = [str(arg) for arg in init_args]
            init_args_str = '\n'.join(init_args_str)
            actual_values_normalized = normalize_text(class_result['actual_object'])
            actual_values_normalized.pop('methods', None)
            actual_values_normalized = prettify_dictionary(actual_values_normalized)

            for expected_var_value, expected_var_type in class_result['init_expected_values'].items():
                
                if isinstance(expected_var_type, Iterable):
                    types_str = ' or '.join([type.__name__ for type in expected_var_type])
                else:
                    types_str = expected_var_type.__name__
                
                expected_value_found = False
                # if there is a variable with the correct value, it will pass the test. variable names don't matter.
                for actual_var_value in class_result['actual_object'].values():
                    normalized_expected_value = normalize_text(expected_var_value)
                    normalized_actual_value = normalize_text(actual_var_value)

                    if normalized_expected_value == normalized_actual_value:
                        expected_value_found = True
                        break
                
                assert expected_value_found, format_error_message(
                    custom_message=(f"When creating an object from your {class_name} class with the following arguments passed into your constructor:\n\n"
                                    f"{init_args_str}\n\n"
                                    f"The created object was expected to have this value (ignoring punctuation / capitalization):\n\n"
                                    f"EXPECTED VALUE: {normalized_expected_value}\n\nEXPECTED DATA TYPE OF VALUE: {types_str}\n\n"
                                    f"But no variable was found in your object that matched that value. "
                                    f"Below are all the variables contained in your {class_name} object, ignoring punctuation / capitalization for both the variable name and value:\n\n"
                                    f"{actual_values_normalized}\n\n"),
                    test_case=test_case,
                )
        
    except AssertionError:
        raise
    except Exception as e:
        exception_message_for_students(e, test_case)

