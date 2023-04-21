"""
snitch.py - Functions for handling philosophers at a dining table and
detecting anomalies.

This file contains various functions related to handling philosophers at a 
dining table, including functions for error handling and debugging information.
The functions implemented here are used to process philosopher records, perform
tests, and update the state of philosophers at the dining table. 

Author: plopez-b
Date: 2023-04-19
"""

import sys


class Colors:
    """
    Custom class for defining color codes for console output.

    Attributes:
        ENDC (str): Reset color code.
        INPUT (str): Color code for input messages.
        ERROR (str): Color code for error messages.
        DEBUG (str): Color code for debug messages.
    """

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

    def __init__(self, msgs, references):
        """
        Initialize the PhilosopherError instance.

        Args:
            msgs (list): List of error messages.
            references (list): List of references related to the error.
        """
        super().__init__()
        self.msgs = []
        self.msgs.extend(msgs)
        references = [ref for ref in references if ref]
        references.sort(key=lambda x: x[0])
        self.msgs.extend([ref[3] for ref in references])
        self.args = self.msgs


class PhilosopherDebugInfo(PhilosopherError):
    """
    Custom class for handling debug information related to philosophers.

    Inherits from PhilosopherError class.
    """

    pass


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
    except ValueError:
        raise ValueError("Error: Arguments must be integers.")
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
        tuple: A tuple containing extracted information from the input string.

    Raises:
        ValueError: If the first two elements of the input string are not
            integers.
    """
    parts = string.split()
    try:
        num1 = int(parts[0])
        num2 = int(parts[1])
    except ValueError:
        raise ValueError(
            "The first two elements of the string must be integers."
        )
    remaining_part = " ".join(parts[2:])
    tuple = (num1, num2, remaining_part, " ".join(parts))
    return tuple


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
    philosophers, table_config, line, tests, log_file=None
):
    """
    Process a philosopher record by performing tests, logging errors and debug
    information, and updating the state.

    Args:
        philosophers (dict): A dictionary of philosophers.
        table_config (dict): A configuration dictionary for the table.
        line (str): A line representing a philosopher record.
        log_file (Optional[file]): An optional log file to write the output.
            Defaults to None.

    Returns:
        None

    Notes:
        - This function processes a philosopher record by performing tests on
            the record using the `philosophers`, `table_config`, and `record`
            information.
        - If any errors or debug information is encountered during the tests,
            they are logged to the `log_file` if provided, otherwise printed to
            the console.
        - The `philosophers` dictionary is updated with the new record
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
    except ValueError as e:
        errors.append("Unexpected input")
    if record:
        for test in tests:
            try:
                test(philosophers, table_config, record)
            except PhilosopherDebugInfo as e:
                if "debug" in table_config:
                    debug.extend(e.args)
            except PhilosopherError as e:
                errors.extend(e.args)
            except Exception as e:
                errors.append(Colors.ENDC + str(e))
    print_line_info(line, errors, debug, log_file)
    update_state(philosophers, table_config, record)


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
    input_color = Colors.INPUT
    msgs = []
    if errors:
        msgs.extend([(Colors.ERROR, ". " + d) for d in errors])
        input_color = Colors.ERROR
    if debug:
        msgs.extend([(Colors.DEBUG, ". " + d) for d in debug])
    if not msgs:
        msgs = [("", "")]
    start = " ".join(line.split())
    for m in msgs:
        print("\n%s%-36s%s%s" % (input_color, start, m[0], m[1]), end="")
        if input_color == Colors.ERROR and log_file:
            log_file.write("\n%-36s%s" % (start, m[1]))
        start = ""


