#!/bin/bash

uvicorn model_analyse_cpu:app --host 0.0.0.0 --port 8004 --workers 1 &
uvicorn aftercure:app --host 0.0.0.0 --port 8005 --workers 1 &
wait -n