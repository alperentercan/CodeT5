import json
import os
import sys

AGENT_CHAR = {'south': 'v', 'west': '<', 'north': '^', 'east': '>'}


def task_json2ascii(json_repr):
    pregrid = [['.'] * json_repr['gridsz_num_cols'] for _ in range(json_repr['gridsz_num_rows'])]
    postgrid = [['.'] * json_repr['gridsz_num_cols'] for _ in range(json_repr['gridsz_num_rows'])]
    print(json_repr)
    for wall_x, wall_y in json_repr['walls']:
        pregrid[wall_x][wall_y] = '#'
        postgrid[wall_x][wall_y] = '#'

    for pre_marker_x, pre_marker_y in json_repr['pregrid_markers']:
        pregrid[pre_marker_x][pre_marker_y] = '1'

    for post_marker_x, post_marker_y in json_repr['postgrid_markers']:
        postgrid[post_marker_x][post_marker_y] = '1'


    pregrid_agent_str = f"Agent Location: (row={json_repr['pregrid_agent_row']},col={json_repr['pregrid_agent_col']})" +\
                        f", Agent Direction: {json_repr['pregrid_agent_dir']} "
    postgrid_agent_str = f"Agent Location: (row={json_repr['postgrid_agent_row']},col={json_repr['postgrid_agent_col']})" + \
                        f", Agent Direction: {json_repr['postgrid_agent_dir']} "


    pregrid_grid_str = "\n".join([" ".join(row) for row in pregrid])
    postgrid_grid_str = "\n".join([" ".join(row) for row in postgrid])

    ascii_repr = "Pregrid\n" + pregrid_grid_str + "\n" + pregrid_agent_str + "\n\n" + "Postgrid\n" + postgrid_grid_str + "\n" + postgrid_agent_str

    return ascii_repr

