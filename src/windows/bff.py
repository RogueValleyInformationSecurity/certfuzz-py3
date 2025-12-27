# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "numpy>=1.24.0",
#     "scipy>=1.11.0",
#     "PyYAML>=6.0",
#     "pywin32>=306",
#     "WMI>=1.5.1",
# ]
# ///
'''
Created on Feb 8, 2012

@organization: cert.org
'''
import sys
from pathlib import Path

# Add src directory to path so certfuzz package can be found
src_dir = Path(__file__).resolve().parent.parent
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

from certfuzz.bff.windows import main

if __name__ == '__main__':
    main()
