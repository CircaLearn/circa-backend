# circa-backend
 Backend AI and MongoDB API for Circa. 

 Built using **HuggingFace Transformers**, **PyMongo**, and **FastAPI**.

## Startup
- Test the development API server with `fastapi dev app/main.py`

## Setup
- Using virtualenv package for my isolated virtual environment
    - Not necessary, but nice since it stores Python version as well
- To create virtual environment:
    - `pip install virtualenv`
    - `virtualenv .venv`
    - `source .venv/bin/activate`
    - Use `which python3` to ensure you're in the venv, every time you reopen
- To enter virtual environment:
  - `source .venv/bin/activate` everytime on startup
  - Make sure the correct virtualenv Python interpreter is selected in VSCode
    for IntelliSense to work
    - The correct interpreter is the copy inside the virtual environment
    - Its path is located with `which python3`
    - ex: .../Circa/circa-backend/.venv/bin/python3

To enable Intellisense (which sometimes bugs with venvs), ensure the venv is
activated and you've selected the .venv's Python interpreter in VSCode -- 
`which python3` will give you the path the the interpreter

## File Structure
Organized according to file structure suggested by [FastAPI](https://fastapi.tiangolo.com/tutorial/bigger-applications/)

```
circa-backend/
│
├── app/
│ ├── init.py
│ ├── main.py
│ ├── db/
│ │ ├── init.py
│ │ ├── database.py # Database connection and dependency injection
│ │ ├── collections/ # Directory for database operation files
│ │ │ ├── init.py
│ │ │ ├── <collection>.py # Database helper operations for each collection
│ ├── helpers/
│ │ ├── init.py
│ │ ├── <helper>.py # Operations related to ML processing, or other helper
│ ├── models/
│ │ ├── init.py
│ │ ├── <model>.py # Pydantic models for database schema
│ ├── routes/
│ │ ├── init.py
│ │ ├── <route>.py # API route definitions
│
├── requirements.txt 
├── .env
└── README.md
```


### HuggingFace Citations
```
@misc{grosman2021xlsr53-large-english,
  title={Fine-tuned {XLSR}-53 large model for speech recognition in {E}nglish},
  author={Grosman, Jonatas},
  howpublished={\url{https://huggingface.co/jonatasgrosman/wav2vec2-large-xlsr-53-english}},
  year={2021}
}

sentence-transformers/all-MiniLM-L6-v2 model
```

