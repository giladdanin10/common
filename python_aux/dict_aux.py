def get_partial_dict(data_dic, keys_list):
    """
    Extract a partial dictionary from the original dictionary based on a list of keys.
    
    Parameters:
    - data_dic (dict): The original dictionary.
    - keys_list (list): The list of keys to extract.
    
    Returns:
    - dict: A new dictionary with only the specified keys.
    """
    return {key: data_dic[key] for key in keys_list if key in data_dic}

# Example usage:
original_dict = {
    'a': 1,
    'b': 2,
    'c': 3,
    'd': 4
}

keys_to_extract = ['a', 'c']

partial_dict = get_partial_dict(original_dict, keys_to_extract)
