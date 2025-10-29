from openai import OpenAI
import os
import pandas as pd
import json
import openai
import time
import glob
import re

os.environ["OPENAI_API_KEY"]= ""
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
A. We introduce linear backpropagation (LinBp), a method that performs backpropagation in a more linear fashion using off-the-shelfattacks that exploit gradients.
Example A creates a method that crafts adversarial examples which is enhancing AML in an adversarial aspect.
B. We establish a connection between adversarial robustness of streaming algorithms and the notion of differential privacy. 
Example B desgins a new adversarial robust streaming algorithm which can be conceived as a defense to protect models against adversarial attacks.
C.  Linear relaxation based perturbation analysis (LiRPA) for neural networks, which computes provable linear bounds of output neurons given a certain amount of input perturbation, has become a core component in robustness verification and certified defense. We develop an automatic framework to enable perturbation analysis on any neural network structures, by generalizing existing LiRPA algorithms such as CROWN to operate on general computational graphs.
Example C is a type of AML because it constructs a way certify neural network defense and robustness.
D. Create debiasing algorithms and evaluate on adversarial level is to minimize the ambiguiosity of fraud machine learning applications which is related to fairness and bias in AML.
"""

negative_examples = """Negative examples:
E. We develop a GNN model based on transform-sum-cat, which obtains (1) a higher accuracy in node classification, (2) a lower absolute error in graph regression, and (3) greater stability in adversarial training of graph generation. 
Example E only shows that the GNN model obtains a higher stability in robustness which does not exploits a model in a malicious way or develop a defense for that.
F. we propose a graph contrastive learning (GraphCL) framework for learning unsupervised representations of graph data and systematically study its settings on adversarial attacks.
Example F is mostly about proposing a new graph contrastive learning not implementing actual attacks or defenses.
"""

edge_cases = """Robustness verification techniques are unrelated to AML because it does not develop adversarial attack or implement defenses against them.
Adversarial linear bandits are a type of online learning problem where a learner repeatedly chooses actions in an environment, and the goal is to maximize cumulative reward (or minimize regret) over time which means contains the word "adversarial" does not neccessarily mean relevant to AML.
Generative Adversarial Network is not related to AML.
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
    venue='iclr'
    abstract_path = os.path.join(abstract_dir, venue)
    
    batch_size=20
    count = 0
    all_files = os.listdir(abstract_path)

    target_files = [f for f in all_files if re.match(r'abstracts202[3-4]\.csv$', os.path.basename(f))]
   
    for file in target_files:
        input_file = os.path.join(abstract_path, file)
        df = pd.read_csv(input_file)
        
        os.makedirs(f'./ml-track/{venue}', exist_ok=True)
        output_file = f'./ml-track/{venue}/{input_file[-8:]}'
        print("output_file: ", output_file)
        for i in range(0, len(df), batch_size):
            batch_df = df.iloc[i:i+batch_size].copy()
            batch_df['response'] = batch_df['abstract'].apply(classify_abstract)
            df_out = batch_df[['uuid', 'title', 'abstract', 'response']]
            df_out.to_csv(output_file, mode='a', index=False, header=not os.path.exists(output_file))
            print(f"Processed and saved rows {i} to {i+batch_size} to {output_file}")
