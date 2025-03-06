max_score = 9  # This value is pulled by yml_generator.py to assign a score to this test.
from conftest import normalize_text, load_student_code, format_error_message, exception_message_for_students, round_match
import re

# Checks if the expected printed messages actually appear, but doesn't check for specific inputs or correct calculations.
def test_01_printed_messages(current_test_name, input_test_cases):
    try:
        # Ensure test_cases is valid and iterable
        if not isinstance(input_test_cases, list):
            test_case = {"id_test_case": None}
            exception_message_for_students(ValueError("test_cases should be a list of dictionaries. Contact your professor."), test_case=test_case) 
            return  # Technically not needed, as exception_message_for_students throws a pytest.fail Error, but included for clarity that this ends the test.

        # this is just a lazy way to prevent students from sometimes passing and sometimes not if they are accidentally displaying data for the same move
        # multiple times instead of 3 distinct moves
        for _ in range(15):
            expected_get_info_messages = [
                "Quick Attack (Type: Normal): 6 to 25 Attack Points",
                "Tackle (Type: Normal): 5 to 20 Attack Points",
                "Flamethrower (Type: Fire): 5 to 30 Attack Points",
                "Ember (Type: Fire): 10 to 20 Attack Points",
                "Hydro Pump (Type: Water): 20 to 25 Attack Points",
                "Solar Beam (Type: Grass): 18 to 27 Attack Points",
                "Slash (Type: Normal): 10 to 30 Attack Points",
                "Vine Whip (Type: Grass): 10 to 25 Attack Points",
                "Water Gun (Type: Water): 5 to 15 Attack Points",
            ]

            expected_get_info_messages.sort()

            expected_get_info_messages_normalized = [normalize_text(message) for message in expected_get_info_messages]
            expected_get_info_messages_normalized = [re.sub(r'\d+(?:\.\d+)?', "<any number>", message) for message in expected_get_info_messages_normalized]
            expected_get_info_messages_normalized_str = '\n'.join(expected_get_info_messages_normalized)

            expected_printed_messages = [
                'Charmander - Type: Fire - Hit Points: 55',
                'Charmander has been healed to 70 hit points.',
                'Charmander - Type: Fire - Hit Points: 70',
                'Bulbasaur - Type: Grass - Hit Points: 60',
                'Charmander - Type: Fire - Hit Points: 70',
                'Squirtle - Type: Water - Hit Points: 65',
                'Generated attack value: 5']
            
            expected_printed_messages.sort()
            
            # Use the appropriate test case
            test_case = input_test_cases[0]
            inputs = test_case["inputs"]

            # Load in the student's code and capture output
            queue_payloads = load_student_code(inputs, input_test_cases[0])

            captured_output = queue_payloads.get('captured_output')
            
            # Split the captured output into lines
            captured_lines = captured_output.splitlines()
            captured_lines.sort()

            # Normalize the captured output to remove spaces, punctuation, and symbols
            normalized_captured_print_statements = [normalize_text(captured_print) for captured_print in captured_lines]

            # add regex for any number for the generated attack value portion:
            
            normalized_captured_print_statements = '\n'.join(normalized_captured_print_statements)
            normalized_captured_print_statements = re.sub(r'\d+(?:\.\d+)?', round_match, normalized_captured_print_statements)

            normalized_captured_print_statements = re.sub(r'\d+(?:\.\d+)?', "<any number>", normalized_captured_print_statements)
            # first check if at least 5 of the get_info() phrases are found:
            phrase_counter = 0

            for expected_get_info in expected_get_info_messages_normalized:
                if re.search(expected_get_info, normalized_captured_print_statements):
                    phrase_counter += 1
            
            assert phrase_counter == 3, format_error_message(
                    custom_message=(f"Exactly 3 of the following phrases need to appear in your code (ignoring punctuation / capitalization):\n\n"
                                    f"{expected_get_info_messages_normalized_str}\n\n"
                                    f"However, {phrase_counter} were found in your code. Be sure to double check your spelling and make sure "
                                    f"you aren't printing the same message twice."
                                    f"Below are all the printed messages from your code (ignoring punctuation / capitalization):\n\n"
                                    f"{normalized_captured_print_statements}\n\n"),
                    current_test_name=current_test_name
                )


            # Check that each required phrase (regex pattern) is found in the normalized captured output
            for expected_phrase in expected_printed_messages:
                # Ensure the expected phrase is normalized as well
                expected_phrase = normalize_text(expected_phrase)

                # Convert any floats to an identical rounding method
                expected_phrase = re.sub(r'\d+(?:\.\d+)?', round_match, expected_phrase)
                expected_phrase = re.sub(r'\d+(?:\.\d+)?', "<any number>", expected_phrase)
                # if there are numbers that can vary, allow any number to match.
                if "generated attack value" in expected_phrase:
                    error_message_version = re.sub(r'\d+', '<any number>', expected_phrase)
                    expected_phrase = re.sub(r'\d+', r'\\d+', expected_phrase)

                # Check if the pattern exists in the normalized captured print statements
                match = re.search(expected_phrase, normalized_captured_print_statements)

                expected_phrase = error_message_version if 'error_message_version' in locals() else expected_phrase
                assert match, format_error_message(
                    custom_message=("The expected printed message (ignoring punctuation / capitalization):\n\n"
                                    f"\"{expected_phrase}\"\n\n"
                                    f"wasn't printed in your code.\n\n"
                                    f"Below are all the printed messages from your code (ignoring punctuation / capitalization):\n\n"
                                    f"{normalized_captured_print_statements}\n\n"),
                    current_test_name=current_test_name
                )

    # assert raises an AssertionError, but I don't want to actually catch it
    # this is just so I can have another Exception catch below it in case
    # anything else goes wrong.
    except AssertionError:
        raise
    
    except Exception as e:
        # Handle other exceptions
        input_test_case = {"id_input_test_case": None, "input_test_case_description": None}
        exception_message_for_students(e, input_test_case, current_test_name)
    