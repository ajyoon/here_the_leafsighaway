import os
import sys

FileNameIndex = 0
# All units in points at 72 DPI (per ReportLab's system)
LeftMargin = 72  # 1 Inch
RightMargin = 72  # 1 Inch
DocWorkingWidth = 468  # 8.5 Inch document, 1 inch margins on left & right, gives 6.5 inches of working space
MinColumnWidth = 99.212598  # Inches
PartOutputFolder = os.path.realpath(os.path.join(__file__, '..', '..', 'output'))
ResourcesFolder = os.path.realpath(os.path.join(__file__, '..', '..', 'resources'))
ImageDPI = 400
FontName = 'Crimson Text'
FontSize = 11
PlatformName = sys.platform
'''
Supported PlatformName values are:
Linux (2.x and 3.x)     ---> 'linux2' [for Linux PlatformName tests use PlatformName.startswith('linux')]
Windows                 ---> 'win32'
Mac OS X                ---> 'darwin'
'''
