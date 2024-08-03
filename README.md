# circa-backend
 Backend AI and MongoDB API for Circa. 

 Built using [**HuggingFace
 Transformers**](https://huggingface.co/docs/transformers/v4.41.3/en/index),
 [**Motor**](https://motor.readthedocs.io/en/stable/),
 [**Pydantic**](https://docs.pydantic.dev/latest/), and
 [**FastAPI**](https://fastapi.tiangolo.com/) for an asychronous, 
 high-performance, and scalable RESTful API.

**Coming soon:** Docker containerization of project.

## Startup
- Ensure your current IP is added in MongoDB Atlas
  - Otherwise, no API requests will function
- Test the development API server with `uvicorn app.main:app --reload`
- Alternative: `fastapi dev app/main.py`
- Use the FastAPI Swagger UI at `http://127.0.0.1:8000/docs` to test routes and requests

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

### WITH direnv
- With [direnv](https://direnv.net/) configured to zsh and allowed, it should
  automatically activate the virtualenv
    - The .envrc file is not included in commits but necessary for this to work
    - To add it, add a file name `.envrc` in the root direction with the command `layout python`

### Bugs
- Make sure the correct virtualenv Python interpreter is selected in VSCode
  for IntelliSense to work
  - The correct interpreter is the copy inside the virtual environment
  - Its path is located with `which python3`
  - ex: .../Circa/circa-backend/.venv/bin/python3


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

