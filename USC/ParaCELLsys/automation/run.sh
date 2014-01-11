#!/bin/bash

run_old_code(){
    cd orig/forMiriah
    python /Users/mavinm/Documents/SCI/mlm/USC/MP/orig/forMiriah/plotParallelData_pos_newFormat.py
}

run_new_code(){
    python /Users/mavinm/Documents/SCI/mlm/USC/MP/plotParallelData_pos_newFormat.py
}
cd ..
run_new_code & run_old_code
echo "Complete"