#!/bin/bash

RUN_CMD="scrapy crawl $1"

function run_app() {
  pushd crawler 1>/dev/null

  attrs=("date" "src" "dest")
  attr_values=("$date" "$src" "$dest")
  for ((i = 0; i < "${#attrs[@]}"; i++))
  do
    if [ -n "${attr_values[$i]}" ]
    then
      RUN_CMD+=" -a ${attrs[$i]}=${attr_values[$i]}"
    fi
  done

  settings=("MIN_SEATS" "NUM" "SEAT_TYPE" "LANG" "TG_TOKEN" "TG_CHAT_ID" "RETRY_URL" "JOB_ID")
  settings_values=("$MIN_SEATS" "$NUM" "$SEAT_TYPE" "$LANG" "$TG_TOKEN" "$TG_CHAT_ID" "$RETRY_URL" "$JOB_ID")
  for ((i = 0; i < "${#settings[@]}"; i++))
  do
    if [ -n "${settings_values[$i]}" ]
    then
      RUN_CMD+=" -s ${settings[$i]}=${settings_values[$i]}"
    fi
  done

  $RUN_CMD

  popd 1>/dev/null
}

run_app
