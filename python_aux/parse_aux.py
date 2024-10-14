import traceback
import inspect
import convert_aux as converta
def func1(**params):
    # Define default and optional values for each parameter in default_params
    default_params = {
        'a': {'default': 5, 'optional': {5, 7, 3}},
        'b': {'default': 10, 'optional': {2, 5, 10}}
    }

    try:
        params = parse_func_params(params, default_params)
    except ValueError as e:
        print(e)  # Print the exception message with calling stack path
        return None

    # Perform calculations using parsed parameters
    a = params['a']
    b = params['b']
    c = a + b
    return c

def func2(e,g,**params):
    # Define default and optional values for each parameter in default_params
    default_params = {
        'a': 5,
        'd': {'default': 2, 'optional': {2, 5, 10}}
    }

    try:
        params = parse_func_params(params, default_params)
    except ValueError as e:
        print(e)  # Print the exception message with calling stack path
        return None
    
    # Call func1 with validated params and perform additional calculation
    f = func1(**params) + params['d']+e

    return f




def parse_parameter(parameter, allowed_values,parameter_name=None):
    """
    Example function that only accepts specific values for its parameter.

    Parameters:
    - parameter: str, the input parameter which must be one of the allowed values.
    - allowed_values: list, the set of allowed values for the parameter.

    Raises:
    - ValueError: if the parameter is not in the allowed values.
    """
    if (parameter_name is not None):
        str = f"for {parameter_name}"
    else:
        str = ""
    
    if (isinstance(parameter,list)):
        allowed_values = converta.VarToList(allowed_values)
        for value in parameter:
            if value not in allowed_values:
                raise ValueError(f"Invalid value '{value}' {str}. Allowed values are: {allowed_values}")
    else: 
        if parameter not in allowed_values:
            raise ValueError(f"Invalid value '{parameter}' {str}. Allowed values are: {allowed_values}")
    

def parse_func_params(params, default_params):
    parsed_params = {}

    # Get the name of the calling function
    calling_func_name = inspect.currentframe().f_back.f_code.co_name
    

    strict_params = ('strict_params' not in params.keys()) or ('strict_params' in params.keys() and params['strict_params']==True)
    
    # Check for unexpected parameters if strict mode is enabled
    if strict_params:
        for param_name in params:
            if param_name not in default_params:
                raise ValueError(f"{calling_func_name}: Unexpected parameter '{param_name}' found.")

    # Validate and parse each parameter
    for param_name, param_info in default_params.items():
        if isinstance(param_info, dict):
            default_value = param_info.get('default')
            allowed_values = param_info.get('optional', [])
        else:
            default_value = param_info
            allowed_values = []

        if param_name in params:
            param_value = params[param_name]
        else:
            param_value = default_value

        # Validate parameter value against allowed_values if provided
        if allowed_values and param_value not in allowed_values:
            raise ValueError(f"{calling_func_name}: Invalid value '{param_value}' for parameter '{param_name}'. Allowed values are {(allowed_values)}.")

        parsed_params[param_name] = param_value

    return parsed_params





def compare_dicts(dict1, dict2):
    # Find keys only in dict1
    only_in_dict1 = set(dict1) - set(dict2)
    # Find keys only in dict2
    only_in_dict2 = set(dict2) - set(dict1)
    # Find common keys with different values
    common_different = {key: (dict1[key], dict2[key]) for key in set(dict1) & set(dict2) if dict1[key] != dict2[key]}

    print("Keys only in first dictionary:")
    for key in only_in_dict1:
        print(f"  {key}: {dict1[key]}")

    print("\nKeys only in second dictionary:")
    for key in only_in_dict2:
        print(f"  {key}: {dict2[key]}")

    print("\nCommon keys with different values:")
    for key, (val1, val2) in common_different.items():
        print(f"  {key}: dict1={val1}, dict2={val2}")


def check_none_keys(input_dict, keys_to_check):
    none_keys = [key for key in keys_to_check if input_dict.get(key) is None]

    if none_keys:
        raise ValueError(f"The following keys have None values: {', '.join(none_keys)}")
    
def check_none(param_value,param_name):    
    if param_value is None:
        raise ValueError(f"{param_name} cannot be None.")