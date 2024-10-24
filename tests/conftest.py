'''
conftest.py is a configuration file automatically accessed by pytest
any @pytest.fixture created here is available to any other test file
if they reference it as a parameter.
'''

import pytest, re, sys, os, json, traceback, pickle, inspect, multiprocessing, ast, importlib
from io import StringIO
from collections.abc import Iterable
from tests.class_test_cases import test_cases_classes_dict


# ================
# GLOBAL VARIABLES
# ================

# Enter the name of the file to be tested here, but leave out the .py file extention.
solution_module = "a8_solution_pokemon_and_move_classes"
student_module = "a8_pokemon_and_move_classes"

def detect_module(solution_module, student_module):
    if os.path.exists(f"{solution_module}.py"):
        return solution_module
    elif os.path.exists(f"{student_module}.py"):
        return student_module
    else:
        return "PATH NOT FOUND"

#default_module_to_test = "a6_function_smorgasbord"#detect_module(solution_module, student_module)
default_module_to_test = detect_module(solution_module, student_module)

# default per-test-case timeout amount in seconds:
default_timeout_seconds = 6

# default decimal place to round to for regex comparisons
# helpful for accounting for different rounding methods students could use.
global_decimal_places = 2

# global that keeps track of exceptions raised within a subprocess.
raised_exceptions = []

# Path to the directory containing this file
CURRENT_DIR = os.path.dirname(__file__)

# ========
# FIXTURES
# ========

@pytest.fixture
def test_cases():
    # Path to the final captured test cases JSON file
    captured_test_cases_file = os.path.join(CURRENT_DIR, 'test_cases_final.json')
    
    # Load the test cases
    with open(captured_test_cases_file, 'r') as f:
        test_cases = json.load(f)
    
    return test_cases

@pytest.fixture
def test_cases_classes(): 
    return test_cases_classes_dict

# =====
# HOOKS
# =====

# Global set to track which tests have been run
_run_tests = set()

# Hook that runs before each test is executed
@pytest.hookimpl(tryfirst=True)
def pytest_runtest_call(item):
    """
    I sometimes use this in testing to make sure tests work regardless of the order
    they are run in. Currently not called
    """
    test_name = item.nodeid  # Get the test's identifier (e.g., file path + test name)
    
    if test_name not in _run_tests:
        print(f"First time running {test_name}")
        _run_tests.add(test_name)
    else:
        print(f"{test_name} has already been run in this session")


def pytest_sessionfinish():
    """
    This is a keyword name of a function for pytest.
    It will run automatically when done with
    a session of pytest. I used to have cleanup logic here, but
    after refactoring it was no longer necessary. If I need cleanup
    again, place logic here.
    """
    pass

# =================================
# RUNNING STUDENT CODE SUBPROCESSES
# =================================

def load_student_code(inputs, test_case=None, module_to_test=default_module_to_test,
                      function_tests=None, class_tests=None):
    """
    Loads the student's code in a subprocess with mocked inputs to prevent hanging the main test process.

    If code is successfully executed, will return:
    captured_input_prompts, captured_output, module_globals, function_results, class_results, raised_exceptions
    """
    try:
        # Create a Manager object and dictionary to communicate with the subprocess
        manager = multiprocessing.Manager()
        shared_data = manager.dict()

        # Start the subprocess
        p = multiprocessing.Process(target=_load_student_code_subprocess,
                                    args=(shared_data, inputs, test_case, module_to_test, function_tests, class_tests))
        p.start()

        # Wait for the subprocess to finish, or continue if the timeout limit is reached
        p.join(default_timeout_seconds)

        if p.is_alive():
            # Subprocess is still running; terminate it
            p.terminate()
            p.join()  # Ensure the main program waits for the subprocess to fully terminate

            # Handle timeout
            pytest.fail(timeout_message_for_students(test_case))
        else:
            # Subprocess finished; get the result
            if 'status' in shared_data:
                status = shared_data['status']
                if status == 'success':
                    return shared_data['payload']
                elif status == 'exception':
                    exception_data = shared_data['payload']  # Exception data dictionary
                    exception_message_for_students(exception_data, test_case)
                else:
                    pytest.fail("Unexpected status from subprocess. Contact your professor.")
            else:
                pytest.fail("Subprocess finished without returning any data. Contact your professor.")
    except Exception as e:
        exception_message_for_students(e, test_case)


