

def replace_char_with_count(input_string, char_to_search):
    # Escape the character to search to avoid issues with special regex characters
    pattern = f"({re.escape(char_to_search)}{{2,}})"
    
    # Find all groups of consecutive occurrences of the character
    matches = re.findall(pattern, input_string)
    
    # For each match, replace it with the count and the character
    for match in matches:
        count = len(match)
        replacement = f"{count}{char_to_search[0]}"
        input_string = input_string.replace(match, replacement, 1)
    
    return input_string

import re


# def filter_strs(strs, str_filter):
#     if (str_filter is None) or (str_filter == ""):
#         return strs

#     def evaluate_filter(s, str_filter):
#         # Split the filter into components
#         components = str_filter.split()
        
#         # Reconstruct the filter condition as a valid Python expression
#         new_filter = ""
#         for component in components:
#             if component in {'and', 'or', 'not'}:
#                 new_filter += f" {component} "
#             else:
#                 new_filter += f"'{component}' in s"
        
#         try:
#             # Evaluate the expression
#             return eval(new_filter)
#         except Exception as e:
#             print(f'Error evaluating filter: {e}')
#             return False

#     # Apply the filter to each string
#     filtered_strs = [s for s in strs if evaluate_filter(s, str_filter)]
#     return filtered_strs


# # Example usage:
# strs = ["apple", "banana", "cherry", "date"]
# str_filter1 = "apple and banana"
# str_filter2 = "(apple and banana) or cherry"
# str_filter3 = "(apple and banana) or (cherry and not(date))"

# print(filter_strs(strs, str_filter1))  # Should return []
# print(filter_strs(strs, str_filter2))  # Should return ["cherry"]
# print(filter_strs(strs, str_filter3))  # Should return ["cherry"]


def replace_multiple_chars(string, to_replace=[',', '.', '/', "'", '"','(', ')', ' ', '[', ']'], replacement='_'):
    """
    Replaces multiple specified characters in a string with a single replacement character.

    Parameters:
    string (str): The input string to be modified.
    to_replace (list of str): A list of characters to be replaced.
    replacement (str): The character to replace with.

    Returns:
    str: The modified string with specified characters replaced.
    """
    for char in to_replace:
        string = string.replace(char, replacement)
    return string


def filter_strs(strs, str_filter):
    if (str_filter is None) or (str_filter == ""):
        return strs

    def evaluate_filter(s, str_filter):
        # Replacing special characters with Python-friendly syntax
        str_filter = str_filter.replace("'", r"\'").replace('"', r'\"')
        
        # Split the filter into components while preserving special characters
        components = str_filter.split()
        
        # Reconstruct the filter condition as a valid Python expression
        new_filter = ""
        i = 0
        while i < len(components):
            component = components[i]
            if component in {'and', 'or', 'not', '(', ')'}:
                new_filter += f" {component} "
            elif component == '/':
                new_filter += f" '/' in s "
            elif component == "'":
                new_filter += f" '\\'' in s "
            elif component == '_':
                new_filter += f" '_' in s "
            elif component == '"':
                new_filter += f" '\"' in s "
            else:
                new_filter += f"'{component}' in s"
            i += 1
        
        try:
            # Evaluate the expression
            return eval(new_filter)
        except Exception as e:
            print(f'Error evaluating filter: {e}')
            return False

    # Apply the filter to each string
    filtered_strs = [s for s in strs if evaluate_filter(s, str_filter)]
    return filtered_strs

# # Example usage:
# strs = ["hello", "world'", "test/string", "sample_with_un,derscores_and\"quotes\"", "example"]

# # Apply filters
# filters = [
#     "' or /",       # Contains either ' or /
#     "not (' or /)", # Does not contain either ' or /
#     "_ and \"",      # Contains both _ and "
#     ",",      # Contains , or ' or /
# ]

# for f in filters:
#     filtered = filter_strs(strs, f)
#     print(f"Filter '{f}': {filtered}")
