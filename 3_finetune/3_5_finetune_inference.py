import os
import json
import pandas as pd
from tqdm import tqdm
from transformers import BartForSequenceClassification, BartTokenizer
import torch
import sys

# Device configuration
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# Model paths
finetune_model_path = './NLP_IEQ/finetune_models/bart-large-mnli-IEQ'

# Load models and tokenizer
nli_model = BartForSequenceClassification.from_pretrained(finetune_model_path, device=device)
tokenizer = BartTokenizer.from_pretrained(finetune_model_path)

# Label set
label_to_int = ['Indoor Air Quality', 'Thermal', 'Acoustic', 'Visual']

def classify_text(df_path):
    # Load CSV
    df = pd.read_csv(df_path)

    # Extract directory for saving JSON output
    output_dir = os.path.dirname(df_path)
    output_path = os.path.join(output_dir, 'classification_results.json')

    # List to store output results
    output_results = []

    for index, each_row in tqdm(df.iterrows(), total=len(df)):
        premise = each_row['post_body']

        prob_list = []
        for each_label in label_to_int:
            hypothesis = f'This text is about {each_label}.'
            # Encode input
            x = tokenizer.encode(premise, hypothesis, return_tensors='pt', truncation=True)
            x = x.to(device)

            # Get model output
            logits = nli_model(x)[0]

            # Consider only entailment and contradiction logits
            entail_contradiction_logits = logits[:, [0, 2]]
            probs = entail_contradiction_logits.softmax(dim=1)
            prob_label_is_true = probs[:, 1].cpu().detach().numpy()[0]
            prob_list.append(prob_label_is_true)

        # Append results in structured format
        result = {
            'premise': premise,
            'probabilities': {label: prob for label, prob in zip(label_to_int, prob_list)}
        }
        output_results.append(result)

    # Save results to JSON
    with open(output_path, 'w') as json_file:
        json.dump(output_results, json_file, indent=4)

    print(f'Results saved to {output_path}')

if __name__ == "__main__":
    # Get the input CSV path from the command line arguments
    if len(sys.argv) != 2:
        print("Usage: python finetune_inference.py <path_to_csv>")
    else:
        df_path = sys.argv[1]
        classify_text(df_path)
