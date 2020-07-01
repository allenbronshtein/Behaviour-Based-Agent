# Details : 206228751 Allen Bronshtein

# -------- Imports -------------#

from sys import argv

# ------------------------------#

# -------- Globals -------------#

maze_flag = False
football_flag = False

# ------------------------------#


def getDomainType():
    global maze_flag, football_flag
    f = open(argv[1], "r")
    line = f.readline()
    while line == '\r\n':
        line = f.readline()
    f.close()
    if "maze" in line:
        maze_flag = True
    elif "football" in line:
        football_flag = True
    else:
        print "Error reading pddl file."


getDomainType()
if maze_flag:
    from maze_executer import MazeExecuter
if football_flag:
    from football_executer import FootballExecuter
