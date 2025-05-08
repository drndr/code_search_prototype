from flask import Flask, request, jsonify, render_template_string, render_template
import requests
from transformers import AutoTokenizer, AutoModel
from search_funcs import hybrid_search, code_comment_search, author_search, dataset_search, project_search
import torch

app = Flask(__name__)

###########################
# Search functionalities
###########################

def get_embedding(query):
    encoded_input = tokenizer(
        query, padding=False, truncation=False, return_tensors="pt"
    )
    encoded_input = {k: v for k, v in encoded_input.items()}
    model_output = model(**encoded_input)
    #print(model_output.shape)
    return model_output

def start_search(query, query_vector, search_type):
    if search_type == "Code/Comment":
        return code_comment_search(query_vector)
    elif search_type == "Author":
        return author_search(query)
    elif search_type == "Title":
        return project_search(query)
    elif search_type == "Datasets":
        return dataset_search(query)
    # Flash message for no filter selected
    else:
        # Return empty results
        return []


###########################
# Web App
###########################

@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        # Hier verarbeitest du die Suchanfrage und holst die Ergebnisse
        query = request.form.get('search_query')
        query_embedding = get_embedding(query)
        selected_filters = request.form.getlist('filters')
        match_filter = {"option1": "Code", "option2": "Author", "option3":"Title", "option4": "Datasets"}
        global html_list 
        html_list = []
        
        # Fill seperate search
        result = start_search(query, query_embedding, selected_filters[0])
        # remove tensors
        if selected_filters[0] == "Code/Comment":
            for i in result:
                k=i["_source"]
                try:
                    del k["code-vector"]
                    del k["comment-vector"]
                except KeyError:
                    print("key not found")
                html_list.append(k)
        else:
            for i in result[0]["hits"]["hits"]:
                k=i["_source"]
                del k["code-vector"]
                del k["comment-vector"]
                html_list.append(k) 
        while len(html_list) < 3:
            html_list.append("")
            
        # Fill hybrid search
        result2 = hybrid_search(query=query, query_vector= query_embedding)
        for i in result2:
            k=i["_source"]
            print(k)
            # remove tensors
            try:
                del k["code-vector"]
                del k["comment-vector"]
            except KeyError:
                print("key not found")
            html_list.append(k)
        while len(html_list) < 6:
            html_list.append("")
        print(html_list[0])
        
        return render_template('index.html', query=query, result1=html_list[0], result2=html_list[1], result3=html_list[2], result4=html_list[3], result5=html_list[4], result6=html_list[5], search_type=selected_filters[0])
    
    # Initiale Anzeige ohne Ergebnisse
    return render_template('index.html')

@app.route('/search_results', methods=['POST', 'GET'])
def results():
    query = request.form['search_query']
    query_embedding = get_embedding(query)
    selected_filters = request.form.getlist('filters')
    match_filter = {"option1": "Code/Comment", "option2": "Author", "option3":"Title", "option4": "Datasets"}
    result = start_search(query, query_embedding, comment_vector, selected_filters[0])
    global html_list 
    html_list = []
    if selected_filters[0] == "Code":
        for i in result:
            k=i["_source"]
            try:
                del k["code-vector"]
                del k["comment-vector"]
            except KeyError:
                print("key not found")
            html_list.append(k)
    else:
        for i in result[0]["hits"]["hits"]:
            k=i["_source"]
            try:
                del k["code-vector"]
                del k["comment-vector"]
            except KeyError:
                print("key not found")
            html_list.append(k) 
    while len(html_list) < 3:
        html_list.append("")
    return render_template("results.html", query = query, result1 = html_list[0], result2 = html_list[1], result3= html_list[2], search_type=selected_filters[0])

@app.route('/json/<int:result_id>')
def serve_json(result_id):
    result = html_list[result_id]
    return jsonify(result)


@app.route('/result_data.json', methods=['GET'])
def results_data():
    query = request.form['search_query']
    print("Query: ", query)
    query_embedding = get_embedding(query)
    result = start_search(query, query_embedding)
    return result

def start_search(query, query_vector, search_type):
    if search_type == "Code/Comment":
        return code_comment_search(query_vector)
    elif search_type == "Author":
        return author_search(query)
    elif search_type == "Title":
        return project_search(query)
    elif search_type == "Datasets":
        return dataset_search(query)
    # Flash message for no filter selected
    else:
        # Return empty results
        return []

if __name__ == '__main__':

    header= {
        "Content-Type": "application/json",
        'Authorization': 'ApiKey YWRxNDNvOEJCN21WS1p3VFcyRmc6akczRGlnc2pUQzZZV0tkTlUyelpUZw=='
    }
    
    endpoint = "https://localhost:9200"
    username = 'elastic'
    password = "tBJlp0NIf-vNuRYgH22C"
    
    # Model Initalization
    model_ckpt = "Salesforce/codet5p-110m-embedding"
    tokenizer = AutoTokenizer.from_pretrained(model_ckpt, trust_remote_code=True)
    model = AutoModel.from_pretrained(model_ckpt, trust_remote_code=True)
    
    try:        
        model.load_state_dict(torch.load('training/fine-tuned_codet5p.pth'))
    except FileNotFoundError:
        print("Error: Fine-tuned model file not found.")
        
    # Run Web App: http://127.0.0.1:5000/
    app.run(host='0.0.0.0', port=5000, debug=True)