def generate_data_const():
    current_data_idx = 1

    def gen():
        nonlocal current_data_idx

        old_data_idx = current_data_idx
        current_data_idx += 1

        return chr(old_data_idx)

    return gen


data_generator = generate_data_const()

# Handlers' states
SOURCE_CHOICE = data_generator()
DESTINATION_CHOICE = data_generator()
DATE_CHOICE = data_generator()
MIN_SEATS_CHOICE = data_generator()
TRAIN_NUM_CHOICE = data_generator()
SEAT_TYPE_CHOICE = data_generator()
LANGUAGE_CHOICE = data_generator()

FULFIL_STATE = data_generator()
WAIT_FOR_INPUT = data_generator()

START_OVER = data_generator()

SEARCH_CHOICE = data_generator()

WAIT_JOB_RESULTS = data_generator()

# Commands
START_COMMAND = 'start'
RESET_COMMAND = 'reset'
UNDO_COMMAND = 'undo'

# User data keys
STATE = 'state'
STATE_CHANGES = 'state_changes'
CURRENT_CHOICE_TYPE = 'current_choice_type'

# other settings
CALENDAR_NEXT_DAYS_INTERVAL = 60
