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


def test_07_move_generate_attack_value(current_test_name, input_test_cases, class_test_cases):
    try:
        rec = pc_get_or_create(current_test_name, max_score)
        # Ensure test_cases is valid and iterable
        if not isinstance(input_test_cases, list):
            input_test_case = {"id_test_case": None}
            exception_message_for_students(ValueError("test_cases should be a list of dictionaries. Contact your professor."), test_case=input_test_case) 
            return  # Technically not needed, as exception_message_for_students throws a pytest.fail Error, but included for clarity that this ends the test.

        # Use the appropriate test case
        input_test_case = input_test_cases[0]
        inputs = input_test_case["inputs"]

        # Name of the class being tested:
        class_name = "Move"
        method_to_test = 'generate_attack_value'
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
            
            for index, method_result in enumerate(method_results_list, start=1):

                expected_return_value_tuple = normalize_text(method_result.get('expected_return_value'))
                actual_return_values_list = normalize_text(method_result.get('actual_return_value'))

                found_value_outside_range = False

                for actual_return_value in actual_return_values_list:
                    low_bound, high_bound = expected_return_value_tuple
                    try:
                        if not (low_bound <= actual_return_value and actual_return_value <= high_bound):
                            found_value_outside_range = True
                            break
                    except TypeError:
                        found_value_outside_range = True
                        break


                if found_value_outside_range:
                    formatted = format_error_message(
                    custom_message=(f"When the values for the low and high attack values are {low_bound} and {high_bound}, the method {method_to_test} is expected to return a value (inclusive) between:\n"
                                    f"```\n{low_bound} and {high_bound}\n```\n"
                                    f"However, your function sometimes returns this value:\n"
                                    f"```\n{actual_return_value}\n```\n"
                                    f"Make sure your method is either returning a value according to the instructions and that the logic matches "
                                    f"what the instructions say. If the message above says your function is returning \"None\" when it shouldn't, "
                                    f"that means your function likely doesn't have a return statement. Make sure you are returning "
                                    f"a value, not just printing it out directly in the function."),
                    input_test_case=input_test_case,
                    current_test_name=current_test_name
                    )
                    rec.fail_case(case_id=f"method:{class_name}-{method_to_test}:{index}",  custom_message=formatted, case_type="method")
                else:
                    rec.pass_case(case_id=f"method:{class_name}-{method_to_test}:{index}", case_type="method")

    except AssertionError:
        raise
    except Exception as e:
        exception_message_for_students(e, input_test_case, current_test_name)
    finally:
        pc_finalize_and_maybe_fail(rec)