def _load_student_code_subprocess(shared_data, inputs, test_case, module_to_test, function_tests, class_tests):
    """
    Executes the student's code in a subprocess, capturing inputs, outputs, exceptions, and testing functions/classes.
    """
    try:
        # Prepare the mocked input function and capture variables
        queue_payload = {}
        captured_input_prompts = []
        input_iter = iter(inputs)

        def mock_input(prompt=''):
            if prompt == '':
                return ''
            elif normalize_text(prompt) == normalize_text("Press enter to continue..."):
                captured_input_prompts.append(prompt)
                return ''
            else:
                captured_input_prompts.append(prompt)
            try:
                return next(input_iter)
            except StopIteration:
                # Handle the case where there are more input() calls than provided inputs
                raise

        # Prepare the global namespace for exec()
        globals_dict = {
            '__name__': '__main__',  # Ensures that the if __name__ == '__main__' block runs
            'input': mock_input,     # Overrides input() in the student's code
        }

        # Prepare to capture 'main' function's locals
        main_locals = {}

        # Initialize raised_exceptions list
        raised_exceptions = []

        # Read the student's code from the file
        module_file_path = module_to_test + '.py'
        with open(module_file_path, 'r', encoding='utf-8', errors='replace') as f:
            code = f.read()

        # Build exception handlers mapping
        exception_handlers = get_exception_handlers_from_source(code)

        # Create the trace function using the closure
        trace_function = create_trace_function(main_locals, raised_exceptions, exception_handlers)

        # Set the trace function
        sys.settrace(trace_function)

        # Redirect sys.stdout to capture print statements
        old_stdout = sys.stdout
        sys.stdout = StringIO()

        # Execute the student's code within the controlled namespace
        exec(code, globals_dict)

        # Remove the trace function
        sys.settrace(None)

        # Capture the output printed by the student's code
        captured_output = sys.stdout.getvalue()

        # Reset sys.stdout
        sys.stdout = old_stdout

        # Test functions if provided
        if function_tests:
            function_results = test_functions(function_tests, globals_dict)
        else:
            function_results = {"No functions tested": "No functions tested"}

        # Test classes if provided
        if class_tests:
            class_results = test_classes(class_tests, globals_dict)
        else:
            class_results = {"No classes tested": "No classes tested"}

        # Collect global variables from the student's code
        module_globals = {k: v for k, v in globals_dict.items() if is_picklable(v)}

        # Add main_locals to module_globals under a special key
        module_globals['__main_locals__'] = main_locals
        
        # add each payload into a dictionary:
        queue_payload['captured_input_prompts'] = captured_input_prompts
        queue_payload['captured_output'] = captured_output
        queue_payload['module_globals'] = module_globals
        queue_payload['function_results'] = function_results
        queue_payload['class_results'] = class_results
        queue_payload['raised_exceptions'] = raised_exceptions

        # Send back the results
        shared_data['status'] = 'success'
        shared_data['payload'] = queue_payload

    except StopIteration as e:
        # Send the exception back as a dictionary
        exc_type, exc_value, exc_tb = sys.exc_info()
        test_case_inputs = '\n'.join(test_case["inputs"])
        exception_data = {
            'type': type(e).__name__,
            'message': (f"{str(e)}\n\nHOW TO FIX IT:\n\nThis error was very likely caused by your code asking for more input() calls than the test case expected. "
                        f"To see where this is happening in your code, run your code and input THESE EXACT INPUTS IN THIS ORDER:\n\n"
                        f"{test_case_inputs}\n\n"
                        f"If, after entering those exact inputs in that order, your code asks for another input, THAT is the cause of this error. "
                        f"Make it so your code doesn't ask for any more inputs after the last input entered. If you believe that is a mistake, please "
                        f"reach out to your professor."),
            'traceback': traceback.format_exception(exc_type, exc_value, exc_tb)
        }
        shared_data['status'] = 'exception'
        shared_data['payload'] = exception_data

    except EOFError as e:
        # Send the exception back as a dictionary
        exc_type, exc_value, exc_tb = sys.exc_info()
        exception_data = {
            'type': type(e).__name__,
            'message': (f"{str(e)}\n\nThis was most likely caused by an input() function being present "
                        f"in a .py module that you imported. Please only use the input() function in the main assignment .py file."),
            'traceback': traceback.format_exception(exc_type, exc_value, exc_tb)
        }
        shared_data['status'] = 'exception'
        shared_data['payload'] = exception_data

    except BaseException as e:
        # Send the exception back as a dictionary
        exc_type, exc_value, exc_tb = sys.exc_info()
        exception_data = {
            'type': type(e).__name__,
            'message': str(e),
            'traceback': traceback.format_exception(exc_type, exc_value, exc_tb)
        }
        shared_data['status'] = 'exception'
        shared_data['payload'] = exception_data

    finally:
        sys.settrace(None)
        if 'old_stdout' in globals() or 'old_stdout' in locals():
            sys.stdout = old_stdout


