#!/usr/bin/env python3

import matplotlib.pyplot as plt

log_file_paths = \
    [
        '../output/small_log.txt',
        '../output/med_small_log.txt',
        '../output/med_large_log.txt',
        '../output/large_log.txt'
    ]

NUM_EVALS_PERFORMED = 2000

for file_index in range(len(log_file_paths)):
    with open(log_file_paths[file_index], 'r') as log_file:
        # Create a list of lines from the log file, disregarding all config parameters and empty lines
        log_file = log_file.read().split('\n')
        log_file = [line for line in log_file[log_file.index('Run 1'):] if not line == '']

        # Get the index of each run header
        run_header_indices = []
        for index, line in enumerate(log_file):
            if 'Run' in line:
                run_header_indices.append(index)

        # Determine the last best score
        last_best_score_run_index = 0
        best_score = 0
        for i, run_header_index in enumerate(run_header_indices[1:] + [len(log_file)]):
            last_line_index = run_header_index - 1

            last_score = int(log_file[last_line_index].split('\t')[1])

            if last_score > best_score:
                best_score = last_score
                last_best_score_run_index = i

        # Get data for the run containing the last best score
        log_file = log_file[run_header_indices[last_best_score_run_index]:run_header_indices[last_best_score_run_index + 1]]

        # Get evals and fitnesses for the best run
        evals = []
        fits = []

        for line in log_file[1:]:
            eval_num, fitness = line.split('\t')
            evals.append(int(eval_num))
            fits.append(int(fitness))

        # Adjust evals and fitnesses to be the correct length
        evals += [NUM_EVALS_PERFORMED]
        fits += [fits[-1]]

        # Plot the results
        plt.step(evals, fits, '-b')

        # Include necessary labels
        plt.xlabel('Evaluations')
        plt.ylabel('Fitness')

        # Save and close the plot
        plt.savefig(log_file_paths[file_index][:log_file_paths[file_index].find('log')] + 'graph.png')
        plt.close()

