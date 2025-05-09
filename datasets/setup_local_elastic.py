import os
from elasticsearch import Elasticsearch
import requests
from datasets import Dataset
import json
import pandas as pd
from requests.auth import HTTPBasicAuth


# Run this one time to create the elasticsearch database and index and change the urls for each request and the API Key in the code above matching with the one from your accounts
header= {
        "Content-Type": "application/json",
        'Authorization': 'ApiKey YWRxNDNvOEJCN21WS1p3VFcyRmc6akczRGlnc2pUQzZZV0tkTlUyelpUZw=='
    }
endpoint = "https://localhost:9200"

username = 'elastic'
password = "tBJlp0NIf-vNuRYgH22C" 

auth = HTTPBasicAuth(username, password)

es = Elasticsearch(
    ['https://localhost:9200'],
    http_auth=(username, password),
    verify_certs=None
)

#Creating the index in elastic
def create_index(index_name):
    payload =   {"settings": {
                    "number_of_shards": 5,
                    'number_of_replicas': 0,
                    "index.mapping.total_fields.limit": 100000,
                    "index.max_ngram_diff": "10",
                    "analysis": {
                        "analyzer": {
                            "trigrams_analyzer": {
                                "tokenizer": "trigrams_tokenizer",
                                "filter": ["lowercase"]
                        },
                            "html_strip_analyzer": {
                                "tokenizer": "standard",
                                "char_filter": ["html_strip"],
                                "filter": ["lowercase"]         
                            }
                        },
                        "tokenizer": {
                            "trigrams_tokenizer": {
                                "type": "ngram",
                                "min_gram": 4,
                                "max_gram": 8,
                                "token_chars":[
                                    "letter",
                                    "digit"
                                ]
                                
                            }
                            }
                        }
                },  
                "mappings": {
                    "_source": {"enabled": True},
                    "dynamic_templates": [
                        {"all_text" : {"match_mapping_type": "string", "mapping": {"copy_to": "_all","type" : "text"}}}],
                    "properties": {
                        "code-vector": {
                            "type": "dense_vector",
                            "dims": 256,
                            "similarity": "l2_norm"
                        },
                        "comment-vector": {
                            "type": "dense_vector",
                            "dims": 256,
                            "similarity": "l2_norm"
                        },
                        "_all": {
                            "type": "text",  
                            "store": True,
                            "analyzer": "html_strip_analyzer",
                            "index_options": "offsets"
                        },
                        "type": {
                            "type": "keyword",  
                        },
                        "title": {
                            "type": "text",
                            "index_options": "offsets",  
                            "fields": {
                                "keyword": {"type": "keyword"},
                                "partial": {'type': 'text', 'analyzer': 'trigrams_analyzer', 'index_options': 'offsets'}
                            },
                        },
                        "abstract": {
                            "type": "text",
                            'index_options':'offsets',
                            'fields': {
                                'partial': {'type': 'text', 'analyzer': 'trigrams_analyzer', 'index_options': 'offsets'}
                            }
                        },
                        "content": {
                            "type": "text",  
                            'index_options': 'offsets',
                            'fields': {
                                'partial': {'type': 'text', 'analyzer': 'trigrams_analyzer', 'index_options': 'offsets'}
                            }
                        },    
                        "topic": {
                            "type": "text",  
                            'index_options':'offsets',
                            'fields': {
                                'keyword': {'type': 'keyword'},
                                'partial': {'type': 'text', 'analyzer': 'trigrams_analyzer', 'index_options': 'offsets'}
                            }
                        },
                        "title_en": {
                            "type": "text",  
                            'copy_to': '_all',
                            'index_options': 'offsets',
                            'fields': {
                                'keyword': {'type': 'keyword'},
                                'partial': {'type': 'text', 'analyzer': 'trigrams_analyzer', 'index_options': 'offsets'}
                            }
                        },
                        "abstract_en": {
                            "type": "text",  
                            'type': 'text',
                            'copy_to': '_all',
                            'index_options': 'offsets',
                            'fields': {
                                'partial':  {'type': 'text', 'analyzer': 'trigrams_analyzer', 'index_options': 'offsets'}
                            }
                        },
                        "topic_en": {
                            "type": "text", 
                            'copy_to': '_all',
                            'index_options': 'offsets',
                            'fields': {
                                'keyword': {'type': 'keyword'},
                                'partial': {'type': 'text', 'analyzer': 'trigrams_analyzer'}
                            } 
                        },
                        "date": {
                            "type": "text",  
                            'fields': {
                                'keyword': {'type': 'keyword'}
                            }
                        },
                        "date_recency": {
                            "type": "date",  
                        },
                        "person": {
                            "type": "text",
                            'fields': {
                                'keyword':  {'type': 'keyword'}
                            },  
                        },
                        "person_sort": {
                            "type": "keyword",  
                        },
                        "study_title": {
                            "type": "text",  
                            'fields': {
                                'keyword': {'type': 'keyword'},
                            }
                        },
                        "study_title_en": {
                            "type": "text",  
                            'fields': {
                                'keyword': {'type': 'keyword'},
                            }
                        },
                        "time_collection": {
                            "type": "text",  
                        },
                        "publisher": {
                            "type": "text", 
                            'fields': {
                                'keyword': {'type': 'keyword'}
                            } 
                        },
                        "database": {
                            "type": "text",
                            'fields': {
                                'keyword': {'type': 'keyword'}
                            } 
                        },
                        "item_categories": {
                            "enabled": False  
                        },
                        "item_categories_en": {
                            "enabled": False,  
                        },
                        "count_items": {
                            "type": "text",
                            'fields': {
                                'keyword': {'type': 'keyword'}
                            }  
                        },
                        "countries_collection": {
                            "type": "text",  
                            'fields': {
                                'keyword': {'type': 'keyword'}
                            }
                        },
                        "countries_colleciton_en": {
                            "type": "text",
                            'fields': {
                                'keyword': {'type': 'keyword'}
                            }  
                        },
                        "data_source": {
                            "type": "text",
                            'fields': {
                                'keyword': {'type': 'keyword'}
                            }  
                        },
                        "index_source": {
                            "type": "text", 
                            'fields': {
                                'keyword': {'type': 'keyword'}
                            } 
                        },
                        "full_text": {
                            "type": "text", 
                            'index_options': 'offsets' 
                        },
                        "source": {
                            "type": "text", 
                            'index_options': 'offsets' 
                        },
                        "study_group": {
                            "type": "text", 
                            'fields': {
                                'keyword': {'type': 'keyword'}
                            } 
                        },
                        "study_group_en": {
                            "type": "text",  
                            'fields': {
                                'keyword': {'type': 'keyword'}
                            } 
                        },
                        "time_collection_years": {
                            "type": "text",  
                            'fields': {
                                'keyword': {'type': 'keyword'}
                            } 
                        },
                        "thematic_collection": {
                            "type": "text",  
                            'fields': {
                                'keyword': {'type': 'keyword'}
                            } 
                        },
                        "thematic_collection_en": {
                            "type": "text",  
                            'fields': {
                                'keyword': {'type': 'keyword'}
                            } 
                        },
                        "methodology_collection_ddi": {
                            "type": "text",  
                            'fields': {
                                'keyword': {'type': 'keyword'}
                            } 
                        },
                        "methodology_collection_ddi": {
                            "type": "text",  
                            'fields': {
                                'keyword': {'type': 'keyword'}
                            } 
                        },
                        "selection_method_ddi": {
                            "type": "text",  
                            'fields': {
                                'keyword': {'type': 'keyword'}
                            }
                        },
                        "selection_method_ddi_en": {
                            "type": "text",  
                            'fields': {
                                'keyword': {'type': 'keyword'}
                            }
                        },
                        "time_method": {
                            "type": "text", 
                            'fields': {
                                'keyword': {'type': 'keyword'}
                            } 
                        },
                        "time_method_en": {
                            "type": "text",  
                            'fields': {
                                'keyword': {'type': 'keyword'}
                            }
                        },
                        "analysis_unit": {
                            "type": "text",  
                            'fields': {
                                'keyword': {'type': 'keyword'}
                            }
                        },
                        "analysis_unit_en": {
                            "type": "text",  
                            'fields': {
                                'keyword': {'type': 'keyword'}
                            }
                        },
                        "kind_data": {
                            "type": "text",  
                            'fields': {
                                'keyword': {'type': 'keyword'}
                            }
                        },
                        "kind_data_en": {
                            "type": "text",  
                            'fields': {
                                'keyword': {'type': 'keyword'}
                            }
                        },
                        "study_lang": {
                            "type": "text",  
                            'fields': {
                                'keyword': {'type': 'keyword'}
                            }
                        },
                        "study_lang_en": {
                            "type": "text",  
                            'fields': {
                                'keyword': {'type': 'keyword'}
                            }
                        },
                        "status_instrument": {
                            "type": "text",  
                            'fields': {
                                'keyword': {'type': 'keyword'}
                            }
                        },
                        "status_instrument_en": {
                            "type": "text",  
                            'fields': {
                                'keyword': {'type': 'keyword'}
                            }
                        },
                        "language_items": {
                            "type": "text",  
                            'fields': {
                                'keyword': {'type': 'keyword'}
                            }
                        },
                        "language_items_en": {
                            "type": "text",  
                            'fields': {
                                'keyword': {'type': 'keyword'}
                            }
                        },
                        "language_documentation": {
                            "type": "text",  
                            'fields': {
                                'keyword': {'type': 'keyword'}
                            }
                        },
                        "language_documentation_en": {
                            "type": "text",  
                            'fields': {
                                'keyword': {'type': 'keyword'}
                            }
                        },
                        "principal": {
                            "type": "text",  
                            'fields': {
                                'keyword': {'type': 'keyword'}
                            }
                        },
                        "principal_en": {
                            "type": "text",  
                            'fields': {
                                'keyword': {'type': 'keyword'}
                            }
                        },
                        "survey_mode": {
                            "type": "text",  
                            'fields': {
                                'keyword': {'type': 'keyword'}
                            }
                        },
                        "survey_mode_en": {
                            "type": "text",  
                            'fields': {
                                'keyword': {'type': 'keyword'}
                            }
                        },
                        "variable_name_sorting": {
                            "type": "text",  
                            'fields': {
                                'keyword': {'type': 'keyword'}
                            }
                        },
                        "variable_label": {
                            "type": "text",  
                            'fields': {
                                'keyword': {'type': 'keyword'}
                            }
                        },
                        "language": {
                            "type": "text",  
                            'fields': {
                                'keyword': {'type': 'keyword'}
                            }
                        },
                        "language_en": {
                            "type": "text", 
                            'fields': {
                                'keyword': {'type': 'keyword'}
                            } 
                        },
                        "multilingual": {
                            "type": "text",  
                            'fields': {
                                'keyword': {'type': 'keyword'}
                            }
                        },
                        "multilingual_en": {
                            "type": "text",  
                            'fields': {
                                'keyword': {'type': 'keyword'}
                            }
                        },
                        "link_count": {
                            "type": "text",  
                            'fields': {
                                'keyword': {'type': 'keyword'}
                            }
                        },
                        "related_references": {
                            'properties': {
                                'id': {'type': 'text'},
                                'view': {'type': 'text', 'index': False}
                            }
                        },
                        "doi": {
                            "type": "text",  
                            'fields': {
                                'keyword': {'type': 'keyword'}
                            }
                        },
                        "id": {
                            "type": "text", 
                            'fields': {
                                'keyword': {'type': 'keyword'}
                            } 
                        },
                        "datasets": {
                            "type": "text",   
                        },
                        "datasets_url_string": {
                            "type": "text",   
                        },
                        "datasets_url_html": {
                            "type": "text",   
                        },
                        "packages": {
                            "type": "text",
                        },
                        "packages_url_string": {
                            "type": "text",
                        },
                        "packages_url_html": {
                            "type": "text",
                        },
                        "output_types": {
                            "type": "text",     
                        },
                        "output_names": {
                            "type": "text",   
                        },
                        "license": {
                            "type": "text",    
                        },
                        "source_file": {
                            "type": "text",    
                        },
                        "code_line": {
                            "type": "text",   
                        },
                        "code": {
                            "type": "text",   
                        },
                        "comment": {
                            "type": "text",   
                        },
                        "segmentation_link": {
                            "type": "text",    
                        },
                        "binder_link": {
                            "type": "text",    
                        }
                        }
                    }   
                }   
    
    s = requests.put(url=endpoint+"/"+str(index_name), headers=header, json=payload, verify=False, auth= (username, password))
    print(s.status_code)
    print(s.json())