def is_picklable(obj):
    """
    Each test case is run in a subprocess, with relevant info/variables
    Sent back to the main process through a Queue. Because that requires
    pickling the data, this is used to check if something I'm trying to send
    is actually able to be pickled before I actually send it.
    """

    try:
        pickle.dumps(obj)
    except Exception:
        return False
    else:
        return True

# ===================================================
# TRACE FUNCTIONS
# (for tracking exceptions variables in student code)
# ===================================================

def create_trace_function(main_locals, raised_exceptions, exception_handlers):
    pending_exception = {'type': None, 'frame': None}

    def trace_function(frame, event, arg):
        nonlocal pending_exception
        if event == 'call':
            code_obj = frame.f_code
            func_name = code_obj.co_name
            if func_name == 'main':
                # We are entering the 'main' function
                def trace_lines(frame, event, arg):
                    if event == 'return':
                        # We are exiting 'main', capture locals
                        main_locals.update(frame.f_locals)
                    elif event == 'exception':
                        exc_type, exc_value, exc_traceback = arg
                        exception_name = exc_type.__name__
                        raised_exceptions.append({'exception': exception_name, 'handled_by': None})
                        pending_exception['type'] = exception_name
                        pending_exception['frame'] = frame
                    elif event == 'line':
                        if pending_exception['type']:
                            lineno = frame.f_lineno
                            # Check if current line is within any exception handler
                            for handler in exception_handlers:
                                if handler['start_lineno'] <= lineno <= handler['end_lineno']:
                                    # Found the handler
                                    handled_exception_type = handler['type']
                                    raised_exceptions[-1]['handled_by'] = handled_exception_type
                                    # Reset pending_exception
                                    pending_exception['type'] = None
                                    pending_exception['frame'] = None
                                    break
                    return trace_lines
                return trace_lines
            else:
                # For other functions, we can still track exceptions
                def trace_all(frame, event, arg):
                    if event == 'exception':
                        exc_type, exc_value, exc_traceback = arg
                        exception_name = exc_type.__name__
                        raised_exceptions.append({'exception': exception_name, 'handled_by': None})
                        pending_exception['type'] = exception_name
                        pending_exception['frame'] = frame
                    elif event == 'line':
                        if pending_exception['type']:
                            lineno = frame.f_lineno
                            # Check if current line is within any exception handler
                            for handler in exception_handlers:
                                if handler['start_lineno'] <= lineno <= handler['end_lineno']:
                                    # Found the handler
                                    handled_exception_type = handler['type']
                                    raised_exceptions[-1]['handled_by'] = handled_exception_type
                                    # Reset pending_exception
                                    pending_exception['type'] = None
                                    pending_exception['frame'] = None
                                    break
                    return trace_all
                return trace_all
        elif event == 'exception':
            exc_type, exc_value, exc_traceback = arg
            exception_name = exc_type.__name__
            raised_exceptions.append({'exception': exception_name, 'handled_by': None})
            pending_exception['type'] = exception_name
            pending_exception['frame'] = frame
        elif event == 'line':
            if pending_exception['type']:
                lineno = frame.f_lineno
                # Check if current line is within any exception handler
                for handler in exception_handlers:
                    if handler['start_lineno'] <= lineno <= handler['end_lineno']:
                        # Found the handler
                        handled_exception_type = handler['type']
                        raised_exceptions[-1]['handled_by'] = handled_exception_type
                        # Reset pending_exception
                        pending_exception['type'] = None
                        pending_exception['frame'] = None
                        break
        return trace_function

    return trace_function