def task_json2pddl(json_repr):

    init_walls = [f"wall at ({x},{y})" for x,y in json_repr['walls']]
    init_walls = ";".join(init_walls)

    init_markers = [f"marker at ({x},{y})" for x,y in json_repr['pregrid_markers']]
    init_markers = ";".join(init_markers)


    init_non_empty_cells = [(x,y) for x,y in json_repr['pregrid_markers']] + [(x,y) for x,y in json_repr['walls']]
    init_empty = [f"empty at ({x},{y})" for x,y in zip(range(json_repr['gridsz_num_rows']),range(json_repr['gridsz_num_cols'])) if (x,y) not in init_non_empty_cells]
    init_empty = ";".join(init_empty)

    init_agent = f"agent at ({json_repr['pregrid_agent_row']},{json_repr['pregrid_agent_col']}), direction {json_repr['pregrid_agent_dir']}"

    init = "<INIT>" + " " + init_agent + ";" + init_markers + ";" + init_walls + ";" + init_empty


    goal_agent = f"agent at ({json_repr['postgrid_agent_row']},{json_repr['postgrid_agent_col']}), direction {json_repr['postgrid_agent_dir']}"
    goal_marker = [f"marker at ({x},{y})" for x,y in json_repr['postgrid_markers']]
    goal_marker = ";".join(goal_marker)

    goal_non_empty_cells = [(x, y) for x, y in json_repr['postgrid_markers']] + [(x, y) for x, y in json_repr['walls']]
    goal_empty = [f"empty at ({x},{y})" for x, y in
                  zip(range(json_repr['gridsz_num_rows']), range(json_repr['gridsz_num_cols'])) if
                  (x, y) not in goal_non_empty_cells]
    goal_empty = ";".join(goal_empty)


    goal = "<GOAL>" + " " + goal_agent + ";" + goal_marker + ";" + goal_empty

    move_action_header = "<ACTION> move"
    move_action_s = "<PRE> agent at (x,y), direction west" + "\n" + "<EFFECT> agent at (x, y-1), direction west"
    move_action_w = "<PRE> agent at (x,y), direction west" + "\n" + "<EFFECT> agent at (x, y-1), direction west"
    move_action_n= "<PRE> agent at (x,y), direction north" + "\n" + "<EFFECT> agent at (x-1, y), direction north"
    move_action_e = "<PRE> agent at (x,y), direction east" + "\n" + "<EFFECT> agent at (x, y+1), direction east"
    move = move_action_header + "\n" + move_action_s + "\n" + move_action_w + "\n" + move_action_n + "\n" + move_action_e

    turn_left_action_header = "<ACTION> turn_left"
    turn_left_action_s = "<PRE> agent at (x,y), direction south" + "\n" + "<EFFECT> agent at (x, y), direction east"
    turn_left_action_w = "<PRE> agent at (x,y), direction west" + "\n" + "<EFFECT> agent at (x, y), direction south"
    turn_left_action_n = "<PRE> agent at (x,y), direction north" + "\n" + "<EFFECT> agent at (x, y), direction west"
    turn_left_action_e = "<PRE> agent at (x,y), direction east" + "\n" + "<EFFECT> agent at (x, y), direction north"
    turn_left = turn_left_action_header + "\n" + turn_left_action_s + "\n" + turn_left_action_w + "\n" + turn_left_action_n + "\n" + turn_left_action_e

    turn_right_action_header = "<ACTION> turn_right"
    turn_right_action_s = "<PRE> agent at (x,y), direction south" + "\n" + "<EFFECT> agent at (x, y), direction west"
    turn_right_action_w = "<PRE> agent at (x,y), direction west" + "\n" + "<EFFECT> agent at (x, y), direction north"
    turn_right_action_n = "<PRE> agent at (x,y), direction north" + "\n" + "<EFFECT> agent at (x, y), direction east"
    turn_right_action_e = "<PRE> agent at (x,y), direction east" + "\n" + "<EFFECT> agent at (x, y), direction south"
    turn_right = turn_right_action_header + "\n" + turn_right_action_s + "\n" + turn_right_action_w + "\n" + turn_right_action_n + "\n" + turn_right_action_e

    put_marker = "<ACTION> put_marker" + "\n" + "<PRE> agent at (x,y); empty at (x,y)" + "\n" + "<EFFECT> agent at (x, y); marker at (x,y)"
    pick_marker = "<ACTION> pick_marker" + "\n" + "<PRE> agent at (x,y); marker at (x,y)" + "\n" + "<EFFECT> agent at (x, y); empty at (x,y)"

    problem_instance = init + "\n" + goal + "\n" + move + "\n" + turn_left + "\n" + turn_right + "\n" + put_marker + "\n" + pick_marker

    return problem_instance

