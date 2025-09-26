max_score = 15  # This value is pulled by yml_generator.py to assign a score to this test.
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

def test_04_pokemon_get_info(current_test_name, input_test_cases, class_test_cases):
    try:
        rec = pc_get_or_create(current_test_name, max_score)
        # Ensure test_cases is valid and iterable
        if not isinstance(input_test_cases, list):
            input_test_case = {"id_test_case": None}
            exception_message_for_students(ValueError("test_cases should be a list of dictionaries. Contact your professor."), input_test_case=input_test_case) 
            return  # Technically not needed, as exception_message_for_students throws a pytest.fail Error, but included for clarity that this ends the test.

        # Use the appropriate test case
        input_test_case = input_test_cases[0]
        inputs = input_test_case["inputs"]

        # Name of the class being tested:
        class_name = "Pokemon"
        method_to_test = 'get_info'
        class_test_cases_payload = {'class_name': class_name}
        class_test_cases_payload['class_test_cases'] = class_test_cases.get(class_name)
        class_test_cases_payload['test_type'] = 'method_test'
        class_test_cases_payload['method_to_test'] = method_to_test

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

        elif manager_payload.get('class_results').get('FUNCTION ERROR') is not None:
            exception_message_for_students(
                exception_data=manager_payload.get('class_results').get('FUNCTION ERROR').get("FUNCTION ERROR"),
                input_test_case=input_test_case,
                current_test_name=current_test_name,
                )
            return # the failure is already recorded by the function above, so just end this test.

        class_results_list = manager_payload.get('class_results').get('class_test_cases')


        # loop through each class test case
        for class_result in class_results_list:
            
            # get results of the methods we are looking at:
            method_results_list = [method_result for method_result in class_result.get('method_test_cases') if method_result.get('function_name') == method_to_test]
            
            if not method_results_list:
                exception_message_for_students(ValueError("No method test cases were found. Contact your professor."), input_test_case, current_test_name)
                return

            case_failed_messages = []  # collect case's failure messages (exactly as before)
            for index, method_result in enumerate(method_results_list, start=1):
                # first check if there were any function errors when running the method:
                if method_result.get('FUNCTION ERROR') is not None:
                    exception_message_for_students(
                                            exception_data=method_result.get('FUNCTION ERROR'), 
                                            input_test_case=input_test_case,
                                            current_test_name=current_test_name,
                                            )
                    return
                    
                test_inputs = method_result.get('args')
                if test_inputs == []:
                    test_inputs_str = "No arguments besides \"self\""
                else:
                    test_inputs_str = ', '.join(str(item) for item in test_inputs)

                expected_return_value = normalize_text(method_result.get('expected_return_value'))
                actual_return_value = normalize_text(method_result.get('actual_return_value')[0])
                
                if not expected_return_value == actual_return_value:
                    formatted = format_error_message(
                        custom_message=(f"When the method {method_to_test} is provided with the following argument(s) other than \"self\":\n\n"
                                        f"### Method arguments:\n"
                                        f"```\n{test_inputs_str}\n```\n"
                                        f"the expected return value (ignoring capitalization / punctuation) is:\n\n"
                                        f"### Expected return value:\n"
                                        f"```\n{expected_return_value} (data type: {type(expected_return_value).__name__})\n```\n"
                                        f"However, your method is returning this value (ignoring capitalization / punctuation):\n\n"
                                        f"### Your return value:\n"
                                        f"```\n{actual_return_value} (data type: {type(actual_return_value).__name__})\n```\n"
                                        f"Make sure your method is either returning a value (or not returning) according to the instructions and that the logic matches "
                                        f"what the instructions say. If the message above says your function is returning \"None\" when it shouldn't, "
                                        f"that means your function likely doesn't have a return statement. Make sure you are returning "
                                        f"a value, not just printing it out directly in the function."),
                        current_test_name=current_test_name,
                        input_test_case=input_test_case,
                        )
                    case_failed_messages.append(formatted)

                
                expected_object_updates_list = method_result.get('expected_object_update')
                if expected_object_updates_list:
                    for run_index, (expected_update_variable_name, expected_update_values) in enumerate(expected_object_updates_list.items()):
                        initial_value_found = False
                        student_var_name = None  # keep the ORIGINAL key we matched so we can read final value consistently

                        # Compare on logical names (unmangled) then normalize for punctuation/case-insensitive compare
                        logical_expected_name = unmangle_name(expected_update_variable_name)
                        normalized_expected_name = normalize_text(logical_expected_name)
                        normalized_expected_initial_value = normalize_text(expected_update_values.get('initial_value'))
                        normalized_expected_final_value   = normalize_text(expected_update_values.get('final_value'))

                        # Unmangle ALL keys for the student’s initial state (for fair compare + nicer messages)
                        initial_obj_state_vars_raw = method_result.get('initial_obj_state')[run_index].get('instance_variables')
                        initial_obj_state_vars_unmangled = unmangle_keys(initial_obj_state_vars_raw)

                        # Pretty string for the failure message (use unmangled keys)
                        initial_state_vars_str = '\n'.join(
                            f"{normalize_text(k)}: {normalize_text(v)}"
                            for k, v in initial_obj_state_vars_unmangled.items()
                        )

                        # Try to find the matching var by logical name + initial value
                        for actual_var_name_raw, initial_var_value in initial_obj_state_vars_raw.items():
                            # Compare names on logical form
                            logical_actual_name = unmangle_name(actual_var_name_raw)
                            normalized_actual_var_name = normalize_text(logical_actual_name)
                            expected_name_match = (normalized_actual_var_name == normalized_expected_name)

                            # Compare initial values
                            normalized_actual_initial_var_value = normalize_text(initial_var_value)
                            expected_value_match = (normalized_actual_initial_var_value == normalized_expected_initial_value)

                            if expected_name_match and expected_value_match:
                                initial_value_found = True
                                student_var_name = actual_var_name_raw  # store ORIGINAL key for reading final state
                                normalized_student_var_name = normalize_text(logical_actual_name)
                                break
                        normalized_expected_name_str = normalized_expected_name.replace('wins', '__wins').replace('losses', '__losses')
                        initial_state_vars_str = initial_state_vars_str.replace('wins', '__wins').replace('losses', '__losses')
                        if not initial_value_found:
                            formatted = format_error_message(
                                custom_message=(f"The method `{method_to_test}` is provided with the following argument(s) other than \"self\":\n"
                                                f"### Method arguments:\n"
                                                f"```\n{test_inputs_str}\n```\n"
                                                f"The {class_name} object is expected to start out with the following variable and value (ignoring capitalization / punctuation):\n"
                                                f"### Expected initial value:\n"
                                                f"```\n{normalized_expected_name_str}: {normalized_expected_initial_value} (data type: {type(normalized_expected_initial_value).__name__})\n```\n"
                                                f"But either no variables could be found that matched that name, or the initial value of the variable didn't match. \n\n"
                                                f"Make sure you are actually adding instance variables to the object by using \"self\". "
                                                f"Double check that you are following the logic provided in the instructions.\n\n"
                                                f"Here are all the variables the test could find in your `{class_name}` object (ignoring capitalization / punctuation):\n\n"
                                                f"### Your variables in {class_name}:\n"
                                                f"```\n{initial_state_vars_str}\n```\n"),
                                current_test_name=current_test_name,
                                input_test_case=input_test_case,
                                )
                            case_failed_messages.append(formatted)
                        
                        # only check the updated value if the initial value actually matches.
                        if initial_value_found:
                            normalized_actual_final_value = normalize_text(
                                method_result.get('final_obj_state')[run_index].get('instance_variables').get(student_var_name)
                            )

                            if not normalized_actual_final_value == normalized_expected_final_value:
                                formatted = format_error_message(
                                    custom_message=(f"The method `{method_to_test}` is provided with the following argument(s) other than \"self\":\n"
                                                    f"### Method arguments:\n"
                                                    f"```\n{test_inputs_str}\n```\n"
                                                    f"It is expected to update the {class_name} object in the following way (ignoring capitalization / punctuation):\n"
                                                    f"### Expected initial value:\n"
                                                    f"```\n{normalized_expected_name}: {normalized_expected_initial_value} (data type: {type(normalized_expected_initial_value).__name__})\n```\n"
                                                    f"### Should become the expected final value:\n"
                                                    f"```\n{normalized_expected_name}: {normalized_expected_final_value} (data type: {type(normalized_expected_final_value).__name__})\n```\n"
                                                    f"In your {class_name} object, this was your initial value:\n"
                                                    f"### Your initial value:\n"
                                                    f"```\n{normalized_student_var_name}: {normalized_actual_initial_var_value} (data type: {type(normalized_actual_initial_var_value).__name__})\n```\n"
                                                    f"But the final value of {normalized_student_var_name} after calling the method `{method_to_test}` was:\n"
                                                    f"### Your final value:\n"
                                                    f"```\n{normalized_student_var_name}: {normalized_actual_final_value} (data type: {type(normalized_actual_final_value).__name__})\n```\n"
                                                    f"If your initial and final value are the same, make sure you are actually updating the object by changing an instance variable through \"self\". "
                                                    f"Otherwise, double check that you are following the logic provided in the instructions."),
                                    current_test_name=current_test_name,
                                    input_test_case=input_test_case,
                                    )        
                                case_failed_messages.append(formatted)

                # Record the case result for partial credit
                if case_failed_messages:
                    # Join multiple messages (if both a required and invalid check failed)
                    full_msg = "\n\n".join(case_failed_messages)
                    rec.fail_case(case_id=f"method:{class_name}-{method_to_test}:{index}",  custom_message=full_msg, case_type="method")
                else:
                    rec.pass_case(case_id=f"method:{class_name}-{method_to_test}:{index}", case_type="method")

    except AssertionError:
        raise
    except Exception as e:
        exception_message_for_students(e, input_test_case, current_test_name)
    finally:
        pc_finalize_and_maybe_fail(rec)