### Format resume information
uvicorn model_analyse:app --host 0.0.0.0 --port 8004 --workers 1 &
uvicorn aftercure:app --host 0.0.0.0 --port 8005 --workers 1 &
wait -n

### Generate labels
use_browser_tag-api.py 
use_standardization_map_updated_company.py
merged_tags_for_companies.py
remove_single_unit_duplicate_labels.py
remove_duplicate_labels.py

### Final labels
标签名_公司名_替换后_v8.csv

