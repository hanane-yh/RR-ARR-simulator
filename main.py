import random
from collections import deque
import matplotlib
from matplotlib import pyplot as plt
from tabulate import tabulate
import copy
matplotlib.use('TkAgg')


class Process:
    def __init__(self, pid, arrival_time, burst_time):
        self.pid = pid
        self.arrival_time = arrival_time
        self.burst_time = burst_time
        self.remaining_time = burst_time
        self.waiting_time = 0
        self.turnaround_time = 0
        self.completion_time = 0


def round_robin(processes: list, quantum: int) -> list:
    """
    Simulates the Round Robin (RR) scheduling algorithm for a list of processes.

    Parameters:

    processes (list): A list of `Process` objects. Each `Process` object must have the following attributes:
        - pid (int): Process ID.
        - arrival_time (int): The arrival time of the process.
        - burst_time (int): The burst time required for the process.
        - remaining_time (int): The remaining time the process needs to execute (initialized to burst_time).
        - waiting_time (int): The total waiting time for the process (initialized to 0).
        - turnaround_time (int): The total turnaround time for the process (initialized to 0).
        - completion_time (int): The time at which the process completes execution (initialized to 0).

    quantum (int): The time slice (quantum) for each process to run in each cycle of execution.

    Returns:
    list: A list of tuples representing the Gantt chart, where each tuple contains:
        - pid (int): Process ID.
        - start_time (int): The start time of the process in the Gantt chart.
        - end_time (int): The end time of the process in the Gantt chart.
    """
    time = 0
    queue = deque()
    sorted_processes = sorted(processes, key=lambda p: p.arrival_time)
    ready_index = 0  # Tracks the next process that can enter the queue
    gantt_chart = []

    # If the first process doesn't arrive at time 0, set time to first arrival
    if sorted_processes[0].arrival_time > time:
        time = sorted_processes[0].arrival_time

    # Add processes that have arrived initially
    while ready_index < len(sorted_processes) and sorted_processes[ready_index].arrival_time <= time:
        queue.append(sorted_processes[ready_index])
        ready_index += 1

    while queue:
        process = queue.popleft()
        start_time = time
        if process.remaining_time > quantum:
            print(
                f'{time}->{time + quantum}: P{process.pid} ran for {quantum} units of time. remaining: {process.remaining_time - quantum}.')
            time += quantum
            process.remaining_time -= quantum
        else:
            print(
                f'{time}->{time + process.remaining_time}: P{process.pid} ran for {process.remaining_time} units. process completed.')
            time += process.remaining_time
            process.remaining_time = 0
            process.completion_time = time
            process.turnaround_time = process.completion_time - process.arrival_time
            process.waiting_time = process.turnaround_time - process.burst_time

        gantt_chart.append((process.pid, start_time, time))

        # Add new processes that have arrived at the current time
        while ready_index < len(sorted_processes) and sorted_processes[ready_index].arrival_time <= time:
            queue.append(sorted_processes[ready_index])
            ready_index += 1

        # If the process still has remaining time, requeue it
        if process.remaining_time > 0:
            queue.append(process)

        # Move time forward to the next process's arrival if the queue is empty but there are still processes left
        if not queue and ready_index < len(sorted_processes):
            time = sorted_processes[ready_index].arrival_time
            while ready_index < len(sorted_processes) and sorted_processes[ready_index].arrival_time <= time:
                queue.append(sorted_processes[ready_index])
                ready_index += 1

    return gantt_chart


