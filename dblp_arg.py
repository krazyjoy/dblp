import csv

venue = "nips"
venue_id = "neurips"
year = 2020

csvfile = open(f"venue_arg/{venue_id}/venue_catalog{year}.csv", 'w', newline='', encoding='utf-8')

headers = ['venue', 'year', 'identifier']

paper_list = [
   
    {'venue': venue, 'year': year, 'identifier': f'conf/{venue}/{venue_id}{year}'},
    
]

f = csv.DictWriter(csvfile, fieldnames=headers)
f.writeheader()
f.writerows(paper_list)
csvfile.close()