def check_time_travel(philosophers, config, record):
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
        philosophers (dict): A dictionary of philosophers.
        config (dict): A configuration dictionary.
        record (tuple): A record containing information about an action
            performed by a philosopher.

    Raises:
        PhilosopherError: If a philosopher has traveled through time.
    """
    last_update = config.get("last update", 0)
    update = config.get("last record", (0, 0, 0, ""))
    travel = last_update - record[0]
    if travel > 0:
        raise PhilosopherError(
            [
                f"{record[1]} has traveled through time",
                f"At least {travel} miliseconds backwards in time.",
            ],
            [update],
        )


def check_philosopher_death(philosophers, config, record):
    """
    This function checks if a philosopher has died based on the record of an
    action. The input parameters are a dictionary of philosophers, a
    configuration dictionary, and a record containing information about an
    action performed by a philosopher. The function checks if there is a record
    of a philosopher who has died in the configuration. If so, a
    PhilosopherError is raised with an error message indicating the
    philosopher's name and a request for a minute of silence.

    Args:
        philosophers (dict): A dictionary of philosophers.
        config (dict): A configuration dictionary.
        record (tuple): A record containing information about an action
            performed by a philosopher.

    Raises:
        PhilosopherError: If a philosopher has died.
    """
    dead = config.get("last died", None)
    if dead:
        raise PhilosopherError(
            [
                f"{record[1]} shhh!",
                f"Let's take a minute of silence for {dead[1]}.",
            ],
            [dead],
        )


def check_strange_smell(philosophers, config, record):
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
        philosophers (dict): A dictionary of philosophers.
        config (dict): A configuration dictionary.
        record (tuple): A record containing information about an action
            performed by a philosopher.

    Raises:
        PhilosopherError: If a strange smell is detected among the philosophers.
    """
    time_to_die = config["time to die"]
    init_smell = record[0] - time_to_die
    for p in range(1, config["number of philosophers"]):
        if p not in philosophers and init_smell > 10:
            raise PhilosopherError(
                [
                    f"Has a strange smell",
                    f"{p} should have died {init_smell} ms ago.",
                ],
                [],
            )
        if p in philosophers:
            last_is_eating = philosophers[p].get("last is eating", (0,))
            smell = record[0] - last_is_eating[0] - time_to_die
            if smell > 10:
                raise PhilosopherError(
                    [
                        f"Has a strange smell",
                        f"{p} should have died {smell} ms ago.",
                        f"Time to die: {time_to_die}",
                    ],
                    [philosophers[p].get("last is eating", None)],
                )


def check_eating_habits(philosophers, config, record):
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
        philosophers (dict): A dictionary of philosophers.
        config (dict): A configuration dictionary.
        record (tuple): A record containing information about an action
            performed by a philosopher.

    Raises:
        PhilosopherError: If the philosopher has eaten too little.
    """
    if record[2] == "is sleeping":
        time_to_eat = config["time to eat"]
        p = philosophers.get(record[1], {})
        last_time_eat = p.get("last is eating", (0,))
        time_eating = record[0] - last_time_eat[0]
        if time_eating < time_to_eat:
            raise PhilosopherError(
                [
                    f"Has eaten too little",
                    f"{record[1]} has been eating only {time_eating} ms.",
                    f"Time to eat: {time_to_eat}",
                ],
                [p.get("last is eating", None)],
            )
        raise PhilosopherDebugInfo(
            [f"Has been eating {time_eating} ms."],
            [p.get("last is eating", None)],
        )


def check_wakeup_time(philosophers, config, record):
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
        philosophers (dict): A dictionary of philosophers.
        config (dict): A configuration dictionary.
        record (tuple): A record containing information about an action 
            performed by a philosopher.

    Raises:
        PhilosopherError: If the philosopher woke up early.
    """
    if record[2] == "is thinking":
        time_to_sleep = config["time to sleep"]
        p = philosophers.get(record[1], {})
        last_time_sleep = p.get("last is sleeping", (0,))
        time_sleeping = record[0] - last_time_sleep[0]
        if time_sleeping < time_to_sleep:
            raise PhilosopherError(
                [
                    f"Woke up early",
                    f"{record[1]} has been sleeping only {time_sleeping} ms.",
                    f"Time to sleep: {time_to_sleep}",
                ],
                [p.get("last is sleeping", None)],
            )
        raise PhilosopherDebugInfo(
            [f"Has been sleeping {time_sleeping} ms."],
            [p.get("last is sleeping", None)],
        )


