import pandas as pd
from pathlib import Path

if __name__ == '__main__':
    df_gpt = pd.concat(Path('Path/to/GPT/input/CSV'))

    # Define labels and filter the dataset based on class
    label_to_int = ['Indoor Air Quality', 'Thermal', 'Acoustic', 'Visual']

    df_iaq = df_gpt[df_gpt['class'] == 'Indoor Air Quality']
    df_a = df_gpt[df_gpt['class'] == 'Acoustic']
    df_t = df_gpt[df_gpt['class'] == 'Thermal']
    df_v = df_gpt[df_gpt['class'] == 'Visual']

    # Sample 500 records from each class for balancing
    df_iaq = df_iaq.sample(n=500, random_state=42)
    df_a = df_a.sample(n=500, random_state=42)
    df_t = df_t.sample(n=500, random_state=42)
    df_v = df_v.sample(n=500, random_state=42)

    # Combine the sampled data
    df_balanced = pd.concat([df_iaq, df_a, df_t, df_v], axis=0)

    # Shuffle the combined dataset
    shuffled_df = df_balanced.sample(frac=1, random_state=42)

    # Save the shuffled DataFrame to a new CSV file
    shuffled_df.to_csv(Path('Path/to/GPT/output/CSV'),index=False)
