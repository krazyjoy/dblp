import pandas as pd
from collections import Counter, defaultdict
import yaml




def read_codes(file: str)->list:
    df = pd.read_csv(file)

    code_cols = df[['Code 1', 'Code 2', 'Code 3', 'Code 4']]
    # print(code_cols.values.tolist())
    code_list = code_cols.values.tolist()
    print(len(code_list))
    # print(code_list)
    return code_list

def count_codes(all_tags: None, code_book="codes.yaml" ):
    with open(code_book, "r") as f:
        yml = yaml.safe_load(f)

    
    map_counter = {}
    for title, subtitles in yml.items():
        counter = {}
        for subtitle in subtitles:
            counter[subtitle] = all_tags[subtitle]
        map_counter[title] = counter

    return map_counter

def split_codes(code_list: list)->Counter:
    all_tags = Counter()
    total_cells = 0
    for lecture_codes in code_list:
    
        for code in lecture_codes:
            # drop na
            if isinstance(code, str):
                parts = code.split('->')
                total_cells += 1
                for part in parts:
                    part = part.strip()
                    all_tags[part] += 1

    print("total_cells: ", total_cells)

    # for tag, count in all_tags.items():
    #     print(f"{tag}: {count}")

    print(count_codes(all_tags=all_tags))



def count_attk_defense(file: str)->defaultdict:
    df = pd.read_csv(file)

    df_melted = df.melt(id_vars="Class_Id", value_vars=["Code 1", "Code 2", "Code 3", "Code 4"], var_name="code_type", value_name="code")
    df_melted = df_melted.dropna(subset=["code"])
    df_exploded = df_melted.explode("code")
    keyword_counts = (
        df_exploded.groupby(['Class_Id', "code"])
        .size()
        .reset_index(name="count")
    )
    
    code_counts = keyword_counts.groupby("code").size().reset_index(name="num_courses")
    code_counts_dict = dict(zip(code_counts['code'], code_counts['num_courses']))

    # Print the dictionary
    print(code_counts_dict)


    # ad = defaultdict(lambda: {"attack": 0, "defense": 0})
    # for lectures in entries:
    #     for entry in lectures:
    #         if isinstance(entry, str):
    #             parts = entry.split("->")
    #             if len(parts) >= 2:
    #                 key = "->".join(parts[:-1])
    #                 value = parts[-1].strip()
    #                 if value in ("attack", "defense"):
    #                     ad[key][value] += 1
    #                     continue
    #                 value2 = parts[-2].strip() 
    #                 if value2 in ("attack", "defense"):
    #                     ad[key][value2] += 1


            
    # for key, counts in ad.items():
    #     print(f"{key} : attack: {counts['attack']}, defense: {counts['defense']}")




def get_union_codes(keyword: str, file: str):
    df = pd.read_csv(file)
    
    graduate_df = df[df["Education Level"]==keyword][["Code 1", "Code 2", "code 3", "code 4"]]
    courses = graduate_df.values.tolist()
    all_tags = Counter()
    total_lectures = 0
    total_cells = 0
    for lectures in courses:
        total_lectures += 1
        for code in lectures:
            if isinstance(code, str):
                parts = code.split("->")
                total_cells += 1
                for part in parts:
                    part = part.strip()
                    all_tags[part]+=1

    print("total lectures: \n", total_lectures)
    print("total cells: \n", total_cells)
    print(count_codes(all_tags=all_tags))
                



def merge_attk_def(dd1: defaultdict, dd2: defaultdict):
    for key in dd2:
        if key not in dd1:
            dd1[key] = dd2[key]
        else:
            for subkey in dd2[key]:
                dd1[key][subkey] = dd1[key].get(subkey, 0) + dd2[key][subkey]
    
    return dd1



def code_count_by_course(file: str, output: str):
    df = pd.read_csv(file)

    df_melted = df.melt(id_vars="Class_Id", value_vars=["Code 1", "Code 2", "Code 3", "Code 4"], var_name="code_type", value_name="code")
    df_melted = df_melted.dropna(subset=["code"])

    df_melted["code_parts"] = df_melted["code"].str.split("->")
    df_exploded = df_melted.explode("code_parts")

    print(df_exploded)

    keyword_counts = (
        df_exploded.groupby(['Class_Id', "code_parts"])
        .size()
        .reset_index(name="count")
    )
    keyword_counts.to_csv(f"./course/{output}", index=False)
    print("Saved to keyword_counts_by_course.csv")
    
    code_counts = keyword_counts.groupby("code_parts").size().reset_index(name="num_courses")
    code_counts_dict = dict(zip(code_counts['code_parts'], code_counts['num_courses']))

    # Print the dictionary
    print(code_counts_dict)


if __name__ == "__main__":
    # # attk_def_dict  = defaultdict(lambda: {"attack":0, "defense": 0})
    # code_lists = []
    # code_list1 = read_codes(file="Security-Authors - Codebook-Course-Level.csv")
    # split_codes(code_list1)
    # ad1 = count_attk_defense(code_list1)
    # print("===================================")
    # code_list2 = read_codes(file="Top CS Schools - Code-Lecture-Level.csv")
    # split_codes(code_list2)
    
    # # aggregate version
    # # code_list1.extend(code_list2)
    
    # ad2 = count_attk_defense(code_list2)
    # get_union_codes(keyword="graduate", file="Security-Authors - Codebook-Course-Level.csv")
    # print("===========================")
    # get_union_codes(keyword="undergraduate", file="Security-Authors - Codebook-Course-Level.csv")
    
    # code_count_by_course(file="Security-Authors - Codebook-Course-Level.csv", output="sec-authors.csv")
    code_count_by_course(file="ML-Authors - Lecture-Level.csv", output="ml-authors.csv")
    # count_attk_defense(file="ML-Authors - Top ML - Lecture Level.csv")
    

