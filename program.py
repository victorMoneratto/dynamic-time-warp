#! /usr/bin/env python

import dtw
import argparse
from multiprocessing.pool import ThreadPool

default_training_filename = "input/treino.txt"
default_testing_filename = "input/teste.txt"
default_labels_filename = "input/rotulos.txt"

default_training3D_filename = "input/treino3D.txt"
default_testing3D_filename = "input/teste3D.txt"
default_labels3D_filename = "input/rotulos3D.txt"


def main():
    # parse command line arguments
    parser = argparse.ArgumentParser(description="dynamic Time Warp program")
    parser.add_argument('-b', '--bandwidth', dest='bandwidth',
                        metavar='percentage', type=int, default=0.1, help='bandwidth for Sakoe-Chiba')
    parser.add_argument(
        '-3D', '-3d', dest='tridimensional', action="store_true", help='3D DTW')
    parser.add_argument('-t', '--threads', dest='threads',
                        metavar='num_threads', type=int, default=1, help='max number of threads')
    args = parser.parse_args()
    args.threads = max(args.threads, 1)
    args.bandwidth = max(0, min(args.bandwidth, 1)) # clamp bandwidth
    
    num_dimensions = 0
    training_filename = None
    testing_filename = None
    labels_filename = None
    if args.tridimensional:
        num_dimensions = 3
        training_filename = default_training3D_filename
        testing_filename = default_testing3D_filename
        labels_filename = default_labels3D_filename
    else:
        num_dimensions = 1
        training_filename = default_training_filename
        testing_filename = default_testing_filename
        labels_filename = default_labels_filename

    # read label names
    label_names = {}
    with open(labels_filename) as labels_file:
        for line in labels_file:
            line_parts = line.strip().split("\t")
            label_names[line_parts[0]] = line_parts[1]

    # read training data
    training_array = [series for series in gen_series(training_filename, num_dimensions)]

    testing_array = []
    last_testing_label = None
    label_start_index = 0
    results_queue = []
    threads = None
    if args.threads > 1:
    	threads = ThreadPool(args.threads)
    for i, testing in enumerate(gen_series(testing_filename, num_dimensions)):
        if last_testing_label == None:
            last_testing_label = testing.label

        if last_testing_label != testing.label:
            if args.threads == 1:
                WorkerDTW(testing_array[label_start_index:], training_array, args.bandwidth, label_names, results_queue)
            else:
                threads.apply_async(WorkerDTW, args=(testing_array[label_start_index:], training_array, args.bandwidth, label_names, results_queue))
            label_start_index = i

        testing_array.append(testing)
        last_testing_label = testing.label

    if args.threads == 1:
        WorkerDTW(testing_array[label_start_index:], training_array, args.bandwidth, label_names, results_queue)
    else:
        threads.apply_async(WorkerDTW, args=(testing_array[label_start_index:], training_array, args.bandwidth, label_names, results_queue))

    if args.threads > 1:
        threads.close()
        threads.join()

    report_all(results_queue, len(testing_array))


def WorkerDTW(testing_array, training_array, bandwidth, label_names, results_queue):
    gotRight = 0
    for testing in testing_array:
        training_id, _ = dtw.dtw(testing, training_array, bandwidth)
        if testing.label == training_array[training_id].label:
            gotRight += 1
    report_single(label_names[testing_array[0].label], gotRight, len(testing_array))
    results_queue.append(gotRight)


def gen_series(filename, dimension):
    """series generator from file"""
    with open(filename) as training:
        for line in training:
            series, label = (parse_series_line(line, dimension))
            yield dtw.Series(series, label)


def parse_series_line(line, dimension):
    """parser for single line"""
    parts = line.split(" ")
    label = parts[0]
    parts = parts[1:]
    series = [[0.0]*dimension for i in range(len(parts)/dimension)]
    for i in range(0, (len(parts))/dimension, dimension):
        for j in range(dimension):
            series[i][j] = float(parts[i+j])
    return (series, label)


def report_single(label_name, gotRight, total):
    """report results for label"""
    print "%-21s %6.2f%% (%d/%d) correct" % (label_name, 100.0*float(gotRight)/total, gotRight, total)


def report_all(results, total):
    """report total results"""
    sum = 0
    for result in results:
        sum += result
    print "="*45
    print "Total: %6.2f%% (%d/%d) correct" % (100.0*float(sum)/total, sum, total)

if __name__ == '__main__':
    main()
    