"""
Quick test to create a sample Excel file for testing the executable.
"""
import polars as pl
from pathlib import Path

# Create sample data
data = {
    'Name': ['Alice', 'Bob', 'Charlie', 'Diana', 'Eve'],
    'Age': [25, 30, 35, 28, 32],
    'Department': ['Engineering', 'Marketing', 'Sales', 'Engineering', 'Marketing'],
    'Salary': [75000, 65000, 80000, 70000, 72000]
}

# Create DataFrame
df = pl.DataFrame(data)

# Save to Excel
output_path = Path("sample_test.xlsx")
df.write_excel(output_path, worksheet="Employees")

print(f"Sample Excel file created: {output_path.absolute()}")
print(f"Data shape: {df.shape}")
print("\nFirst few rows:")
print(df)