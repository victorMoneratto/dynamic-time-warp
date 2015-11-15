import argparse

default_training_filename = "input/treino.txt"
default_testing_filename = "input/teste.txt"
default_labels_filename = "input/rotulos.txt"

default_bandwidth = 3


def main():
	# Parse command line arguments
	parser = argparse.ArgumentParser(description="Dynamic Time Warp program")
	parser.add_argument('-b', '--bandwidth', metavar='band', type=int, help='Sakoi-Chiba bandwidth treshold')

	args = parser.parse_args()
	#set command line arguments
	bandwidth = args.bandwidth or default_bandwidth


	# read label names
	label_names = {}
	with open(default_labels_filename) as labels_file:
		for line in labels_file:
			line_parts = line.strip().split("\t")
			label_names[line_parts[0]] = line_parts[1]

	# read training data
	training_array = [line for line in gen_series(default_training_filename)]


	# for each test 
	stats = {}	# dict of type	label: (tries, correct)
	last_testing_label = None
	for testing, testing_label in gen_series(default_testing_filename):
		# if current label is different than last one, report results for last
		if last_testing_label != None and last_testing_label != testing_label:
			report_single(label_names[last_testing_label], stats[last_testing_label])


		min_cost = float('inf')
		min_label = ''
		# go through all training data
		for training, training_label in training_array:
			dtw = [[float('inf')]*len(testing) for i in range(len(training))]
			dtw[0][0] = 0

			# perform dtw
			for i in range(1, len(training)):
				for j in range(1, len(testing)):
					if (abs(i - j) < bandwidth): # Sakoi-Chiba band
						cost = (training[i] - testing[j])**2
						dtw[i][j] = cost + min(dtw[i-1][j],
											   dtw[i][j-1],
											   dtw[i-1][j-1])
			# store minimum cost and label
			if (dtw[-1][-1] < min_cost):
				min_cost = dtw[-1][-1]
				min_label = training_label

		# increment total and correct counts for label
		stat_value = stats.get(testing_label, (0, 0))
		stats[testing_label] = (stat_value[0]+1, stat_value[1] + (1 if min_label == testing_label else 0))
		#update last label
		last_testing_label = testing_label

	# report all
	report_all(stats.itervalues())

# Report total results
def report_all(stats):
	sum = [0, 0]
	for stat in stats:
		sum[0] += stat[0]
		sum[1] += stat[1]
	print "Total: %.2f%% (%d/%d) correct" % (100.0*float(sum[1])/sum[0], sum[1], sum[0])

# Report results for label
def report_single(label_name, stat):
	print "%s: %.2f%% (%d/%d) correct" % (label_name, 100.0*float(stat[1])/stat[0], stat[1], stat[0])	

# series generator from file
def gen_series(filename):
	with open(filename) as training:
		for line in training:
			yield parse_series_line(line)

# parser for single line
def parse_series_line(line):
	parts = line.split(" ")
	label = parts[0]
	series = [float(x) for x in parts[1:]]
	return (series, label)

if __name__ == '__main__':
	main()