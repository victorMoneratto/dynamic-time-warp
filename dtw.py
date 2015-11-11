training_filename = "input/treino.txt"
testing_filename = "input/teste.txt"

# Parse command line arguments
import argparse
parser = argparse.ArgumentParser(description="dtw parameters")
parser.add_argument('bandwidth', metavar='band', type=int)
args = parser.parse_args()

bandwidth = args.bandwidth

def main():
	# read training data
	training_array = [line for line in gen_series(training_filename)]

	# perform dtw for each test 
	for testing, testing_label in gen_series(testing_filename):
		min_cost = float('inf')
		min_label = ''
		for training, training_label in training_array:
			dtw = [[float('inf')]*len(testing) for i in range(len(training))]
			dtw[0][0] = 0

			# dtw
			for i in range(1, len(training)):
				for j in range(1, len(testing)):
					if (abs(i - j) < bandwidth): # Sakoi-Chiba band
						cost = (training[i] - testing[j])**2
						dtw[i][j] = cost + min(dtw[i-1][j],
											   dtw[i][j-1],
											   dtw[i-1][j-1])
			# store minimum cost 
			if (dtw[-1][-1] < min_cost):
				min_cost = dtw[-1][-1]
				min_label = training_label

		print(min_label == testing_label, min_label, testing_label, min_cost)

# series generator from file
def gen_series(filename):
	with open(filename) as training:
		for line in training:
			yield parse_line(line)

# parser for single line
def parse_line(line):
	parts = line.split(" ")
	label = parts[0]
	series = [float(x) for x in parts[1:]]
	return (series, label)

if __name__ == '__main__':
	main()