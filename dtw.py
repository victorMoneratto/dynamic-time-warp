import argparse

default_training_filename = "input/treino.txt"
default_testing_filename = "input/teste.txt"
default_labels_filename = "input/rotulos.txt"

default_training3D_filename = "input/treino3D.txt"
default_testing3D_filename = "input/teste3D.txt"
default_labels3D_filename = "input/rotulos3D.txt"

default_bandwidth = 5


def main():
	# parse command line arguments
	parser = argparse.ArgumentParser(description="dynamic Time Warp program")
	parser.add_argument('-b', '--bandwidth', dest='bandwidth', metavar='width', type=int, default=default_bandwidth, help='bandwidth for Sakoe-Chiba')
	parser.add_argument('-3D', '-3d', dest='tridimensional', action="store_true", help='3D DTW')
	args = parser.parse_args()
	
	# save command line arguments
	bandwidth = args.bandwidth

	num_dimensions = 0
	training_filename = ""
	testing_filename = ""
	labels_filename = ""
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
	training_array = [line for line in gen_series(training_filename, num_dimensions)]


	# for each test 
	stats = {}	# dict of type	label: (tries, correct)
	last_testing_label = None
	for testing, testing_label in gen_series(testing_filename, num_dimensions):
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
					if (abs(i - j) < bandwidth): # Sakoe-Chiba band
						cost = dist(training[i], testing[j])
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
		# update last label
		last_testing_label = testing_label

	# report all
	report_all(stats.itervalues())

def dist(training, testing):
	sum = 0
	for i in range(len(training)):
		sum += (training[i] - testing[i])**2
	return sum

# report total results
def report_all(stats):
	sum = [0, 0]
	for stat in stats:
		sum[0] += stat[0]
		sum[1] += stat[1]
	print "="*60
	print "Total: %.2f%% (%d/%d) correct" % (100.0*float(sum[1])/sum[0], sum[1], sum[0])

# report results for label
def report_single(label_name, stat):
	print "%s: %.2f%% (%d/%d) correct" % (label_name, 100.0*float(stat[1])/stat[0], stat[1], stat[0])	

# series generator from file
def gen_series(filename, dimension):
	with open(filename) as training:
		for line in training:
			yield parse_series_line(line, dimension)

# parser for single line
def parse_series_line(line, dimension):
	parts = line.split(" ")
	label = parts[0]
	parts = parts[1:]
	series = [[0.0]*dimension for i in range(len(parts)/dimension)]
	for i in range(0, (len(parts))/dimension, dimension):
		for j in range(dimension):
			series[i][j] = float(parts[i+j])
	return (series, label)

if __name__ == '__main__':
	main()