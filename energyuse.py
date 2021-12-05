import energyusage
import os

# user function to be evaluated
def realtime():
	os.system('py realtime20.py')

energyusage.evaluate(realtime, 40, pdf=True, locations = "Virginia")