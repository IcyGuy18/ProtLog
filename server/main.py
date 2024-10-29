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
####

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
    return_response = dict.fromkeys(
        [
            'uniProtID',
            'uniProtAC',
            'proteinName',
            'geneName',
            'organism',
            'sequenceLength',
            'proteinFunction',
            'proteinSequence',
            'message'
        ],
        ''
    )
    try:
        response = requests.get(
            f"https://rest.uniprot.org/uniprotkb/{prot_id}",
            headers={
                'Accept': 'application/json'
            }
        )
        if response.ok:
            try:
                response: dict = response.json()
                # Handle demerged/deleted problems first.
                if 'inactiveReason' in response.keys():
                    inactive_reason = response['inactiveReason']['inactiveReasonType']

                    # For DELETED
                    if 'DELETED' in inactive_reason:
                        prot_id = response['extraAttributes']['uniParcId']
                        response = requests.get(
                            f'https://rest.uniprot.org/uniparc/{prot_id}',
                            headers={
                                'Accept': 'application/json'
                            }
                        )
                        # This is processed a LOT differently
                        try:
                            return_response['uniProtAC'] = response['uniParcCrossReferences'][0]['id']
                        except:
                            print(traceback.format_exc())
                            return_response['uniProtAC'] = ''
                        try:
                            return_response['proteinName'] = response['uniParcCrossReferences'][0]['proteinName']
                        except:
                            print(traceback.format_exc())
                            return_response['proteinName'] = ''
                        try:
                            return_response['geneName'] = response['uniParcCrossReferences'][0]['geneName']
                        except:
                            print(traceback.format_exc())
                            return_response['geneName'] = ''
                        try:
                            return_response['organism'] = (
                                f"{response['uniParcCrossReferences'][0]['organism']['scientificName']}"
                                f" ({response['uniParcCrossReferences'][0]['organism']['commonName']})"
                            )
                        except:
                            print(traceback.format_exc())
                            return_response['organism'] = ''
                        try:
                            return_response['sequenceLength'] = response['sequence']['length']
                        except:
                            print(traceback.format_exc())
                            return_response['sequenceLength'] = ''
                        try:
                            return_response['proteinSequence'] = response['sequence']['value']
                        except:
                            print(traceback.format_exc())
                            return_response['proteinSequence'] = ''

                        # UniParc doesn't hold UniProtID and Protein function, which is a shame,
                        # because this will be the THIRD call to the UniProt API
                        response = requests.get(
                            f"https://rest.uniprot.org/uniprotkb/{return_response['uniProtAC']}",
                            headers={
                                'Accept': 'application/json'
                            }
                        )
                        response: dict = response.json()
                        # And now we resume.
                        try:
                            return_response['proteinFunction'] = ''.join(
                                i['texts'][0]['value'] for i in response['comments']
                                if 'FUNCTION' in i['commentType']
                            )
                        except:
                            print(traceback.format_exc())
                            return_response['proteinFunction'] = ''
                        try:
                            return_response['uniProtID'] = response['uniProtkbId']
                        except:
                            print(traceback.format_exc())
                            return_response['uniProtID'] = ''
                    
                    # For DEMERGED
                    elif 'DEMERGED' in inactive_reason:
                        prot_id = response['inactiveReason']['mergeDemergeTo'][0]
                        response = requests.get(
                            f"https://rest.uniprot.org/uniprotkb/{prot_id}",
                            headers={
                                'Accept': 'application/json'
                            }
                        )
                        # And this is also processed the same way as the original response
                        try:
                            return_response['uniProtID'] = response['uniProtkbId']
                        except:
                            print(traceback.format_exc())
                            return_response['uniProtID'] = ''
                        try:
                            return_response['uniProtAC'] = response['primaryAccession']
                        except:
                            print(traceback.format_exc())
                            return_response['uniProtAC'] = ''
                        try:
                            return_response['proteinName'] = (
                                response['proteinDescription']['recommendedName']['fullName']['value'] # Wow
                            )
                        except:
                            try:
                                return_response['proteinName'] = (
                                    response['proteinDescription']['submissionNames'][0]['fullName']['value'] # Wow
                                )
                            except:
                                print(traceback.format_exc())
                                return_response['proteinName'] = ''
                        try:
                            return_response['geneName'] = response['genes'][0]['geneName']['value']
                        except:
                            print(traceback.format_exc())
                            return_response['geneName'] = ''
                        try:
                            return_response['organism'] = (
                                f"{response['organism']['scientificName']} ({response['organism']['commonName']})"
                            )
                        except:
                            print(traceback.format_exc())
                            return_response['organism'] = ''
                        try:
                            return_response['sequenceLength'] = response['sequence']['length']
                        except:
                            print(traceback.format_exc())
                            return_response['sequenceLength'] = ''
                        try:
                            return_response['proteinFunction'] = ''.join(
                                i['texts'][0]['value'] for i in response['comments']
                                if 'FUNCTION' in i['commentType']
                            )
                        except:
                            print(traceback.format_exc())
                            return_response['proteinFunction'] = ''
                        try:
                            return_response['proteinSequence'] = response['sequence']['value']
                        except:
                            print(traceback.format_exc())
                            return_response['proteinSequence'] = ''

                # Otherwise just process as usual.
                else:
                    # Populate the dictionary with the values acquired from the API
                    try:
                        return_response['uniProtID'] = response['uniProtkbId']
                    except:
                        print(traceback.format_exc())
                        return_response['uniProtID'] = ''
                    try:
                        return_response['uniProtAC'] = response['primaryAccession']
                    except:
                        print(traceback.format_exc())
                        return_response['uniProtAC'] = ''
                    try:
                        return_response['proteinName'] = (
                            response['proteinDescription']['recommendedName']['fullName']['value'] # Wow
                        )
                    except:
                        try:
                            return_response['proteinName'] = (
                                response['proteinDescription']['submissionNames'][0]['fullName']['value'] # Wow
                            )
                        except:
                            print(traceback.format_exc())
                            return_response['proteinName'] = ''
                    try:
                        return_response['geneName'] = response['genes'][0]['geneName']['value']
                    except:
                        print(traceback.format_exc())
                        return_response['geneName'] = ''
                    try:
                        return_response['organism'] = (
                            f"{response['organism']['scientificName']} ({response['organism']['commonName']})"
                        )
                    except:
                        print(traceback.format_exc())
                        return_response['organism'] = ''
                    try:
                        return_response['sequenceLength'] = response['sequence']['length']
                    except:
                        print(traceback.format_exc())
                        return_response['sequenceLength'] = ''
                    try:
                        return_response['proteinFunction'] = ''.join(
                            i['texts'][0]['value'] for i in response['comments']
                            if 'FUNCTION' in i['commentType']
                        )
                    except:
                        print(traceback.format_exc())
                        return_response['proteinFunction'] = ''
                    try:
                        return_response['proteinSequence'] = response['sequence']['value']
                    except:
                        print(traceback.format_exc())
                        return_response['proteinSequence'] = ''
            except Exception as e:
                print(traceback.format_exc())
                return_response['message'] = f"Error: {e}"
    except Exception as e:
        print(traceback.format_exc())
        return_response['message'] = f"Error: {e}"

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
        df.to_csv('./temp.csv')
    elif format == "JSON":
        df.to_json('./temp.json')

    with open(f'./temp.{format.lower()}', 'rb') as f:
        raw_data = f.read()
    os.remove(f'./temp.{format.lower()}')
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

######## API CALLS ########

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
    options = [i.split('\\')[-1].split('.')[0] for i in glob.glob('./data/tables/*.json')]
    return {'ptms': options}

@app.get("/ptmkb/api/data")
async def get_data(request: Request, selection: str = None):
    if not selection:
        files = glob.glob('./data/tables/*.json')
        response = {}
        for file in files:
            with open(file, 'r', encoding='utf-8') as f:
                response[file.split('\\')[-1].split('.')[0]] = json.load(f)
        return response
    return FileResponse(
        './data/tables/{selection}.json'.format(
            selection=selection
        )
    )