def get_exception_handlers_from_source(source):
    exception_handlers = []

    tree = ast.parse(source)

    class ExceptionHandlerVisitor(ast.NodeVisitor):
        def visit_Try(self, node):
            for handler in node.handlers:
                if handler.type is None:
                    # Bare except: catches all exceptions
                    exception_type = 'Exception'
                    is_general_exception_handler = True
                elif isinstance(handler.type, ast.Name):
                    exception_type = handler.type.id
                    is_general_exception_handler = (exception_type == 'Exception')
                else:
                    # Handles complex exception types like tuples
                    exception_type = ast.unparse(handler.type)
                    is_general_exception_handler = ('Exception' in exception_type)

                start_lineno = handler.lineno
                # Get the last line number in the handler's body
                if handler.body:
                    end_lineno = handler.body[-1].lineno
                else:
                    end_lineno = start_lineno

                exception_handlers.append({
                    'type': exception_type,
                    'start_lineno': start_lineno,
                    'end_lineno': end_lineno,
                    'is_general': is_general_exception_handler
                })

            self.generic_visit(node)

    visitor = ExceptionHandlerVisitor()
    visitor.visit(tree)

    return exception_handlers

def exception_profiler(frame, event, arg):
    """Profile function to track exceptions raised."""
    if event == 'exception':
        exc_type, exc_value, exc_traceback = arg
        raised_exceptions.append(exc_type.__name__)

# ==================================
# TESTING CUSTOM FUNCTIONS & CLASSES
# ==================================

def get_function(module_name, func_name):
    """
    Try to import the function from a module with various naming conventions.
    """
    function_variations = [
    func_name,  # snake_case
        func_name.title().replace("_", ""), # PascalCase
        (func_name[0].lower() + func_name.title()[1:]).replace("_", ""),    # camelCase
    ]

    module = importlib.import_module(module_name)
    
    for variation in function_variations:
        if hasattr(module, variation):
            return getattr(module, variation)
    
    raise AttributeError(f"Function '{func_name}' not found in {module_name}.")

def get_custom_functions_from_module(module):
    """
    Given a module object, return a dictionary of all custom functions defined in the module.
    """
    return {name: obj for name, obj in vars(module).items() if inspect.isfunction(obj)}

def is_user_defined_module(module):
    """
    Determines if a module is user-defined by checking if it resides in the student's directory.
    Excludes standard library and external packages.
    """
    module_path = getattr(module, '__file__', '')
    if module_path:  # Only proceed if the module has a __file__ attribute
        base_dir = os.path.dirname(os.path.realpath(module_path))  # Get the directory of the module
        # Compare to standard library or third-party package paths
        return not base_dir.startswith(sys.prefix)  # Exclude standard library and packages
    return False

def get_all_custom_functions(globals_dict):
    """
    Retrieve all custom functions defined within the student's code and any user-defined modules
    they import. Excludes functions from external libraries like random, numpy, etc.
    """
    custom_functions = {}
    
    # First, collect all custom functions defined in the main file
    for name, obj in globals_dict.items():
        if inspect.isfunction(obj):
            # Only include functions defined in the student's main file (__main__) or other files
            if obj.__module__ == '__main__' or is_user_defined_module(sys.modules[obj.__module__]):
                if name != 'input':  # this just exlcudes the mocked input function run during the tests.
                    custom_functions[name] = obj

    # Now, check for any imported modules in the globals_dict
    for name, obj in globals_dict.items():
        if inspect.ismodule(obj) and is_user_defined_module(obj):
            # Add custom functions from this imported module
            custom_functions.update(get_custom_functions_from_module(obj))

    return custom_functions

