import importlib.util
import os

def load_test_cases_from_file(file_path):
    """Dynamically load test_cases_classes_dict from the given Python file path."""
    module_name = "test_cases_classes_module"
    
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    return getattr(module, "test_cases_classes_dict", None)

# Specify the file path to test_cases_classes.py
test_cases_file_path = r"tests/test_cases/class_test_cases.py"  # Update this path

# Load the test cases dictionary
test_cases_classes_dict = load_test_cases_from_file(test_cases_file_path)

if not test_cases_classes_dict:
    print("Error: Could not load test_cases_classes_dict from the provided file path.")
    exit(1)

# Output folder for markdown files
output_folder = r"descriptions_of_test_cases"
os.makedirs(output_folder, exist_ok=True)

# Function to format values with their type
def format_value(value):
    """Formats any value to display the value followed by its data type."""
    return f'"{value}" - {type(value).__name__}' if isinstance(value, str) else f"{value} - {type(value).__name__}"

# Generate Markdown files for each class
for class_name, class_test_cases in test_cases_classes_dict.items():
    class_file_name = f"class_test_cases_{class_name}.md"
    class_file_path = os.path.join(output_folder, class_file_name)
    
    # Initialize markdown content
    markdown_content = f"# {class_name} Class Tests\n\n"
    for idx, class_case in enumerate(class_test_cases, start=1):
        markdown_content += f"## {class_name} Class Test {idx}\n\n"
        markdown_content += "### Initial Arguments\n````\n"
        for arg, value in class_case["init_args"].items():
            markdown_content += f"{arg}: {format_value(value)}\n"
        markdown_content += "````\n\n"
        
        markdown_content += "### Expected Initial Values\n````\n"
        for var, value in class_case["init_expected_values"].items():
            markdown_content += f"{var}: {format_value(value)}\n"
        markdown_content += "````\n\n"
        
        markdown_content += "### Expected Method Names\n````\n"
        markdown_content += "\n".join(class_case["expected_function_names"]) + "\n````\n\n"
    
    # Write to the class markdown file
    with open(class_file_path, "w") as md_file:
        md_file.write(markdown_content)
    
    # Generate Markdown files for each method test case
    method_test_cases_dict = {}
    for class_case in class_test_cases:
        for method_case in class_case["method_test_cases"]:
            method_name = method_case['function_name']
            if method_name not in method_test_cases_dict:
                method_test_cases_dict[method_name] = []
            method_test_cases_dict[method_name].append((class_case, method_case))
    
    for method_name, method_cases in method_test_cases_dict.items():
        method_file_name = f"method_test_cases_{class_name}_{method_name}.md"
        method_file_path = os.path.join(output_folder, method_file_name)
        
        # Initialize markdown content
        method_markdown_content = f"# {class_name} - {method_name} Method Tests\n\n"
        
        for idx, (class_case, method_case) in enumerate(method_cases, start=1):
            method_markdown_content += f"## {class_name} - {method_name} Method Test {idx}\n\n"
            method_markdown_content += "### Initial Object Values\n````\n"
            for var, value in class_case["init_expected_values"].items():
                method_markdown_content += f"{var}: {format_value(value)}\n"
            method_markdown_content += "````\n\n"
            
            method_markdown_content += "### Arguments\n````\n"
            if method_case["args"]:
                for i, arg in enumerate(method_case["args"], start=1):
                    method_markdown_content += f"{i}: {format_value(arg)}\n"
            else:
                method_markdown_content += "No arguments besides 'self'\n"
            method_markdown_content += "````\n\n"
            
            expected_return = method_case["expected_return_value"]
            method_markdown_content += "### Expected Return Value\n````\n"
            method_markdown_content += f"{format_value(expected_return) if expected_return is not None else 'Does not return anything'}\n````\n\n"
            
            expected_update = method_case["expected_object_update"]
            method_markdown_content += "### Expected Object Update\n````\n"
            if expected_update:
                for var, change in expected_update.items():
                    method_markdown_content += f"{var}:\n\tInitial: {format_value(change['initial_value'])}\n\tFinal: {format_value(change['final_value'])}\n"
            else:
                method_markdown_content += "Not applicable\n"
            method_markdown_content += "````\n\n"
        
        # Write to the method markdown file
        with open(method_file_path, "w") as md_file:
            md_file.write(method_markdown_content)

print(f"Markdown files for class and method test cases have been successfully created in the '{output_folder}' folder.")