def delete_index(index_name):
    s = requests.delete(url=endpoint+"/"+str(index_name), headers=header, auth=auth, verify=False)
    print(s.status_code)
    print(s.json())

#One time call to initally add all the required documents to the index created before
def add_to_index(index_name):
    file = open("./ds_json_schema.jsonl", "r", encoding="utf8")
    jsonObj = pd.read_json(path_or_buf=file, lines=True)
    loaded = Dataset.load_from_disk("./fine-tuned_embs/embeddings_code") #pre-trained_embs
    loaded2 = Dataset.load_from_disk("./fine-tuned_embs/embeddings_comment") #pre-trained_embs
    data2 = []
    for i, embedding in enumerate(loaded):
        
        embedding_code = [loaded[i][str(j)] for j in range(256)]
        embedding_comment = [loaded2[i][str(j)] for j in range(256)]
        # For the dataset field remove paths and file extensions
        datasets = []
        dataset_field = jsonObj["Datasets"][i]

        # Handle the case where dataset_field might be None
        if dataset_field is not None:
            # Check if it's a string representation of a list
            if isinstance(dataset_field, str):
                # Try to parse it if it looks like a list
                if dataset_field.startswith('[') and dataset_field.endswith(']'):
                    try:
                        # Use ast.literal_eval to safely evaluate the string as a list
                        import ast
                        dataset_list = ast.literal_eval(dataset_field)
                        for ds in dataset_list:
                            if isinstance(ds, str) and ds:
                                datasets.append(os.path.splitext(os.path.basename(ds))[0])
                    except (ValueError, SyntaxError):
                        # If parsing fails, just use the string as is
                        datasets.append(os.path.splitext(os.path.basename(dataset_field))[0])
            # If it's already a list
            elif isinstance(dataset_field, list):
                for ds in dataset_field:
                    if isinstance(ds, str) and ds:
                        datasets.append(os.path.splitext(os.path.basename(ds))[0])
        
        #print(datasets)
        
        Project = jsonObj['Project'][i]
        Filename = jsonObj['Filename'][i]
        Line = jsonObj['Line'][i]
        Code = jsonObj['Code'][i]
        Comment = jsonObj['Comment'][i]
        Author = jsonObj['Author'][i]
        Datasets_URL_String = jsonObj["Datasets URL String"][i]
        Datasets_URL_HTML = jsonObj["Datasets URL HTML"][i]
        Packages = jsonObj['Packages'][i]
        Packages_URL_String = jsonObj["Packages URL String"][i]
        Packages_URL_HTML = jsonObj["Packages URL HTML"][i]
        Output_Types = jsonObj['Output Types'][i]
        Output_Names = jsonObj['Output Names'][i]
        Source = jsonObj['Source'][i]
        Domain = jsonObj['Domain'][i]
        License = jsonObj['License'][i]
        Publication_Date = jsonObj['Publication Date'][i]
        DOI = jsonObj['DOI'][i]
        Date_modified = jsonObj['Date Modified'][i]
        Segmentation_Link = jsonObj['Segmentation Link'][i]
        Binder_Link = jsonObj['Binder Link'][i]
        
        request_body = ''
        entry = {
            "index": {"_index": str(index_name), "_id": i}
        }
        data2.append(entry)
        data2.append({
            "_all":[str(Project), str(Author)],
            "code-vector": embedding_code,
            "comment-vector": embedding_comment,
            "type": "research_code",
            "title": str(Project),
            "abstract": "",
            "content": "",
            "topic": str(Domain),
            "title_en": "",
            "abstract_en": "",
            "topic_en": "",
            "date": str(Publication_Date),
            "date_recency": Date_modified,
            "person": str(Author),
            "person_sort": "",
            "study_title_en": "",
            "time_collection": "",
            "publisher": "",
            "database": "",
            "item_categories": "",
            "item_categories_en": "",
            "count_items": "",
            "countries_collection": "",
            "countries_colleciton_en": "",
            "data_source": "CodeInspector",
            "index_source": "CodeInspector",
            "full_text": "",
            "source": str(Source),
            "study_group": "",
            "study_group_en": "",
            "time_collection_years": "",
            "thematic_collection": "",
            "thematic_collection_en": "",
            "methodology_collection_ddi": "",
            "selection_method_ddi": "",
            "selection_method_ddi_en": "",
            "time_method": "",
            "time_method_en": "",
            "analysis_unit": "",
            "analysis_unit_en": "",
            "kind_data": "",
            "kind_data_en": "",
            "study_lang": "",
            "study_lang_en": "",
            "status_instrument": "",
            "status_instrument_en": "",
            "language_items": "",
            "language_items_en": "",
            "language_documentation": "",
            "language_documentation_en": "",
            "principal": "",
            "principal_en": "",
            "survey_mode": "",
            "survey_mode_en": "",
            "variable_name_sorting": "",
            "variable_label": "",
            "language": "",
            "language_en": "",
            "multilingual": "",
            "multilingual_en": "",
            "link_count": "",
            "doi": str(DOI),
            "id": "",
            "datasets": str(datasets),
            "datasets_url_string": str(Datasets_URL_String),
            "datasets_url_html": str(Datasets_URL_HTML),
            "packages": str(Packages),
            "packages_url_string": str(Packages_URL_String),
            "packages_url_html": str(Packages_URL_HTML),
            "output_types": str(Output_Types),
            "output_names": str(Output_Names),
            "license": str(License),
            "source_file": str(Filename),
            "code_line": str(Line),
            "code": str(Code),
            "comment": str(Comment),
            "segmentation_link": str(Segmentation_Link),
            "binder_link": str(Binder_Link)
        })
    for item in data2:
        request_body += json.dumps(item) + '\n'
        #print(item)
    s = requests.post(url=endpoint+"/"+str(index_name)+"/_bulk?pretty", headers=header, data=request_body, verify=False, auth=(username, password))
    print(s.status_code)

def check_if_index_exists(index_name):
    if not es.indices.exists(index=index_name):
        es.indices.create(index=index_name)
        print(f"Index '{index_name}' created successfully.")
    else:
        print(f"Index '{index_name}' already exists.")

delete_index("new-index3")
create_index("new-index3")
add_to_index("new-index3")
print("Elastic DB created")