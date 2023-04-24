"""

snitch.py - Functions for handling philosophers at a dining table and
detecting anomalies.

This file contains various functions related to handling philosophers at a 
dining table, including functions for error handling and debugging information.
The functions implemented here are used to process philosopher records, perform
tests, and update the state of philosophers at the dining table. 

Date: 2023-04-19

MIT License

Copyright (c) 2023 Pablo López Bergillos

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import sys


ENDC = "\033[0m"
INPUT = "\033[0m\033[1m"
ERROR = "\033[0m\033[91m\033[1m"
DEBUG = "\033[0m\033[93m\033[1m"


class PhilosopherError(Exception):
    """
    Custom exception class for handling errors related to philosophers.

    Attributes:
        msgs (list): List of error messages.
    """

    def __init__(self, source, msgs, records):
        """
        Initialize the PhilosopherError instance.

        Args:
            msgs (list): List of error messages.
            references (list): List of references related to the error.
        """
        super().__init__()
        self.msgs = []
        self.msgs.extend(msgs)
        records = [ref for ref in records if ref]
        records.sort(key=lambda x: x[0])
        self.msgs.extend([ref[3] + f" ({source[0] - ref[0]} ms ago)" for ref in records])
        self.args = self.msgs


class PhilosopherDebugInfo(PhilosopherError):
    """
    Custom class for handling debug information related to philosophers.

    Inherits from PhilosopherError class.
    """


def read_command_line_arguments(args):
    """
    This function reads command line arguments and parses them to generate a
    configuration dictionary. The configuration may include settings such as
    'debug' mode, 'bonus' mode, number of philosophers, time to die, time to
    eat, time to sleep, and number of times each philosopher must eat.
    The function returns a dictionary with the collected configuration.

    Args:
        args (list): A list of command line arguments.

    Returns:
        dict: A dictionary containing the configuration parsed from the command
        line arguments.

    Raises:
        ValueError: If the arguments are not valid integers or the number of
        arguments is not 4 or 5.
    """
    config = {}
    while len(args) > 0 and args[0].lower() in ["debug", "bonus"]:
        if len(args) > 0 and args[0].lower() == "debug":
            config["debug"] = True
            args = args[1:]
        if len(args) > 0 and args[0].lower() == "bonus":
            config["bonus"] = True
            args = args[1:]
    if "bonus" in config:
        raise NotImplementedError("bonus mode not implemented.")
    try:
        config["number of philosophers"] = int(args[0])
        config["time to die"] = int(args[1])
        config["time to eat"] = int(args[2])
        config["time to sleep"] = int(args[3])
        if len(args) == 5:
            config["number of times each philosopher must eat"] = int(args[4])
    except ValueError as exc:
        raise ValueError("Error: Arguments must be integers.") from exc
    if len(args) not in [4, 5]:
        raise ValueError("Error: 4 or 5 integers must be specified.")
    return config


def read_record(string):
    """
    This function reads a string and extracts information to create a tuple.
    The input should contain at least two integers separated by whitespace.
    The function extracts the first two integers and the remaining part of the
    string, and creates a tuple with four elements: the first integer, second
    integer, remaining part, and the original input string. If the first two
    elements of the input string are not integers, a ValueError is raised.

    Args:
        string (str): The input string to be parsed.

    Returns:
        record: A tuple containing extracted information from the input string.

    Raises:
        ValueError: If the first two elements of the input string are not
            integers.
    """
    parts = string.split()
    try:
        num1 = int(parts[0])
        num2 = int(parts[1])
    except Exception as exc:
        raise ValueError(
            "The first two elements of the string must be integers."
        ) from exc
    remaining_part = " ".join(parts[2:])
    record = (num1, num2, remaining_part, " ".join(parts))
    return record


def update_state(philosophers_dict, config_dict, action_record):
    """
    This function updates the state of a philosopher and the overall
    configuration based on a record of their action. The philosopher's state is
    stored in the 'philosophers_dict' dictionary, and the configuration is
    stored in the 'config_dict' dictionary. The 'action_record' parameter should
    contain information about the philosopher's action, such as whether they are
    thinking, eating, sleeping, taking a fork, or if they have died. The
    function updates the dictionaries with the latest information from the
    action_record, including the last action, last update time, number of forks
    taken, number of times eaten, and last death record.

    Args:
        philosophers_dict (dict): A dictionary storing the state of each
            philosopher.
        config_dict (dict): A dictionary storing the overall configuration.
        action_record (list): A list containing the record of a philosopher's
            action.

    Returns:
        None
    """
    philosopher = philosophers_dict.get(action_record[1], {})
    action = action_record[2]
    if action in [
        "is thinking",
        "is eating",
        "is sleeping",
        "has taken a fork",
        "died",
    ]:
        philosopher["last " + action] = action_record
        philosopher["last action"] = action_record
        config_dict["last record"] = action_record
        config_dict["last update"] = max(
            config_dict.get("last update", 0), action_record[0]
        )
    if action == "has taken a fork":
        philosopher["forks"] = philosopher.get("forks", 0) + 1
    if action == "is sleeping":
        philosopher["forks"] = 0
        philosopher["times eat"] = philosopher.get("times eat", 0) + 1
    if action == "is eating":
        philosopher["forks"] = 0
    if action == "died":
        config_dict["last died"] = action_record
        philosopher["forks"] = 0
    philosophers_dict[action_record[1]] = philosopher


def process_philosopher_record(
    philosophers_dict, config_dict, line, tests, log_file=None
):
    """
    Process a philosopher record by performing tests, logging errors and debug
    information, and updating the state.

    Args:
        philosophers_dict (dict): A dictionary of philosophers.
        config_dict (dict): A configuration dictionary for the table.
        line (str): A line representing a philosopher record.
        log_file (Optional[file]): An optional log file to write the output.
            Defaults to None.

    Returns:
        None

    Notes:
        - This function processes a philosopher record by performing tests on
            the record using the `philosophers_dict`, `config_dict`, and `record`
            information.
        - If any errors or debug information is encountered during the tests,
            they are logged to the `log_file` if provided, otherwise printed to
            the console.
        - The `philosophers_dict` dictionary is updated with the new record
            information using the `update_state` function.
        - Any unexpected input in the `line` will result in an error message
            appended to the `errors` list.
        - If any other exception occurs during the tests, the error message is
            appended to the `errors` list.
    """
    errors = []
    debug = []
    try:
        record = read_record(line)
    except ValueError:
        record = None
        errors.append("Unexpected input")
    if record:
        for test in tests:
            try:
                test(
                    philosophers_dict=philosophers_dict,
                    config_dict=config_dict,
                    action_record=record,
                )
            except PhilosopherDebugInfo as exc:
                if "debug" in config_dict:
                    debug.extend(exc.args)
            except PhilosopherError as exc:
                errors.extend(exc.args)
    print_line_info(line, errors, debug, log_file)
    update_state(philosophers_dict, config_dict, record)


def print_line_info(line, errors, debug, log_file=None):
    """
    This function prints line information with optional error and debug
    messages. The input parameters are the line to be printed, a list of errors,
    a list of debug messages, and an optional log file. If there are errors, the
    line is printed with an error color and the error messages. If there are
    debug messages, the line is printed with a debug color and the debug
    messages. If there are no messages, an empty line is printed. If a log file
    is provided, the error messages are also written to the log file. The
    function uses the 'Colors' class for color formatting.

    Args:
        line (str): The line to be printed.
        errors (list): A list of error messages.
        debug (list): A list of debug messages.
        log_file (file, optional): An optional log file to write the error
            messages to.
    """
    input_color = INPUT
    msgs = []
    if errors:
        msgs.extend([(ERROR, ". " + d) for d in errors])
        input_color = ERROR
    if debug:
        msgs.extend([(DEBUG, ". " + d) for d in debug])
    if not msgs:
        msgs = [("", "")]
    start = " ".join(line.split())
    for msg in msgs:
        print(f"\n{input_color}{start : <36}{msg[0]}{msg[1]}", end="")
        if input_color == ERROR and log_file:
            log_file.write(f"\n{start : <36}{msg[1]}")
        start = ""


def check_time_travel(**kwargs):
    """
    This function checks if a philosopher has traveled through time based on the
    record of an action. The input parameters are a dictionary of philosophers,
    a configuration dictionary, and a record containing information about an
    action performed by a philosopher. The function calculates the time travel
    by comparing the timestamp of the record with the last update timestamp in
    the configuration. If the calculated time travel is greater than 0, a
    PhilosopherError is raised with an error message indicating the
    philosopher's name and the amount of time traveled.

    Args:
        philosophers_dict (dict): A dictionary of philosophers.
        config_dict (dict): A configuration dictionary.
        action_record (tuple): A record containing information about an action
            performed by a philosopher.

    Raises:
        PhilosopherError: If a philosopher has traveled through time.
    """
    config_dict = kwargs["config_dict"]
    action_record = kwargs["action_record"]
    last_update = config_dict.get("last update", 0)
    update = config_dict.get("last record", None)
    travel = last_update - action_record[0]
    philosopher_id = action_record[1]
    if travel > 0:
        raise PhilosopherError(
            action_record,
            [
                "ERROR: TIME TRAVEL",
                f"{philosopher_id} traveled at least {travel} miliseconds backwards in time.",
            ],
            [update],
        )


def check_philosopher_death(**kwargs):
    """
    This function checks if a philosopher has died based on the record of an
    action. The input parameters are a dictionary of philosophers, a
    configuration dictionary, and a record containing information about an
    action performed by a philosopher. The function checks if there is a record
    of a philosopher who has died in the configuration. If so, a
    PhilosopherError is raised with an error message indicating the
    philosopher's name and a request for a minute of silence.

    Args:
        philosophers_dict (dict): A dictionary of philosophers.
        config_dict (dict): A configuration dictionary.
        action_record (tuple): A record containing information about an action
            performed by a philosopher.

    Raises:
        PhilosopherError: If a philosopher has died.
    """
    config_dict = kwargs["config_dict"]
    action_record = kwargs["action_record"]
    dead_record = config_dict.get("last died", (0, 0, 0, ""))
    dead_philosopher_id = dead_record[1]
    if dead_philosopher_id:
        raise PhilosopherError(
            action_record,
            [
                "ERROR: DEAD PHILOSOPHER.",
                f"Let's take a minute of silence for {dead_philosopher_id}.",
            ],
            [dead_record],
        )


def check_strange_smell(**kwargs):
    """
    This function checks for any strange smell among the philosophers based on
    their recent actions and time to die. The input parameters are a dictionary
    of philosophers, a configuration dictionary, and a record containing
    information about an action performed by a philosopher. The function
    calculates the time elapsed since the last philosopher's meal and compares
    it with the time to die specified in the configuration. If the elapsed time
    exceeds 10 milliseconds, a PhilosopherError is raised with an error message
    indicating a strange smell and the expected time of death.

    Args:
        philosophers_dict (dict): A dictionary of philosophers.
        config_dict (dict): A configuration dictionary.
        action_record (tuple): A record containing information about an action
            performed by a philosopher.

    Raises:
        PhilosopherError: If a strange smell is detected among the philosophers.
    """
    philosophers_dict = kwargs["philosophers_dict"]
    config_dict = kwargs["config_dict"]
    action_record = kwargs["action_record"]
    time_to_die = config_dict["time to die"]
    init_smell = action_record[0] - time_to_die
    for philosopher_id in range(1, config_dict["number of philosophers"]):
        if philosopher_id not in philosophers_dict and init_smell > 10:
            raise PhilosopherError(
                action_record,
                [
                    "Has a strange smell",
                    f"{philosopher_id} should have died {init_smell} ms ago.",
                ],
                [],
            )
        if philosopher_id in philosophers_dict:
            last_is_eating = philosophers_dict[philosopher_id].get(
                "last is eating", (0,)
            )
            smell = action_record[0] - last_is_eating[0] - time_to_die
            if smell > 10:
                raise PhilosopherError(
                    action_record,
                    [
                        "ERROR: STRANGE SMELL.",
                        f"{philosopher_id} should have died {smell} ms ago.",
                        f"Time to die: {time_to_die}",
                    ],
                    [
                        philosophers_dict[philosopher_id].get(
                            "last is eating", None
                        )
                    ],
                )
    philosopher_id = action_record[1]
    philosopher = philosophers_dict.get(philosopher_id, {})
    last_is_eating = philosopher.get("last is eating", (0,))
    time_remaining = time_to_die - (action_record[0] - last_is_eating[0])
    raise PhilosopherDebugInfo(
        action_record,
        [f"time to die: {time_remaining} ms"], []
    )


def check_eating_habits(**kwargs):
    """
    This function checks if a philosopher has eaten too little based on their
    recent actions and the configured time to eat. The input parameters are a
    dictionary of philosophers, a configuration dictionary, and a record
    containing information about an action performed by a philosopher. The
    function first checks if the philosopher is sleeping, and if so, it
    calculates the time elapsed since their last eating action. If the elapsed
    time is less than the configured time to eat, a PhilosopherError is raised
    with an error message indicating that the philosopher has eaten too little.

    Args:
        philosophers_dict (dict): A dictionary of philosophers.
        config_dict (dict): A configuration dictionary.
        action_record (tuple): A record containing information about an action
            performed by a philosopher.

    Raises:
        PhilosopherError: If the philosopher has eaten too little.
    """
    philosophers_dict = kwargs["philosophers_dict"]
    config_dict = kwargs["config_dict"]
    action_record = kwargs["action_record"]
    if action_record[2] == "is sleeping":
        time_to_eat = config_dict["time to eat"]
        philosopher_id = action_record[1]
        philosopher = philosophers_dict.get(philosopher_id, {})
        last_time_eat = philosopher.get("last is eating", (0,))
        time_eating = action_record[0] - last_time_eat[0]
        if time_eating < time_to_eat:
            raise PhilosopherError(
                action_record,
                [
                    "ERROR: ATE TOO LITTLE.",
                    f"{action_record[1]} has been eating only {time_eating} ms.",
                    f"Time to eat: {time_to_eat}",
                ],
                [philosopher.get("last is eating", None)],
            )
        times_eat = philosopher.get("times eat", 0)
        raise PhilosopherDebugInfo(
            action_record,
            [f"Has been eating {time_eating} ms.",
             f"{philosopher_id} ate {times_eat} times"],
            [philosopher.get("last is eating", None)],
        )


def check_wakeup_time(**kwargs):
    """
    This function checks if a philosopher woke up early based on their most
    recent thinking action and the configured sleep time. The input parameters
    are a dictionary of philosophers, a configuration dictionary, and a record
    that contains information about an action performed by a philosopher. The
    function first checks if the philosopher is thinking, and if so, calculates
    the elapsed time since their last sleep action. If the elapsed time is less
    than the configured sleep time, a PhilosopherError is raised with an error
    message indicating that the philosopher woke up early.

    Args:
        philosophers_dict (dict): A dictionary of philosophers.
        config_dict (dict): A configuration dictionary.
        action_record (tuple): A record containing information about an action
            performed by a philosopher.

    Raises:
        PhilosopherError: If the philosopher woke up early.
    """
    philosophers_dict = kwargs["philosophers_dict"]
    config_dict = kwargs["config_dict"]
    action_record = kwargs["action_record"]
    if action_record[2] == "is thinking":
        time_to_sleep = config_dict["time to sleep"]
        philosopher = philosophers_dict.get(action_record[1], {})
        last_time_sleep = philosopher.get("last is sleeping", (0,))
        time_sleeping = action_record[0] - last_time_sleep[0]
        if time_sleeping < time_to_sleep:
            raise PhilosopherError(
                action_record,
                [
                    "ERROR: WOKE UP EARLY.",
                    f"{action_record[1]} has been sleeping only {time_sleeping} ms.",
                    f"Time to sleep: {time_to_sleep}",
                ],
                [philosopher.get("last is sleeping", None)],
            )
        raise PhilosopherDebugInfo(
            action_record,
            [f"Has been sleeping {time_sleeping} ms."],
            [philosopher.get("last is sleeping", None)],
        )


def check_fork_duplication(**kwargs):
    """
    This function checks if a philosopher has duplicated a fork , based on the
    recent actions recorded in the `philosophers` dictionary and the
    configuration settings. The input parameters are a dictionary of
    philosophers, a configuration dictionary, and a record that contains
    information about an action performed by a philosopher. The function
    iterates over the neighboring philosophers in both directions (left and
    right) and checks their last action. If the neighboring philosopher is
    sleeping or thinking, it's considered that a fork is available for taking.
    If the neighboring philosopher is eating or already has two forks, it's
    considered that the fork is not available. The function then raises a
    PhilosopherError with an error message indicating that the philosopher has
    a magic fork, if the philosopher has taken a fork while already having one
    or more forks.

    Args:
        philosophers_dict (dict): A dictionary of philosophers.
        config_dict (dict): A configuration dictionary.
        action_record (tuple): A record containing information about an action
            performed by a philosopher.

    Raises:
        PhilosopherError: If the philosopher has taken a fork while already
            having a fork.
    """
    philosophers_dict = kwargs["philosophers_dict"]
    config_dict = kwargs["config_dict"]
    action_record = kwargs["action_record"]
    if action_record[2] == "has taken a fork":
        references = []
        phil = philosophers_dict.get(action_record[1], {})
        free_forks = 0
        for direction in [1, -1]:
            pos = action_record[1]
            available = -1
            while available == -1:
                pos = (pos - 1 + direction) % config_dict[
                    "number of philosophers"
                ] + 1
                phil_pos = philosophers_dict.get(pos, {})
                phil_last_action = phil_pos.get(
                    "last action", (0, 0, "is sleeping", "")
                )
                references.append(phil_pos.get("last action", None))
                if pos == action_record[1]:
                    available = 0
                    free_forks = 1
                elif phil_last_action[2] in ["is sleeping", "is thinking"]:
                    available = 1
                elif (
                    phil_last_action[2] == "is eating"
                    or phil_pos.get("forks", 0) == 2
                ):
                    available = 0
            free_forks += available
        forks = phil.get("forks", 0)
        free_forks -= forks
        if free_forks <= 0:
            raise PhilosopherError(
                action_record,
                [
                    "ERROR: MAGIC FORK.",
                    (
                        f"{action_record[1]} picked up a fork "
                        f"while already having {forks} forks"
                    ),
                ],
                list(set(references)),
            )
        raise PhilosopherDebugInfo(
            action_record,
            [f"{free_forks} forks available"], list(set(references))
        )


def check_valid_transition(**kwargs):
    """
    This function checks if a transition from the last action of a philosopher
    to the current action recorded in the `record` is valid, based on the
    predefined valid transitions in the `valid_transitions` dictionary. The
    input parameters are a dictionary of philosophers, a configuration
    dictionary, and a record that contains information about an action performed
    by a philosopher. The function retrieves the last action of the philosopher
    from the `philosophers_dict` dictionary, and then checks if the current action in
    the `action_record` is a valid transition from the last action, based on the valid
    transitions defined in the `valid_transitions` dictionary. If the transition
    is not valid, the function raises a PhilosopherError with an error message
    indicating that the philosopher is playing another game, and provides the
    expected valid transitions. Otherwise, the function raises a
    PhilosopherDebugInfo with a message indicating the expected valid
    transitions.

    Args:
        philosophers_dict (dict): A dictionary of philosophers.
        config_dict (dict): A configuration dictionary.
        action_record (tuple): A record containing information about an action
            performed by a philosopher.

    Raises:
        PhilosopherError: If the transition from the last action is not valid.
    """
    philosophers_dict = kwargs["philosophers_dict"]
    action_record = kwargs["action_record"]
    philosopher = philosophers_dict.get(action_record[1], {})
    last_action = philosophers_dict.get(action_record[1], {}).get(
        "last action", (0, 0, "is thinking", "")
    )
    valid_transitions = {
        "is sleeping": ["is thinking", "died"],
        "is thinking": ["has taken a fork", "died"],
        "has taken a fork": [
            "has taken a fork"
            if philosopher.get("forks", 0) < 2
            else "is eating",
            "died",
        ],
        "is eating": ["is sleeping", "died"],
    }
    transitions = valid_transitions.get(last_action[2], [])
    t_msg = " or ".join(['"' + t + '"' for t in transitions])
    if action_record[2] not in transitions:
        raise PhilosopherError(
            action_record,
            ["ERROR: INVALID TRANSITION", f"Expected {t_msg}."],
            [philosopher.get("last action", None)],
        )
    raise PhilosopherDebugInfo(action_record,[f"Expected {t_msg}."], [None])


def check_finish_eating(**kwargs):
    """
    Check if the condition for philosophers to finish eating is met.

    Args:
        philosophers_dict (dict): A dictionary containing information about the
            philosophers.
        config_dict (dict): A dictionary containing the configuration of the
            problem.
        action_record (list): A list containing the details of the action.

    Raises:
        PhilosopherError: If all philosophers have eaten the required number of
            times.
        PhilosopherDebugInfo: If there are philosophers left to finish eating.
    """
    philosophers_dict = kwargs["philosophers_dict"]
    config_dict = kwargs["config_dict"]
    action_record = kwargs["action_record"]
    number_of_philosophers = config_dict.get("number of philosophers", 0)
    must_eat = number_of_philosophers
    number_of_times_must_eat = config_dict.get(
        "number of times each philosopher must eat", -1
    )
    for philosopher in philosophers_dict.values():
        times_eat = philosopher.get("times eat", 0)
        if (
            number_of_times_must_eat > 0
            and not times_eat < number_of_times_must_eat
        ):
            must_eat = must_eat - 1
    if must_eat == 0:
        raise PhilosopherError(
            action_record,
            ["ERROR: ALL PHILOSOPHERS ATE."],
            [],
        )
    must_eat = max(must_eat, 0)
    raise PhilosopherDebugInfo(
        action_record,
        [f"There are {must_eat} philosophers left to finish."],
        [],
    )


def check_invitation(**kwargs):
    """
    Checks if a philosopher's number in the action record matches the invited
    range.

    Args:
        philosophers_dict (dict): A dictionary containing information about each
            philosopher.
        config_dict (dict): A dictionary containing configuration settings for
            the dinner.
        action_record (list): A list representing the action record of a
            philosopher.

    Raises:
        PhilosopherError: If the philosopher's number is not within the invited
            range.

    Returns:
        None
    """
    config_dict = kwargs["config_dict"]
    action_record = kwargs["action_record"]
    number_of_philosophers = config_dict.get("number of philosophers", 0)
    philosopher_number = action_record[1]
    if philosopher_number > number_of_philosophers or philosopher_number < 1:
        raise PhilosopherError(
            action_record,
            [
                "ERROR: NOT INVITED",
                f"philosopher number must be between 1 and {number_of_philosophers}",
            ],
            [],
        )


def check_premature_death(**kwargs):
    """
    Check if a philosopher has died prematurely based on the action records.

    Args:
        philosophers_data (dict): A dictionary containing information about the
            philosophers.
        config_data (dict): A dictionary containing the program configuration.
        action_record (tuple): A tuple representing a recorded action.

    Raises:
        PhilosopherError: If the philosopher has died prematurely, a
            PhilosopherError exception is raised with an error message that
            includes the name of the philosopher and the remaining time he had
            ahead of him.
    """
    philosophers_dict = kwargs["philosophers_dict"]
    config_dict = kwargs["config_dict"]
    action_record = kwargs["action_record"]
    if action_record[2] == "died":
        philosopher = philosophers_dict.get(action_record[1], {})
        time_to_die = config_dict["time to die"]
        last_is_eating = philosopher.get("last is eating", (0,))[0]
        time_remaining = time_to_die - (action_record[0] - last_is_eating)
        if time_remaining > 0:
            raise PhilosopherError(
                action_record,
                [
                    "ERROR: DIED PREMATURELY.",
                    (
                        f"{action_record[1]} had his whole "
                        f"{time_remaining} ms ahead of him."
                    ),
                ],
                [philosopher.get("last is eating", None)],
            )


if __name__ == "__main__":
    test_suite = [
        check_time_travel,
        check_philosopher_death,
        check_strange_smell,
        check_eating_habits,
        check_wakeup_time,
        check_fork_duplication,
        check_valid_transition,
        check_finish_eating,
        check_premature_death,
        check_invitation,
    ]

    philosophers = {}
    table_config = read_command_line_arguments(sys.argv[1:])

    with open("./log.snitch", "w", encoding="utf8") as log:
        for newline in sys.stdin:
            process_philosopher_record(
                philosophers, table_config, newline, test_suite, log
            )

    print(ENDC)
