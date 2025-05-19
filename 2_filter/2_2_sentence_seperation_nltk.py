import csv
import pathlib
import nltk
import pandas as pd
from pathlib import Path
nltk.download('punkt_tab')

def paragraph_to_list(paragraph : str):
    """
    Convert a paragraph into a list of sentences using NLTK's sentence tokenizer.

    Args:
        paragraph (str): The paragraph to be tokenized.

    Returns:
        list: A list of sentences extracted from the paragraph.
    """
    return nltk.sent_tokenize(paragraph)

if __name__ == '__main__':

    df = pd.read_csv(Path('Path/to/separate/sentence/CSV'))

    # Apply the paragraph_to_list function to the 'comments' column to generate sentence lists
    df['comment_sentence_list'] = df['comments'].apply(paragraph_to_list)
    df['sentence_count'] = df['comment_sentence_list'].apply(lambda x: len(x))

    # Save the modified DataFrame to a new CSV file
    df.to_csv(Path('Path/to/output/separated/sentence/CSV'), index = None, header=True, quotechar='"', quoting=csv.QUOTE_ALL)
