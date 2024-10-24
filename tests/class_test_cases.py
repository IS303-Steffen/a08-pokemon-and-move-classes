class MethodTestCase:
    def __init__(self, function_name, args, expected_return_value, expected_object_update=None, num_calls=1):
        self.function_name = function_name
        self.args = args
        self.expected_return_value = expected_return_value
        self.expected_object_update = expected_object_update
        self.num_calls = num_calls

    def to_dict(self):
        return {
            "function_name": self.function_name,
            "args": self.args,
            "expected_return_value": self.expected_return_value,
            "expected_object_update": self.expected_object_update,
            "num_calls": self.num_calls
        }

class ClassTestCase:
    def __init__(self, class_name, init_args, init_expected_values, expected_function_names, method_test_cases):
        self.class_name = class_name
        self.init_args = init_args
        self.init_expected_values = init_expected_values
        self.expected_function_names = expected_function_names
        self.method_test_cases = [m.to_dict() for m in method_test_cases]

    def to_dict(self):
        return {
            "class_name": self.class_name,
            "init_args": self.init_args,
            "init_expected_values": self.init_expected_values,
            "expected_function_names": self.expected_function_names,
            "method_test_cases": self.method_test_cases
        }

    @classmethod
    def from_dict(cls, data):
        method_test_cases = [MethodTestCase(**m) for m in data["method_test_cases"]]
        return cls(
            class_name=data["class_name"],
            init_args=data["init_args"],
            init_expected_values=data["init_expected_values"],
            expected_function_names=data["expected_function_names"],
            method_test_cases=method_test_cases
        )
    

# Creating MethodTestCase objects for the 'Pokemon' class test cases
bulbasaur_get_info = MethodTestCase(
    function_name='get_info',
    args=[],
    expected_return_value='Bulbasaur - Type: Grass - Hit Points: 60',
    expected_object_update=None
)

bulbasaur_heal = MethodTestCase(
    function_name='heal',
    args=[],
    expected_return_value=None,
    expected_object_update=[{'intial_value': 60, 'final_value': 75}]
)

charmander_get_info = MethodTestCase(
    function_name='get_info',
    args=[],
    expected_return_value='Charmander - Type: Fire - Hit Points: 55',
    expected_object_update=None
)

charmander_heal = MethodTestCase(
    function_name='heal',
    args=[],
    expected_return_value=None,
    expected_object_update=[{'intial_value': 55, 'final_value': 70}]
)

# Creating ClassTestCase objects for the 'Pokemon' class
bulbasaur_test_case = ClassTestCase(
    class_name='Pokemon',
    init_args=['Bulbasaur', 'Grass', 60],
    init_expected_values={'Bulbasaur': str, 'Grass': str, 60: (int, float)},
    expected_function_names=['get_info', 'heal'],
    method_test_cases=[bulbasaur_get_info, bulbasaur_heal]
)

charmander_test_case = ClassTestCase(
    class_name='Pokemon',
    init_args=['Charmander', 'Fire', 55],
    init_expected_values={'Charmander': str, 'Fire': str, 55: (int, float)},
    expected_function_names=['get_info', 'heal'],
    method_test_cases=[charmander_get_info, charmander_heal]
)

# Creating MethodTestCase objects for the 'Move' class (these have no method test cases defined in your data)
# You can leave these empty, or define them later as needed

tackle_get_info = MethodTestCase(
    function_name='get_info',
    args=[],
    expected_return_value='Tackle (Type: Normal): 5 to 20 Attack Points',
    expected_object_update=None
)

water_gun_get_info = MethodTestCase(
    function_name='get_info',
    args=[],
    expected_return_value='Water Gun (Type: Water): 5 to 15 Attack Points',
    expected_object_update=None   
)

tackle_generate_attack_value = MethodTestCase(
    function_name='generate_attack_value',
    args=[],
    expected_return_value=(5, 20),
    expected_object_update=None,
    num_calls=100   
)

water_gun_generate_attack_value = MethodTestCase(
    function_name='generate_attack_value',
    args=[],
    expected_return_value=(5, 15),
    expected_object_update=None,
    num_calls=100   
)

tackle_test_case = ClassTestCase(
    class_name='Move',
    init_args=['Tackle', 'Normal', 5, 20],
    init_expected_values={'Tackle': str, 'Normal': str, 5: (int, float), 20: (int, float)},
    expected_function_names=['get_info', 'generate_attack_value'],
    method_test_cases=[tackle_get_info, tackle_generate_attack_value]
)

water_gun_test_case = ClassTestCase(
    class_name='Move',
    init_args=['Water Gun', 'Water', 5, 15],
    init_expected_values={'Water Gun': str, 'Water': str, 5: (int, float), 15: (int, float)},
    expected_function_names=['get_info', 'generate_attack_value'],
    method_test_cases=[water_gun_get_info, water_gun_generate_attack_value]
)

test_cases_classes_list = [bulbasaur_test_case, charmander_test_case, tackle_test_case, water_gun_test_case]
test_cases_classes_list = [class_test_case.to_dict() for class_test_case in test_cases_classes_list]
unique_class_names = {class_name.get('class_name') for class_name in test_cases_classes_list}

test_cases_classes_dict = {}
for class_name in unique_class_names:
    subset_test_cases_classes = [test_case_class for test_case_class in test_cases_classes_list if test_case_class.get('class_name') == class_name]
    test_cases_classes_dict[class_name] = subset_test_cases_classes
