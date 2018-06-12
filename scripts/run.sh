#!/bin/bash

MYOS=`uname`
if [ "$MYOS" == "Darwin" ]
then
  SPEAK_COMMAND="say"
else
  SPEAK_COMMAND="spd-say"
fi

function run_app() {
  pushd app 1>/dev/null
  runner_cmd="scrapy crawl schedule"

  attrs=("date" "src" "dest")
  attr_values=("$date" "$src" "$dest")
  for ((i = 0; i < "${#attrs[@]}"; i++))
  do
    if [ ! -z "${attr_values[$i]}" ]
    then
      runner_cmd+=" -a ${attrs[$i]}=${attr_values[$i]}"
    fi
  done

  settings=("MIN_SEATS" "TRAIN_NUM" "SEAT_TYPE" "LANG")
  settings_values=("$MIN_SEATS" "$TRAIN_NUM" "$SEAT_TYPE" "$LANG")
  for ((i = 0; i < "${#settings[@]}"; i++))
  do
    if [ ! -z "${settings_values[$i]}" ]
    then
      runner_cmd+=" -s ${settings[$i]}=${settings_values[$i]}"
    fi
  done

  $runner_cmd > $OUTPUT_DATA && cat $OUTPUT_DATA | xargs $SPEAK_COMMAND
  popd 1>/dev/null
}

run_app