def test_functions(function_tests, globals_dict, instance=None):
    """
    Tests functions or methods based on the provided test cases.
    If 'instance' is provided, tests methods of the instance.
    """
    function_results = {}
    is_method_test = False

    if not function_tests:
        function_results["FUNCTION ERROR"] = "No functions were provided to function_tests. Contact your professor."
        return function_results

    if instance is not None:
        is_method_test = True
        # Testing methods of the instance
        all_functions = {name: getattr(instance, name) for name in dir(instance)
                         if callable(getattr(instance, name)) and not name.startswith('__')}
        context = f"object of class {instance.__class__.__name__}"
    else:
        # Testing functions in the globals_dict
        all_functions = get_all_custom_functions(globals_dict)
        context = "your code"

    all_functions_names = '\n'.join(all_functions.keys())

    for test_case in function_tests:
        # Handle function name variations
        func_name_original = test_case.get('function_name')
        function_variations = [
            func_name_original,  # original name
            func_name_original.lower(),
            func_name_original.title().replace("_", ""),
            (func_name_original[0].lower() + func_name_original.title()[1:]).replace("_", ""),
        ]

        func_found = False
        for func_variation in function_variations:
            if func_variation in all_functions:
                func_found = True
                func = all_functions[func_variation]
                break

        if not func_found:
            function_results["FUNCTION ERROR"] = (
                f"This test is looking specifically for the function/method '{func_name_original}' in {context},\n"
                f"But it couldn't find it, nor any of its accepted variations:\n{', '.join(function_variations[1:])}\n\n"
                f"Make sure you are spelling the function/method name correctly. Below are all of "
                f"the functions/methods that the test could find in {context}:\n{all_functions_names}"
            )
            return function_results


        # Run the function with the provided arguments
        if callable(func):
            args = test_case.get("args", [])
            
            num_calls = test_case.get('num_calls', 1)

            try:
                for _ in range(num_calls): # usually just called once, but some tests require several calls
                    if is_method_test:
                    # first store the initial state of the object:
                        object_state = get_object_state(instance)
                        test_case.setdefault('initial_obj_state', []).append(object_state)

                    actual_return_value = func(*args)
                    test_case.setdefault('actual_return_value', []).append(actual_return_value)

                    if is_method_test:
                    # first store the initial state of the object:
                        object_state = get_object_state(instance)
                        test_case.setdefault('final_obj_state', []).append(object_state)

            except Exception as e:
                test_case["FUNCTION ERROR"] = f"While trying to run {func_name_original}, with these argument: {args} this error occured: {type(e).__name__}: {e}"
        else:
            test_case["FUNCTION ERROR"] = f"{func_name_original} was found in {context}, but it isn't callable as a function. Make sure you defined it correctly."
            return function_results

    return function_results

def get_all_custom_classes(globals_dict):
    """
    Retrieves all custom classes defined within the student's code and any user-defined modules
    they import. Excludes classes from external libraries.
    """
    custom_classes = {}

    # First, collect all custom classes defined in the main file
    for name, obj in globals_dict.items():
        if inspect.isclass(obj):
            # Only include classes defined in the student's main file (__main__) or user-defined modules
            if obj.__module__ == '__main__' or is_user_defined_module(sys.modules[obj.__module__]):
                custom_classes[name] = obj

    # Now, check for any imported modules in the globals_dict
    for name, obj in globals_dict.items():
        if inspect.ismodule(obj) and is_user_defined_module(obj):
            # Add custom classes from this imported module
            custom_classes.update({name: cls for name, cls in vars(obj).items() if inspect.isclass(cls)})

    return custom_classes

def test_classes(class_tests, globals_dict):
    """
    Tests the classes defined by the student according to the specifications in class_tests.
    """

    if not class_tests:
        class_tests["CLASS ERROR"] = "No classes were provided to class_tests. Contact your professor."
        return class_tests

    all_custom_classes = get_all_custom_classes(globals_dict)
    all_custom_classes_names = '\n'.join(all_custom_classes.keys())

    # returns pascal, camel, and snake
    class_name_original = class_tests.get('class_name')
    class_variations = list(set(convert_pascal_case(class_name_original))) # if snake or camel are identical, it gets rid of duplicates.

    # Before running any of the tests, check if the class is even in the students' code

    class_found = False
    for class_variation in class_variations:
        if class_variation in all_custom_classes:
            cls = all_custom_classes[class_variation]
            class_found = True
            break

    if not class_found:
        class_tests["CLASS ERROR"] = (
            f"This test is looking specifically for the class:\n\n{class_name_original}\n\n"
            f"But it couldn't find it, nor any of its accepted variations:\n\n{', '.join(class_variations[1:])}\n\n"
            f"Make sure you are spelling the class name correctly. Below are all of "
            f"the classes you made in your code that the test could find:\n\n"
            f"{all_custom_classes_names}"
        )
        return class_tests

    for class_test in class_tests.get('class_test_cases'):

        init_args = class_test.get("init_args", [])
        try:
            obj = cls(*init_args) # attempt to create an object

            # Get all attributes of the object (excluding methods and built-in attributes)
            obj_attributes = {name: value for name, value in vars(obj).items()
                  if not callable(value) and not name.startswith('__')
                  and is_picklable(value)}

            # add in the names of the methods, but not the methods themselves
            # since they aren't picklable.
            obj_attributes["methods"] = [name for name, value in vars(obj).items()
                                        if callable(value) and not name.startswith('__')]
            
            class_test['actual_object'] = obj_attributes

            # if the test is for a specific method, call that method:
            if class_tests.get('test_type') == 'method_test':
                method_to_test = class_tests.get('method_to_test')
                method_test_cases = [method_test_case for method_test_case in class_test.get('method_test_cases') if method_test_case.get('function_name') == method_to_test]

                test_functions(method_test_cases, globals_dict, instance=obj)
                    

        except Exception as e:
            class_test['CLASS ERROR'] = f"{type(e).__name__}: {str(e)}"
        
    return class_tests

