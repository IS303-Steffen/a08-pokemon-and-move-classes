max_score = 15  # This value is pulled by yml_generator.py to assign a score to this test.
from conftest import load_student_code, format_error_message, exception_message_for_students, normalize_text, prettify_dictionary
#from test_cases_classes_final import class_test_cases
from collections.abc import Iterable
import pytest

def test_06_move_get_info(test_cases, test_cases_classes):
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
        class_name = "Move"
        method_to_test = 'get_info'
        class_test_cases = {'class_name': class_name}
        class_test_cases['class_test_cases'] = test_cases_classes.get(class_name)
        class_test_cases['test_type'] = 'method_test'
        class_test_cases['method_to_test'] = method_to_test

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
            
            # get results of the methods we are looking at:
            method_results_list = [method_result for method_result in class_result.get('method_test_cases') if method_result.get('function_name') == method_to_test]
            
            for method_result in method_results_list:

                test_inputs = method_result.get('args')
                if test_inputs == []:
                    test_inputs_str = "No arguments besides \"self\""
                else:
                    test_inputs_str = ', '.join(str(item) for item in test_inputs)

                expected_return_value = normalize_text(method_result.get('expected_return_value'))
                actual_return_value = normalize_text(method_result.get('actual_return_value')[0])

                assert expected_return_value == actual_return_value, format_error_message(
                    custom_message=(f"When the method {method_to_test} is provided with the following argument(s) other than \"self\":\n\n"
                                    f"METHOD ARGUMENTS: {test_inputs_str}\n\n"
                                    f"the expected return value (ignoring capitalization / punctuation) is:\n\n"
                                    f"{expected_return_value}\n\n"
                                    f"However, your function is returning this value (ignoring capitalization / punctuation):\n\n"
                                    f"{actual_return_value}\n\n"
                                    f"Make sure your method is either returning a value (or not returning) according to the instructions and that the logic matches "
                                    f"what the instructions say. If the message above says your function is returning \"None\" when it shouldn't, "
                                    f"that means your function likely doesn't have a return statement. Make sure you are returning "
                                    f"a value, not just printing it out directly in the function."),
                    test_case=test_case,
                    )
                
                expected_object_updates_list = method_result.get('expected_object_update')
                if expected_object_updates_list:
                    for expected_object_update in expected_object_updates_list:
                        initial_value_found = False
                        student_var_name = None
                        expected_initial_value = normalize_text(expected_object_update.get('intial_value'))
                        expected_final_value = normalize_text(expected_object_update.get('final_value'))

                        initial_obj_state_vars = method_result.get('initial_obj_state')[0].get('instance_variables')
                        for var_name, initial_var_value in initial_obj_state_vars.items():
                            if normalize_text(initial_var_value) == expected_initial_value:
                                initial_value_found = True
                                student_var_name = var_name
                                break

                        assert initial_value_found, format_error_message(
                            custom_message=(f"The method {method_to_test} is provided with the following argument(s) other than \"self\":\n\n"
                                            f"METHOD ARGUMENTS: {test_inputs_str}\n\n"
                                            f"The {class_name} object is expected to contain a variable with the following expected value (ignoring capitalization / punctuation):\n\n"
                                            f"EXPECTED INITIAL VALUE: {expected_initial_value}\n\n"
                                            f"But no variables could be found that matched that value.\n\n"
                                            f"Make sure you are actually adding instance variables to the object by using \"self\". "
                                            f"Double check that you are following the logic provided in the instructions."),
                            test_case=test_case,
                            )
                        
                        actual_final_value = normalize_text(method_result.get('final_obj_state').get('instance_variables').get(student_var_name))

                        assert actual_final_value == expected_final_value, format_error_message(
                            custom_message=(f"The method {method_to_test} is provided with the following argument(s) other than \"self\":\n\n"
                                            f"METHOD ARGUMENTS: {test_inputs_str}\n\n"
                                            f"It is expected to update the {class_name} object in the following way (ignoring capitalization / punctuation):\n\n"
                                            f"EXPECTED INITIAL VALUE: {expected_initial_value}\n\n"
                                            f"SHOULD BECOME EXPECTED FINAL VALUE: {expected_final_value}\n\n"
                                            f"In your {class_name} object, this variable matched the expected iniital value:\n\n"
                                            f"YOUR INITIAL VALUE: {student_var_name}: {expected_initial_value}\n\n"
                                            f"But the final value of {student_var_name} after calling the method {method_to_test} was:\n\n"
                                            f"YOUR FINAL VALUE: {student_var_name}: {actual_final_value}\n\n"
                                            f"If your initial and final value are the same, make sure you are actually updating the object by changing an instance variable through \"self\". "
                                            f"Otherwise, double check that you are following the logic provided in the instructions."),
                            test_case=test_case,
                            )

            # # check if each expected value is present in the class

            # init_args = class_result['init_args']
            # init_args_str = [str(arg) for arg in init_args]
            # init_args_str = '\n'.join(init_args_str)
            # actual_values_normalized = normalize_text(class_result['actual_object'])
            # actual_values_normalized.pop('methods', None)
            # actual_values_normalized = prettify_dictionary(actual_values_normalized)

            # for expected_var_value, expected_var_type in class_result['init_expected_values'].items():
                
            #     if isinstance(expected_var_type, Iterable):
            #         types_str = ' or '.join([type.__name__ for type in expected_var_type])
            #     else:
            #         types_str = expected_var_type.__name__
                
            #     expected_value_found = False
            #     # if there is a variable with the correct value, it will pass the test. variable names don't matter.
            #     for actual_var_value in class_result['actual_object'].values():
            #         normalized_expected_value = normalize_text(expected_var_value)
            #         normalized_actual_value = normalize_text(actual_var_value)

            #         if normalized_expected_value == normalized_actual_value:
            #             expected_value_found = True
            #             break
                
            #     assert expected_value_found, format_error_message(
            #         custom_message=(f"When creating an object from your {class_name} class with the following arguments passed into your constructor:\n\n"
            #                         f"{init_args_str}\n\n"
            #                         f"The created object was expected to have this value (ignoring punctuation / capitalization):\n\n"
            #                         f"EXPECTED VALUE: {normalized_expected_value}\n\nEXPECTED DATA TYPE OF VALUE: {types_str}\n\n"
            #                         f"But no variable was found in your object that matched that value. "
            #                         f"Below are all the variables contained in your {class_name} object, ignoring punctuation / capitalization for both the variable name and value:\n\n"
            #                         f"{actual_values_normalized}\n\n"),
            #         test_case=test_case,
            #     )
        
    except AssertionError:
        raise
    except Exception as e:
        exception_message_for_students(e, test_case)

