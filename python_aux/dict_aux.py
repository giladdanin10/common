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

def recursive_merge_dictionaries(base, updates):
    """
    Recursively merges two dictionaries, prioritizing values from the `updates` dictionary
    for overlapping keys. If both `base` and `updates` contain a nested dictionary for
    the same key, their contents are merged recursively, with `updates` values taking precedence.

    Parameters:
        base (dict): The base dictionary that is updated in place with values from `updates`.
        updates (dict): The dictionary containing additional keys and values to merge
                        into the `base` dictionary. Its values take precedence for overlapping keys.

    Returns:
        dict: The merged dictionary, where `updates` values take precedence for overlapping keys
              and additional keys from `updates` are added to `base`.

    Behavior:
        - For overlapping keys:
            - If the value is a dictionary in both `base` and `updates`, the function
              merges them recursively, prioritizing values from `updates`.
            - Otherwise, the value in `updates` overwrites the value in `base`.
        - For non-overlapping keys:
            - Keys and values from `updates` are added to `base`.

    Example:
        >>> base = {'a': 1, 'b': {'x': 10, 'y': 20}}
        >>> updates = {'b': {'y': 200, 'z': 300}, 'c': 3}
        >>> result = recursive_merge_dictionaries(base, updates)
        >>> print(result)
        {'a': 1, 'b': {'x': 10, 'y': 200, 'z': 300}, 'c': 3}

    Notes:
        - This function modifies the `base` dictionary in place.
        - If you need to retain the original `base` dictionary, make a deep copy before calling this function.
    """
    for key, value in updates.items():
        if isinstance(value, dict) and isinstance(base.get(key), dict):
            # Recursively merge dictionaries; `updates` values win
            recursive_merge_dictionaries(base[key], value)
        else:
            # Overwrite or add key from updates
            base[key] = value
    return base

