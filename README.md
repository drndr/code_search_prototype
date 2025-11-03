# Local Code Search Prototype

A small local prototype for code search over the extended StatCodeSearch dataset, combining CodeT5+ embeddings with Elasticsearch and Flask.
The prototype consist of two search modes: semantic search via embedding similarity for code and comments and keyword search in additional metadata fields.

The app lets you search across:

- **Code & comments**
- **Authors**
- **Project titles**
- **Datasets**

## Project Structure

```text
code_search_prototype/
├─ datasets/          # Prepared data / indices (adapted for the GESIS search templates 
├─ static/            # CSS, JS, etc. for the web UI
├─ templates/
│  ├─ index.html      # Main search page 
│  └─ results.html    # Results page
├─ training/          # Notebooks / scripts for data prep and fine-tuning CodeT5+
├─ prototype_app.py   # Flask app + model loading + request handling
├─ search_funcs.py    # All search requests to Elasticsearch
├─ .gitignore
└─ README.md
```

## Requirements

- Python: 3.9+

- Elasticsearch with dense vector support

Python packages:

- flask

- requests

- transformers

- torch

- datasets

- pandas

## Setting up the local prototype

- download Elasticsearch (https://www.elastic.co/downloads/elasticsearch)

- run elastic search in installation folder via bin/elasticsearch (default endpoint: http://localhost:9200)

- update the Authorization, username and password fields for elasticsearch in the `prototype_app.py` and `search_funcs.py` files, with your own elasticsearch credentials

- optional: use `train_eval_t5+.ipynb` for finetuning and creating new code/comment embeddings

- run `prototype_app.py` (default address: http://127.0.0.1:5000/)