def check_fork_duplication(philosophers, config, record):
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
        philosophers (dict): A dictionary of philosophers.
        config (dict): A configuration dictionary.
        record (tuple): A record containing information about an action
            performed by a philosopher.

    Raises:
        PhilosopherError: If the philosopher has taken a fork while already
            having a fork.
    """
    if record[2] == "has taken a fork":
        references = []
        phil = philosophers.get(record[1], {})
        free_forks = 0
        for direction in [1, -1]:
            pos = record[1]
            available = -1
            while available == -1:
                pos = (pos - 1 + direction) % config[
                    "number of philosophers"
                ] + 1
                phil_pos = philosophers.get(pos, {})
                phil_last_action = phil_pos.get(
                    "last action", (0, 0, "is sleeping", "")
                )
                references.append(phil_pos.get("last action", None))
                if pos == record[1]:
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
                [
                    f"Has a magic fork",
                    (
                        f"{record[1]} picked up a fork "
                        f"while already having {forks} forks"
                    ),
                ],
                list(set(references)),
            )
        raise PhilosopherDebugInfo(
            [f"{free_forks} forks available"], list(set(references))
        )


def check_valid_transition(philosophers, config, record):
    """
    This function checks if a transition from the last action of a philosopher
    to the current action recorded in the `record` is valid, based on the
    predefined valid transitions in the `valid_transitions` dictionary. The
    input parameters are a dictionary of philosophers, a configuration
    dictionary, and a record that contains information about an action performed
    by a philosopher. The function retrieves the last action of the philosopher
    from the `philosophers` dictionary, and then checks if the current action in
    the `record` is a valid transition from the last action, based on the valid
    transitions defined in the `valid_transitions` dictionary. If the transition
    is not valid, the function raises a PhilosopherError with an error message
    indicating that the philosopher is playing another game, and provides the
    expected valid transitions. Otherwise, the function raises a
    PhilosopherDebugInfo with a message indicating the expected valid
    transitions.

    Args:
        philosophers (dict): A dictionary of philosophers.
        config (dict): A configuration dictionary.
        record (tuple): A record containing information about an action
            performed by a philosopher.

    Raises:
        PhilosopherError: If the transition from the last action is not valid.
    """
    philosopher = philosophers.get(record[1], {})
    last_action = philosophers.get(record[1], {}).get(
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
    if record[2] not in transitions:
        raise PhilosopherError(
            [f"Is playing another game", f"Expected {t_msg}."],
            [philosopher.get("last action", None)],
        )
    raise PhilosopherDebugInfo([f"Expected {t_msg}."], [None])


def check_finish_eating(philosophers_dict, config_dict, action_record):
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
            [f"All philosophers ate."],
            [],
        )
    if must_eat < 0:
        must_eat = 0
    raise PhilosopherDebugInfo(
        [f"there are {must_eat} philosophers left to finish."],
        [],
    )


def check_invitation(philosophers_dict, config_dict, action_record):
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
    number_of_philosophers = config_dict.get("number of philosophers", 0)
    philosopher_number = action_record[1]
    if philosopher_number > number_of_philosophers or philosopher_number < 1:
        raise PhilosopherError(
            [f"{philosopher_number} was not invited to dinner"],
            []
        )


def check_premature_death(philosophers_dict, config_dict, action_record):
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
    if action_record[2] == "died":
        philosopher = philosophers_dict.get(action_record[1], {})
        time_to_die = config_dict["time to die"]
        last_is_eating = philosopher.get("last is eating", (0,))[0]
        time_remaining = time_to_die - (action_record[0] - last_is_eating)
        if time_remaining > 0:
            raise PhilosopherError(
                [
                    f"Died prematurely.",
                    (
                        f"{action_record[1]} had his whole "
                        f"{time_remaining} ms ahead of him"
                    ),
                ],
                [philosopher.get("last is eating", None)],
            )


if __name__ == "__main__":

    philosophers = {}
    table_config = read_command_line_arguments(sys.argv[1:])
    log_file = open("./log.snitch", "w")

    tests = [
        check_time_travel,
        check_philosopher_death,
        check_strange_smell,
        check_eating_habits,
        check_wakeup_time,
        check_fork_duplication,
        check_valid_transition,
        check_finish_eating,
        check_premature_death,
        check_invitation
    ]

    for line in sys.stdin:
        process_philosopher_record(philosophers, table_config, line, tests, log_file)

    print(Colors.ENDC)