def adaptive_round_robin(processes: list, initial_quantum: int) -> list:
    """
    Simulates the Adaptive Round Robin (ARR) scheduling algorithm for a list of processes.

    This algorithm adjusts the time quantum dynamically based on the completion of processes.
    It decreases the quantum if any process completes during a round, and increases it if no
    process completes.

    A round in this function represents a single cycle of execution for all processes in the ready queue.

    Parameters: processes (list): A list of `Process` objects, each with attributes like `pid`, `arrival_time`,
    `burst_time`, `remaining_time`, `waiting_time`, `turnaround_time`, and `completion_time`.

    initial_quantum (int):
    The initial time slice (quantum) for each process.

    Returns:
    list: A list of tuples representing the Gantt chart, where each tuple contains:
          - pid (int): Process ID.
          - start_time (int): The start time of the process in the Gantt chart.
          - end_time (int): The end time of the process in the Gantt chart.
    """
    time = 0
    curr_round = 1
    queue = deque()
    sorted_processes = sorted(processes, key=lambda p: p.arrival_time)
    ready_index = 0
    gantt_chart = []
    quantum = initial_quantum

    # If the first process doesn't arrive at time 0, set time to first arrival
    if sorted_processes[0].arrival_time > time:
        time = sorted_processes[0].arrival_time

    # Add processes that have arrived initially
    while ready_index < len(sorted_processes) and sorted_processes[ready_index].arrival_time <= time:
        queue.append(sorted_processes[ready_index])
        ready_index += 1

    while queue:
        print(f'Round {curr_round}')
        curr_round += 1
        round_processes = list(queue)  # Snapshot of processes in the current round
        unfinished_before = list(p for p in queue)  # Track unfinished processes
        process_completed = False

        for _ in range(len(round_processes)):
            if not queue:
                break

            process = queue.popleft()
            start_time = time

            if process.remaining_time > quantum:
                print(
                    f'{time}->{time + quantum}: P{process.pid} ran for {quantum} units of time. remaining: {process.remaining_time - quantum}.')
                time += quantum
                process.remaining_time -= quantum

            else:
                print(
                    f'{time}->{time + process.remaining_time}: P{process.pid} ran for {process.remaining_time} units. process completed.')
                time += process.remaining_time
                process.remaining_time = 0
                process.completion_time = time
                process.turnaround_time = process.completion_time - process.arrival_time
                process.waiting_time = process.turnaround_time - process.burst_time

            gantt_chart.append((process.pid, start_time, time))

            while ready_index < len(sorted_processes) and sorted_processes[ready_index].arrival_time <= time:
                queue.append(sorted_processes[ready_index])
                ready_index += 1

            if process.remaining_time > 0:
                queue.append(process)

        for process in unfinished_before:
            if process.completion_time > 0:
                quantum = max(1, quantum - 1)
                print(f'quantum decreases to {quantum}.\n')
                process_completed = True
                break

        if not process_completed:
            quantum += 1
            print(f'quantum increases to {quantum}.\n')

        if not queue and ready_index < len(sorted_processes):
            time = sorted_processes[ready_index].arrival_time
            while ready_index < len(sorted_processes) and sorted_processes[ready_index].arrival_time <= time:
                queue.append(sorted_processes[ready_index])
                ready_index += 1

    return gantt_chart


def draw_gantt_charts(gantt_charts: list) -> None:
    """
    Draws and saves Gantt charts for multiple sets of scheduling data.

    Parameters:
    gantt_charts (list): A list of Gantt chart data, where each entry is a list of tuples.
        Each tuple contains:
        - pid (int): Process ID.
        - start (int): Start time of the process in the Gantt chart.
        - end (int): End time of the process in the Gantt chart.

    Returns:
    None: This function saves each chart as a PNG file and does not return any value.
    """

    if not gantt_charts:
        print("Error: No gantt chart data provided!")
        return

    for i, gantt_chart in enumerate(gantt_charts):
        if gantt_chart is None or len(gantt_chart) == 0:
            print(f"Warning: Gantt chart {i + 1} is empty or None. Skipping.")
            continue

        fig, ax = plt.subplots(figsize=(10, len(set(pid for pid, _, _ in gantt_chart)) * 0.8))

        process_positions = {pid: i for i, pid in enumerate(sorted(set(pid for pid, _, _ in gantt_chart)))}

        for pid, start, end in gantt_chart:
            ax.barh(process_positions[pid], end - start, left=start, height=0.5, color=f'C{pid % 10}')
            ax.text((start + end) / 2, process_positions[pid], f'P{pid}', va='center', ha='center',
                    color='white', fontsize=10, fontweight='bold')

        ax.set_xlabel("Time")
        ax.set_yticks(list(process_positions.values()))
        ax.set_yticklabels([f'P{pid}' for pid in process_positions])
        ax.set_title(f'Gantt Chart for Round Robin Scheduling - Chart {i + 1}')
        ax.set_xlim(0, max(end for _, _, end in gantt_chart) + 1)
        ax.grid(axis='x', linestyle='--', alpha=0.5)

        filename = f'gantt_charts/gantt_chart_{i + 1}.png'
        plt.savefig(filename)

        plt.close(fig)


