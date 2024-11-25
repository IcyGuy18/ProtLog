from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from starlette.responses import Response, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import requests
import glob
import pandas as pd
import matplotlib.pyplot as plt
import os
import traceback
import json

#### Comment whichever you want to use for the time being
#### Only use one at a time though
# from mongo_ptm import fetch_identifiers, search_identifier
from local_ptm import fetch_identifiers, search_identifier
from calculator import additive_calculator, multiplicative_calculator
from response_fetcher import fetch_response_uniprot_trim
from jpred_prediction import submit_job, get_job

app = FastAPI()
templates = Jinja2Templates(directory='templates/')
app.mount('/static', StaticFiles(directory="static"), name="static")

######## CUSTOM FUNCTION FOR SORTING ########

def sort_ids(strings: list[str], substring: str):
    def similarity_score(s: str):
        if substring in s:
            try:
                return (0, s.index(substring))
            except AttributeError:
                return (0, -1)
        else:
            return (1, 0)
    return sorted(strings, key=similarity_score)

######## PAGES ########

@app.get("/")
def home_page(request: Request):
    return templates.TemplateResponse(
        "index.html", context={"request": request}
    )

@app.get("/documentation")
def docs_page(request: Request):
    return templates.TemplateResponse(
        "docs.html", context={"request": request}
    )

@app.get("/download")
def download_page(request: Request):
    return templates.TemplateResponse(
        "download.html", context={"request": request}
    )

@app.get("/integration")
def integration_page(request: Request):
    return templates.TemplateResponse(
        "integration.html", context={"request": request}
    )

@app.get("/about")
def integration_page(request: Request):
    return templates.TemplateResponse(
        "about.html", context={"request": request}
    )

######## PAGE REQUESTS ########

@app.get('/ptmkb/autofill')
async def search(_id: str, request: Request):
    # Probably best to insert elements in a database
    ids = fetch_identifiers(_id)
    ids = sort_ids(ids, _id)
    # Give only top 200 suggestions - otherwise burden on user
    return {'ids': ids[:200]}

@app.post('/ptmkb/search_result')
async def search(request: Request):
    data = await request.json()
    data['id'] = data['id'].strip()
    
    found, results = search_identifier(data['id'])
    # Stupid check, I am aware - need to fix this somehow
    try:
        results = results[0]
    except IndexError:
        ...
    # We're just going to load the HTML file here to include in the iframe.
    with open('./templates/protein.html', 'r', encoding='utf-8') as f:
        html_page = f.read()
    return {
        'found': found,
        'result': results,
        'html': html_page
    }

# I look at this function and cry every single night.
# This was the best I could do given the time constraint
# and my inability to do good frontend programming at all. 
@app.post('/ptmkb/fetch_uniprot')
async def get_uniprot_info(request: Request):
    data = await request.json()
    prot_id: str = data['id']
    # The dataset's protein identifiers all have an underscore
    # That's how we differentiate from accession numbers
    # This is necessary for web scraping purposes
    # OR we can just use the REST API to fetch the necessary information
    # without worrying about the type of ID
    return_response = fetch_response_uniprot_trim(prot_id)

    return return_response

def save_image(df: pd.DataFrame, format: str, ptm: str) -> bytes:
    _, ax = plt.subplots(figsize=(12, 8))

    ax.axis('off')

    table = ax.table(cellText=df.values, colLabels=df.columns, rowLabels=df.index, cellLoc='center', loc='center')

    # Color the columns
    site_idx = 0
    for (i, j), cell in table.get_celld().items():
        if j >= 0 and i == 0 and cell.get_text().get_text() == '0':
            site_idx = j
            break
    
    for (i, j), cell in table.get_celld().items():
        if j == -1:
            cell.set_facecolor('#D0E0E3')
        elif j >= 0:
            if i == 0:
                cell.set_facecolor('#A0C4FF')
            else:
                if j == site_idx:
                    cell.set_facecolor("#F2C998")
                else:
                    cell.set_facecolor('#E0E0E0' if i % 2 == 0 else '#FFFFFF')

    ax.set_title("Log-Odd values for " + ptm)
    plt.text(-0.035, 0.37, "Amino Acid at Position", rotation=90)
    plt.text(0.365, 0.8, "Position Relative to Modification Site")

    plt.savefig(
        f"./temp.{format}",
        dpi=300
    )
    with open(f'./temp.{format}', 'rb') as f:
        raw_data = f.read()
    os.remove(f'./temp.{format}')

    return raw_data

