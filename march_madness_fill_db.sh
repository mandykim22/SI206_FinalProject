#!/bin/bash

for n in {1..70};
do
    python3 $1
done

python3 march_madness_calcs.py

