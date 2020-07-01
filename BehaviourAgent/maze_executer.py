# Details : 206228751 Allen Bronshtein

from sys import argv
from pddlsim.local_simulator import LocalSimulator

move_north_prob = 0.7
move_south_prob = 0.75
move_east_prob = 0.75
move_west_prob = 0.8
DISJUNCTION = "<class 'pddlsim.parser_independent.Disjunction'>"
CONJUNCTION = "<class 'pddlsim.parser_independent.Conjunction'>"
LITERAL = "<class 'pddlsim.parser_independent.Literal'>"
persons = []
north_to = []
south_to = []
east_to = []
west_to = []
walls = []
tiles = []
at = []
policy = {}
flag = True
goals = set()


class MazeExecuter(object):
    def __init__(self):
        self.successor = None

    def create_policy(self):
        for person in persons:
            stop = False
            start_tile = ""
            end_tile = ""
            for entry in at:
                if not stop:
                    if person == entry.split(" ")[0]:
                        start_tile = entry.split(" ")[3]
            for entry in goals:
                if person == entry.split(" ")[0]:
                    end_tile = entry.split(" ")[3]
                    stop = True
                    break
            if start_tile is not "" and end_tile is not "":
                reversed_route = self.plan_routes_bfs(start_tile, end_tile)
                current_tile = ""
                next_tile = ""
                next_next_tile = ""
                first = True
                route = []
                while len(reversed_route) is not 0:
                    if len(reversed_route) == 1 and first:
                        break
                    if current_tile == "":
                        current_tile = reversed_route.pop()
                    if next_tile == "":
                        next_tile = reversed_route.pop()
                        next_next_tile = next_tile
                    if first:
                        route.append("from " + current_tile + " move to " + next_tile)
                        first = False
                    else:
                        next_tile = next_next_tile
                        next_next_tile = reversed_route.pop()
                        route.append("from " + next_tile + " move to " + next_next_tile)
                policy[person] = (route, 0)

    def get_prob(self, t1, t2):
        if self.is_north_of(t1, t2):
            return move_north_prob
        if self.is_south_of(t1, t2):
            return move_south_prob
        if self.is_east_of(t1, t2):
            return move_east_prob
        if self.is_west_of(t1, t2):
            return move_west_prob

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

    def is_north_of(self, t1, t2):
        query = t1 + " is north to " + t2
        for entry in north_to:
            if query == entry:
                return True
        return False

    def is_south_of(self, t1, t2):
        query = t1 + " is south to " + t2
        for entry in south_to:
            if query == entry:
                return True
        return False

    def is_east_of(self, t1, t2):
        query = t1 + " is east to " + t2
        for entry in east_to:
            if query == entry:
                return True
        return False

    def is_west_of(self, t1, t2):
        query = t1 + " is west to " + t2
        for entry in west_to:
            if query == entry:
                return True
        return False

    def get_neighbors(self, current):
        neighbors = []
        is_north_to = current[1] + " is south to "
        is_south_to = current[1] + " is north to "
        is_east_to = current[1] + " is west to "
        is_west_to = current[1] + " is east to "
        for item in south_to:
            if is_north_to in item and item.split(" ")[4] in tiles:
                neighbors.append(item.split(" ")[4])
                break
        for item in north_to:
            if is_south_to in item and item.split(" ")[4] in tiles:
                neighbors.append(item.split(" ")[4])
                break
        for item in east_to:
            if is_west_to in item and item.split(" ")[4] in tiles:
                neighbors.append(item.split(" ")[4])
                break
        for item in west_to:
            if is_east_to in item and item.split(" ")[4] in tiles:
                neighbors.append(item.split(" ")[4])
                break
        return neighbors

    def plan_routes_bfs(self, start_tile, end_tile):
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
                        neighbor_state = (m[0] * self.get_prob(m[1], neighbor), neighbor, m[1])
                        open.append(neighbor_state)
                        open = sorted(open, key=lambda tup: tup[0])
                        open.reverse()
                    else:
                        neighbor_state = (m[0] * self.get_prob(m[1], neighbor), neighbor, m[1])
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
                    for item in at:
                        if literal.args[0] == string.split(" ")[0]:
                            current = item.split(" ")[3]
                            break
                    for item in local_goals:
                        if literal.args[0] == item.split(" ")[0] and string != item:
                            flag = True
                            break
                    if flag:
                        flag = False
                        continue
                    l = self.plan_routes_bfs(current, literal.args[1])
                    if len(l) == 0:
                        continue
                    else:
                        local_goals.append(str(literal.args[0]) + " is at " + str(literal.args[1]))
            elif str(type(entry)) == LITERAL:
                local_goals.append(str(entry.args[0]) + " is at " + str(entry.args[1]))
        goals = set(local_goals)
        print goals

    def initialize(self, services):
        self.services = services

        _pddl_list = list(self.services.perception.get_state().get('person'))
        for item in _pddl_list:
            persons.append(item[0])

        _pddl_list = list(self.services.perception.get_state().get('north'))
        for item in _pddl_list:
            north_to.append(item[0] + " is north to " + item[1])

        _pddl_list = list(self.services.perception.get_state().get('south'))
        for item in _pddl_list:
            south_to.append(item[0] + " is south to " + item[1])

        _pddl_list = list(self.services.perception.get_state().get('east'))
        for item in _pddl_list:
            east_to.append(item[0] + " is east to " + item[1])

        _pddl_list = list(self.services.perception.get_state().get('west'))
        for item in _pddl_list:
            west_to.append(item[0] + " is west to " + item[1])

        _pddl_list = list(self.services.perception.get_state().get('wall'))
        for item in _pddl_list:
            walls.append(item[0])

        _pddl_list = list(self.services.perception.get_state().get('empty'))
        for item in _pddl_list:
            tiles.append(item[0])

        _pddl_list = list(self.services.perception.get_state().get('at'))
        for item in _pddl_list:
            at.append(item[0] + " is at " + item[1])

        _pddl_list = self.services.goal_tracking.uncompleted_goals
        self.choose_goals(_pddl_list)

        self.create_policy()

    def update(self):
        while len(at) is not 0:
            at.pop()
        _pddl_list = list(self.services.perception.get_state().get('at'))
        for item in _pddl_list:
            at.append(item[0] + " is at " + item[1])

    def next_action(self):
        self.update()
        remove_from_at = []
        for item in at:
            remove_from_at.append(item)
        if self.services.goal_tracking.reached_all_goals() or len(goals) == 0:
            return None
        for item in at:
            person = item.split(" ")[0]
            removed = False
            for goal in goals:
                if removed:
                    break
                elif item == goal:
                    continue
                elif person == goal.split(" ")[0]:
                    remove_from_at.remove(item)
                    removed = True
        for item in remove_from_at:
            at.remove(item)
        if len(at) == 0:
            return None
        person = at[0].split(" ")[0]
        location = at[0].split(" ")[3]
        query = "from " + location
        instruction = ""
        item = policy.get(person)
        if policy.get(person) is None:
            return None
        for entry in policy.get(person)[0]:
            if query.split(" ")[1] == entry.split(" ")[1]:
                instruction = entry
                break
        if instruction == "":
            return None
        current = instruction.split(" ")[1]
        next = instruction.split(" ")[4]
        if self.is_north_of(current, next):
            return "(move-north " + person + " " + current + " " + next + ")"
        if self.is_south_of(current, next):
            return "(move-south " + person + " " + current + " " + next + ")"
        if self.is_east_of(current, next):
            return "(move-east " + person + " " + current + " " + next + ")"
        if self.is_west_of(current, next):
            return "(move-west " + person + " " + current + " " + next + ")"


domain_path = argv[1]
problem_path = argv[2]
print LocalSimulator().run(domain_path, problem_path, MazeExecuter())
