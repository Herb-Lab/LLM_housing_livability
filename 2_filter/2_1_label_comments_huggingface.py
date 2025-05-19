from pathlib import Path
import pandas as pd
from tqdm import tqdm
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification, TextClassificationPipeline
tqdm.pandas()

# Define model name and initialize tokenizer and model
model_name = 'qanastek/51-languages-classifier'
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name)
classifier = TextClassificationPipeline(model=model, tokenizer=tokenizer, device=0)

def get_language(str1, str2):
    """
    Determine the language of a combined review text.

    Args:
        str1 (str): Text for 'The reviewer liked'.
        str2 (str): Text for 'The reviewer did not liked'.

    Returns:
        str: Detected language label (e.g., 'en-US').
    """
    
    # Combine the two review text fields and remove newlines
    str_text = str(str1).replace("\n"," ") + str(str2).replace("\n"," ")
    
    # Use the classifier to detect the language
    language_id = classifier(str_text, truncation=True, padding=True, max_length=512)[0]['label']
    
    return language_id

if __name__ == '__main__':
    # Define input and output directories
    results_dir = Path(__file__).parent / 'output' / 'city_result'
    output_dir = results_dir.parent
    merge_results_dir = output_dir / 'merge_result'
    master_merge_file_name = "all_cities_merged.csv"

    # Load the merged dataset of hotel reviews
    all_city_hotel_comments = pd.read_csv(output_dir / master_merge_file_name, sep=',', encoding='utf-8-sig', engine='python')

    # Fill NaN values in the review columns with empty strings
    all_city_hotel_comments['The reviewer liked'] = all_city_hotel_comments['The reviewer liked'].fillna(" ")
    all_city_hotel_comments['The reviewer did not liked'] = all_city_hotel_comments['The reviewer did not liked'].fillna(" ")

    # Detect the language of each review and add it as a new column
    all_city_hotel_comments['language'] = all_city_hotel_comments.progress_apply(lambda x: get_language(x['The reviewer liked'], x['The reviewer did not liked']), axis=1)
    all_city_hotel_comments_filtered = all_city_hotel_comments[all_city_hotel_comments['language']=='en-US']

    # Save the filtered DataFrame to CSV files
    all_city_hotel_comments_filtered.to_csv(output_dir / "all_cities_merged_en.csv", sep=',', index=False, encoding='utf-8-sig')
    all_city_hotel_comments.to_csv(output_dir / "all_cities_merged_labelled.csv", sep=',', index=False, encoding='utf-8-sig')
    all_city_hotel_comments.to_csv(output_dir / "all_cities_merged_label_only.csv", sep=',', index=False, encoding='utf-8-sig', columns=['language'])
