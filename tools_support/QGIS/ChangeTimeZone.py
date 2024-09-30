import pytz
from PyQt5.QtCore import QDateTime, Qt

def ChangeTimeZone(layer_name, time_zone='UTC', column_names='time'):
    """
    Converts one or more time columns in the QGIS layer to the specified time zone.

    :param layer_name: The name of the QGIS layer containing the time data.
    :param time_zone: The target time zone to which the times will be converted (default is 'UTC').
    :param column_names: The name or list of names of the columns that contain the time data (default is 'time').
    """
    # Get the layer by name
    layers = QgsProject.instance().mapLayersByName(layer_name)
    
    if not layers:
        print(f"Layer '{layer_name}' not found.")
        return

    layer = layers[0]

    # Convert column_names to a list if it's a string
    if isinstance(column_names, str):
        column_names = [column_names]

    # Check if all columns exist in the layer
    existing_columns = [field.name() for field in layer.fields()]

    for col in column_names:
        print(col)
        if col not in existing_columns:
            print(f"Error: Column '{col}' not found in the layer.")
            return

    # Get the target timezone
    target_tz = pytz.timezone(time_zone)

    # Start editing the layer
    layer.startEditing()

    # Iterate through each feature in the layer
    for feature in layer.getFeatures():
        for col in column_names:
            original_time = feature[col]

            # Check if original_time is a string and convert it
            if isinstance(original_time, str):
                time_value = QDateTime.fromString(original_time, "yyyy-MM-dd HH:mm:ss")
            else:
                time_value = QDateTime(original_time)
            
            time_value.setTimeSpec(Qt.UTC)  # Set the time to UTC for conversion

            # Convert the time to the specified time zone
            utc_time = time_value.toTimeSpec(Qt.UTC).toPyDateTime()
            target_time = utc_time.astimezone(target_tz)
            
            # Update the feature with the new time
            layer.changeAttributeValue(feature.id(), layer.fields().indexFromName(col), target_time.strftime("%Y-%m-%d %H:%M:%S"))

    # Commit changes to the layer
    layer.commitChanges()
    
    print(f"Time columns {column_names} successfully converted to {time_zone}.")
