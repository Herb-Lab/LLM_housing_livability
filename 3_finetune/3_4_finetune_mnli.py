import pandas as pd
import numpy as np
from pathlib import Path
import torch
import random
from datasets import Dataset
from transformers import BartTokenizerFast, BartForSequenceClassification, Trainer, TrainingArguments
import evaluate
import random
from torch.nn import BCEWithLogitsLoss

# Define template and label mappings
template = 'This text is about {}.'
label_to_int = ['Indoor Air Quality', 'Thermal', 'Acoustic', 'Visual']

# Training and testing split configuration
train_portion = 0.8
test_portion = 0.2

# File paths and directories
model_directory = Path('Path/to/output/finetuned/model')
baseline_model_str = 'facebook/bart-large-mnli'
model = BartForSequenceClassification.from_pretrained(baseline_model_str)
tokenizer = BartTokenizerFast.from_pretrained(baseline_model_str)

# Freeze the encoder to prevent updates during fine-tuning
for param in model.model.encoder.parameters():
    param.requires_grad = False

# Define training arguments
training_args = TrainingArguments(
    output_dir=model_directory,          # Output directory for model checkpoints
    num_train_epochs=2,                  # Number of training epochs
    per_device_train_batch_size=10,      # Batch size for training
    per_device_eval_batch_size=10,       # Batch size for evaluation
    warmup_steps=500,                    # Warmup steps for learning rate scheduler
    weight_decay=0.01,                   # Weight decay strength
    save_steps=1000,                     # Save model every 1000 steps
    evaluation_strategy="steps",         # Evaluate during training at specific steps
    logging_strategy="steps",            # Log metrics during training
    prediction_loss_only=True,           # Log only loss for predictions
    load_best_model_at_end=True,         # Load the best model at the end of training
    metric_for_best_model="eval_loss",   # Metric for saving the best model
    logging_steps=100,                   # Log every 100 steps
    eval_steps=100                       # Evaluate every 100 steps
)

def shuffle_df(old_df: pd.DataFrame, cycles: int = 5) -> pd.DataFrame:
    """
    Shuffle the DataFrame multiple times.

    Args:
        old_df (pd.DataFrame): The original DataFrame to shuffle.
        cycles (int): Number of shuffle cycles.

    Returns:
        pd.DataFrame: The shuffled DataFrame.
    """
    for i in range(cycles):
        new_df = old_df.sample(frac=1).reset_index(drop=True)
    return new_df

def create_input_sequence(sample):
    """
    Tokenize the input text and generate labels for fine-tuning.

    Args:
        sample (dict): A dictionary with keys 'text' and 'class'.

    Returns:
        dict: A dictionary with tokenized inputs and labels.
    """
    text = sample["text"]
    label = sample["class"]
    
    # Tokenize the text and label
    encoded_sequence = tokenizer(text , template.format(label), truncation = 'only_first')
    cur_label = []
    
    # Create smoothed label
    random_0 = random.uniform(0, 0.2)
    random_1 = 1 + random.uniform(-0.2,0)
    
    if sample["labels"] == 2:
        cur_label = [random_0, 0, random_1]
    else:
        cur_label = [random_1, 0, random_0]
    encoded_sequence["labels"] = cur_label
    encoded_sequence["input_sentence"] = tokenizer.batch_decode(encoded_sequence.input_ids)

    return encoded_sequence

class CustomTrainer(Trainer):
    """
    Custom Trainer class to compute loss using BCEWithLogitsLoss.
    """
    def compute_loss(self, model, inputs, return_outputs=False, **kwargs):
        labels = inputs.pop("labels")
        outputs = model(**inputs)
        logits = outputs.logits

        # Use BCEWithLogitsLoss
        loss_fn = BCEWithLogitsLoss()
        loss = loss_fn(logits, labels)

        return (loss, outputs) if return_outputs else loss


if __name__ == "__main__":

    # Load and shuffle dataset
    df = pd.read_csv(Path('Path/to/training/data'))
    df = shuffle_df(df)

    # Split dataset into training and testing sets
    train_portion = int(train_portion*len(df))
    test_portion = int(test_portion*len(df))
    
    # Split to train and test portions
    df_train = df.head(train_portion)
    df_test = df.tail(test_portion)
    
    # Convert to Dataset objects
    train_ds = Dataset.from_pandas(df_train, split="train")
    test_ds = Dataset.from_pandas(df_test, split="test")

    # Tokenize and process datasets
    train_dataset = train_ds.map(create_input_sequence, remove_columns = ["class", "text"])
    test_dataset = test_ds.map(create_input_sequence, remove_columns = ["class", "text"])

    # Initialize the trainer
    trainer = CustomTrainer(
        model = model,                     # The model to be trained (BART-large-MNLI)
        args = training_args,              # Training arguments, defined above
        train_dataset = train_dataset,     # Training dataset
        eval_dataset = test_dataset,       # Evaluation dataset
        tokenizer = tokenizer              # The tokenizer that was used
    )

    # Train and evaluate the model
    trainer.train()
    trainer.evaluate()

    # Save the model and tokenizer
    model.save_pretrained(model_directory)
    tokenizer.save_pretrained(model_directory)
