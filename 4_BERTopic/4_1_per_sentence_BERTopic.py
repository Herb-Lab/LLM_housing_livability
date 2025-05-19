from pathlib import Path
from tqdm import tqdm
import csv
from pathlib import Path

tqdm.pandas()

from bertopic import BERTopic
from cuml.cluster import HDBSCAN
from cuml.manifold import UMAP
from sklearn.feature_extraction.text import CountVectorizer

list_of_housing_livability_related_sentences = [] # Sentence level list of strings for BERTopic 

# Create instances of GPU-accelerated UMAP and HDBSCAN
umap_model = UMAP(n_components=5, n_neighbors=15, min_dist=0.0)
hdbscan_model = HDBSCAN(min_samples=10, gen_min_span_tree=True, prediction_data=True)

# Pass the above models to be used in BERTopic
topic_model = BERTopic(umap_model=umap_model, hdbscan_model=hdbscan_model, verbose=True, nr_topics="auto")
topics, probs = topic_model.fit_transform(list_of_housing_livability_related_sentences)

# Display topic information
print(topic_model.get_topic_info().head(50))

# Reinitialize UMAP and HDBSCAN for stopword pruning
umap_model = UMAP(n_components=5, n_neighbors=15, min_dist=0.0)
hdbscan_model = HDBSCAN(min_samples=10, gen_min_span_tree=True, prediction_data=True)
# Initialize CountVectorizer for better stop-word management
vectorizer_model = CountVectorizer(stop_words="english")

# Pass the above models to be used in BERTopic
topic_model = BERTopic(umap_model=umap_model, hdbscan_model=hdbscan_model, vectorizer_model=vectorizer_model, verbose=True, nr_topics="auto")
topics, probs = topic_model.fit_transform(list_of_housing_livability_related_sentences)

# Display refined topic information
print(topic_model.get_topic_info().head(50))

# Extract representative documents for each topic
representative_list = []
for _index in range(len(topic_model.get_topic_info())):
    representative_list.extend(topic_model.get_representative_docs()[_index])

# Export document-level topic information to CSV
topic_model.get_document_info(representative_list).to_csv(Path('/Path/to/BERTopic_document_info.csv', index = None, header=True, quotechar='"', quoting=csv.QUOTE_ALL))
topic_model.get_topic_info().to_csv(Path('/Path/to/BERTopic_topic_info.csv', index = None, header=True, quotechar='"', quoting=csv.QUOTE_ALL))
