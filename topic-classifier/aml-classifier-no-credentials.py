from openai import OpenAI
import os
import pandas as pd
import json
import openai
import time
import glob


os.environ["OPENAI_API_KEY"] = ''
api_key = os.environ["OPENAI_API_KEY"]

definition = """Adversarial Machine Learning (AML) is the process of extracting information about the behavior and characteristics of a machine learning (ML) system or learning how to manipulate its inputs to achieve a preferred outcome.
The focus of AML should be on either attacking or defineding ML systems.
"""

definition2 = """Attacks can be grouped into three major categories: evasion, poisoning, and exploratory attacks. Evasion attacks attempt to avoid, or force, a classification by a ML system. 
By carefully perturbing a small number of influential features for an input, adversarial examples are generated that maximize the model’s error while minimizing differences, resulting in misclassification. 
Poisoning attacks manipulate training data in order to influence the behavior of the model. This can decrease accuracy or install a backdoor which allows to force a specific classification based on an attacker-chosen attribute. 
Exploratory attacks corrupt the confidentiality of ML models. Using black-box access, techniques can reconstruct the functionality of a model, determine if an input exists in a training dataset, and extract both lowresolution (general statistics) and high resolution (specific examples) information from the original training data set.
"""

positive_examples = """Positive examples:
A.Introduce suite  of adversarial attacks for decentralized learning.
B.Introduce web-scale poisoned training dataset.
Example A is related to AML because decentralized learning is type of machine learning.
Example B is related to AML because new datasets are introduced to perform poisoning attacks to inject malicious text to fool the machine learning models.
"""

negative_examples = """Negative examples:
C. An end-to-end system Orca to accelerate the computation of FSS-based (Function secret sharing) 2PC (two-party computation) protocols with GPUs.
D. Detect mobile apps' inconsistencies in third-party data collection.
E. An efficient and robust watermarking framework designed from LLM trained to preserve the semantic integrity in watermarked content.
Example C is unrelated to AML because it focuses on creating a system to improve the computation efficiency of a cryptographic technique which is more relevant to “security” or “cryptography”. Nothing about machine learning is discussed. 
Example D is unrelated to AML because it designs a detector to check app inconsistencies which is nothing about malicious attacks or defenses.
Example E is unrelated to AML because it is preventing from ML abuse not protecting or exploiting ML systems.
"""

edge_cases = """Homomorphic encryption can be applied to machine learning but more in the domain of cryptography.
PCIe congestion is an attack scheme that is related to side-channel attack.
Federated learning is related to adversarial machine learning because the machine learning framework considers input data privacy.
Intentionally direct ML models to learn in a certain way can be considered as an evasion attack.
Research on making explanations themselves robust to adversarial perturbations or on adversarial robustness in security-sensitive ai systems
Detecting ML-aided attacks such as deepfakes or CAPTCHA is not AML but exploiting or abusing it is.
Offensive, defensive AI or securing applications using AI is not AML because it is not abusing or defending AI systems.
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


def classify_abstract(abstract: str):
    response = client.chat.completions.create(
        model='gpt-4o',
        messages = abstract_msg(abstract),
        max_tokens=100
    )
    choice = response.choices[0].message.content
    print(choice[:5])
    return choice


if __name__ == '__main__':

    abstract_dir = '..\\venue_abstracts'
    batch_size = 20
    venue='nips'
    venue_path = os.path.join(abstract_dir, venue)
    count = 0
    for input_file in glob.glob(os.path.join(venue_path, '*.csv')):
        print("input_file: ", input_file)
        df = pd.read_csv(input_file)
        
        os.makedirs(f'./ml-track/{venue}', exist_ok=True)
        output_file = f'./ml-track/{venue}/{input_file[-8:]}'
        print("output_file: ", output_file)
        if count == 1:
            break
        for i in range(0, len(df), batch_size):
            batch_df = df.iloc[i:i+batch_size].copy()
            batch_df['response'] = batch_df['abstract'].apply(classify_abstract)
            df_out = batch_df[['uuid', 'title', 'abstract', 'response']]
            df_out.to_csv(output_file, mode='a', index=False, header=not os.path.exists(output_file))
            print(f"Processed and saved rows {i} to {i+batch_size} to {output_file}")
        count += 1