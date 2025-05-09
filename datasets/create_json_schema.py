"""
Create a JSON Schema for the ElasticSearch object
"""
import pandas as pd
import json
import re

#Creates the currently used json schema based on the structure given by GESIS
def create_json_schema():
    pd.set_option('display.max_colwidth', None)
    df = pd.read_csv("./statcodesearch_latest.csv", header=0, delimiter=",", escapechar= "\\", encoding= "utf-8")
    output_file = "ds_json_schema.jsonl"
    pattern = r"^\d+\s+(.*?)\s+(\d+)$"
    with open(output_file, 'w') as jsonl_file:
        for index, row in df.iterrows():
            match = re.search(pattern, row["Idx"])
            if match:
                filename = match.group(1)
                line_number = match.group(2)
                #print(f"Filename: {filename}")
                #print(f"Line number: {line_number}")
            else:
                print("No match found")
            json_object = { 
                        "Project": row["Title"],
                        "Filename": filename,
                        "Line": line_number,
                        "Code": row["Code"],
                        "Comment": row["Comment"],
                        "Author": row["Author"],
                        "Datasets": row["Datasets"],
                        "Datasets URL String": row["Datasets_url"],
                        "Datasets URL HTML": row["Datasets_html_url"],
                        "Packages": row["Packages"],
                        "Packages URL String": row["Packages_url"],
                        "Packages URL HTML": row["Packages_html_url"],
                        "Output Types": row["Output Types"],
                        "Output Names": row["Output Names"],
                        "Source": row["Source"],
                        "Title": row["Title"],
                        "Domain": row["Domain"],
                        "License": row["License"],
                        "Publication Date": row["Publication date"],
                        "Date Modified": row["Date modified"],
                        "DOI": row["DOI"],
                        "Segmentation Link": row["Segmentation"],
                        "Binder Link": row["Binder Link"]
                    }
            json_line = json.dumps(json_object, ensure_ascii=True)
            jsonl_file.write(json_line + '\n')

#To recreate the newest jsonl schema
create_json_schema()
