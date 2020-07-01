# Details : 206228751 Allen Bronshtein

from sys import argv
from pddlsim.local_simulator import LocalSimulator

DISJUNCTION = "<class 'pddlsim.parser_independent.Disjunction'>"
CONJUNCTION = "<class 'pddlsim.parser_independent.Conjunction'>"
LITERAL = "<class 'pddlsim.parser_independent.Literal'>"
player_location = ""
balls = []
connections = []
ball_locations = []
kick_prob = 0.75
move_prob = 0.5
goals = set()
count = 0


class FootballExecuter(object):
    def __init__(self):
        self.successor = None

    def in_closed(self, item, closed):
        for entry in closed:
            if entry[1] == item:
                return True
        return False

    def in_open(self, item, open):
        for entry in open:
            if entry[1] == item:
                return True
        return False

    def get_prob(self, action):
        if action == "move":
            return move_prob
        elif action == "kick":
            return kick_prob

    def get_neighbors(self, current):
        neighbors = []
        string = str(current[1]) + " is connected to "
        for item in connections:
            if string in item:
                neighbors.append(item.split(" ")[4])
        return neighbors

    def plan_routes_bfs(self, start_tile, end_tile, for_action):
        open = []
        closed = []
        solution = []
        null_state = (1, start_tile, None)
        open.append(null_state)
        while len(open) is not 0:
            m = (open[0][0], open[0][1], open[0][2])
            open.pop(0)
            open = sorted(open, key=lambda tup: tup[0])
            open.reverse()
            closed.append(m)
            if m[1] == end_tile:
                solution.append(m[1])
                parent = m[2]
                while parent is not null_state[2]:
                    if parent == closed[0][1]:
                        solution.append(closed[0][1])
                        parent = closed[0][2]
                        closed.pop(0)
                    else:
                        closed.append(closed[0])
                        closed.pop(0)
            else:
                neighbors = self.get_neighbors(m)
                for neighbor in neighbors:
                    if self.in_closed(neighbor, closed):
                        continue
                    if not self.in_open(neighbor, open):
                        neighbor_state = (m[0] * self.get_prob(for_action), neighbor, m[1])
                        open.append(neighbor_state)
                        open = sorted(open, key=lambda tup: tup[0])
                        open.reverse()

                    else:
                        neighbor_state = (m[0] * self.get_prob(for_action), neighbor, m[1])
                        replace = False
                        for item in open:
                            if neighbor == item[1] and neighbor_state[0] > item[0]:
                                open.pop(0)
                                replace = True
                        if replace:
                            open.append(neighbor_state)
                            open = sorted(open, key=lambda tup: tup[0])
                            open.reverse()

        return solution

    def choose_goals(self, o):
        global goals
        local_goals = []
        current = ""
        flag = False
        conjunction = o[0]
        for entry in conjunction.parts:
            if str(type(entry)) == CONJUNCTION:
                for literal in entry.parts:
                    local_goals.append(str(literal.args[0]) + " is at " + str(literal.args[1]))
            elif str(type(entry)) == DISJUNCTION:
                for literal in entry.parts:
                    dead_lock = False
                    counter = 0
                    string = str(literal.args[0]) + " is at " + str(literal.args[1])
                    # -------------------------------------------------
                    for temp_entry in conjunction.parts:
                        if str(type(temp_entry)) == DISJUNCTION:
                            for temp_literal in temp_entry.parts:
                                string_1 = str(temp_literal.args[0]) + " is at " + str(temp_literal.args[1])
                                if string == string_1:
                                    counter += 1
                                if counter >= 2:
                                    dead_lock = True
                                if dead_lock:
                                    break

                        if dead_lock:
                            for obj in local_goals:
                                if string.strip(" ")[0] == obj.strip(" ")[0]:
                                    local_goals.remove(obj)
                            local_goals.append(string)
                            continue
                    if dead_lock:
                        continue
                    has_dead_lock = False
                    for i in local_goals:
                        if i.split(" ")[0] == string.split(" ")[0]:
                            has_dead_lock = True
                            break
                    if has_dead_lock:
                        continue
                    # --------------------------------------------------

                    if literal.args[0] == string.split(" ")[0]:
                        current = player_location.split(" ")[3]
                    for item in local_goals:
                        if literal.args[0] == item.split(" ")[0] and string != item:
                            flag = True
                            break
                    if flag:
                        flag = False
                        continue
                    l = self.plan_routes_bfs(current, literal.args[1], "kick")
                    if len(l) == 0:
                        continue
                    else:
                        local_goals.append(str(literal.args[0]) + " is at " + str(literal.args[1]))
            elif str(type(entry)) == LITERAL:
                l = []
                for item in ball_locations:
                    if entry.args[0] == item.split(" ")[0]:
                        l = self.plan_routes_bfs(item.split(" ")[3], entry.args[1], "kick")
                        break
                if len(l) != 0:
                    local_goals.append(str(entry.args[0]) + " is at " + str(entry.args[1]))
        goals = set(local_goals)

    def update(self):
        global player_location
        player_location = "player is at " + str(list(self.services.perception.get_state().get('at-robby'))[0][0])
        while len(ball_locations) != 0:
            ball_locations.pop()
        _pddl_list = list(self.services.perception.get_state().get('at-ball'))
        for item in _pddl_list:
            ball_locations.append(item[0] + " is at " + item[1])

    def initialize(self, services):
        global player_location
        self.services = services
        player_location = "player is at " + str(list(self.services.perception.get_state().get('at-robby'))[0][0])
        _pddl_list = list(self.services.perception.get_state().get('ball'))
        for item in _pddl_list:
            balls.append(item[0])
        _pddl_list = list(self.services.perception.get_state().get('connected'))
        for item in _pddl_list:
            connections.append(item[0] + " is connected to " + item[1])
        _pddl_list = list(self.services.perception.get_state().get('at-ball'))
        for item in _pddl_list:
            ball_locations.append(item[0] + " is at " + item[1])
        self.choose_goals(self.services.goal_tracking.uncompleted_goals)
        # print goals

    def goal_reached(self, goal):
        for item in ball_locations:
            if item == goal:
                return True
        return False

    def near_ball(self, ball):
        ball_location = ""
        for item in ball_locations:
            if ball == item.split(" ")[0]:
                ball_location = item.split(" ")[3]
                break
        my_location = player_location.split(" ")[3]
        if ball_location == my_location:
            return True
        return False

    def kick_ball(self, ball):
        route = []
        my_location = player_location.split(" ")[3]
        ball_goal_tile = ""
        for goal in goals:
            if ball == goal.split(" ")[0]:
                ball_goal_tile = goal.split(" ")[3]
                break
        reversed_route = self.plan_routes_bfs(my_location, ball_goal_tile, "kick")
        while len(reversed_route) is not 0:
            item = reversed_route.pop()
            route.append(item)
        wanted_location = route[1]
        return "(kick " + ball + " " + my_location + " " + str(wanted_location) + " " + str(wanted_location) + ")"

    def move_to_ball(self, ball):
        route = []
        ball_location = ""
        for item in ball_locations:
            if ball == item.split(" ")[0]:
                ball_location = item.split(" ")[3]
                break
        my_location = player_location.split(" ")[3]
        reversed_route = self.plan_routes_bfs(my_location, ball_location, "move")
        while len(reversed_route) is not 0:
            item = reversed_route.pop()
            route.append(item)
        wanted_location = route[1]
        return "(move" + " " + str(my_location) + " " + str(wanted_location) + ")"

    def next_action(self):
        global count
        self.update()
        if self.services.goal_tracking.reached_all_goals():
            return None

        for goal in goals:
            if self.goal_reached(goal):
                count += 1
                continue
            if count >= len(goals):
                return None
            ball = goal.split(" ")[0]
            if self.near_ball(ball):
                return self.kick_ball(ball)
            else:
                return self.move_to_ball(ball)
        return None


domain_path = argv[1]
problem_path = argv[2]
print LocalSimulator().run(domain_path, problem_path, FootballExecuter())
