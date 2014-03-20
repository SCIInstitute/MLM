#!/bin/bash

root=/Users/mavinm/SCI/mlm/USC/ParaCELLsys/

run_old_code(){
    cd orig/forMiriah
    /usr/local/bin/python ${root}/orig/forMiriah/plotParallelData_pos_newFormat.py
}

run_new_code(){
    /usr/local/bin/python ${root}/plotParallelData_pos_newFormat.py
}
cd ..
run_new_code & run_old_code
echo "Complete"