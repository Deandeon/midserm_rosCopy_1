import sys
if sys.prefix == '/usr':
    sys.real_prefix = sys.prefix
    sys.prefix = sys.exec_prefix = '/home/david/MidsermWS/midserm_rosCopy_1/mid-semester-exams-practicals-robottt/install/rover_description'
