import json
import os

from world import World


def bunelExample_to_ascii(input_json, example_id=0):
    w = World.parseJson(input_json['examples'][example_id]['inpgrid_json'])
    pregrid = w.toTSVString()

    w = World.parseJson(input_json['examples'][example_id]['outgrid_json'])
    postgrid = w.toTSVString()

    ascii_repr = "Pregrid\n" + pregrid + "\n\n" + "Postgrid\n" + postgrid
    return ascii_repr


def bunelTokens_to_plan(input_json):
    plan = " ".join(input_json['program_tokens'][3:-1])
    return plan


def bunelFormat2codet5(input_path, output_path, filter_func, code_formatter=None, task_formatter=None):
    if code_formatter == "plain":
        code_format_func = bunelTokens_to_plan
    else:
        raise Exception

    if task_formatter == "ascii":
        task_format_func = bunelExample_to_ascii
    else:
        raise Exception

    with open(os.path.join(output_path, "train", f"course_dataset.jsonl"), "w+") as train_dataset_file:
        with open(os.path.join(output_path, "val", f"course_dataset.jsonl"), "w+") as val_dataset_file:
            with open(input_path) as file:
                i = 0
                for line in file.readlines():
                    json_repr = json.loads(line)
                    if filter_func(json_repr):
                        i += 1
                        data_point = {}
                        data_point['task'] = task_format_func(json_repr)
                        data_point['seq'] = code_format_func(json_repr)
                        if i % 10 < 2:
                            val_dataset_file.write(json.dumps(data_point) + "\n")
                        else:
                            train_dataset_file.write(json.dumps(data_point) + "\n")


if __name__ == "__main__":
    dataset_name = os.path.join("datasets", "bunel_ascii_all")
    input_path = os.path.join("..", "..", "bunel_data", "train_100000_seed_1.json")
    filter_func = lambda x: True
    output_path = os.path.join("..", dataset_name)
    os.makedirs(output_path, exist_ok=False)
    os.makedirs(os.path.join(output_path, "train"), exist_ok=False)
    os.makedirs(os.path.join(output_path, "val"), exist_ok=False)
    bunelFormat2codet5(input_path, output_path, filter_func=filter_func, code_formatter="plain", task_formatter="ascii")
