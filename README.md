<div align="center">
<h1> Large language models encode social media for urban housing livability </h1> 
</div>

This repository contains all the essential scripts and documentation to fine-tune a domain-specific large language model (LLM) that analyzes social media content for insights into **urban housing livability**.  
It also includes scripts used for **visualizing extracted topics** from model outputs.

🚀 **Try it out:**

- 🤗 [View the model](https://huggingface.co/Herb-Lab/LLM_housing_livability) on Hugging Face

- 🤗 [Test the model](https://huggingface.co/spaces/Herb-Lab/LLM_housing_livability) with sentiment analysis on the Huggingface Space

## Project Index

### Root

| File | Description |
|------|-------------|
| [requirements.txt](./requirements.txt) | Lists all Python dependencies required to run the project. |
| [pyproject.toml](./pyproject.toml) | Project metadata and build configuration for Python packaging. |
| [README.md](./README.md) | Provides an overview, setup instructions, and usage information for the project.|

### Step 1: booking.com data scraping

| File | Description |
|------|-------------|
| [1_1_scrapper_booking.py](./1_scrap_booking/1_1_scrapper_booking.py) | Scrapes hotel reviews and metadata from Booking.com.  |
| [1_2_merge_result.py](./1_scrap_booking/1_2_merge_result.py) | Merges individual scraped data files into a single dataset. |
| [1_3_get_all_hotel_codes.py](./1_scrap_booking/1_3_get_all_hotel_codes.py) | Extracts unique hotel IDs for use in scraping URLs. |
| [1_4_scrap_and_save_hotel_page.py](./1_scrap_booking/1_4_scrap_and_save_hotel_page.py) | Downloads and saves raw HTML content of hotel pages. |
| [1_5_hotel_price.py](./1_scrap_booking/1_5_hotel_price.py) | Extracts and stores hotel price information from step 1-4 scraped data. |

### Step 2: data pre-processing

| File | Description |
|------|-------------|
| [2_1_label_comments_huggingface.py](./2_filter/2_1_label_comments_huggingface.py) | Uses language classifier to label comments by written language. |
| [2_2_sentence_seperation_nltk.py](./2_filter/2_2_sentence_seperation_nltk.py) | Splits reviews into individual sentences using NLTK. |

### Step 3: BART fine-tuning

| File | Description |
|------|-------------|
| [3_1_gpt_3_vocabulary_generation.py](./3_finetune/3_1_gpt_3_vocabulary_generation.py) | Generates domain-specific semantics using GPT-3. |
| [3_2_combine_gpt_data.py](./3_finetune/3_2_combine_gpt_data.py) | Samples, merges and shuffles GPT-generated semantics for fine-tuning. |
| [3_3_finetune_data_preprocess.py](./3_finetune/3_3_finetune_data_preprocess.py) | Prepares the dataset for BART fine-tuning. |
| [3_4_finetune_mnli.py](./3_finetune/3_4_finetune_mnli.py) | Fine-tunes BART-MNLI model for text classification. |
| [3_5_finetune_inference.py](./3_finetune/3_5_finetune_inference.py) | Example to run classification using the fine-tuned BART model on new review data. |

### Step 3 data

| File | Description |
|------|-------------|
| [Semantics.csv](./3_finetune/data/Semantics.csv) | Domain-specific semantic generated from [Keyword dictionary.docx](./3_finetune/data/Keyword%20dictionary.docx) in step [3_1_gpt_3_vocabulary_generation.py](./3_finetune/3_1_gpt_3_vocabulary_generation.py). |
| [Keyword dictionary.docx](./3_finetune/data/Keyword%20dictionary.docx) | Domain-specific keywords dictionary. |

### Step 4: BERTopic topic modeling

| File | Description |
|------|-------------|
| [4_1_per_sentence_BERTopic.py](./4_BERTopic/4_1_per_sentence_BERTopic.py) | Applies BERTopic to analyze topics at the sentence level. |
| [4_2_BERTopic_visualization.py](./4_BERTopic/4_2_BERTopic_visualization.py) | Visualizations of BERTopic results. |
