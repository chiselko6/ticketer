# Ticketer

This app was developed in order to help find free tickets on https://www.rw.by/en/.
Setting up needed configuration, one can start the process and wait until voice pronounces found results.

## System requirements

- OS: Mac, Linux
- Python: 2.7+

## Preinstall

- Linux: you need to install `speech-dispatcher` package for voice alarm by running `sudo apt install speech-dispatcher`

Common:

- `scrapy`: `pip install scrapy`

## Configuration

### Spider arguments(required)

- `src`: point of departure, can be in Russian (preferred) or in other language, supported by the site (in this case you should overwrite [LANG](#additional-arguments) argument)
- `dest`: destination (same rules as for `src` parameter)
- `date`: departure time (e.g. *tomorrow*, *today*), available options can be taken from the official site

### Additional arguments

- `MIN_SEATS`(defaults to 1): minimum required # seats for the found train/trains
- `TRAIN_NUM`: if you need to specify train number you want to find available seats for, you should place it here. Without specifying this argument all trains from the schedule are compared to other params
- `SEAT_TYPE`: if you want a specific type of seat (e.g. *Плацкартный*). This option value should be used the same as used in the official site
- `LANG`(defaults to `ru`): if you want to input information in other languages (e.g. `en`), use this argument

Example run (assuming you are in `/ticketer`):

    ./scripts/env.sh && ./clean && ./configure
    src=Гомель dest=Минск date=tomorrow SEAT_TYPE=Плацкартный MIN_SEATS=2 ./scripts/run.sh
