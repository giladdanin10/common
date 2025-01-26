import inspect

def GetCurrentFunctionName():
    """
    Returns the name of the current function being executed.
    """
    return inspect.currentframe().f_back.f_code.co_name
