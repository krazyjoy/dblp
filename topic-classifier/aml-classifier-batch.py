from openai import OpenAI
import os
import pandas as pd
import json
import openai
import argparse
api_key = os.environ["OPENAI_API_KEY"]

definition = """Adversarial Machine Learning (AML) is the process of extracting information about the behavior and characteristics of a machine learning (ML) system or learning how to manipulate its inputs to achieve a preferred outcome.
"""

definition2 = """Attacks can be grouped into three major categories: evasion, poisoning, and exploratory attacks. Evasion attacks attempt to avoid, or force, a classification by a ML system. 
By carefully perturbing a small number of influential features for an input, adversarial examples are generated that maximize the model’s error while minimizing differences, resulting in misclassification. 
Poisoning attacks manipulate training data in order to influence the behavior of the model. This can decrease accuracy or install a backdoor which allows to force a specific classification based on an attacker-chosen attribute. 
Exploratory attacks corrupt the confidentiality of ML models. Using black-box access, techniques can reconstruct the functionality of a model, determine if an input exists in a training dataset, and extract both lowresolution (general statistics) and high resolution (specific examples) information from the original training data set.
"""

positive_examples = """Positive Examples of AML related abstracts:
A. A bert-based malicious prompt detection model to prevent LLMs from generating phishing content.
B.Introduce web-scale poisoned training dataset.
Example A is related to AML because LLM is a machine learning model and this paper works on creating malicious prompts to generate scams for intentional usages and also provides its defenses that helps to prevent the prompts to be used.
Example B is related tp AML because new datasets are introduced to perform poisoning attacks to inject malicious text to fool the machine learning models.
"""

negative_examples = """Negative examples:
C. An end-to-end system Orca to accelerate the computation of FSS-based (Function secret sharing) 2PC (two-party computation) protocols with GPUs.
D. Detect mobile apps' inconsistencies in third-party data collection.
Example C is unrelated to AML because it focuses on creating a system to improve the computation efficiency of a cryptographic technique which is more relevant to “security” or “cryptography”. Nothing about machine learning is discussed. 
Example D is unrelated to AML because it designs a detector to check app inconsistencies which is nothing about malicious attacks or defenses.
"""

edge_cases = """Homomorphic encryption is machine learning related but still belongs closer to the security domain.
PCIe congestion is an attack scheme that is related to side-channel attack.
Federated learning is related to adversarial machine learning because the machine learning framework considers input data privacy.
"""
client = OpenAI(api_key=api_key)

def abstract_msg(abstract):
    messages=[
        {"role": "system", "content": definition},
        {"role": "assistant", "content": "Priorily we discussed about the general definitions of AML. Now we introduce some adversarial attacks and defenses." + definition2},
        {"role": "assistant", "content": positive_examples},
        {"role": "assistant", "content": negative_examples},
        {"role": "assistant", "content": edge_cases},
        {"role": "user", "content": f"Abstract: {abstract}\n\nPlease classify whether the given abstract is related to AML. Response 'Yes' or 'No' without further explanation"}
    ]
    return messages


def write_batch_requests(jsonl:str, input_file: str, start: int, batch_size: int):
    
    df = pd.read_csv(input_file) 
    for i in range(start, min(start+batch_size, df.shape[0])):
        uuid = df.loc[i, 'uuid']
        abstract = df.loc[i, 'abstract']
        row = {"custom_id": uuid, "method": "POST", "url": "/v1/chat/completions",
                "body": {"model": "gpt-4o", 
                         "messages": abstract_msg(abstract=abstract),
                         "max_tokens": 100
                        }
                }
        row_obj = json.dumps(row)
        with open(jsonl, 'a', encoding='utf-8') as f:
            f.write(row_obj+'\n')

def upload_batch_input(file: str):
   
    with open(file, "rb") as f:
        batch_file = openai.files.create(
            file=f,
            purpose="batch"
        )
    
    print("Batch File ID:", batch_file.id)
    return batch_file.id


def get_argument_parser():
    arg_parser = argparse.ArgumentParser()

    arg_parser.add_argument(
        '-v', '--venue-id',
        required=True,
        dest='venue_id'
    )
    arg_parser.add_argument(
        '-y', '--year',
        required=True,
        dest='year'
    )
    arg_parser.add_argument(
        '-s', '--start-index',
        required=True,
        dest='start'
    )
    arg_parser.add_argument(
        '-bj', '--batch-job',
        required=False,
        dest='batch_job'
    )
    arg_parser.add_argument(
        '-e', '--evaluating',
        required=True,
        dest='eval'
    )
    return arg_parser



def get_abstract(args):
    input_file=f'../venue_abstracts/{args.venue_id}/abstracts{args.year}.csv'
    return input_file


def get_response(line: dict):
    response_dict = json.loads(line)
    custom_id = response_dict["custom_id"]
    assistant_response = response_dict["response"]["body"]["choices"][0]["message"]["content"]
    return custom_id, assistant_response


def evaluate(client: openai.OpenAI, batch_status: openai.types.batch.Batch, args: argparse.Namespace):
    batch_status = client.batches.retrieve(args.batch_job)
    response_lines = read_batch_file(batch_status=batch_status)
    abstract_csv = get_abstract(args=args)

    export_file = abstract_csv.replace('../venue_abstracts', './batch_results')
    os.makedirs(f"./batch_results/{args.venue_id}", exist_ok=True)
    if os.path.exists(export_file):
        df = pd.read_csv(export_file, index_col=0)
    else:
        df = pd.read_csv(abstract_csv, index_col=0)

    print(df.head())
    for line in response_lines:
        custom_id, resp = get_response(line=line)
        print(f"custom_id: {custom_id}, resp: {resp}")
        df.loc[df['uuid']==custom_id, 'response'] = resp
    df.to_csv(export_file)



def read_batch_file(batch_status: openai.types.batch.Batch):
    batch_results = openai.files.content(batch_status.output_file_id)
    response_content = batch_results.read()
    response_lines = response_content.decode('utf-8').strip().split('\n')
    return response_lines


if __name__ == "__main__":

    parser = get_argument_parser()
    args = parser.parse_args()
    jsonl = args.venue_id + '_' + args.year + '_' + args.start
   
    if args.eval == 'false':
        if os.path.exists(f"./{jsonl}.jsonl"):
            os.remove(f"./{jsonl}.jsonl")
        # write_batch_requests(jsonl=f'{jsonl}.jsonl', 
        #                      input_file=f'../venue_abstracts/{args.venue_id}/abstracts{args.year}.csv', 
        #                      start=int(args.start), batch_size=20)
       
        # batch_id = upload_batch_input(f'{jsonl}.jsonl')
        batch_job = client.batches.create(
            input_file_id="file-Ck89Z5B3zdsVCkuPrD9guZ",
            endpoint="/v1/chat/completions",
            completion_window="24h",
            metadata={"task": "AML Topic Classification"}
        )

    elif args.eval == 'true':
        print(type(args))
        batch_status = client.batches.retrieve(args.batch_job)
        evaluate(client=client, batch_status=batch_status, args=args)

