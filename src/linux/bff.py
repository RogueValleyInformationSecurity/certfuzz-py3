'''
Created on Oct 15, 2010

@organization: cert.org
'''
import sys
from pathlib import Path

# Add src directory to path so certfuzz package can be found
src_dir = Path(__file__).resolve().parent.parent
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

from certfuzz.bff.linux import main

if __name__ == '__main__':
    main()
