from bertopic import BERTopic

from pathlib import Path
import pandas as pd
from ast import literal_eval
import plotly.graph_objects as go

# Define paths for saving visualizations
root_path = Path('/Path/to/project/dir') 
pic_path = root_path/'pics'
IDM_path = pic_path/'IDM'
hierarchy_path = pic_path/'hierarchy'

# Ensure the output directories exist
IDM_path.mkdir(parents=True, exist_ok=True)
hierarchy_path.mkdir(parents=True, exist_ok=True)

# Load filtered topics DataFrame
filtered_topics_df = pd.read_csv(Path('/Path/to/BERTopic_topic_info.csv') )

# Get lists of topic IDs and names
list_of_topics_full = filtered_topics_df['Topic'].to_list()
list_of_names_full_4 = [' | '.join(name.split('_')[1:]) for name in filtered_topics_df['Name'].to_list()]
list_of_names_full_3 = [' | '.join(name.split('_')[1:4]) for name in filtered_topics_df['Name'].to_list()]

# Define subsets of top topics for different visualizations
list_of_topics_v1 = list_of_topics_full[:50]
list_of_topics_v2 = list_of_topics_full[:100]

# Load the BERTopic model
topic_model = BERTopic.load(Path('/Path/to/BERTopic_model'))

# Change topic labels with a custom format
topic_labels = topic_model.generate_topic_labels(nr_words=5,
                                            topic_prefix=False,
                                            # word_length=10,
                                            separator=" | ")

topic_labels={}
for idx,row in filtered_topics_df.iterrows():
    topic_name = ''
    topic_keywords = literal_eval(row['Representation'])
    for keyword_idx in range(5):
        if keyword_idx == 0:
            topic_name += topic_keywords[keyword_idx]
        else:
            topic_name += ' | ' + topic_keywords[keyword_idx]
    topic_idx = row['Topic'] + 1
    topic_labels[topic_idx] = topic_name

### Intertopic distance map
# Visualize and save intertopic distance maps for different subsets of topics

top_50_IDM = go.Figure(topic_model.visualize_topics(list_of_topics_v1,custom_labels=True))
top_50_IDM.write_html(IDM_path/'top_50_IDM.html')

top_100_IDM = go.Figure(topic_model.visualize_topics(list_of_topics_v2,custom_labels=True))
top_100_IDM.write_html(IDM_path/'top_100_IDM.html')

### Topic hierarchy
# Visualize and save topic hierarchies for different subsets of topics

top_50_hierarchy = go.Figure(topic_model.visualize_hierarchy(topics=list_of_topics_v1,custom_labels=True))
top_50_hierarchy.write_html(hierarchy_path/'top_50_hierarchy.html')
top_50_hierarchy

top_100_hierarchy = go.Figure(topic_model.visualize_hierarchy(topics=list_of_topics_v2,custom_labels=True))
top_100_hierarchy.write_html(hierarchy_path/'top_100_hierarchy.html')
top_100_hierarchy