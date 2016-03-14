import subprocess
import os

# WARNING: only exit the matlab terminal by typing 'exit'.
# YOU WILL HAVE TO RESTART DICE IF YOU DO NOT !!1! (the terminal will not stay open)
cmd_line = """gnome-terminal -e 'tmux new -s matlab "matlab -nodesktop -nojvm"' """
p = subprocess.Popen(cmd_line, shell=True)

# Sleep for 20 sec or so

# Not tested that much: Should work:
os.system('./mx "circles"')

# If it does, circles.txt should be updated. Wait for it to update (make sure to check it!)

# Scrape the values, split into (x,y). In teh file, they look like: x0,x1,...,xn,y0,y1,...,yn

# Print the values

# Make sure the error in the beginning does not persist. Maybe write a bash script.

