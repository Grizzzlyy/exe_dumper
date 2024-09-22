# exe_dumper

## Prerequisites
- Ubuntu
- Python 3

## Setup
- Install packages in venv
```commandline
pip install -r requirements.txt
```

## Run
```commandline
python app.py
```

## Structure
    .
    ├── config/                 # Configuration files
    ├── logic/                  # Backend logic
    ├── static/                 # Static files, css and yara rules
    ├── templates/              # HTML templates
    ├── .env                    # Environment variables. Shouldn't be in git
    ├── .gitignore             
    ├── app.py                  # Main app
    ├── requirements.txt        # Reqiered packages
    └── README.md