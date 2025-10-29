import pandas as pd
import os
import glob
from pathlib import Path

path = Path("C:/Users/huang/OneDrive/桌面/happylab/Dblp")
os.chdir(path)
print("Current Working Directory:", Path.cwd())
main_dir = "topic-classifier/ml-track"
validation_folder = "topic-classifier/validation/ml"

def revalidate(prev_validate_file: str, next_validate_file: str):
    df1 = pd.read_csv(os.path.join(validation_folder, prev_validate_file))
    uuids = df1["uuid"].tolist()
    samples_df = pd.DataFrame()
    for venue in os.listdir("venue_abstracts"):
        if venue == "icml":
            continue
        venue_path = os.path.join("venue_abstracts", venue)
        abstract_files = glob.glob(os.path.join(venue_path, "*.csv"))
        for abstract_file in abstract_files:
            sample_df = pd.read_csv(abstract_file)
            samples_df = pd.concat([samples_df, 
                                    sample_df.loc[sample_df['uuid'].isin(uuids), 
                                                  ["uuid", "title", "authors", "abstract"]]], ignore_index=True)
    samples_df = samples_df.reset_index(drop=True)
    samples_df.to_csv(os.path.join(validation_folder, next_validate_file), index=False)


def sample_50s(venue_list: list):
    all_positive_samples = []
    all_negative_samples = []
    for venue in venue_list:
            venue_path = os.path.join(main_dir, venue)
            if os.path.isdir(venue_path):
                csv_files = glob.glob(os.path.join(venue_path, "*.csv"))
                print("csv_files: ", csv_files)
                for csv_file in csv_files:
                    print("csv_file: ", csv_file)
                    with open(csv_file, encoding='utf-8', errors='replace') as f:
                        df = pd.read_csv(f)
                    positive_samples = df[df['response'] == 'Yes'].sample(n=3, random_state=31, replace=False) if len(df[df['response'] == 'Yes']) >= 10 else df[df['response']=='Yes']
                    negative_samples = df[df['response'] == 'No'].sample(n=3, random_state=31, replace=False) if len(df[df['response'] == 'No']) >= 10 else df[df['response']=='No']
                    
                    all_positive_samples.append(positive_samples)
                    all_negative_samples.append(negative_samples)
    print("positive samples length: ", len(all_positive_samples))
    print("negative samples length: ", len(all_negative_samples))
    all_positive_df = pd.concat(all_positive_samples, ignore_index=True)
    all_negative_df = pd.concat(all_negative_samples, ignore_index=True)

    # Combine and shuffle
    combined_df = pd.concat([all_positive_df, all_negative_df], ignore_index=True)
    shuffled_df = combined_df.sample(frac=1, random_state=42).reset_index(drop=True)     
    shuffled_df.to_csv("topic-classifier/validation/ml/ml.csv")



if __name__ == "__main__":
    # revalidate(prev_validate_file="result2.csv", next_validate_file="inference3.csv")
    venue_list = ["aaai", "iccvw", "icml", "nips"]
    sample_50s(venue_list=venue_list)