def compare_results(quantums: list, TATs: list, WATs:list) -> None:
    """
     Compares the mean turnaround time (TAT) and mean waiting time (WAT) for different quantum values in
     Round Robin scheduling against the values from Adaptive Round Robin.

     Parameters:
     quantums (list): A list of quantum values used for Round Robin scheduling.
     TATs (list): A list of mean turnaround times, where the first value is for Adaptive Round Robin.
     WATs (list): A list of mean waiting times, where the first value is for Adaptive Round Robin.

     Returns:
     None: This function generates and displays a figure comparing TAT and WAT using bar charts.
     """
    if len(TATs) == 0 or len(WATs) == 0 or len(quantums) == 0:
        print("Error: TATs, WATs, or quantums are empty!")
        return

    # Adaptive Round Robin values (assumed to be at index 0)
    adaptive_TAT = TATs[0]
    adaptive_WAT = WATs[0]

    fig, axs = plt.subplots(1, 2, figsize=(14, 6))

    # Plot the TAT comparison
    axs[0].bar(['ARR Q=4'] + [f'RR Q={q}' for q in quantums], [adaptive_TAT] + TATs[1:], color='lightblue')
    axs[0].set_title('Turnaround Time Comparison')
    axs[0].set_xlabel('Scheduling Method / Quantum')
    axs[0].set_ylabel('Mean Turnaround Time')
    axs[0].set_ylim(0, max(max(TATs), adaptive_TAT) * 1.1)  # Add some padding above max value
    axs[0].axhline(y=adaptive_TAT, color='red', linestyle='--', linewidth=1.5, label=f'Adaptive RR TAT = {adaptive_TAT}')
    axs[0].legend()

    # Plot the WAT comparison
    axs[1].bar(['ARR Q=4'] + [f'RR Q={q}' for q in quantums], [adaptive_WAT] + WATs[1:], color='lightgreen')
    axs[1].set_title('Waiting Time Comparison')
    axs[1].set_xlabel('Scheduling Method / Quantum')
    axs[1].set_ylabel('Mean Waiting Time')
    axs[1].set_ylim(0, max(max(WATs), adaptive_WAT) * 1.1)  # Add some padding above max value
    axs[1].axhline(y=adaptive_WAT, color='red', linestyle='--', linewidth=1.5, label=f'Adaptive RR WAT = {adaptive_WAT}')
    axs[1].legend()

    plt.tight_layout()
    plt.show()


def calculate_metrics(processes: list) -> [int, int]:
    """
    Calculates the mean waiting time and mean turnaround time for a list of processes.

    Parameters:
    processes (list): A list of `Process` objects.

    Returns:
    [int, int]: A list containing the mean waiting time and mean turnaround time.
    """
    mean_wait_time = sum(p.waiting_time for p in processes) / len(processes)
    mean_turnaround_time = sum(p.turnaround_time for p in processes) / len(processes)
    return mean_wait_time, mean_turnaround_time


def display_info(processes: list) -> None:
    """
    Displays a table of process information (PID, arrival time, burst time, completion time, turnaround time, waiting time).

    Parameters:
    processes (list): A list of `Process` objects.
    """

    table_data = [
        (p.pid, p.arrival_time, p.burst_time, p.completion_time, p.turnaround_time, p.waiting_time)
        for p in processes
    ]
    headers = ["PID", "Arrival Time", "Burst Time", "Completion Time", "Turnaround Time", "Waiting Time"]
    print(tabulate(table_data, headers=headers, tablefmt="grid"))


def main():
    # Step 1: Initialize the processes and other variables
    processes = []
    gantt_data = []
    for i in range(5):
        processes.append(Process(i, random.randint(0,100), random.randint(10,30)))
    TATs = []
    WATs = []
    ARR_quantum = 4
    RR_quantums = [2, 3, 4, 5]

    # Step 2: Run adaptive round-robin
    print(f'adaptive round robin, starting quantum= {ARR_quantum}')
    processes_copy = copy.deepcopy(processes)
    data = adaptive_round_robin(processes_copy, ARR_quantum)
    gantt_data.append(data)
    mean_wait, mean_tat = calculate_metrics(processes_copy)
    WATs.append(mean_wait)
    TATs.append(mean_tat)
    display_info(processes_copy)
    print(f'mean turnaround time: {mean_tat}, mean waiting time: {mean_wait}\n')

    # Step 3: Run normal round-robin with different quantums
    for q in RR_quantums:
        print(f'round robin, quantum= {q}')
        processes_copy = copy.deepcopy(processes)
        data = round_robin(processes_copy, q)
        gantt_data.append(data)
        mean_wait, mean_tat = calculate_metrics(processes_copy)
        WATs.append(mean_wait)
        TATs.append(mean_tat)
        display_info(processes_copy)
        print(f'mean turnaround time: {mean_tat}, mean waiting time: {mean_wait}\n')

    # Step 4: Draw Gantt charts and compare results
    draw_gantt_charts(gantt_data)
    compare_results(RR_quantums, TATs, WATs)


if __name__ == "__main__":
    main()
