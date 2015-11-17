def dtw(testing, training_array, bandwidth):
    """dynamic time warp"""
    min_cost = float('inf')
    min_index = 0
    # go through all training data
    for i_training, training in enumerate(training_array):
        dtw = [[float('inf')]*len(testing.series)
               for i in range(len(training.series))]
        dtw[0][0] = 0

        # perform dtw
        for i in range(1, len(training.series)):
            for j in range(1, len(testing.series)):
                if (abs(i - j) < bandwidth):  # Sakoe-Chiba band
                    cost = dist(training.series[i], testing.series[j])
                    dtw[i][j] = cost + min(dtw[i-1][j],
                                           dtw[i][j-1],
                                           dtw[i-1][j-1])
        # store minimum cost and label
        if (dtw[-1][-1] < min_cost):
            min_index = i_training
            min_cost = dtw[-1][-1]
            
    return (min_index, min_cost)

class Series(object):
	"""Series and Label"""
	def __init__(self, series, label):
		super(Series, self).__init__()
		self.series = series
		self.label = label

def dist(training, testing):
    """N-dimensional distance function"""
    sum = 0
    for i in range(len(training)):
        sum += (training[i] - testing[i])**2
    return sum

