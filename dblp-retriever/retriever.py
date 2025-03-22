import argparse
import logging
import csv
from dblp.venue_list import VenueList
import os

logger = logging.getLogger('dblp-retriever_logger')


def get_argument_parser():
    arg_parser = argparse.ArgumentParser(
        description='Retrieve paper metadata from DBLP,'
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
    arg_parser.add_argument(
        '-d', '--delimiter',
        required=False,
        default=',',
        help='delimiter for CSV files (default: \',\')',
        dest='delimiter'
    )
    arg_parser.add_argument(
        '-v', '--venue-id',
        required=True,
        help='venue id',
        dest='venue_id'
    )
    return arg_parser

def create_dblp_venue_uri(venue_id: str, year: int):
    filename = f"../venue_arg/{venue_id}/catalog{year}.csv"
    os.makedirs(os.path.join("../venue_arg", venue_id), exist_ok=True)
    csvfile = open(filename, 'w', newline='', encoding='utf-8')
    headers = ['venue', 'year', 'identifier']
    paper_list = [
        {'venue': venue_id, 'year': year, 'identifier': f'conf/{venue_id}/{venue_id}{year}'},
    ]

    f = csv.DictWriter(csvfile, fieldnames=headers)
    f.writeheader()
    f.writerows(paper_list)
    csvfile.close()
    return filename


def get_dblp_papers(venue_id: str, year_start: int, year_end: int):
    for year in range(year_start, year_end+1):
        venue_list = VenueList()
        input_file = create_dblp_venue_uri(venue_id=venue_id, year=year)
        output_dir = f"..\\venue_list\\{venue_id}"
        os.makedirs(output_dir, exist_ok=True)
        venue_list.read_from_csv(input_file=input_file, delimiter=',')
        venue_list.retrieve_papers()
        venue_list.validate_page_ranges()
        venue_list.write_to_csv(output_dir=output_dir, delimiter=',')



if __name__ == '__main__':
    parser = get_argument_parser()
    args = parser.parse_args()
    get_dblp_papers(args.venue_id, int(args.start_year), int(args.end_year))

