import os
from typing import Optional


def find_trains(*,
                src: str,
                dest: str,
                date: str,
                min_seats: int,
                lang: str,
                train_num: Optional[str] = None,
                seat_type: Optional[str] = None,
                tg_bot_token: str,
                tg_chat_id: str,
                retry_url: str,
                queue_job_id: str) -> None:
    cmd = (
        f'src={src} dest={dest} date={date} '
        f'MIN_SEATS={min_seats} LANG={lang}'
    )

    if train_num is not None:
        cmd = f'{cmd} NUM={train_num} '
    if seat_type is not None:
        cmd = f'{cmd} SEAT_TYPE={seat_type} '

    cmd = (
        f'{cmd} TG_TOKEN={tg_bot_token} TG_CHAT_ID={tg_chat_id} '
        f'RETRY_URL={retry_url} JOB_ID={queue_job_id} '
        './scripts/run.sh train_schedule'
    )
    os.system(cmd)