def task_json2pddltech(json_repr):

    init_walls = [f"Wall({x},{y})" for x,y in json_repr['walls']]
    init_walls = " and ".join(init_walls)

    init_markers = [f"Marker({x},{y})" for x,y in json_repr['pregrid_markers']]
    init_markers = " and ".join(init_markers)


    init_non_empty_cells = [(x,y) for x,y in json_repr['pregrid_markers']] + [(x,y) for x,y in json_repr['walls']]
    init_empty = [f"not Marker({x},{y})" for x,y in zip(range(json_repr['gridsz_num_rows']),range(json_repr['gridsz_num_cols'])) if (x,y) not in init_non_empty_cells]
    init_empty = " and ".join(init_empty)

    init_agent = f"AgentLoc({json_repr['pregrid_agent_row']},{json_repr['pregrid_agent_col']}) and AgentDirection({json_repr['pregrid_agent_dir']})"

    init = "<INIT>" + " " + init_agent + " and " + init_markers + " and "*(len(init_markers) != 0) + init_walls + " and " + init_empty


    goal_agent = f"AgentLoc({json_repr['postgrid_agent_row']},{json_repr['postgrid_agent_col']}) and AgentDirection({json_repr['postgrid_agent_dir']})"
    goal_marker = [f"Marker({x},{y})" for x,y in json_repr['postgrid_markers']]
    goal_marker = " and ".join(goal_marker)

    goal_non_empty_cells = [(x, y) for x, y in json_repr['postgrid_markers']] + [(x, y) for x, y in json_repr['walls']]
    goal_empty = [f"not Marker({x},{y})" for x, y in
                  zip(range(json_repr['gridsz_num_rows']), range(json_repr['gridsz_num_cols'])) if
                  (x, y) not in goal_non_empty_cells]
    goal_empty = " and ".join(goal_empty)


    goal = "<GOAL>" + " " + goal_agent + " and " + goal_marker + " and "*(len(goal_marker) != 0) + goal_empty

    move_action_header = "<ACTION> move"
    move_action_s = "<PRE> AgentLoc(x,y) and AgentDirection(south)" + "\n" + "<EFFECT> AgentLoc(x, y-1) and AgentDirection(south)"
    move_action_w = "<PRE> AgentLoc(x,y) and AgentDirection(west)" + "\n" + "<EFFECT> AgentLoc(x, y-1) and AgentDirection(west)"
    move_action_n= "<PRE> AgentLoc(x,y) and AgentDirection(north)" + "\n" + "<EFFECT> AgentLoc(x-1, y) and AgentDirection(north)"
    move_action_e = "<PRE> AgentLoc(x,y) and AgentDirection(east)" + "\n" + "<EFFECT> AgentLoc(x, y+1) and AgentDirection(east)"
    move = move_action_header + "\n" + move_action_s + "\n" + move_action_w + "\n" + move_action_n + "\n" + move_action_e

    turn_left_action_header = "<ACTION> turn_left"
    turn_left_action_s = "<PRE> AgentLoc(x,y) and AgentDirection(south)" + "\n" + "<EFFECT> AgentLoc(x, y) and AgentDirection(east)"
    turn_left_action_w = "<PRE> AgentLoc(x,y) and AgentDirection(west)" + "\n" + "<EFFECT> AgentLoc(x, y) and AgentDirection(south)"
    turn_left_action_n = "<PRE> AgentLoc(x,y) and AgentDirection(north)" + "\n" + "<EFFECT> AgentLoc(x, y) and AgentDirection(west)"
    turn_left_action_e = "<PRE> AgentLoc(x,y) and AgentDirection(east)" + "\n" + "<EFFECT> AgentLoc(x, y) and AgentDirection(north)"
    turn_left = turn_left_action_header + "\n" + turn_left_action_s + "\n" + turn_left_action_w + "\n" + turn_left_action_n + "\n" + turn_left_action_e

    turn_right_action_header = "<ACTION> turn_right"
    turn_right_action_s = "<PRE> AgentLoc(x,y) and AgentDirection(south)" + "\n" + "<EFFECT> AgentLoc(x, y) and AgentDirection(west)"
    turn_right_action_w = "<PRE> AgentLoc(x,y) and AgentDirection(west)" + "\n" + "<EFFECT> AgentLoc(x, y) and AgentDirection(north)"
    turn_right_action_n = "<PRE> AgentLoc(x,y) and AgentDirection(north)" + "\n" + "<EFFECT> AgentLoc(x, y) and AgentDirection(east)"
    turn_right_action_e = "<PRE> AgentLoc(x,y) and AgentDirection(east)" + "\n" + "<EFFECT> AgentLoc(x, y) and AgentDirection(south)"
    turn_right = turn_right_action_header + "\n" + turn_right_action_s + "\n" + turn_right_action_w + "\n" + turn_right_action_n + "\n" + turn_right_action_e

    put_marker = "<ACTION> put_marker" + "\n" + "<PRE> AgentLoc(x,y) and not Marker(x,y)" + "\n" + "<EFFECT> AgentLoc(x, y) and Marker(x,y)"
    pick_marker = "<ACTION> pick_marker" + "\n" + "<PRE> AgentLoc(x,y) and Marker(x,y)" + "\n" + "<EFFECT> AgentLoc(x, y) and not Marker(x,y)"

    problem_instance = init + "\n" + goal + "\n" + move + "\n" + turn_left + "\n" + turn_right + "\n" + put_marker + "\n" + pick_marker

    return problem_instance

