import subprocess
import os
import re
# WARNING: only exit the matlab terminal by typing 'exit'.
# YOU WILL HAVE TO RESTART DICE IF YOU DO NOT !!1! (the terminal will not stay open)
cmd_line = """gnome-terminal -e 'tmux new -s matlab "matlab -nodesktop -nojvm"' """
p = subprocess.Popen(cmd_line, shell=True)

# Sleep for 20 sec or so

# Not tested that much: Should work:
os.system('./mx "circles"')

# If it does, circles.txt should be updated. Wait for it to update (make sure to check it!)

# Scrape the values, split into (x,y). In teh file, they look like: x0,x1,...,xn,y0,y1,...,yn
fname = 'circles.txt'
file = open(fname).read()
file_coords = re.findall('[A-Za-z\+\-0-9]+[A-Za-z0-9_\.]*|[()]',file)
coords = {}
n = len(file_coords)
for i in range(0,n/2):
    coords[i] = (float(file_coords[i]),float(file_coords[i+n/2]))
    print coords[i]



# Print the values

# Make sure the error in the beginning does not persist. Maybe write a bash script.