def save_data(df: pd.DataFrame, format: str) -> bytes:
    if format == "CSV":
        # Simple fix for CSV
        df = df.astype(str)
        df.to_csv(f'./temp.csv')
    elif format == "JSON":
        df.to_json('./temp.json')
    with open(f'./temp.{format.lower()}', 'rb') as f:
        raw_data = f.read()
    os.remove(f'./temp.{format.lower()}')
    print(raw_data)
    return raw_data

@app.post('/ptmkb/download')
async def download(request: Request):
    data: dict = await request.json()

    return_header = {
        "CSV": 'text/csv',
        "PNG": 'image/png',
        "PDF": 'application/pdf',
        "SVG": 'image/svg+xml',
        "JSON": 'application/json'
    }
    
    ptm = data.get("ptm")
    format = data.get("format")
    rounded = True # data.get('rounded')

    df = pd.read_json(f"./data/tables/{ptm}.json")
    
    if rounded and format in ["PNG", "PDF", "SVG"]: df = df.round(2)
    
    # Check format
    raw_data = save_image(df, format, ptm) if format in ["PNG", "PDF", "SVG"] else save_data(df, format)

    return Response(
        content=raw_data,
        media_type=return_header[format]
    )

# This function is a separate call
@app.post('/ptmkb/get_protein_log')
async def get_log_value(request: Request):
    data: dict = await request.json()
    data = dict(sorted(data.items(), key=lambda item: int(item[0])))
    vector = [list(v.values())[0] for _, v in data.items()]
    # Use the above vector to calculate additive and multiplicative scores
    a_score, m_scores = additive_calculator(vector), multiplicative_calculator(vector)
    m_score = m_scores[1]['multiplicative_score']
    asterisk_m_score = m_scores[1]['adjusted_multiplicative_score']
    return {
        'a_score': round(a_score, 3) if not isinstance(a_score, str) else a_score,
        'm_score': round(m_score, 3) if not isinstance(m_score, str) else m_score,
        '*_m_score': round(asterisk_m_score, 3) if not isinstance(asterisk_m_score, str) else asterisk_m_score
    }


######## API CALLS ########

@app.post('/ptmkb/unrel/submitJpred')
async def get_jpred_prediction(request: Request):
    info = await request.json()
    return await submit_job(info['sequence'])

@app.get('/ptmkb/unrel/getJpred')
def get_jpred_prediction(request: Request, jobid: str):
    return get_job(jobid)

@app.get("/ptmkb/api/proteins")
def get_protein(request: Request, upid: str = None, upac: str = None):
    if not upid and not upac:
        return {'result': '', 'message': 'Please enter a protein identifier or an accession number first!'}
    _id = upid or upac
    _id = _id.upper()
    found, results = search_identifier(_id)
    if found:
        return {'result': results}
    return {'result': results, 'message': 'Could not find the queried protein!'}

@app.get("/ptmkb/api/ptms")
async def get_options():
    options = [i.split("\\")[-1] for i in glob.glob(r'data\tables\*')]
    return {'ptms': options}

@app.get("/ptmkb/api/ptms_detailed")
async def get_options():
    with open('./data/ptms-expanded.json', 'r') as f:
        options = json.load(f)
    return {'ptms': options}

@app.get("/ptmkb/api/data")
async def get_data(request: Request, selection: str = None, aa: str = None):
    if not selection:
        ptms = [i.split("\\")[-1] for i in glob.glob(r'data\tables\*')]
        response = {ptm: [] for ptm in ptms}
        for ptm in ptms:
            # Pick out all AAs in that folder
            AAs = [i.split("\\")[-1].split('.')[0] for i in glob.glob(f'data/tables/{ptm}/log-e/*.json')]
            for aa in AAs:
                with open(f"data/tables/{ptm}/log-e/{aa}.json", 'r', encoding='utf-8') as f:
                    response[ptm].append(
                        {
                            aa: json.load(f)
                        }
                    )
        return response
    elif not aa:
        response = {selection: []}
        AAs = [i.split("\\")[-1].split('.')[0] for i in glob.glob(f'data/tables/{selection}/log-e/*.json')]
        for aa in AAs:
            with open(f"data/tables/{selection}/log-e/{aa}.json", 'r', encoding='utf-8') as f:
                response[selection].append(
                    {
                        aa: json.load(f)
                    }
                )
    else:
        print(f'./data/tables/{selection}/log-e/{aa}.json')
        return FileResponse(
            './data/tables/{selection}/log-e/{aa}.json'.format(
                selection=selection, aa=aa
            )
        )