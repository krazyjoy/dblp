import pandas as pd
import requests
from bs4 import BeautifulSoup
import csv
import argparse

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
import time


def get_argument_parser():
    arg_parser = argparse.ArgumentParser()

    arg_parser.add_argument(
        '-v', '--venue-id',
        required=True,
        dest='venue_id'
    )
    arg_parser.add_argument(
        '-start', '--year-start',
        required=True,
        help='start year',
        dest='start_year'
    )
    arg_parser.add_argument(
        '-end', '--year-end',
        required=True,
        help='end year',
        dest='end_year'
    )
    return arg_parser



def get_ieee(driver, uri, row):
    print(f"get ieee: {uri}")
    driver.get(uri)
    driver.save_screenshot('screenshot.png')
    try:
        WebDriverWait(driver, 100).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "span[xplmathjax]"))
        )
    except TimeoutException:
        print("timeout")
        row['abstract'] = None
        return None
    
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    
    layout_wrapper = soup.find("div", id="LayoutWrapper")
    if layout_wrapper:
        h2_abstracts = soup.find_all("h2", string=" Abstract:")
        print(h2_abstracts)

    for abstract in h2_abstracts:
        if abstract:
            print("✅ Found <h2>Abstract</h2>!")

            element = driver.find_element(By.CSS_SELECTOR, "div[xplmathjax]")
            full_text = element.get_attribute("innerText").strip()
            time.sleep(2)
            
            print("element:")
            print(full_text)
            row['abstract'] = full_text
            return row['abstract']
        else:
            print("❌ <h2>Abstract</h2> not found!")
            row['abstract'] = None
            return None

def get_uss(driver, uri, row):
    print("get uss: ", uri)
    driver.get(uri)
    try:
        WebDriverWait(driver, 100).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.field-item.odd"))
        )
    except TimeoutException:
        print("timeout")
        row['abstract'] = None
        return None
    
    soup = BeautifulSoup(driver.page_source, "html.parser")
    content = soup.find("section", id="content")
    if content:
        try:
            labels= content.find_all("div", class_="field-label") # bs find all
            for label in labels:
                text = label.get_text(strip=True)
                print("label: ", text)
                if "Abstract:" in text:
                    field_items = label.find_next_sibling("div", class_="field-items")
                    if field_items:
                        abstracts = field_items.find_all("p")
                        if abstracts:
                            combined_abstract = " ".join(abstract.get_text(strip=True) for abstract in abstracts)
                            print("Abstract:\n", combined_abstract)
                            row['abstract'] = combined_abstract
                            return row['abstract']             
        except:
            print("❌ <p> abstract </p>")
            row['abstract'] = None
            return None
    row['abstract'] = None
    return None

def get_icml(driver, uri, row):
    print("get icml: ", uri)
    driver.get(uri)
    try:
        WebDriverWait(driver, 100).until(
            EC.presence_of_element_located((By.ID, "abstract"))
        )
    except TimeoutException:
        print("timeout")
        row['abstract'] = None
        return None
    

    soup = BeautifulSoup(driver.page_source, "html.parser")
    content = soup.find("div", id="abstract")
    if content:
        abstract = content.get_text(strip=True)
        print("abstract: ", abstract)
        row['abstract'] = content
        return abstract
    row['abtract'] = None
    return None

def get_ccs(driver, uri, row):
    print("get_ccs: ", uri)
    driver.get(uri)
    try:
        WebDriverWait(driver, 60).until(
            EC.presence_of_element_located((By.ID, "pb-page-content"))
        )
    except TimeoutException:
        print("timeout")
        row['abstract'] = None
        return None
    

    soup = BeautifulSoup(driver.page_source, "html.parser")
    abstract_section = soup.select_one('section#abstract')
    print("abstract_section: ", abstract_section)
    if abstract_section:
        paragraphs = abstract_section.findAll('div', role='paragraph')
        
        abstract = " ".join(paragraph.get_text(strip=True) for paragraph in paragraphs)
        print("abstract: ", abstract)
        row['abstract'] = abstract
        return abstract
    row['abtract'] = None
    return None

def get_ndss(driver, uri, row):
    print("get ndss uri: ", uri)
    driver.get(uri)
    try:
        WebDriverWait(driver, 60).until(
            EC.presence_of_element_located((By.CLASS_NAME, "content"))
        )
    except TimeoutException:
        print("timeout")
        row['abstract'] = None
        return None
    soup = BeautifulSoup(driver.page_source, "html.parser")
    content = soup.find("div", class_="paper-data")
    if content:
        p_tags = content.find_all("p")
        if len(p_tags) > 2:
            abstract = p_tags[2].get_text()
            print("abstract:\n", abstract)
            row['abstract'] = abstract
            return row['abstract']             
            
        else:
            print("Less than two <p> elements found.")
    return None


def get_neurips(driver, uri, row):
    print(f"get neurips: {uri}")
    driver.get(uri)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    all_abstracts = ""
    for h4 in soup.find_all('h4'):
        for sibling in h4.find_next_siblings():
            if sibling.name == 'p':
                all_abstracts += sibling.get_text(strip=True) + " "
    print("all_abstracts: ", all_abstracts)
    if all_abstracts:
        row['abstract'] = all_abstracts.strip()
    else:
        row['abstract'] = None
    return row['abstract']
def default_func():
    return ""
 
def write_abstract(df, file_name, batch_size=20):
    headers = ['uuid', 'venue', 'year', 'title', 'authors', 'abstract']
    print("write_abstract...")
    for i in range(0, len(df), batch_size):
        batch = df.iloc[i:i+batch_size]
        if i==0:
            batch.to_csv(file_name, index=False, columns=headers, mode='w')
        else:
            batch.to_csv(file_name, index=False, columns=headers, mode='a', header=False)

def main():
    parser = get_argument_parser()
    args = parser.parse_args()


    options = webdriver.ChromeOptions()

    options.add_argument('--headless') 
    options.add_argument("--disable-blink-features=AutomationControlled")  
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    start_year = int(args.start_year)
    end_year = int(args.end_year)
    for year in range(start_year, end_year+1):
        input_file = f'./venue_list/{args.venue_id}/catalog{year}.csv'
        print("input_file: ", input_file)
        df = pd.read_csv(input_file)
        for index, row in df.iterrows():
            if args.venue_id == 'ieee':
                df.at[index, 'abstract'] = get_ieee(driver, row['electronic_edition'], row)
            elif args.venue_id == 'uss':
                df.at[index, 'abstract'] = get_uss(driver, row['electronic_edition'], row)
            elif args.venue_id == 'icml':
                df.at[index, 'abstract'] = get_icml(driver, row['electronic_edition'], row)
            elif args.venue_id == 'ccs':
                df.at[index, 'abstract'] = get_ccs(driver, row['electronic_edition'], row)
            elif args.venue_id == 'ndss':
                df.at[index, 'abstract'] = get_ndss(driver, row['electronic_edition'], row)
            elif args.venue_id == 'nips':
                df.at[index, 'abstract'] = get_neurips(driver, row['electronic_edition'], row)


            df.at[index, 'uuid'] = args.venue_id + '_' + str(row['year']) + '_' + str(index)
            if (index+1) % 20 == 0 or index == len(df)-1:
                output_file = f'./venue_abstracts/{args.venue_id}/abstracts{year}.csv'
                write_abstract(df.iloc[:index+1], file_name=output_file)

    driver.quit()

if __name__ == '__main__':
    main()






            
    





