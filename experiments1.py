__author__ = 's1309645'
# import mlab.latest_release as matlab
from pymatlab.matlab import MatlabSession


# session = MatlabSession(matlab_root='/opt/matlab-R2015a/')
# session.close()

import pymatlab
session = MatlabSession(matlab_root='/opt/matlab-R2015a/')
session.putvalue('A',5)
print session.run('B=2*A')
del session

print "derp"