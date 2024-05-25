class DataProcessor:
    def process(self, data):

        time, coordinates, action = data
        processed_data = (timestamp, value.lower())  # Beispielverarbeitung
        return processed_data