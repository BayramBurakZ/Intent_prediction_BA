import os

log_folder = r'../data/test_data/result_logs'
output_file = r'../data/test_data/summary_results.log'

# result categories
result_categories = {
    "Success": {"count": 0, "prob": 0.0, "sample": 0, "distance": 0.0},
    "Pass1": {"count": 0, "prob": 0.0, "sample": 0, "distance": 0.0},
    "Pass2": {"count": 0, "prob": 0.0, "sample": 0.0, "distance": 0.0},
    "Fail": {"count": 0, "prob": 0.0, "sample": 0, "distance": 0.0}
}

# Process each log file
for filename in os.listdir(log_folder):
    if filename.endswith("_results.log"):
        with open(os.path.join(log_folder, filename), 'r') as file:
            for line in file:
                
                # Extracting result type
                for result_type in result_categories.keys():
                    if result_type in line:

                        # Count result type
                        result_categories[result_type]["count"] += 1

                        # Extract the highest probability
                        try:
                            prob_part = line.split("Highest Probability: ")[1]
                            probability = float(prob_part.split()[0])
                            result_categories[result_type]["prob"] += probability
                        except (IndexError, ValueError):
                            pass

                        # Extract sample and distance from [time, sample, distance]
                        try:
                            last_bracket_index = line.rfind("[")
                            component = line[last_bracket_index:].strip()
                            cleaned_component = component.strip("[]")

                            # Remove the brackets and split by "/"
                            t, s, d = cleaned_component.split("/")
                            sample = int(s)
                            distance = float(d)

                            # Update the dictionary if the values are valid
                            if sample != 'None':
                                result_categories[result_type]["sample"] += int(sample)
                            if distance != 'None':
                                result_categories[result_type]["distance"] += float(distance)
                        except (IndexError, ValueError):
                            pass

# Calculate averages and write to the summary log file
with open(output_file, "w") as summary_file:
    for result_type, data in result_categories.items():
        count = data["count"]
        if count > 0:
            avg_prob = data["prob"] / count
            avg_sample = data["sample"] / count
            avg_distance = data["distance"] / count
        else:
            avg_prob = avg_sample = avg_distance = 0

        summary_file.write(f"Result Type: {result_type}\n")
        summary_file.write(f"Count: {count}\n")
        summary_file.write(f"Average Highest Probability: {avg_prob:.2f}\n")
        summary_file.write(f"Average Sample: {avg_sample:.2f}\n")
        summary_file.write(f"Average Distance: {avg_distance:.2f}\n")
        summary_file.write("\n")
