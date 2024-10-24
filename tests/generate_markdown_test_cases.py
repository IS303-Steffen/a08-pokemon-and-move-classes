import json

imported_json_file_path = 'tests/test_cases_final.json'
exported_md_file_path = 'tests/markdown_generated.md'

# Global variable to specify any additional keys to include in the detailed test case tables
ADDITIONAL_KEYS = []  # For example, 'dicts' key in the JSON

# Read the JSON file
with open(imported_json_file_path, 'r') as f:
    test_cases = json.load(f)

# Collect all unique input_prompts and printed_messages across all test cases
input_prompts_set = set()
printed_messages_set = set()

for test_case in test_cases:
    input_prompts_set.update(test_case.get('input_prompts', []))
    printed_messages_set.update(test_case.get('printed_messages', []))

# Start building the markdown output
output = ""

# All Possible Input Prompts
output += "### All Possible Input Prompts:\n"
for prompt in sorted(input_prompts_set):
    output += f"- `{prompt}`\n"
output += "\n"

# All Possible Printed Messages
output += "### All Possible Printed Messages:\n"
for message in sorted(printed_messages_set):
    # Remove leading/trailing whitespace and newlines
    message = message.strip()
    output += f"- `{message}`\n"
output += "\n"

# Test Cases Summary
output += "## Test Cases Summary\n"
output += '<table>\n'
output += '  <tr>\n'
output += '    <th>Test Case Description</th>\n'
output += '    <th>Inputs</th>\n'
output += '  </tr>\n'

for test_case in test_cases:
    id_test_case = test_case.get('id_test_case')
    test_case_description = test_case.get('test_case_description')
    inputs = test_case.get('inputs', [])

    # First cell: id_test_case: test_case_description with anchor link
    anchor_id = f"testcase{id_test_case}"
    description_cell = f'<a href="#{anchor_id}">{id_test_case}: {test_case_description}</a>'

    # Second cell: inputs as unordered list, with each input wrapped in <code></code>
    inputs_cell = '<ul>\n'
    for inp in inputs:
        inputs_cell += f'  <li><code>{inp}</code></li>\n'
    inputs_cell += '</ul>'

    # Add row to the table
    output += '  <tr>\n'
    output += f'    <td>{description_cell}</td>\n'
    output += f'    <td>{inputs_cell}</td>\n'
    output += '  </tr>\n'

output += '</table>\n\n'

# Define the keys to include in the detailed test case tables
default_keys = ['inputs', 'input_prompts', 'invalid_input_prompts', 'printed_messages', 'invalid_printed_messages']
all_keys = default_keys + ADDITIONAL_KEYS

# For each test case, generate the detailed section
for test_case in test_cases:
    id_test_case = test_case.get('id_test_case')
    test_case_description = test_case.get('test_case_description')

    anchor_id = f"testcase{id_test_case}"
    output += f'<h3 id="{anchor_id}">Test Case {id_test_case} Details - {test_case_description}</h3>\n\n'
    output += '<table>\n'
    output += '  <tr>\n'
    output += '    <th>Requirement</th>\n'
    output += '    <th>Components</th>\n'
    output += '  </tr>\n'

    for key in all_keys:
        # Requirement: key name with underscores replaced by spaces, capitalize each word
        requirement = ' '.join([word.capitalize() for word in key.replace('_', ' ').split()])

        # Components: individual elements associated with each key
        components_list = []

        if key in test_case:
            value = test_case[key]
            if isinstance(value, dict):
                if key in ADDITIONAL_KEYS:
                    # For keys like 'dicts', display only the values
                    for subkey in value:
                        subvalue = value[subkey]
                        # Convert subvalue to JSON string
                        value_str = json.dumps(subvalue)
                        components_list.append(value_str)
                else:
                    # For other dicts, flatten the dict
                    for subkey in value:
                        components_list.append(f'"{subkey}": {value[subkey]}')
            elif isinstance(value, list):
                components_list = value
            else:
                components_list = [str(value)]
        else:
            components_list = []

        # Build the components cell
        if components_list:
            components_cell = '<ul>\n'
            for item in components_list:
                item = item.strip()
                components_cell += f'  <li><code>{item}</code></li>\n'
            components_cell += '</ul>'
        else:
            components_cell = ''

        # Add the row to the table
        output += '  <tr>\n'
        output += f'    <td>{requirement}</td>\n'
        output += f'    <td>{components_cell}</td>\n'
        output += '  </tr>\n'

    output += '</table>\n\n'

    # Include example_output surrounded by triple backticks
    example_output = test_case.get('example_output', '')
    if example_output:
        output += f'<h4>Example Ouput:</h4>\n\n'
        output += f'```{example_output}\n```\n\n'

# Write the output to a markdown file
with open(exported_md_file_path, 'w') as f:
    f.write(output)

print(f"Markdown file {exported_md_file_path} has been generated.")