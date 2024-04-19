import csv
import pandas as pd

data = pd.read_csv('Data_Bank.csv')
print(data)
dataset_bank = data.to_numpy()
for i, row in enumerate(dataset_bank):
    stt, account_number_check, _, _, _ = row[0], row[1], row[2], row[3], row[4]
    print(account_number_check)