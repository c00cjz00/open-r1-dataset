#!/bin/bash

for page in {1..1375}; do
    template_index=$(( (page - 1) % 5 + 1 ))
    template="CUSTOM_TEMPLATE0$template_index"

    #echo "Running: python distilabel.py.py --page $page --template \"$template\""
    echo python distilabel.py.py --page $page --template "$template"
done
