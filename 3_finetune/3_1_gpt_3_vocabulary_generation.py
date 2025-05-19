import requests
import openai
import pandas as pd
from tqdm import tqdm
import traceback
import ast
from tenacity import retry, stop_after_attempt, wait_random_exponential

# Initialize OpenAI API key and URL request
openai.api_key = f"YOUR_OPENAI_API_KEY"
URL = "https://api.openai.com/v1/chat/completions"
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {openai.api_key}"
}

# Retry mechanism for handling request failures
@retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))
def completion_with_backoff(**kwargs):
    """
    Make a POST request with exponential backoff for retries.

    Args:
        **kwargs: Arguments to pass to the `requests.post` method.

    Returns:
        Response object from the POST request.
    """
    return requests.post(**kwargs)

def process_corpua(cur_text, CUR_LABEL):
    """
    Generate 10 housing accommodation posts using OpenAI API for a given keyword and label.

    Args:
        cur_text (str): Keyword to include in the reviews.
        CUR_LABEL (str): The label describing the review theme (e.g., 'Visual').

    Returns:
        list or int: A list of generated reviews if successful, -1 if an error occurs.
    """
    payload = {
        "model": "gpt-3.5-turbo",
        "temperature": 0.7,
        "messages": [
            {
                "role": "system",
                "content": (
                    f"Generate 10 housing accommodation posts regarding {CUR_LABEL}. "
                    f"Include the following keyword \"{cur_text}\". "
                    f"Do not include the exact word of {CUR_LABEL}. "
                    f"Return in a format that could be easily parsed into a Python list. "
                    f"Do not include any indexes or numbers at the beginning of each review."
                ),
            },
        ]
    }
    
    # Make the API request
    response = requests.post(URL, headers=headers, json=payload)
    response = response.json()
    response = response['choices'][0]['message']['content']
    
    # Attempt to parse the response as a Python list
    try:
        response = ast.literal_eval(response)
        return response
    except Exception:
        # results.append('')
        traceback.print_exc()
        try:
            # Fallback: Split response into lines
            response = response.splitlines()
            return response
        except Exception:
            traceback.print_exc()
            return -1



# Define vocabulary lists (example: for Visual label)
corpua_list_iaq = ['Smell', 'smelling', 'smelly', 'odoriferous', 'crisp', 'fresh', 'scented', 'perfumed', 'pungent', 'malodorous', 'putrid', 'rancid', 'musty', 'damp', 'fungal', 'mildew', 'mildewy', 'mold', 'moldy', 'fusty', 'dusty', 'filthy', 'grimy', 'stink', 'stench', 'reek', 'stale', 'fusty', 'soggy', 'clammy', 'parched', 'tight', 'stuffy', 'suffocating', 'irritative', 'irritation', 'irritating', 'dizzy', 'scratchy', 'allergic', 'allergy', 'hypersensitive', 'allergenic', 'allergen', 'asthma', 'sore', 'itchy', 'itching', 'wheezing', 'rash', 'redness', 'hives', 'dermatitis', 'headache', 'migraine', 'sneezing', 'cough', 'coughed', 'coughing', 'sneezing', 'sneeze', 'nausea', 'nose', 'eyes', 'throat', 'chest', 'skin', 'stuffy', 'odor', 'odour']
corpua_list_acoustic = ['Noise', 'noises', 'noisy', 'loud', 'sound', 'disturbance', 'clamor', 'racket', 'hubbub', 'din', 'commotion', 'cacophony', 'uproar', 'hear', 'heard', 'hearing', 'listen to', 'pick up', 'catch', 'boisterous', 'resounding', 'thunderous', 'piercing', 'earsplitting', 'blaring', 'deafening', 'roaring', 'blaring', 'strident', 'shrill', 'raucous', 'audio', 'acoustic', 'sonic', 'vibration', 'reverberation', 'melody', 'clatter', 'tumultuous', 'pandemonium', 'shattering', 'squeak', 'screech', 'squeal', 'creak', 'whine', 'groan', 'grind', 'screech']
corpua_list_visual = ['Glare', 'glares', 'glared', 'glaring', 'light', 'glimmering', 'glinting', 'searing', 'dim', 'faint', 'low lighting', 'flickers', 'flickering', 'flashes', 'twinkling', 'fluttering', 'dark', 'shadowed', 'shadowy', 'gloomy', 'bright', 'luminous', 'shining', 'brightness', 'illumination', 'luminosity', 'murky', 'bedazzling', 'badly lit', 'poorly lit', 'poorly illuminated', 'insufficient lighting', 'dimly lit', 'inadequately bright']
corpua_list_thermal = ['Cold', 'chilled', 'freezing', 'sweat', 'sweating', 'frigid', 'icy', 'numbing', 'frosty', 'arctic', 'gelid', 'draughty', 'drafty', 'moist', 'clammy', 'sultry', 'sticky', 'chilly', 'cool', 'brisk', 'nippy', 'biting', 'shivery', 'bitterly cold', 'scorching', 'blistering', 'searing', 'roasting', 'sweltering', 'burning hot', 'oppressive heat', 'suffocating', 'sizzling', 'hot temperature', 'warm', 'steaming', 'toasty', 'balmy', 'boiling', 'boiling hot', 'scalding', 'comfortably warm', 'mildly hot', 'cozy', 'pleasantly warm', 'chilled to the bone', 'polar', 'extreme cold', 'fiery', 'blazing', 'seething', 'broiling']

if __name__ == '__main__':
    # Configuration for the current batch processing e.g. visual
    batch_size = 5
    start_idx = 0
    CUR_CORPUA_LIST = corpua_list_visual
    CUR_LABEL = "Visual"
    CUR_LABEL_SHORT = "visual"

    for batch_start in tqdm(range(start_idx, len(CUR_CORPUA_LIST), batch_size)):

        # Initialize an empty list to store results
        results = []
        vocabulary_df = pd.DataFrame(columns=['text'])
        batch_end = min(batch_start + batch_size, len(CUR_CORPUA_LIST))
        batch_corpua = CUR_CORPUA_LIST[batch_start:batch_end]

        # Process each row in the current batch
        for index in tqdm(range(len(batch_corpua))):
            request_result =  process_corpua(batch_corpua[index], CUR_LABEL)
            if request_result != -1:
                results.append(request_result)

        # Add the results to the DataFrame
        vocabulary_df['text'] = results

        # Determine the output CSV file name based on the batch
        output_file = f'NLP_IEQ/nli/validation/gpt_simple_{CUR_LABEL_SHORT}_3.csv'

        # If it's the first batch, create a new CSV file
        if batch_start == 0:
            vocabulary_df.to_csv(output_file, index=False)
        else:
            # If it's a subsequent batch, append to the existing CSV file
            vocabulary_df.to_csv(output_file, mode='a', header=False, index=False)
