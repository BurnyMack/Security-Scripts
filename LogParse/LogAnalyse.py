import pandas as pd
from datetime import datetime

class LogAnalyzer:

    def __init__(self):
        self.central_dataframe = pd.DataFrame()
        self.log_dataframes = {}

    def analyze_apache_logs(self, apache_logs):
        apache_df = pd.DataFrame(apache_logs)
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        source_type = "Apache Logs"
        apache_df['Timestamp'] = timestamp
        apache_df['Source Type'] = source_type
        self.central_dataframe = pd.concat([self.central_dataframe, apache_df])
        self.log_dataframes['Apache'] = apache_df

    def analyze_iis_logs(self, iis_logs):
        iis_df = pd.DataFrame(iis_logs)
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        source_type = "IIS Logs"
        iis_df['Timestamp'] = timestamp
        iis_df['Source Type'] = source_type
        self.central_dataframe = pd.concat([self.central_dataframe, iis_df])
        self.log_dataframes['IIS'] = iis_df

    def analyze_and_aggregate(self):
        if not self.central_dataframe.empty:
            aggregation_result = self.central_dataframe.groupby('Source Type')['Bytes Sent'].mean()
            print("Aggregation Result:")
            print(aggregation_result)

    def save_to_excel(self, output_file):
        writer = pd.ExcelWriter(output_file, engine='xlsxwriter')
        self.central_dataframe.to_excel(writer, sheet_name='Central Data', index=False)
        for log_type, log_df in self.log_dataframes.items():
            log_df.to_excel(writer, sheet_name=log_type, index=False)
        writer.save()