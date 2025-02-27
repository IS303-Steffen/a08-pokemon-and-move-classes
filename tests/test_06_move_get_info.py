max_score = 15  # This value is pulled by yml_generator.py to assign a score to this test.
from conftest import load_student_code, format_error_message, exception_message_for_students, normalize_text, prettify_dictionary
#from test_cases_classes_final import class_test_cases
from collections.abc import Iterable
import pytest

def test_06_move_get_info(current_test_name, input_test_cases, class_test_cases):
    try:
        # Ensure test_cases is valid and iterable
        if not isinstance(input_test_cases, list):
            input_test_case = {"id_test_case": None}
            exception_message_for_students(ValueError("test_cases should be a list of dictionaries. Contact your professor."), input_test_case=input_test_case) 
            return  # Technically not needed, as exception_message_for_students throws a pytest.fail Error, but included for clarity that this ends the test.

        # Use the appropriate test case
        input_test_case = input_test_cases[0]
        inputs = input_test_case["inputs"]

        # Name of the class being tested:
        class_name = "Move"
        method_to_test = 'get_info'
        class_test_cases_payload = {'class_name': class_name}
        class_test_cases_payload['class_test_cases'] = class_test_cases.get(class_name)
        class_test_cases_payload['test_type'] = 'method_test'
        class_test_cases_payload['method_to_test'] = method_to_test

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

        elif manager_payload.get('class_results').get('FUNCTION ERROR') is not None:
            exception_message_for_students(
                exception_data=manager_payload.get('class_results').get('FUNCTION ERROR').get("FUNCTION ERROR"),
                input_test_case=input_test_case,
                current_test_name=current_test_name,
                )

        class_results_list = manager_payload.get('class_results').get('class_test_cases')

        # loop through each class test case
        for class_result in class_results_list:
            
            # get results of the methods we are looking at:
            method_results_list = [method_result for method_result in class_result.get('method_test_cases') if method_result.get('function_name') == method_to_test]
            
            if not method_results_list:
                pytest.fail(f"{exception_message_for_students(ValueError('No method test cases were found. Contact your professor.'), input_test_case, current_test_name)}")

            for method_result in method_results_list:
                # first check if there were any function errors when running the method:
                if method_result.get('FUNCTION ERROR') is not None:
                    exception_data = method_result.get('FUNCTION ERROR')
                    exception_message_for_students(
                        exception_data=exception_data,
                        input_test_case=input_test_case,
                        current_test_name=current_test_name,
                        )
                    
                test_inputs = method_result.get('args')
                if test_inputs == []:
                    test_inputs_str = "No arguments besides \"self\""
                else:
                    test_inputs_str = ', '.join(str(item) for item in test_inputs)

                expected_return_value = normalize_text(method_result.get('expected_return_value'))
                actual_return_value = normalize_text(method_result.get('actual_return_value')[0])

                assert expected_return_value == actual_return_value, format_error_message(
                    custom_message=(f"When the method {method_to_test} is provided with the following argument(s) other than \"self\":\n\n"
                                    f"METHOD ARGUMENTS:\n"
                                    f"-----------------\n"
                                    f"{test_inputs_str}\n\n"
                                    f"the expected return value (ignoring capitalization / punctuation) is:\n\n"
                                    f"EXPECTED RETURN VALUE:\n"
                                    f"----------------------\n"
                                    f"{expected_return_value}\n\n"
                                    f"However, your function is returning this value (ignoring capitalization / punctuation):\n\n"
                                    f"YOUR RETURN VALUE:\n"
                                    f"------------------\n"
                                    f"{actual_return_value}\n\n"
                                    f"Make sure your method is either returning a value (or not returning) according to the instructions and that the logic matches "
                                    f"what the instructions say. If the message above says your function is returning \"None\" when it shouldn't, "
                                    f"that means your function likely doesn't have a return statement. Make sure you are returning "
                                    f"a value, not just printing it out directly in the function."),
                    current_test_name=current_test_name,
                    input_test_case=input_test_case,
                    )
                
                expected_object_updates_list = method_result.get('expected_object_update')
                if expected_object_updates_list:
                    for run_index, (expected_update_variable_name, expected_update_values) in enumerate(expected_object_updates_list.items()):
                        initial_value_found = False
                        student_var_name = None
                        normalized_expected_name = normalize_text(expected_update_variable_name)
                        normalized_expected_initial_value = normalize_text(expected_update_values.get('initial_value'))
                        normalized_expected_final_value = normalize_text(expected_update_values.get('final_value'))

                        initial_obj_state_vars = method_result.get('initial_obj_state')[run_index].get('instance_variables')
                        initial_state_vars_str = '\n'.join([f"{normalize_text(name)}: {normalize_text(value)}" for name, value in initial_obj_state_vars.items()])
                        for actual_var_name, initial_var_value in initial_obj_state_vars.items():
                            # check the var names:
                            normalized_actual_var_name = normalize_text(actual_var_name)
                            expected_name_match = normalized_actual_var_name == normalized_expected_name

                            # check the var values:
                            normalized_actual_initial_var_value = normalize_text(initial_var_value)
                            exepcted_value_match = normalized_actual_initial_var_value == normalized_expected_initial_value

                            if expected_name_match and exepcted_value_match:
                                initial_value_found = True
                                student_var_name = actual_var_name
                                normalized_student_var_name = normalize_text(student_var_name)
                                break
                        
                        for original, replacement in [('soccerteam', '__'), ('sponsoredteam', '__')]:
                            normalized_expected_name = normalized_expected_name.replace(original, replacement)
                            initial_state_vars_str= initial_state_vars_str.replace(original, replacement)
                        assert initial_value_found, format_error_message(
                            custom_message=(f"The method \"{method_to_test}\" is provided with the following argument(s) other than \"self\":\n\n"
                                            f"METHOD ARGUMENTS:\n"
                                            f"-----------------\n"
                                            f"{test_inputs_str}\n\n"
                                            f"The {class_name} object is expected to start out with the following variable and value (ignoring capitalization / punctuation):\n\n"
                                            f"EXPECTED INITIAL VALUE:\n"
                                            f"-----------------------\n"
                                            f"{normalized_expected_name}: {normalized_expected_initial_value}\n\n"
                                            f"But no variables could be found that matched that name.\n\n"
                                            f"Make sure you are actually adding instance variables to the object by using \"self\". "
                                            f"Double check that you are following the logic provided in the instructions.\n\n"
                                            f"Here are all the variables the test could find in your {class_name} object (ignoring capitalization / punctuation):\n\n"
                                            f"YOUR VARIABLES IN {class_name.upper()}:\n"
                                            f"{'-'*len('YOUR VARIABLES IN ' + class_name + ':')}\n"
                                            f"{initial_state_vars_str}"),
                            current_test_name=current_test_name,
                            input_test_case=input_test_case,
                            )
                        
                        normalized_actual_final_value = normalize_text(method_result.get('final_obj_state')[run_index].get('instance_variables').get(student_var_name))
                        
                        for original, replacement in [('soccerteam', '__'), ('sponsoredteam', '__')]:
                            normalized_student_var_name = normalized_student_var_name.replace(original,replacement)

                        assert normalized_actual_final_value == normalized_expected_final_value, format_error_message(
                            custom_message=(f"The method {method_to_test} is provided with the following argument(s) other than \"self\":\n\n"
                                            f"METHOD ARGUMENTS:\n"
                                            f"-----------------\n"
                                            f"{test_inputs_str}\n\n"
                                            f"It is expected to update the {class_name} object in the following way (ignoring capitalization / punctuation):\n\n"
                                            f"EXPECTED INITIAL VALUE:\n"
                                            f"-----------------------\n"
                                            f"{normalized_expected_name}: {normalized_expected_initial_value}\n\n"
                                            f"SHOULD BECOME EXPECTED FINAL VALUE:\n"
                                            f"-----------------------------------\n"
                                            f"{normalized_expected_name}: {normalized_expected_final_value}\n\n"
                                            f"In your {class_name} object, this was your initial value:\n\n"
                                            f"YOUR INITIAL VALUE:\n"
                                            f"-------------------\n"
                                            f"{normalized_student_var_name}: {normalized_actual_initial_var_value}\n\n"
                                            f"But the final value of {normalized_student_var_name} after calling the method {method_to_test} was:\n\n"
                                            f"YOUR FINAL VALUE:\n"
                                            f"-----------------\n"
                                            f"{normalized_student_var_name}: {normalized_actual_final_value}\n\n"
                                            f"If your initial and final value are the same, make sure you are actually updating the object by changing an instance variable through \"self\". "
                                            f"Otherwise, double check that you are following the logic provided in the instructions."),
                            current_test_name=current_test_name,
                            input_test_case=input_test_case,
                            )        
    
    except AssertionError:
        raise
    except Exception as e:
        exception_message_for_students(e, input_test_case, current_test_name)

