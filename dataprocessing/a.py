import pandas as pd

# Đọc file
df = pd.read_csv("dataprocessing\laptop_data_clear1.csv")

# Xoá phần trong ngoặc và khoảng trắng dư
df["name"] = df["name"].str.replace(r"\s*\(.*?\)", "", regex=True).str.strip()

# Ghi đè lại file
df.to_csv("dataprocessing\laptop_data_clear1.csv", index=False)