def get_object_state(obj):
    """
    Returns a dictionary representing the object's state,
    including class name, instance variables, and methods.
    """
    # Get instance variables
    instance_variables = {name: value for name, value in vars(obj).items()
                          if is_picklable(value)}
    # Get methods
    methods = [name for name, value in inspect.getmembers(obj, predicate=inspect.ismethod)
               if not name.startswith('__')]
    return {
        'class_name': obj.__class__.__name__,
        'instance_variables': instance_variables,
        'methods': methods,
    }

# ========================
# ERROR MESSAGE FORMATTING
# ========================

def format_error_message(custom_message: str = None,
                         test_case: dict = None,
                         display_inputs: bool = False,
                         display_input_prompts: bool = False,
                         display_invalid_input_prompts: bool = False,
                         display_printed_messages: bool = False,
                         display_invalid_printed_messages: bool = False,
                         line_length: int = 74) -> str:
    """
    Constructs the main error students will see in the Test Results window.
    The main purpose in the error message is to communicate which test case
    a test failed on, and then optionally include extra details that might
    help out the student

    Keep line_length at 74, that is where pytest splits lines in its error
    reporting
    """
    
    # some starting strings. All messages will be appended to error_message
    error_message = ''
    divider = f"\n{"-"*line_length}\n"
    error_message += divider
    error_message += f"IS 303 STUDENTS: READ THE ERROR MESSAGES IN RED BELOW\n\n"
    error_message += "↓"*line_length + "\n"
    if test_case:
        error_message += divider
        error_message += f"TEST FAILED DURING TEST CASE: {test_case["id_test_case"]}"
        error_message += divider
        error_message += insert_newline_at_last_space((
            f"\nLook at the \"Test Cases\" section of the instructions in README.md. "
            f"Run your code while inputting the EXACT inputs shown there to see where/why "
            f"your code either breaks or doesn't pass this test.\n\n"
        ), line_length)
        test_case_description = f"FOR TEST CASE: {test_case["id_test_case"]}"
    else:
        test_case_description = ''

    if custom_message:
        error_message += divider
        error_message += f"WHAT WENT WRONG:"
        error_message += divider
        error_message += insert_newline_at_last_space("\n" + custom_message, line_length)

    if display_inputs:
        inputs_concatenated = '\n'.join(test_case["inputs"])
        error_message += divider
        error_message += f"INPUTS ENTERED {test_case_description}"
        error_message += divider
        error_message += insert_newline_at_last_space(f"\nThese inputs will be entered in this exact order during this test case:\n\n\n", line_length)
        error_message += inputs_concatenated + "\n"

    if display_input_prompts:
        expected_input_prompts_concatenated = '\n'.join(test_case["input_prompts"])
        error_message += divider
        error_message += f"EXPECTED INPUT PROMPTS {test_case_description}"
        error_message += divider
        error_message += insert_newline_at_last_space(f"\nThese inputs prompts must appear at least once during this test case:\n\n\n", line_length)
        error_message += expected_input_prompts_concatenated + "\n"

    if display_invalid_input_prompts:
        invalid_input_prompts_concatenated = '\n'.join(test_case["invalid_input_prompts"])
        error_message += divider
        error_message += f"INVALID INPUT PROMPTS {test_case_description}"
        error_message += divider
        error_message += insert_newline_at_last_space(f"\nThe test will fail if any of the following appear during this test case:\n\n\n", line_length)
        error_message += invalid_input_prompts_concatenated + "\n"

    if display_printed_messages:
        expected_printed_messages_concatenated = '\n'.join(test_case["printed_messages"])
        error_message += divider
        error_message += f"EXPECTED PRINTED MESSAGES {test_case_description}"
        error_message += divider               
        error_message += insert_newline_at_last_space(f"\nThese printed messages must appear at least once during this test case:\n\n\n", line_length)
        error_message += expected_printed_messages_concatenated + "\n"

    if display_invalid_printed_messages:
        invalid_printed_messages_concatenated = '\n'.join(test_case["invalid_printed_messages"])
        error_message += divider
        error_message += f"INVALID PRINTED MESSAGES {test_case_description}"
        error_message += divider
        error_message += insert_newline_at_last_space(f"\nThe test will fail if any of the following appear during this test case:\n\n\n", line_length)
        error_message += invalid_printed_messages_concatenated + "\n"

    error_message += "\n"

    return error_message


