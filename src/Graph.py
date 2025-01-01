import pandas as pd
import matplotlib.pyplot as plt

class BehaviourGraph:
    def __init__(self, csv_file="behavior_log.csv"):
        self.csv_file = csv_file

    def load_data(self):
        """Load the CSV file into a DataFrame."""
        return pd.read_csv(self.csv_file)

    def plot_behavior_counts(self):
        """Plot the count of each behavior."""
        data = self.load_data()
        behavior_counts = data["Behavior"].value_counts()

      

        # Plotting Behavior Counts in a separate window
        plt.figure(figsize=(8, 6))
        behavior_counts.plot(kind="bar", color="skyblue")
        plt.title("Behavior Counts")
        plt.xlabel("Behavior")
        plt.ylabel("Frequency")
        plt.show()

    def plot_behavior_over_time(self):
        """Plot the behavior occurrences over time."""
        data = self.load_data()
        data["Timestamp"] = pd.to_datetime(data["Timestamp"])
        data.set_index("Timestamp", inplace=True)

        # Plotting Behavior Occurrences Over Time in a separate window
        plt.figure(figsize=(10, 6))
        data["Behavior"].groupby(data.index).count().plot(marker='o')
        plt.title("Behavior Occurrences Over Time")
        plt.xlabel("Time")
        plt.ylabel("Occurrences")
        plt.show()

    def show_plots_separately(self):
        """Display the plots in separate windows at the same time."""
        # Plot behavior counts in one window
        self.plot_behavior_counts()

        # Plot behavior occurrences over time in another window
        self.plot_behavior_over_time()

    
