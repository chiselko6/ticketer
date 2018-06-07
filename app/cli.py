import argparse
from crawler.crawler.spiders.schedule import ScheduleSpider


def create_parser():
    parser = argparse.ArgumentParser(prog='ticketer',
                                     epilog='Have a nice trip')
    parser.add_argument('src')
    parser.add_argument('dest')
    parser.add_argument('--train-num')

    condition = parser.add_mutually_exclusive_group()
    condition.add_argument('--more-place', type=int)
    condition.add_argument('--has-place', action='store_true')

    return parser

def run_command(namespace):
    pass

def start():
    parser = create_parser()
    namespace = parser.parse_args()
    run_command(namespace)