def exception_message_for_students(exception_data, test_case):
    """
    Gets called when a test fails because of an exception occuring, rather than
    the test failing because it didn't produce the right output, etc.

    If an exception occurs during the subprocess of the code running, it gets
    returned as a dictionary (since you can't pickle Exception objects and send them
    to a higher process). Otherwise, this function just expects an exception object.
    """

    if isinstance(exception_data, dict):
        # Exception data from the subprocess
        error_type = exception_data['type']
        error_message_str = exception_data['message']
        traceback_list = exception_data['traceback']
        # Attempt to get the last traceback entry for the error location
        if traceback_list:
            error_location = ''.join(traceback_list[-2:]) if len(traceback_list) >= 2 else ''.join(traceback_list)
        else:
            error_location = "No traceback available."
    else:
        # Exception object with traceback
        e = exception_data
        tb_list = traceback.extract_tb(e.__traceback__)
        if tb_list:
            last_traceback = [tb_list[-1]]
            error_location = ''.join(traceback.format_list(last_traceback))
        else:
            error_location = "No traceback available."
        error_type = type(e).__name__
        error_message_str = str(e)

    # Because the student's code is run by exec in a subprocess, it just shows up as <string>
    # These just puts back their python file name in that case, as well as improves
    # some of the messaging to make it easier for students to understand
    # at a glance by clearly separating the location of the error and the error itself.
    error_location = error_location.replace('File "<string>"', f"{default_module_to_test}.py" )
    error_location = error_location.replace(', in <module>', '' )
    error_message = f"\n{error_type}: {error_message_str}"
    error_location = error_location = error_location.replace(error_message, '')

    # Check if 'inputs' is in test_case and set display_inputs_option accordingly
    if test_case.get("inputs", None):
        display_inputs_option = True
    else:
        display_inputs_option = False

    if error_type == "StopIteration":
        pytest.fail(f"{format_error_message(
            custom_message=(f"While trying to run the test, python ran into an error.\n\n"
                            f"LOCATION OF ERROR:\n\n{error_location}\n"
                            f"ERROR MESSAGE:\n{error_message}\n\n"), 
            test_case=test_case,
            display_inputs=display_inputs_option
            )}")
    else:
        # Call pytest.fail with the formatted error message
        pytest.fail(f"{format_error_message(
            custom_message=(f"While trying to run the test, python ran into an error.\n\n"
                            f"LOCATION OF ERROR:\n\n{error_location}\n"
                            f"ERROR MESSAGE:\n{error_message}\n\n"
                            f"HOW TO FIX IT:\n\n"
                            f"If the error occurred in {default_module_to_test}.py or another .py file that you wrote, set a breakpoint at the location in that file where "
                            f"the error occurred and see if you can repeat the error by running your code using the inputs for Test Case {test_case['id_test_case']}. "
                            f"That should help you see what went wrong.\n\n"
                            f"If the error occurred in a different file, reach out to your professor.\n\n"), 
            test_case=test_case,
            display_inputs=display_inputs_option
            )}")

def timeout_message_for_students(test_case):
    """
    Just returns a message for timeout errors.
    I put this in a function just so there is one central place
    to edit the message if I change it in the future.
    """
    test_case_inputs = test_case.get("inputs", "No inputs")
    test_case_inputs = '\n'.join(test_case_inputs)

    return format_error_message(
                custom_message=(f"You got a Timeout Error, meaning this test case didn't complete after {default_timeout_seconds} seconds. "
                                f"The test timed out during test case {test_case["id_test_case"]}. To try and identify the problem, run your code like normal, but enter these EXACT inputs "
                                f"in this order:\n\n"
                                f"{test_case_inputs}\n\n"
                                f"Most likely, "
                                f"you wrote your code in a way that the inputs of this test case make it so your code never exits properly. "
                                f"Double check the test case examples in the instructions and make sure your code isn't asking for additional "
                                f"or fewer inputs than the test case expects.\n\n"),
                test_case=test_case,
                display_inputs=True,
                display_input_prompts=True,
                display_invalid_input_prompts=True)

