import pandas as pd
import os
import ace_tools_open as tools
import glob
import argparse
from collections import Counter
import json
import csv


catalog_dir = '..\\venue_list'
abstract_dir = '..\\venue_abstracts'
topic_classifier_dir = '..\\topic-classifier\\results'

# def get_argument_parser():
#     arg_parser = argparse.ArgumentParser()
#     arg_parser.add_argument(
#         '-y', '--year',
#         required=True,
#         dest='year'
#     )
#     return arg_parser

def sample_responses():
    df_list = []
    venues = ["uss", "ieee", "ndss", "ccs"]
    for venue in venues:
        
        for year in range(2020, 2025):
            df_resp = get_input_file(venue, year)
            df_abs = get_abstract_file(venue, year)
            merged_df = pd.merge(df_resp[['uuid', 'response']], df_abs[['uuid', 'authors', 'title', 'abstract']], on='uuid', how='inner')
            merged_df = merged_df.reset_index(drop=True)
            for i in range(merged_df.shape[0]):
                response = merged_df.loc[i, 'response']    
                if response == 'No':
                        merged_df.loc[i, 'label'] = 0
                elif response == 'Yes':
                        merged_df.loc[i, 'label'] = 1
            df_list.append(merged_df)
        df = pd.concat(df_list, ignore_index=True)
        print("shape of concat df: ", df.shape[0])
    positive_samples = df[df['label']==1].sample(n=50, random_state=42)
    negative_samples = df[df['label']==0].sample(n=50, random_state=42)

    sampled_df = pd.concat([positive_samples, negative_samples]).sample(
            frac=1,
            random_state=42
    )
    tools.display_dataframe_to_user(name='Sampled Data', dataframe=sampled_df)
    sampled_df.to_csv('./validation/result2.csv')


def get_input_file(venue: str, year: int):
    input_file = f"./ml-track/{venue}/{year}.csv"
    if not os.path.exists(input_file):
        return pd.DataFrame()
    with open(input_file, encoding='utf-8', errors='replace') as f:
        df_resp = pd.read_csv(f)
    print(df_resp.head())
    return df_resp
     
def get_abstract_file(venue: str, year: int):
    abstract_file = f"../venue_abstracts/{venue}/abstracts{year}.csv"
    df_abs = pd.read_csv(abstract_file)
    print(df_abs.head())
    return df_abs

def get_all_authors(venue: str, year: int):
    df_resp = get_input_file(venue, year)
    if df_resp.empty:
        return dict()
    df_abs = get_abstract_file(venue, year)
    merged_df = pd.merge(df_resp[['uuid', 'response']], df_abs[['uuid', 'authors']], on='uuid', how='inner')
    merged_df = merged_df.reset_index(drop=True)
    print(merged_df.head())
    author_list = []
    for i in range(0, merged_df.shape[0]):
        if merged_df.loc[i, 'response'] == 'Yes':
            author_row = merged_df.loc[i, 'authors']
            authors = author_row.split('; ')
            author_list.extend(authors)
    ct = Counter(author_list)
    print(ct)
    return dict(ct)
        

def count_authors(counter_file: str, data: dict):
    prev_data = {}
    if os.path.exists(counter_file) and os.path.getsize(counter_file) > 0:
        with open(counter_file, 'r') as f:
            prev_data = json.load(f)
            f.close()

    total_author = prev_data.copy()
    for author in data:
        if author in total_author.keys():
            total_author[author] += data[author]
        else:
            total_author[author] = data[author]
    with open(counter_file, 'w') as f:
        json.dump(total_author, f)


def merge_json_to_csv(json_files: list, csv_file: str):
    merged_data = {}

    for json_file, year in json_files:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        if not isinstance(data, dict):
            raise ValueError(f"Expected JSON data to be a dictionary in {json_file}.")

        for author, count in data.items():
            if author not in merged_data:
                merged_data[author] = {}
            merged_data[author][year] = count

    # Ensure all years are represented in every row
    years = sorted({year for _, year in json_files})
    fieldnames = ["author"] + years

    # Convert dictionary to list format for CSV writing
    csv_data = []
    for author, counts in merged_data.items():
        row = {"author": author}
        for year in years:
            row[year] = counts.get(year, 0)  # Default to 0 if year is missing
        csv_data.append(row)

    # Write to CSV
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(csv_data)



if __name__ == "__main__":
    
    # venues = ["ccs", "ndss", "ieee", "uss"]
    venues = ['nips', 'aaai', 'iccvw', 'icml', "iclr"]

    # for venue in venues:
    #     for year in range(2020, 2025):
    #         author_data = get_all_authors(venue=venue, year=year)
    #         count_authors(f'ml_author_count/author_counts_llm_{year}.json', author_data)
    json_file_list = [("ml-track/ml_track_results/author_counts_llm_2020.json", 2020), 
                      ("ml-track/ml_track_results/author_counts_llm_2021.json", 2021), 
                      ("ml-track/ml_track_results/author_counts_llm_2022.json", 2022), 
                      ("ml-track/ml_track_results/author_counts_llm_2023.json", 2023), 
                      ("ml-track/ml_track_results/author_counts_llm_2024.json", 2024)]
    merge_json_to_csv(json_files=json_file_list, csv_file='ml-track/ml_track_results/author_counts_llm.csv')
    # sample_responses()
