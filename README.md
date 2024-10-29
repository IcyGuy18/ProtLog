# Setup

1. Clone the repository and navigate inside the server folder:
```bash
git clone https://www.github.com/IcyGuy18/ProtLog.git
cd ProtLog/server
```
2. Set up a Python environment by entering the following:
```bash
python -m venv env
```
Once done, enter this command:
```bash
source env/bin/activate
```
3. Install the necessary libraries by entering the following command:
```bash
pip install -r requirements.txt
```
4. Run the server by calling this function:
```bash
uvicorn main:app --reload
```

# ProtLog

Additional files are given in `ProtLog` folder.

This is where some of the functions used during preprocessing steps of `dbPTM` were used.

They are designed to be modular and scalable, with minimal changing if needed.