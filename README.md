# Ticketer

This app was developed in order to help find free tickets from different websites (currently from https://www.rw.by/en/ only).
Setting up needed configuration, one can start the process and wait until voice pronounces found results.

## System requirements

- OS: Mac, Linux
- Python: 3.5+

## Preinstall

- Linux: you need to install `speech-dispatcher` package for voice alarm by running `sudo apt install speech-dispatcher`

[poetry](https://python-poetry.org/) is used as a package manager. To install dependencies, run:

    poetry install

## Configuration

### Spider arguments (required)

- `src`: point of departure, can be in Russian (preferred) or in other language, supported by the site (in this case you should overwrite [LANG](#additional-arguments) argument)
- `dest`: destination (same rules as for `src` parameter)
- `date`: departure time (e.g. *tomorrow*, *today*), available options can be taken from the official site

As a parameter you need to pass a spider name to be used for scrapping. It is assigned for each spider separately, e.g.:
    
    ...
    class TrainScheduleSpider(scrapy.Spider):
        name = 'train_schedule'
        ...

### Additional arguments

- `MIN_SEATS`(defaults to 1): minimum required # seats for the found transports.
- `NUM`: if you need to specify transport number you want to find available seats for, you should place it here. Without specifying this argument all transports from the schedule are compared to other params.
- `SEAT_TYPE`: if you want a specific type of seat (e.g. *Плацкартный*). This option value should be used the same as used in the official site.
- `LANG`(defaults to `ru`): if you want to input information in other languages (e.g. `en`), use this argument.

Example runs (assuming you are in `/ticketer`):

    ./scripts/env.sh && ./clean && ./configure
    src=Гомель dest=Минск date=tomorrow SEAT_TYPE=Плацкартный MIN_SEATS=2 NUM=627Б ./scripts/run.sh train_schedule

or

    ./scripts/env.sh && ./clean && ./configure
    src=Гомель dest=Минск date=tomorrow ./scripts/run.sh train_schedule

## Custom spiders

If you want to crawl any other web-site (e.g. for buses), all you need to do is to parse it using new spider. You should:

- Place its source code to `ticketer/ticketer/spiders/<your_spider>.py` (you can refer to existing [schedule.py](https://github.com/chiselko6/ticketer/blob/master/ticketer/ticketer/spiders/train_schedule.py) spider).
- Name your spider inside its class (e.g. `name = 'bus_schedule'`).
- Run the ticketer with your spider name: `./scripts/run.sh bus_schedule` with same arguments mentioned earlier.