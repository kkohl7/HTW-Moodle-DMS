#!E:\DMSMoodle\venv\Scripts\python.exe
# EASY-INSTALL-ENTRY-SCRIPT: 'pypptx==0.2.2','console_scripts','pptx'
__requires__ = 'pypptx==0.2.2'
import re
import sys
from pkg_resources import load_entry_point

if __name__ == '__main__':
    sys.argv[0] = re.sub(r'(-script\.pyw?|\.exe)?$', '', sys.argv[0])
    sys.exit(
        load_entry_point('pypptx==0.2.2', 'console_scripts', 'pptx')()
    )
