# Ticketer telegram notifier

This app contains a simple telegram bot to fill in the required data to find available tickets for. On "Search" it triggers a separate service to crawl the tickets.

## System requirements

- OS: Mac, Linux
- Python: 3.5+


## Preinstall

[poetry](https://python-poetry.org/) is used as a package manager. To install dependencies, run:

    poetry install

## Configuration

To start the telegram bot, you will need to obtain its token via [BotFather](https://core.telegram.org/bots#6-botfather) service. Also, you will need to have your crawling service running and specify its host in `FINDER_HOST` variable. Then run the following script:

    poetry run env TG_TOKEN=<TOKEN> FINDER_HOST=<HOST> python telegram_run.py