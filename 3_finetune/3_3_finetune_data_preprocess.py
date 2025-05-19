import pandas as pd
from tqdm import tqdm
from pathlib import Path

if __name__ == '__main__':

    df_finetune = pd.read_csv(Path('Path/to/finetune/input/CSV'))

    label_to_int = ['Indoor Air Quality', 'Thermal', 'Acoustic', 'Visual']

    df_finetune['labels'] = 2

    # Create a DataFrame to store additional rows
    df_finetune_2 = pd.DataFrame(columns=['text', 'class', 'labels'])

    # Iterate through each row of the original DataFrame
    for idx in tqdm(range(len(df_finetune))):
        cur_text = df_finetune.iloc[idx]['text']
        true_label = df_finetune.iloc[idx]['class']
        
        # Generate rows with alternative (incorrect) labels
        for cur_label in label_to_int:
            if true_label == cur_label:
                continue
            
            # Add a new row with the current text, alternative label, and 'labels' set to 0
            df_finetune_2.loc[len(df_finetune_2)] = {'text': cur_text, 'class': cur_label, 'labels': 0}

    # Combine the original and new DataFrame and save to CSV
    df_finetune = pd.concat([df_finetune, df_finetune_2], ignore_index=True)
    df_finetune.to_csv(Path('Path/to/finetune/output/CSV'),index=False)