def task_json2python(json_repr):

    # instance_class = "class Grid():\n" + f"\tdef __init__():\n\t\tself.agent_loc = ({json_repr['pregrid_agent_row']},{json_repr['pregrid_agent_col']})" +\
    #                  "\n" + f"\t\tself.agent_dir = `{json_repr['pregrid_agent_dir']}\n\t\tself.walls = {[(x,y) for x,y in json_repr['walls']]}" + "\n" +\
    #                  "\t\tself.markers = "

    preamble = f"agent_loc_x, agent_loc_y = {json_repr['pregrid_agent_row']},{json_repr['pregrid_agent_col']}" +\
                     "\n" + f"agent_dir = `{json_repr['pregrid_agent_dir']}\nwalls = {[(x,y) for x,y in json_repr['walls']]}" + "\n" +\
                     f"markers = {[(x,y) for x,y in json_repr['pregrid_markers']]}" +\
                    f"\ngoal_agent_loc_x, goal_agent_loc_y = {json_repr['postgrid_agent_row']},{json_repr['postgrid_agent_col']}" + \
                    f"\ngoal_agent_dir = {json_repr['postgrid_agent_dir']}" +\
                    f"\ngoal_markers = {[(x,y) for x,y in json_repr['pregrid_markers']]}"

    move_function = "def move():" +\
                    "\n\tif agent_dir == 'south': agent_loc_x += 1" +\
                    "\n\telif agent_dir == 'west': agent_loc_y -= 1" +\
                    "\n\telif agent_dir == 'north': agent_loc_x -= 1" + \
                    "\n\telif agent_dir == 'east': agent_loc_y += 1"

    turn_left_function = "def turnLeft():" +\
                    "\n\tif agent_dir == 'south': agent_dir = 'east'" +\
                    "\n\telif agent_dir == 'west': agent_dir = 'south'" +\
                    "\n\telif agent_dir == 'north': agent_dir = 'west'" + \
                    "\n\telif agent_dir == 'east': agent_dir = 'north"
    turn_right_function = "def turnRight():" +\
                    "\n\tif agent_dir == 'south': agent_dir = 'west'" +\
                    "\n\telif agent_dir == 'west': agent_dir = 'north'" +\
                    "\n\telif agent_dir == 'north': agent_dir = 'east'" + \
                    "\n\telif agent_dir == 'east': agent_dir = 'south"

    put_marker_function = "def putMarker():" +\
                    "\n\tif (agent_loc_x, agent_loc_y) not in markers: markers.append((agent_loc_x, agent_loc_y))" +\
                    "\n\telse: raise Exception"

    pick_marker_function = "def pickMarker():" +\
                    "\n\tif (agent_loc_x, agent_loc_y) in markers: markers.remove((agent_loc_x, agent_loc_y))" +\
                    "\n\telse: raise Exception"

    finish_function = "def finish():" +\
                    "\n\tif agent_loc_x == goal_agent_loc_x and agent_loc_y == goal_agent_loc_y and agent_dir == goal_agent_dir and set(markers) == set(goal_markers):"+\
                    "\n\t\treturn True" +\
                    "\n\telse:" +\
                    "\n\t\treturn False"

    problem_instance = "\n\n".join([preamble, move_function, turn_left_function, turn_right_function, put_marker_function, pick_marker_function, finish_function])

    return problem_instance


