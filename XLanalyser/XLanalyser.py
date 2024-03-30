import pandas as pd


class XLanalyser:
    def __init__(self, input_file):
        self.input_file = input_file
        self.data = None

    def load_data(self):
        if self.input_file.endswith(".csv"):
            self.data = pd.read_csv(self.input_file)
        elif self.input_file.endswith(".xlsx"):
            self.data = pd.read_excel(self.input_file)
        else:
            raise ValueError(
                "Unsupported file format. Please provide a CSV or XLSX file."
            )

    def read(self):
        if self.data is None:
            raise ValueError("Data has not been loaded. Call load_data() first.")
        summary_stats = self.data.describe()
        null_counts = self.data.isnull().sum()
        return summary_stats, null_counts

    def save(self, output_file):
        if output_file.endswith(".csv"):
            self.basic_analysis()[0].to_csv(output_file)
        elif output_file.endswith(".xlsx"):
            with pd.ExcelWriter(output_file) as writer:
                self.basic_analysis()[0].to_excel(writer, sheet_name="Summary Stats")
                self.basic_analysis()[1].to_excel(writer, sheet_name="Null Counts")
        else:
            raise ValueError("Unsupported output file format. Please use CSV or XLSX.")
