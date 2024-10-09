def find_var_in_list(lst, var):
    """
    Find the indices of a variable in a list.

    Parameters:
    lst (list): List of integers or strings.
    var (int or str): Variable to find in the list.

    Returns:
    list: Indices of all occurrences of the variable in the list.
    """
    if not isinstance(var, (int, str)):
        raise ValueError("Variable must be an integer or a string")
    
    indices = [i for i, x in enumerate(lst) if x == var]
    return indices


def remove_list_member(lst, identifier):
    """
    Removes elements from a list by their values or indices.

    Parameters:
    lst (list): The list from which to remove the elements.
    identifier (int, str, or list): The index (int), value (str), or list of indices/values to remove.

    Returns:
    list: The updated list with the specified elements removed.
    """
    if isinstance(identifier, list):
        # If identifier is a list, handle each element in it
        for item in sorted(identifier, reverse=True):  # Sort and reverse to handle indices correctly
            lst = remove_list_member(lst, item)
    elif isinstance(identifier, int):
        try:
            lst.pop(identifier)
        except IndexError:
            print(f"Error: Index {identifier} is out of range.")
    elif isinstance(identifier, str):
        try:
            lst.remove(identifier)
        except ValueError:
            print(f"Error: Value '{identifier}' not found in the list.")
    else:
        print("Error: Identifier must be an int (index), str (value), or list of indices/values.")
    
    return lst

# # Example usage
# my_list = ['apple', 'banana', 'cherry', 'date', 'elderberry', 'fig', 'grape']

# # Remove by index
# print(remove_list_member(my_list.copy(), 2))  # Outpu


def get_partial_list(input_list, indices):
    """
    Retrieves elements from input_list based on the specified indices or ranges.
    
    Parameters:
    - input_list (list): The list from which to retrieve elements.
    - indices (int, list, or range): Can be a single index, a list of indices, or a range.
    
    Returns:
    - (list, list): A tuple of two lists:
                    - First list contains the values.
                    - Second list contains the corresponding indices.
                    If a single index is provided, the function returns individual values and index.
    """
    values = []
    indices_list = []

    # If indices is a single integer
    if isinstance(indices, int):
        if 0 <= indices < len(input_list):
            return input_list[indices], indices  # Return single value and index directly
        else:
            raise IndexError("Index out of range.")

    # If indices is a range, slice, or list of indices
    for index in indices:
        # Check if it's a slice object (e.g., 10:12)
        if isinstance(index, int):
            if 0 <= index < len(input_list):
                values.append(input_list[index])
                indices_list.append(index)
        else:
            raise ValueError("Unsupported index type. Only int or range is allowed.")

    return values, indices_list


def remove_nans_and_nones_from_list(lst):
    """
    Removes all occurrences of None, NaN, and their string representations from a list.

    Parameters:
    - lst (list): The list from which to remove None, NaN, and their string representations.

    Returns:
    - list: A new list with None, NaN, and their string representations removed.
    """
    return [
        item for item in lst
        if item is not None
        and not (isinstance(item, float) and np.isnan(item))
    ]


def remove_from_list(lst, value=None, index=None):
    """
    Removes all occurrences of a specified value or a specific index from a list.

    Parameters:
    - lst (list): The list from which to remove the value or index.
    - value: The value to remove from the list. Default is None.
    - index: The index of the element to remove from the list. Default is None.

    Returns:
    - list: A new list with the specified value or index removed.

    Raises:
    - ValueError: If neither value nor index is provided.
    - IndexError: If the specified index is out of range.
    """
    if value is None and index is None:
        raise ValueError("Either 'value' or 'index' must be provided.")

    if index is not None:
        if not isinstance(index, int) or index < 0 or index >= len(lst):
            raise IndexError("Index out of range.")
        # Create a new list excluding the element at the specified index
        return [item for i, item in enumerate(lst) if i != index]

    # Create a new list excluding all occurrences of the specified value
    return [item for item in lst if item != value]


def test (k):
    return k+1  

def print_list_as_column(lst):
    """
    Prints a list of items, one item per line.

    Parameters:
    - lst (list): The list of items to print.
    """
    for item in lst:
        print(item)


