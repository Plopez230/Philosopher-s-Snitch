# Philosopher-s-Snitch
Introducing **"Philosopher's Snitch"** - a cutting-edge software program designed to detect anomalies in the output of the 42's Philosophers project. This groundbreaking tool employs simple algorithms to analyze the behavior of the philosophers and identify any irregularities in their dining patterns. With its intuitive interface and powerful detection capabilities, Philosopher's Snitch is poised to revolutionize the field of distributed computing, providing invaluable insights and early warning signals to ensure smooth and reliable operation of the philosophers' dining process. Say goodbye to unexpected deadlocks and resource contention issues - with Philosopher's Snitch, you can proactively identify and resolve issues before they disrupt the harmony of the philosophers' feast.

## Smooth Operations, 10 Robust Checks
"Philosopher's Snitch" is equipped with a comprehensive set of 10 robust checks to ensure the correct operation of the 42's Philosophers project. These checks include time travel detection, philosopher death monitoring, strange smell detection, eating habits analysis, wakeup time verification, fork duplication prevention, valid transition validation, finish eating verification, and premature death detection. Each of these checks is meticulously designed to detect anomalies and ensure the optimal performance of the philosophers' dining process.

## Installation
Clone this repository
```
git clone https://github.com/Plopez230/Philosopher-s-Snitch.git
```
## Usage
The program receives the same command-line arguments as the original "philo" program, but also has the option to accept two additional optional arguments to activate the "debug" mode, which displays detailed information for each record, or the "bonus" mode, which follows the rules of the "philo_bonus" program. The program takes the sequence of instructions through standard input and displays them on standard output, along with information about any errors detected.
### Example
```
philo 3 500 150 300 | python3 snitch.py 3 500 150 300
```
![image](https://user-images.githubusercontent.com/4245390/233247607-f1475670-4e59-4a59-adba-44f3ed1d9759.png)

### Early Development Notice
As the program is still in an early stage of development, it is susceptible to containing errors. We appreciate it if any issues or bugs are reported through the GitHub repository's issue tracker. Your feedback is valuable in helping us improve the program and make it more robust. Thank you for your assistance in identifying any potential issues as we continue to refine and enhance the software.
