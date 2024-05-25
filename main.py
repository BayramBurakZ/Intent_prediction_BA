import time
import queue
import threading
#from process import DataProcessor
from prediction_model import PredictionModel
from probability_evaluator import ProbabilityEvaluator
from data_emitter import DataEmitter
import pandas as pd
import numpy as np


class Main:
    def __init__(self):
        path = r'data/goals/goals.csv'
        df = pd.read_csv(path)
        coordinates = []
        for index, row in df.iterrows():
            coordinates.append(np.array([[row['x']], [row['y']], [row['z']]]))

        self.data_queue = queue.Queue()
        #self.processor = DataProcessor()
        self.prediction_model = PredictionModel(coordinates)
        self.probability_evaluator = ProbabilityEvaluator(len(coordinates))
        self.data_generator = DataEmitter(self.data_queue, 0)

    def process_data(self, data):
        #processed_data = self.processor.process(data)
        direction_vectors = self.prediction_model.calculate_predicted_angles(data[0], data[1])
        self.probability_evaluator.evaluate_angles(self.prediction_model.dp_current, direction_vectors)
        print(f"Zeitstempel: {data[1]}, Wert: {data[0]}, Wahrscheinlichkeit: {self.probability_evaluator.probability_goals}")

    def run(self):
        producer_thread = threading.Thread(target=self.data_generator.emit_data)
        producer_thread.start()

        while True:
            try:
                data = self.data_queue.get(timeout=1)  # Timeout von 1 Sekunde
                self.process_data(data)
            except queue.Empty:
                print("Warten auf Daten...")
                time.sleep(1)



if __name__ == "__main__":
    main = Main()
    main.run()

