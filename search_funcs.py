import requests
from datasets import Dataset
import json
import pandas as pd
from requests.auth import HTTPBasicAuth

header= {
        "Content-Type": "application/json",
        'Authorization': 'ApiKey YWRxNDNvOEJCN21WS1p3VFcyRmc6akczRGlnc2pUQzZZV0tkTlUyelpUZw=='
    }
endpoint = "https://localhost:9200"
username = 'elastic'
password = "tBJlp0NIf-vNuRYgH22C"  

auth = HTTPBasicAuth(username, password)

def hybrid_search(query, query_vector):
    payload = {
    "query": {
        "bool": {
        "must": [
        {
          "multi_match": {
            "query": query,
            "fields": ["person", "database", "title"]
          }
        },
        {
          "script_score": {
            "query": {
              "match_all": {}
            },
            "script": {
              "source": "cosineSimilarity(params.query_vector, 'code-vector') + 1.0",
              "params": {
                "query_vector": query_vector.tolist()[0]
              }
            }
          }
        },
        {
          "script_score": {
            "query": {
              "match_all": {}
            },
            "script": {
              "source": "cosineSimilarity(params.query_vector, 'comment-vector') + 1.0",
              "params": {
                "query_vector": query_vector.tolist()[0]
              }
            }
          }
        }
      ]
    }
    }
    }

    results = requests.post(url=endpoint+"/new-index3/_search", headers=header, json=payload, verify=False, auth=(username, password))
    print("status_code: ")
    results_json = results.json()
    
    # Delete vectors from returned json
    for i in results_json["hits"]["hits"]:
        k=i["_source"]
        del k["code-vector"]
        del k["comment-vector"]
    
    return results_json["hits"]["hits"]
    
#Creating the Search for the query in code vector search
def code_search(query_vector):
    payload = {
                "knn": {
                    "field": "code-vector",
                    "query_vector": query_vector.tolist()[0],
                    "k": 5,
                    "num_candidates": 1070 #Max amount of candidates to look through
                },
                "fields": [ "title"]
                } 
    s = requests.post(url=endpoint+"/new-index3/_search", headers=header, json=payload, verify=False, auth=auth)
    results = []
    score = []
    for i in s.json()['hits']['hits']:
        score.append(i['_score'])
        results.append(i['fields']['title'])
    
    return s.json(), score

#Searching for matches with a 
def author_search(query):
    payload = {
                "query": {
                    "match": {"person": {"query": query,
                              "fuzziness": 2}}
                }
            } 
    s = requests.post(url=endpoint+"/new-index3/_search", headers=header, json=payload, verify=False, auth=auth)
    print(s.status_code)
    #print(s.json())
    results = []
    score = []
    for i in s.json()['hits']['hits']:
        score.append(i['_score'])
        results.append([i['_source']['title']])
    return s.json(), score

#Searching for matches with a max distance of 2 in the projects
def project_search(query):
    payload = {
                "query": {
                    "match": {"title": {"query": query,
                              "fuzziness": 2}}
                }
            } 
    s = requests.post(url=endpoint+"/new-index3/_search", headers=header, json=payload, verify=False, auth=auth)
    print(s.status_code)
    results = []
    score = []
    for i in s.json()['hits']['hits']:
        score.append(i['_score'])
        results.append([i['_source']['title']])
    return s.json(), score

#Searching for matches with distance of 2 in the datasets
def dataset_search(query):
    payload = {
                "query": {
                    "match": {
                        "datasets":{"query": query,
                              "fuzziness": 2}
                    }
                }
            }
    s = requests.post(url=endpoint+"/new-index3/_search", headers=header, json=payload, verify=False, auth=auth)
    print(s.status_code)
    #print(s.json())
    results = []
    score = []
    for i in s.json()['hits']['hits']:
        score.append(i['_score'])
        results.append([i['_source']['title']])
    return s.json(), score

#Create the request for the query in comment
def comment_search(query_vector):
    payload = {     
                "knn": {
                    "field": "comment-vector",
                    "query_vector": query_vector.tolist()[0],
                    "k": 5,
                    "num_candidates": 1070
                },
                "fields": [ "title"]
                } 
    s = requests.post(url=endpoint+"/new-index3/_search", headers=header, json=payload, verify=False, auth=auth)
    results = []
    score= []
    for i in s.json()['hits']['hits']: 
        score.append(i['_score'])
        results.append(i['fields']['title'])
    return s.json(), score

#Combine Code and Comment searches
def code_comment_search(query_vector):
    # Get search results and scores from both code and comment searches
    query_code = code_search(query_vector)
    query_comment = comment_search(query_vector)
    
    code_results = query_code[0]
    comment_results = query_comment[0]
    code_scores = query_code[1]
    comment_scores = query_comment[1]
    
    # Create a list to store combined results with their scores
    combined_results = []
    
    # Process code search results
    for i, result in enumerate(code_results["hits"]["hits"]):
        if i < len(code_scores):  # Make sure we have a score for this result
            combined_results.append({
                "result": result,
                "score": code_scores[i]
            })
    
    # Process comment search results
    for i, result in enumerate(comment_results["hits"]["hits"]):
        if i < len(comment_scores):  # Make sure we have a score for this result
            combined_results.append({
                "result": result,
                "score": comment_scores[i]
            })
    
    # Sort by score in descending order (highest score first)
    sorted_results = sorted(combined_results, key=lambda x: x["score"], reverse=True)
    
    # Take the top 3 results (or fewer if there aren't that many)
    top_results = [item["result"] for item in sorted_results[:3]]
    
    return top_results
