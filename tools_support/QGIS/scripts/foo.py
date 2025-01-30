import sys

# Add the parent directory where PyQt5 is located
sys.path.append(r'C:\\Program Files\\QGIS 3.40.2\\apps\\Python312\\Lib\\site-packages')

print(1)
import PyQt5 as foo  # Now it should work!
print(2)
