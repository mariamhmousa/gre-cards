def sm_2(repetition, interval, ef, rating):
	if rating < 3:
		repetition = 0
		interval = 1

	elif repetition == 0:
		repetition = 1
		interval = 1

	elif repetition == 1:
		repetition = 2
		interval = 6
	
	else:
		interval = int(interval * ef)
		repetition += 1
	
	ef = max(1.3, ef + (0.1 - (5 - rating) * (0.08 + (5 - rating) * 0.02)))

	return repetition, interval, ef