def task_json2asciitokens(json_repr):
    pregrid = [['<empty>'] * json_repr['gridsz_num_cols'] for _ in range(json_repr['gridsz_num_rows'])]
    postgrid = [['<empty>'] * json_repr['gridsz_num_cols'] for _ in range(json_repr['gridsz_num_rows'])]
    print(json_repr)
    for wall_x, wall_y in json_repr['walls']:
        pregrid[wall_x][wall_y] = '<wall>'
        postgrid[wall_x][wall_y] = '<wall>'

    for pre_marker_x, pre_marker_y in json_repr['pregrid_markers']:
        pregrid[pre_marker_x][pre_marker_y] = '<marker>'

    for post_marker_x, post_marker_y in json_repr['postgrid_markers']:
        postgrid[post_marker_x][post_marker_y] = '<marker>'


    pregrid_agent_str = f"Agent Location: (row={json_repr['pregrid_agent_row']},col={json_repr['pregrid_agent_col']})" +\
                        f", Agent Direction: {json_repr['pregrid_agent_dir']} "
    postgrid_agent_str = f"Agent Location: (row={json_repr['postgrid_agent_row']},col={json_repr['postgrid_agent_col']})" + \
                        f", Agent Direction: {json_repr['postgrid_agent_dir']} "


    pregrid_grid_str = "\n".join([" ".join(row) for row in pregrid])
    postgrid_grid_str = "\n".join([" ".join(row) for row in postgrid])

    ascii_repr = "Pregrid\n" + pregrid_grid_str + "\n" + pregrid_agent_str + "\n\n" + "Postgrid\n" + postgrid_grid_str + "\n" + postgrid_agent_str

    return ascii_repr

def code_seq2plan(code_seq):
    return " ".join(code_seq['sequence'])


def courseFormat2codet5(input_path, output_path, code_formatter=None, task_formatter=None):
    if code_formatter == "plain":
        code_format_func = code_seq2plan
    else:
        raise Exception

    if task_formatter == "ascii":
        task_format_func = task_json2ascii
    elif task_formatter == "ascii-style-tokens":
        task_format_func = task_json2asciitokens
    elif task_formatter == "pddl":
        task_format_func = task_json2pddl
    elif task_formatter == 'pddl_technical':
        task_format_func = task_json2pddltech
    elif task_formatter == 'python':
        task_format_func = task_json2python
    else:
        raise Exception

    with open(os.path.join(output_path, f"course_dataset.jsonl"), "w+") as dataset_file:
        for filename in os.listdir(os.path.join(input_path, "task")):
            i = filename.split("_")[0]
            data_point = {}
            with open(os.path.join(input_path, "task", f"{i}_task.json")) as file:
                task_repr = json.load(file)
                data_point['task'] = task_format_func(task_repr)
            with open(os.path.join(input_path, "seq", f"{i}_seq.json")) as file:
                seq_repr = json.load(file)
                data_point['seq'] = code_format_func(seq_repr)
            dataset_file.write(json.dumps(data_point) + "\n")


if __name__ == "__main__":
    dataset_name = os.path.join("datasets", "python")
    for dataset_type in ["train", "val"]:
        input_path = os.path.join("..", "..", "karel_data", dataset_type)
        output_path = os.path.join("..", dataset_name, dataset_type)
        os.makedirs(output_path, exist_ok=False)
        courseFormat2codet5(input_path, output_path, code_formatter="plain", task_formatter="python")


# if __name__ == "__main__":
#     task_id = int(sys.argv[1])
#     with open(os.path.join("..", "..", "karel_data", "train", "task", f"{task_id}_task.json")) as file:
#         json_repr = json.load(file)
#
#     print(task_json2ascii(json_repr))
#
#     with open(os.path.join("..", "..", "karel_data", "train", "seq", f"{task_id}_seq.json")) as file:
#         json_repr = json.load(file)
#     print(code_seq2plan(json_repr))
#
#     # with open(os.path.join("..", "codet5_data", "train.jsonl")) as file:
#     #     for i, line in enumerate(file.readlines()):
#     #         d = json.loads(line)
#     #         if i == 1:
#     #             print(json.dumps(d, indent=4))
#     #     print(i)
