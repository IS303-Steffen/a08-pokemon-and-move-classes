import importlib.util
import os

def load_test_cases_from_file(file_path):
    """Dynamically load test_cases_functions_dict from the given Python file path."""
    module_name = "test_cases_module"
    
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    return getattr(module, "test_cases_functions_dict", None)

# Specify the file path to test_cases_functions.py
test_cases_file_path = r"tests/test_cases/function_test_cases.py"  # Update this path

# Load the test cases dictionary
test_cases_functions_dict = load_test_cases_from_file(test_cases_file_path)

if not test_cases_functions_dict:
    print("Error: Could not load test_cases_functions_dict from the provided file path.")
    exit(1)

# Output folder for markdown files
output_folder = r"descriptions_of_test_cases"
os.makedirs(output_folder, exist_ok=True)

# Function to format values with their type
def format_value(value):
    """Formats any value to display the value followed by its data type."""
    return f'"{value}" - {type(value).__name__}' if isinstance(value, str) else f"{value} - {type(value).__name__}"

# Generate Markdown files for each function
for function_name, test_cases in test_cases_functions_dict.items():
    file_name = f"function_test_cases_{function_name}.md"
    file_path = os.path.join(output_folder, file_name)

    # Initialize markdown content
    markdown_content = f"# {function_name} Function Tests\n\n"

    # Loop through test cases for the function
    for idx, test_case in enumerate(test_cases, start=1):
        args = test_case.get("args", [])
        expected_return_value = test_case.get("expected_return_value", "N/A")

        # Format inputs with numbering
        inputs_formatted = '\n'.join([f"{i+1}: {format_value(arg)}" for i, arg in enumerate(args)])

        # Format expected output without numbering
        expected_output = format_value(expected_return_value)

        # Append test case details to markdown content
        markdown_content += f"## {function_name} - Function Test Case {idx}\n\n"
        markdown_content += f"### Inputs\n```\n{inputs_formatted if inputs_formatted else 'No inputs'}\n```\n\n"
        markdown_content += f"### Expected Output\n```\n{expected_output}\n```\n\n"

    # Write the markdown content to the file
    with open(file_path, "w") as md_file:
        md_file.write(markdown_content)

print(f"Markdown files have been successfully created in the '{output_folder}' folder.")