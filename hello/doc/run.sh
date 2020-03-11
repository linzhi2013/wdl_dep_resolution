rm -rf _build/*
python3 extract_comments_from_WDL_v3.py -a ../src/wdl -o src/
make html
