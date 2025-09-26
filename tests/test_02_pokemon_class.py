max_score = 10  # This value is pulled by yml_generator.py to assign a score to this test.
from conftest import (
    normalize_text,
    load_student_code,
    format_error_message,
    exception_message_for_students,
    prettify_dictionary,
    pc_get_or_create,
    pc_finalize_and_maybe_fail,
    unmangle_keys,
    unmangle_name,
    default_module_to_test
)


def test_02_pokemon_class(current_test_name, input_test_cases, class_test_cases):
    try:
        rec = pc_get_or_create(current_test_name, max_score)
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

        if not manager_payload:
            return # if there was an error in running student code, it's already been logged. Just skip to the next test case.

        # first check if there was an error trying to run the code
        if manager_payload.get('class_results').get('CLASS ERROR') is not None:
            custom_message = f"{manager_payload.get('class_results').get('CLASS ERROR').get('message')}\n\n"
            formatted_message = format_error_message(
                                    custom_message=custom_message, 
                                    input_test_case=input_test_case,
                                    current_test_name=current_test_name)
            rec.fail_case(
                case_id=f"class:{class_name}:setup",
                custom_message=formatted_message,
                case_type="class",
                label=f"{class_name} (setup)"
            )
            return
            
        class_results_list = manager_payload.get('class_results').get('class_test_cases')

        # loop through each class test case
        for class_result in class_results_list:
            # check if each expected value is present in the class
            index = 1
            for expected_var_name, expected_var_value in class_result['init_expected_values'].items():
                        
                # Checks for a match among the variable names (normalized) and values (normalized)
                expected_value_found = False
                for actual_var_name, actual_var_value in class_result['actual_object'].get("__data__").items():
                    # check the variable names
                    normalized_expected_name = normalize_text(unmangle_name(expected_var_name))
                    normalized_actual_name = normalize_text(unmangle_name(actual_var_name))
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

                    # Unmangle all keys to logical names for a fair, name-style-agnostic comparison/readout
                    actual_data_unmangled = unmangle_keys(class_result['actual_object'].get("__data__"))
                    actual_data_unmangled.pop('methods', None)

                    # Normalize + prettify for the message
                    actual_obj_values_normalized = prettify_dictionary(normalize_text(actual_data_unmangled))
                    actual_obj_values_normalized = actual_obj_values_normalized.replace('wins', '__wins').replace('losses', '__losses')
                    normalized_expected_name_error_str = normalized_expected_name.replace('wins', '__wins').replace('losses', '__losses')

                    # the actual error message creation
                    formatted = format_error_message(
                        custom_message=(f"When creating an object from your {class_name} class with the following arguments passed into your constructor:\n"
                                        f"```\n{init_args_str}\n```\n"
                                        f"The created object was expected to have a variable with this name and value (ignoring punctuation / capitalization):\n\n"
                                        f"### Expected variable name:\n"
                                        f"```\n{normalized_expected_name_error_str}\n```\n"
                                        f"### Expected data type:\n"
                                        f"```\n{type_str}\n```\n"
                                        f"### Expected value:\n"
                                        f"```\n{normalized_expected_value}\n```\n"
                                        f"But no variable was found in your object with a matching variable name and value. Make sure you aren't misspelling a variable name. "
                                        f"Below are all the variables contained in your {class_name} object, ignoring punctuation / capitalization for both the variable name and value:\n\n"
                                        f"### Your actual {class_name} object:\n"
                                        f"```\n{actual_obj_values_normalized}\n```\n"),
                        current_test_name=current_test_name,
                        input_test_case=input_test_case,
                        )
                    rec.fail_case(
                    case_id=f"class:{class_name}:{index}",
                    custom_message=formatted,
                    case_type="class",
                    label=f"{class_name}: expected value: {normalized_expected_name}"
                    )
                else:
                    rec.pass_case(
                        case_id=f"class:{class_name}:{index}",
                        case_type="class",
                        label=f"{class_name}: expected value: {normalized_expected_name}"
                    )
                index += 1
        
    except AssertionError:
        raise
    except Exception as e:
        exception_message_for_students(e, input_test_case, current_test_name)
    finally:
        pc_finalize_and_maybe_fail(rec)