# =========================
# ASSORTED HELPER FUNCTIONS
# =========================

def normalize_text(text):
    """
    Used by tests that look for specific output or input prompts.
    Makes all text lowercase, reduces all spacing to just one space
    and removes any extra symbols, except for negative signs and decimals
    associated with numbers. Handles recursion for iterables and dictionaries.
    """
    
    if isinstance(text, str):
        # Lowercase the input
        text = text.lower()
        
        # Replace newlines with a single space
        text = text.replace('\n', ' ')
        
        # Replace multiple spaces with a single space
        text = re.sub(r'\s+', ' ', text)
        
        # Remove periods not between digits
        text = re.sub(r'(?<!\d)\.(?!\d)', '', text)
        
        # If there is any character followed by a colon : other than a space, add a space
        text = re.sub(r'(:)(\S)', r'\1 \2', text)
    
        # Remove all other punctuation and symbols
        text = re.sub(r'[!"#$%&\'()*+,/:;<=>?@\[\]^_`{|}~]', '', text)
        
        # Temporarily replace negative signs with a placeholder
        text = re.sub(r'((?<=^)|(?<=\s))-(?=\d)', 'NEG_SIGN_PLACEHOLDER', text)
        
        # Replace remaining hyphens (e.g., between numbers) with a space
        text = text.replace('-', ' ')
        
        # Replace multiple spaces again in case punctuation removal created extra spaces
        text = re.sub(r'\s+', ' ', text)
        
        # Restore negative signs
        text = text.replace('NEG_SIGN_PLACEHOLDER', '-')
        
        # Strip leading and trailing spaces
        return text.strip()
    
    elif isinstance(text, dict):
        # Apply normalize_text to both keys and values in the dictionary
        return {normalize_text(k): normalize_text(v) for k, v in text.items()}
    
    elif isinstance(text, Iterable) and not isinstance(text, (str, bytes)):
        # Apply normalize_text recursively for each item in the iterable (excluding strings/bytes)
        return type(text)(normalize_text(item) for item in text)
    
    else:
        # If the text is not a string, iterable, or dictionary, return as is
        return text

def insert_newline_at_last_space(s, width=74):
    """
    Because pytest fail messages have a specific width they are printed at,
    if I don't format my own error messages at that same width, they
    look much worse. This just adds in a new line before the width limit
    is hit for any string that you pass to it.
    """

    lines = []
    current_line = ""
    
    for char in s:
        current_line += char
        
        # If we hit a newline, append the current line and reset the line
        if char == '\n':
            lines.append(current_line.strip())  # Add the line and strip any extra spaces
            current_line = ""
            continue
        
        # If the current line exceeds the width, break at the last space
        if len(current_line) > width:
            # Find the last space before the width limit
            break_index = current_line.rfind(' ', 0, width)
            
            # If no space is found, break at the width limit
            if break_index == -1:
                break_index = width
            
            # Append the part of the line before the break
            lines.append(current_line[:break_index].strip())
            
            # Reset current_line to the remaining unprocessed part of the string
            current_line = current_line[break_index:].lstrip()  # Remove leading spaces in the next line
            
    # Append the last part of the string (if any)
    if current_line:
        lines.append(current_line.strip())
    
    return '\n'.join(lines)

def round_match(match):
    number = match.group()
    # Check if the number is a float (contains a decimal point)
    if '.' in number:
        # Convert to float and round to 2 decimal places
        # it uses the global_decimal_places that is defined at the top of this module.
        rounded_number = round(float(number), global_decimal_places)
        return f"{rounded_number}"
    else:
        # If it's an integer, just return it as is
        return number
    

def convert_pascal_case(pascal_str):
    # Convert to camelCase
    camel_case = pascal_str[0].lower() + pascal_str[1:]

    # Convert to snake_case
    snake_case = re.sub(r'([A-Z])', r'_\1', pascal_str).lower().lstrip('_')

    return pascal_str, camel_case, snake_case

def prettify_dictionary(dictionary):
    if not isinstance(dictionary, dict):
        return None
    
    formatted_dict_str = ''
    for key, value in dictionary.items():
        formatted_dict_str += f'{key}: {value}\n'
    
    # return it without the last newline
    return formatted_dict_str[:-1]