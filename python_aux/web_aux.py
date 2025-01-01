import webbrowser

def OpenUrlInBrowser(url, new_window=False):
    """
    Open a URL in Microsoft Edge.
    
    Parameters:
        url (str): The URL to open.
        new_window (bool): If True, opens the URL in a new browser window.
                           If False, opens the URL in a new tab.
    """
    edge_path = "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe %s"
    
    try:
        # Register Edge as the browser
        edge = webbrowser.get(edge_path)
        
        # Open the URL
        if new_window:
            edge.open_new(url)
        else:
            edge.open(url)
        
        print(f"URL opened successfully in Edge: {url}")
    except Exception as e:
        print(f"Failed to open URL in Edge: {url}. Error: {e}")
