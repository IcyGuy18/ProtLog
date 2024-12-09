from fastapi import FastAPI, Request, Body, Query
from fastapi.templating import Jinja2Templates
from starlette.responses import Response, FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.base import BaseHTTPMiddleware
import requests
import glob
import pandas as pd
import matplotlib.pyplot as plt
import os
import traceback
import json
from typing import Annotated

#### Comment whichever you want to use for the time being
#### Only use one at a time though
# from mongo_ptm import fetch_identifiers, search_identifier
from local_ptm import fetch_identifiers, search_identifier
from calculator import additive_calculator, multiplicative_calculator
from response_fetcher import fetch_response_uniprot_trim
from jpred_prediction import submit_job, get_job
from mdtraj_calculations import (
    create_file,
    get_secondary_structure,
    get_solvent_accessible_surface_area,
    get_protein_sequence
)

app = FastAPI(
    docs_url=None,
    redoc_url=None,
    title="PTMKB",
    version="1.0.0",
    swagger_ui_oauth2_redirect_url=None,
    redirect_slashes=False,
)
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

@app.get('/favicon.ico', include_in_schema=False)
async def favicon():
    return FileResponse('./icon-ptmkb.ico')

@app.get('/download_script', include_in_schema=False)
async def get_started_script():
    return FileResponse('./ptmkb_get_started.py')

@app.get('/picture', include_in_schema=False)
async def picture(picture: str):
    return FileResponse(f'./help/{picture}')

@app.get("/", include_in_schema=False)
def home_page(request: Request):
    return templates.TemplateResponse(
        "index.html", context={"request": request}
    )

@app.get("/search", include_in_schema=False)
def home_page(request: Request):
    return templates.TemplateResponse(
        "search.html", context={"request": request}
    )

@app.get("/propensity", include_in_schema=False)
def docs_page(request: Request):
    return templates.TemplateResponse(
        "propensity.html", context={"request": request}
    )


@app.get("/documentation", include_in_schema=False)
def docs_page(request: Request):
    return templates.TemplateResponse(
        "docs.html", context={"request": request}
    )

@app.get("/download", include_in_schema=False)
def download_page(request: Request):
    return templates.TemplateResponse(
        "download.html", context={"request": request}
    )

@app.get("/integration", include_in_schema=False)
def integration_page(request: Request):
    return templates.TemplateResponse(
        "integration.html", context={"request": request}
    )

@app.get("/about", include_in_schema=False)
def integration_page(request: Request):
    return templates.TemplateResponse(
        "about.html", context={"request": request}
    )

######## PAGE REQUESTS ########

@app.get('/ptmkb/protein_autofill', include_in_schema=False)
async def search(_id: str, request: Request):
    
    # Probably best to insert elements in a database
    ids = fetch_identifiers(_id)
    ids = sort_ids(ids, _id)
    # Give only top 200 suggestions - otherwise burden on user
    return {'ids': ids[:200]}

@app.post('/ptmkb/search_result', include_in_schema=False)
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
    if found:
        if not isinstance(results['Accession Number'], str):
            results['Accession Number'] = ''
    return {
        'found': found,
        'result': results,
        'html': html_page
    }

@app.post('/ptmkb/structure_calculations', include_in_schema=False)
async def get_structure_calculations(request: Request, data: dict = Body(...)):
    
    raw_bytes = data.get('raw_pdb_data', None)
    if data is None:
        return {'message': "Please submit a PDB file in bytes."}
    traj = create_file(raw_bytes.encode('utf-8'))
    response = dict()
    ss = get_secondary_structure(traj)
    sasa = get_solvent_accessible_surface_area(traj, 'residue')
    response.update(ss)
    response.update(sasa)
    response.update({
        'sequence': get_protein_sequence(traj)
    })
    return response


# I look at this function and cry every single night.
# This was the best I could do given the time constraint
# and my inability to do good frontend programming at all. 
@app.post('/ptmkb/fetch_uniprot', include_in_schema=False)
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

@app.post('/ptmkb/download', include_in_schema=False)
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
    aa = data.get('aa')
    table = data.get('table')
    format = data.get("format")
    rounded = True # data.get('rounded')

    df = pd.read_json(f"./data/tables/{ptm}/{table}/{aa}.json")
    
    if rounded and format in ["PNG", "PDF", "SVG"]: df = df.round(2)
    
    # Check format
    raw_data = save_image(df, format, ptm) if format in ["PNG", "PDF", "SVG"] else save_data(df, format)

    return Response(
        content=raw_data,
        media_type=return_header[format]
    )

# This function is a separate call
@app.post('/ptmkb/get_protein_log', include_in_schema=False)
async def get_log_value(request: Request):
    
    data: dict = await request.json()
    data = dict(sorted(data.items(), key=lambda item: int(item[0])))
    vector = list(data.values())
    # Use the above vector to calculate additive and multiplicative scores
    a_score, m_scores = additive_calculator(vector), multiplicative_calculator(vector)
    m_score = m_scores[1]['multiplicative_score']
    asterisk_m_score = m_scores[1]['logLogProduct']
    return {
        'logSum': round(a_score, 3) if not isinstance(a_score, str) else a_score,
        'logLogProduct': round(asterisk_m_score, 3) if not isinstance(asterisk_m_score, str) else asterisk_m_score
    }

@app.get('/ptmkb/getAminoAcids', include_in_schema=False)
def get_amino_acids(request: Request, ptm: str):
    
    if not ptm:
        return {
            'response': False,
            'message': "No PTM was provided."
        }
    data = [i.split("\\")[-1].split('.')[0] for i in glob.glob(f'./data/tables/{ptm}/log-e/*.json')]
    return {
        'response': True,
        'data': data
    }

@app.get('/ptmkb/getPTM', include_in_schema=False)
async def get_ptm_details(request: Request, resid: str = None, ptm: str = None, aa: str = None):
    
    # Read the file initially
    with open('./data/resid/residues.json', 'r') as f:
        entries = json.load(f)['Database']['Entry']
    # Check whether RESID ID or both PTM and Residue are given.
    # Both will be handled differently.
    entry = None
    if resid:
        resid = resid.upper()
        entry = [entry for entry in entries if entry['@id'] == resid]
        # If caught entry,
        if entry:
            _id = entry[0]['@id']
            # going to send image and model files as raw data.
            with open(
                f"./data/resid/images/{_id}.GIF", 'rb'
            ) as f:
                entry[0]['Image'] = {}
                entry[0]['Image']['Data'] = f.read().decode('latin-1')
                entry[0]['Image']['Encoding'] = 'latin-1'
                entry[0]['Image']['FileType'] = '.GIF'
            with open(
                f"./data/resid/models/{_id}.PDB", 'rb'
            ) as f:
                entry[0]['Model'] = {}
                entry[0]['Model']['Data'] = f.read().decode()
                entry[0]['Model']['Encoding'] = 'utf-8'
                entry[0]['Model']['FileType'] = '.PDB'

    elif (ptm and aa):
        aa = aa.upper()
        entry = [
            entry for entry in entries
            if entry.get('PTM', None) == ptm and (
                (
                    isinstance(entry.get('AminoAcid', None), str) and
                    entry.get('AminoAcid', None) == aa
                ) or
                (
                    isinstance(entry.get('AminoAcid', None), list) and
                    aa in entry.get('AminoAcid', None)
                )
            )
        ]
        if entry:
            for i in range(len(entry)):
                _id = entry[i]['@id']
                # going to send image and model files as raw data.
                with open(
                    f"./data/resid/images/{_id}.GIF", 'rb'
                ) as f:
                    entry[i]['Image'] = {}
                    entry[i]['Image']['Data'] = f.read().decode('latin-1')
                    entry[i]['Image']['Encoding'] = 'latin-1'
                    entry[i]['Image']['FileType'] = '.GIF'
                with open(
                    f"./data/resid/models/{_id}.PDB", 'rb'
                ) as f:
                    entry[i]['Model'] = {}
                    entry[i]['Model']['Data'] = f.read().decode()
                    entry[i]['Model']['Encoding'] = 'utf-8'
                    entry[i]['Model']['FileType'] = '.PDB'
    else:
        return {'message': "Please enter either a RESID ID or a PTM name along with a residue!"}

    return {'response': entry}


######## API CALLS ########

@app.post('/ptmkb/unrel/submitJpred', include_in_schema=False)
async def get_jpred_prediction(request: Request):
    info = await request.json()
    return await submit_job(info['sequence'])

@app.get('/ptmkb/unrel/getJpred', include_in_schema=False)
def get_jpred_prediction(request: Request, jobid: str):
    return get_job(jobid)

@app.get('/ptmkb/api/get-ptm-details', responses={
    200: {
        "description": "Success",
        "content": {
            "application/json": {
                "example": {
                    "AA0039": {
                        "@id": "AA0039",
                        "PTM": "Phosphorylation",
                        "AminoAcid": "Y",
                        "Header": {
                            "Code": "AA0039",
                            "Dates": {
                                "CreationDate": "31-Mar-1995",
                                "StrucRevDate": "31-Mar-1995",
                                "TextChngDate": "31-Dec-2011"
                            }
                        },
                        "Names": {
                            "Name": "O4'-phospho-L-tyrosine",
                            "AlternateName": [
                                "2-amino-3-(4-hydroxyphenyl)propanoic acid 4'-phosphate",
                                "2-azanyl-3-(4-phosphonooxyphenyl)propanoic acid",
                                "O4-phosphotyrosine",
                                "tyrosine phosphate"
                            ],
                            "SystematicName": "(2S)-2-amino-3-(4-phosphonooxyphenyl)propanoic acid",
                            "Xref": [
                                "CAS:21820-51-9",
                                "ChEBI:61972",
                                "PDBHET:PTR"
                            ]
                        },
                        "FormulaBlock": {
                            "Formula": "C 9 H 10 N 1 O 5 P 1",
                            "Weight": [
                                {
                                    "@type": "chemical",
                                    "#text": "243.15"
                                },
                                {
                                    "@type": "physical",
                                    "#text": "243.029659"
                                }
                            ]
                        },
                        "CorrectionBlock": {
                            "@uids": "AA0019",
                            "Formula": "C 0 H 1 N 0 O 3 P 1",
                            "Weight": [
                                {
                                    "@type": "chemical",
                                    "#text": "79.98"
                                },
                                {
                                    "@type": "physical",
                                    "#text": "79.966331"
                                }
                            ]
                        },
                        "ReferenceBlock": [
                        {
                            "Authors": {
                                "Author": [
                                    "Aebersold, R.",
                                    "Watts, J.D.",
                                    "Morrison, H.D.",
                                    "Bures, E.J."
                                ]
                            },
                            "Citation": "Anal. Biochem. 199, 51-60, 1991",
                            "Title": "Determination of the site of tyrosine phosphorylation at the low picomole level by automated solid-phase sequence analysis.",
                            "Xref": [
                                "DOI:10.1016/0003-2697(91)90268-X",
                                "PMID:1725475"
                            ],
                            "Note": "chromatographic detection"
                        },
                        {
                            "Authors": {
                                "Author": [
                                    "Wolfender, J.L.",
                                    "Chu, F.",
                                    "Ball, H.",
                                    "Wolfender, F.",
                                    "Fainzilber, M.",
                                    "Baldwin, M.A.",
                                    "Burlingame, A.L."
                                ]
                            },
                            "Citation": "J. Mass Spectrom. 34, 447-454, 1999",
                            "Title": "Identification of tyrosine sulfation in Conus pennaceus conotoxins alpha-PnIA and alpha-PnIB: further investigation of labile sulfo- and phosphopeptides by electrospray, matrix-assisted laser desorption/ionization (MALDI) and atmospheric pressure MALDI mass spectrometry.",
                            "Xref": [
                                "DOI:10.1002/(SICI)1096-9888(199904)34:4<447::AID-JMS801>3.3.CO;2-T",
                                "PMID:10226369"
                            ],
                            "Note": "attempt to distinguish between the essentially isobaric protonated forms of phosphotyrosine and sulfotyrosine (see RESID:AA0172) by negative ion mode MALDI"
                        }
                        ],
                        "GeneratingEnzyme": {
                            "EnzymeName": "protein-tyrosine kinase (EC 2.7.1.112)"
                        },
                        "SequenceCode": {
                            "SequenceSpec": "Y",
                            "Xref": [
                                "GO:0018108",
                                "GO:0018334",
                                "PSI-MOD:00048"
                            ]
                        },
                        "Source": "natural",
                        "Keywords": {
                            "Keyword": "phosphoprotein"
                        },
                        "Features": {
                            "Feature": {
                                "@type": "UniProt",
                                "@key": "mod_res__phosphotyrosine__y",
                                "#text": "MOD_RES Phosphotyrosine"
                            }
                        }
                    }
                }
            }
        }
    }
})
def get_post_translational_modification_details(
    request: Request,
    resid: str = Query('', description='The RESID Database ID to use.', example='AA0039')
):
    """
    Get information on a Post-Translational Modification using RESID ID.

    **Returns:**
    - Detailed information on a Post-Translational Modification. (type: *JSON*)
    """

    # Let's do some input validation first.
    resid = resid.upper().strip() # And that's about it.

    # We can read the file per operation since it's not a large file
    # (only barely 3 megabytes)
    with open('./data/resid/residues.json', 'r') as f:
        entries = json.load(f)['Database']['Entry']
        entries = [_id for _id in entries if _id['@id'] == resid]

    # We also have to include raw bytes of PDB and image
    for i in range(len(entries)):
        _id = entries[i]["@id"]
        with open(
            f"./data/resid/images/{_id}.GIF", 'rb'
        ) as f:
            entries[i]['Image'] = {}
            entries[i]['Image']['Data'] = f.read().decode('latin-1')
            entries[i]['Image']['Encoding'] = 'latin-1'
            entries[i]['Image']['FileType'] = '.GIF'
        with open(
            f"./data/resid/models/{_id}.PDB", 'rb'
        ) as f:
            entries[i]['Model'] = {}
            entries[i]['Model']['Data'] = f.read().decode()
            entries[i]['Model']['Encoding'] = 'utf-8'
            entries[i]['Model']['FileType'] = '.PDB'
    if entries:
        return {resid: entries[0]}
    return {'message': 'Please provide a valid RESID Database ID.'}


@app.get("/ptmkb/api/get-protein-details", responses={
    200: {
        "description": "Success",
        "content": {
            "application/json": {
                "example": {
                    "result": [
                        {
                            "Protein Identifier": "TERT_HUMAN",
                            "Accession Number": "O14746",
                            "PTMs": [
                                [
                                    1059,
                                    "Acetylation",
                                    "30592905"
                                ],
                                [
                                    227,
                                    "Phosphorylation",
                                    "22366458;30395287;22817900;10224060"
                                ],
                                [
                                    349,
                                    "Phosphorylation",
                                    "25954137;30301811;22964224;17081983"
                                ],
                                [
                                    353,
                                    "Phosphorylation",
                                    "24719451"
                                ],
                                [
                                    457,
                                    "Phosphorylation",
                                    "30395287;23362280"
                                ],
                                [
                                    707,
                                    "Phosphorylation",
                                    "16627250;19147845;30395287;17392301;16247010;19760749;12808100;18042801;17460043;15814878;14654914;23362280;9443919;15082768;17264120;12869302;15857955;16990594;16332973;22512499;17785587;15885610;17296728;20211239;19777057;22817900;21483807;9389643;21436073;21602826;17026956;18829466"
                                ],
                                [
                                    797,
                                    "Phosphorylation",
                                    "16565220"
                                ],
                                [
                                    824,
                                    "Phosphorylation",
                                    "22817900;10224060"
                                ],
                                [
                                    1101,
                                    "Phosphorylation",
                                    "16094384"
                                ],
                                [
                                    1113,
                                    "Phosphorylation",
                                    "16094384;22817900"
                                ],
                                [
                                    1125,
                                    "Phosphorylation",
                                    "16094384;22817900"
                                ],
                                [
                                    679,
                                    "Phosphorylation",
                                    "27251275"
                                ],
                                [
                                    692,
                                    "Phosphorylation",
                                    "27251275"
                                ],
                                [
                                    1045,
                                    "Phosphorylation",
                                    "24719451"
                                ],
                                [
                                    1095,
                                    "Phosphorylation",
                                    "24719451"
                                ],
                                [
                                    283,
                                    "Phosphorylation",
                                    "22210691"
                                ],
                                [
                                    284,
                                    "Phosphorylation",
                                    "22210691"
                                ],
                                [
                                    344,
                                    "Phosphorylation",
                                    "30622161"
                                ],
                                [
                                    348,
                                    "Phosphorylation",
                                    "17081983;30301811;24719451;30622161"
                                ],
                                [
                                    480,
                                    "Phosphorylation",
                                    "24719451"
                                ],
                                [
                                    618,
                                    "Phosphorylation",
                                    "24719451"
                                ],
                                [
                                    731,
                                    "Phosphorylation",
                                    "24719451"
                                ],
                                [
                                    707,
                                    "Phosphorylation",
                                    "12808100"
                                ]
                            ]
                        }
                    ]
                }
            }
        }
    }
})
def get_protein_details(
    upid: str = Query(None, description='UniProt Protein Identifier', example='AF9_HUMAN'),
    upac: str = Query(None, description='UniProt Accession Number', example='O14746')
):
    """
    Get the details of a protein and its Post-Translational Modifications (PTMs),
    given a UniProt Protein Identifier or Accession Number.

    *Note that if both parameters are supplied, the UniProt Protein Identifier will take precedence over the Accession Number.*

    **Returns:**
    - Detailed Post-Translational Modification details of a protein. (type: *JSON*)
    """

    if not upid and not upac:
        return {'result': '', 'message': 'Please enter a protein identifier or an accession number first!'}
    _id = upid or upac
    _id = _id.upper()
    found, results = search_identifier(_id)
    if found:
        return {'result': results}
    return {'message': 'Could not find the queried protein!'}

@app.get("/ptmkb/api/get-available-ptms", responses={
    200: {
        "description": "Success",
        "content": {
            "application/json": {
                "example": {
                    "ptms": [
                        "Acetylation",
                        "ADP-ribosylation",
                        "Amidation",
                        "AMPylation",
                        "Biotinylation",
                        "Blocked amino end",
                        "Butyrylation",
                        "C-linked Glycosylation",
                        "Carbamidation",
                        "Carboxyethylation",
                        "Carboxylation",
                        "Cholesterol ester",
                        "Citrullination",
                        "Crotonylation",
                        "D-glucuronoylation",
                        "Deamidation",
                        "Deamination",
                        "Decanoylation",
                        "Decarboxylation",
                        "Dephosphorylation",
                        "Disulfide bond",
                        "Farnesylation",
                        "Formation of an isopeptide bond",
                        "Formylation",
                        "Gamma-carboxyglutamic acid",
                        "Geranylgeranylation",
                        "Glutarylation",
                        "Glutathionylation",
                        "GPI-anchor",
                        "Hydroxyceramide ester",
                        "Hydroxylation",
                        "Iodination",
                        "Lactoylation",
                        "Lactylation",
                        "Lipoylation",
                        "Malonylation",
                        "Methylation",
                        "Myristoylation",
                        "N-carbamoylation",
                        "N-linked Glycosylation",
                        "N-palmitoylation",
                        "Neddylation",
                        "Nitration",
                        "O-linked Glycosylation",
                        "O-palmitoleoylation",
                        "O-palmitoylation",
                        "Octanoylation",
                        "Oxidation",
                        "Phosphatidylethanolamine amidation",
                        "Phosphorylation",
                        "Propionylation",
                        "Pyrrolidone carboxylic acid",
                        "Pyrrolylation",
                        "Pyruvate",
                        "S-archaeol",
                        "S-carbamoylation",
                        "S-Cyanation",
                        "S-cysteinylation",
                        "S-diacylglycerol",
                        "S-linked Glycosylation",
                        "S-nitrosylation",
                        "S-palmitoylation",
                        "Serotonylation",
                        "Stearoylation",
                        "Succinylation",
                        "Sulfation",
                        "Sulfhydration",
                        "Sulfoxidation",
                        "Sumoylation",
                        "Thiocarboxylation",
                        "Ubiquitination",
                        "UMPylation"
                    ]
                }
            }
        }
    }
})
async def get_available_post_translational_modifications():
    """
    Get a list of available Post-Translational Modifications (PTMs) in the database.

    **Returns:**
    - A list of available PTMs paired with a key. (type: *JSON*)
    """

    options = [i.split("\\")[-1] for i in glob.glob(r'data\tables\*')]
    return {'ptms': options}

@app.get("/ptmkb/api/get-positional-frequency-matrix", responses={
    200: {
        "description": "Success",
        "content": {
            "application/json": {
                "example": {
                    "-10": {
                        "A": 0.07007255857134956,
                        "C": 0.009577767683828496,
                        "D": 0.052707641452041806,
                        "E": 0.07040710952509177,
                        "F": 0.02385647492091814,
                        "G": 0.06497178982946968,
                        "H": 0.021027751409601884,
                        "I": 0.033014467288804514,
                        "K": 0.07115146273111442,
                        "L": 0.06983139175916683,
                        "M": 0.018719440492995735,
                        "N": 0.04155684963611917,
                        "P": 0.07334463009453558,
                        "Q": 0.04200563750089531,
                        "R": 0.0679065904724603,
                        "S": 0.11648357028425951,
                        "T": 0.05360249725514089,
                        "V": 0.047556100749702394,
                        "W": 0.006309322729246734,
                        "Y": 0.017888956282622118
                    },
                    "-9": {
                        "A": 0.07052225307827677,
                        "C": 0.009749123050379385,
                        "D": 0.05235767758173152,
                        "E": 0.06948505445746081,
                        "F": 0.023708692250294885,
                        "G": 0.06556745372271801,
                        "H": 0.021381341848516415,
                        "I": 0.032743381285636704,
                        "K": 0.07189853586359025,
                        "L": 0.07030012575126635,
                        "M": 0.019313291101941937,
                        "N": 0.0409720654486836,
                        "P": 0.07281333779401272,
                        "Q": 0.0415414367195511,
                        "R": 0.06997010800827945,
                        "S": 0.11731405449463313,
                        "T": 0.05393160835597672,
                        "V": 0.04772654947410222,
                        "W": 0.006002877682187473,
                        "Y": 0.017927941895117823
                    },
                    "-8": {
                        "A": 0.07018044898732605,
                        "C": 0.010220576968932093,
                        "D": 0.052466474639859075,
                        "E": 0.06824295471050462,
                        "F": 0.024043243204037095,
                        "G": 0.06484304664401874,
                        "H": 0.021530031161290732,
                        "I": 0.033403416771610496,
                        "K": 0.07079152579714244,
                        "L": 0.07134095094068657,
                        "M": 0.01926977227869092,
                        "N": 0.04118875292278763,
                        "P": 0.07345433379481418,
                        "Q": 0.04193310612881028,
                        "R": 0.07024119401144727,
                        "S": 0.11962055212693716,
                        "T": 0.053910755586502275,
                        "V": 0.047905157977861615,
                        "W": 0.005574942586885784,
                        "Y": 0.01804217880615175
                    },
                    "-7": {
                        "A": 0.07103359925147625,
                        "C": 0.008922265408610018,
                        "D": 0.053416635614172994,
                        "E": 0.06937353747288007,
                        "F": 0.023239051616044303,
                        "G": 0.0669827221205272,
                        "H": 0.021218146261325094,
                        "I": 0.03172703543429519,
                        "K": 0.07246881377660881,
                        "L": 0.06893109610316137,
                        "M": 0.018507286229647018,
                        "N": 0.04116336694255787,
                        "P": 0.07504367748562746,
                        "Q": 0.041364641500093835,
                        "R": 0.07198557351009228,
                        "S": 0.12096056922620813,
                        "T": 0.054233520192280664,
                        "V": 0.047084646831149685,
                        "W": 0.005699152561581402,
                        "Y": 0.017687681725086155
                    },
                    "-6": {
                        "A": 0.07094474832067207,
                        "C": 0.008871493448150495,
                        "D": 0.053335944462728394,
                        "E": 0.06901269389675703,
                        "F": 0.023887300754054278,
                        "G": 0.06688933797896772,
                        "H": 0.02062701557883208,
                        "I": 0.03364549022594429,
                        "K": 0.06873254147207859,
                        "L": 0.07171086093832023,
                        "M": 0.018743919831074433,
                        "N": 0.04092763998328152,
                        "P": 0.07449334569993227,
                        "Q": 0.03995753288164421,
                        "R": 0.07226663257692179,
                        "S": 0.12368321560585002,
                        "T": 0.054693187762869556,
                        "V": 0.04847362260657805,
                        "W": 0.005162420408152163,
                        "Y": 0.018004099835807107
                    },
                    "-5": {
                        "A": 0.06904351972989317,
                        "C": 0.008668405606312405,
                        "D": 0.05327519943860718,
                        "E": 0.0663009272229279,
                        "F": 0.026143026425898778,
                        "G": 0.06357374763253068,
                        "H": 0.02232606296992396,
                        "I": 0.03575615315361873,
                        "K": 0.06381491444471342,
                        "L": 0.08418716357909682,
                        "M": 0.020795651018929783,
                        "N": 0.039988358714780355,
                        "P": 0.07352142531399285,
                        "Q": 0.03861751578237325,
                        "R": 0.0731288492625826,
                        "S": 0.12072574890908283,
                        "T": 0.053960620904810734,
                        "V": 0.04922976216056451,
                        "W": 0.0055549964595624,
                        "Y": 0.018309638240715305
                    },
                    "-4": {
                        "A": 0.07033185822655355,
                        "C": 0.00815433950665974,
                        "D": 0.05523626641135624,
                        "E": 0.07072896748871911,
                        "F": 0.02357269592763545,
                        "G": 0.06762009155272442,
                        "H": 0.020659654696270346,
                        "I": 0.0314115239657253,
                        "K": 0.06563545188404772,
                        "L": 0.06730639336845665,
                        "M": 0.01756075182393735,
                        "N": 0.041588582111406376,
                        "P": 0.0722004476998942,
                        "Q": 0.0419349194131124,
                        "R": 0.06821575544597275,
                        "S": 0.14167371580939117,
                        "T": 0.05646204659959328,
                        "V": 0.04719072396282405,
                        "W": 0.0051170883005990184,
                        "Y": 0.01699319383737197
                    },
                    "-3": {
                        "A": 0.06457830713590838,
                        "C": 0.007356494413724386,
                        "D": 0.055628842462766476,
                        "E": 0.06396360375748773,
                        "F": 0.021507365107514158,
                        "G": 0.06684309922926351,
                        "H": 0.021838289492652117,
                        "I": 0.029207476896491384,
                        "K": 0.0662102630078216,
                        "L": 0.0685956385072681,
                        "M": 0.01690887611732312,
                        "N": 0.0358595103588399,
                        "P": 0.0698322984013179,
                        "Q": 0.036587544006143405,
                        "R": 0.11634304075084477,
                        "S": 0.13710877257878948,
                        "T": 0.05181913214400016,
                        "V": 0.04165204706198078,
                        "W": 0.004362762030914684,
                        "Y": 0.01609652474997076
                    },
                    "-2": {
                        "A": 0.07145881442032474,
                        "C": 0.009142579451318304,
                        "D": 0.05264961635437378,
                        "E": 0.0616425998507667,
                        "F": 0.022318809832715458,
                        "G": 0.06268795825094223,
                        "H": 0.019630615854813953,
                        "I": 0.03286940454463445,
                        "K": 0.04975108139742568,
                        "L": 0.07009794455157932,
                        "M": 0.017943354811685894,
                        "N": 0.04351157011381079,
                        "P": 0.07818337925475828,
                        "Q": 0.039904947636882564,
                        "R": 0.07356857070584812,
                        "S": 0.15979205255623222,
                        "T": 0.05939956716903708,
                        "V": 0.04935397213526013,
                        "W": 0.0045513435983357674,
                        "Y": 0.01675837352024668
                    },
                    "-1": {
                        "A": 0.0731170629146188,
                        "C": 0.00906642151062902,
                        "D": 0.06459462669462751,
                        "E": 0.05766334744975163,
                        "F": 0.02615934598461791,
                        "G": 0.08251078224178152,
                        "H": 0.02433518197667935,
                        "I": 0.03359199833903158,
                        "K": 0.0489686492210584,
                        "L": 0.08039377281904964,
                        "M": 0.019602509948131,
                        "N": 0.04361039410827665,
                        "P": 0.07836833425357512,
                        "Q": 0.03539802950394888,
                        "R": 0.06200616335334293,
                        "S": 0.13748956228223588,
                        "T": 0.052233467607035906,
                        "V": 0.04796862292843602,
                        "W": 0.0044153472756763325,
                        "Y": 0.018490966670927884
                    },
                    "0": {
                        "A": 0.0,
                        "C": 0.0,
                        "D": 0.0,
                        "E": 0.0,
                        "F": 0.0,
                        "G": 0.0,
                        "H": 0.0,
                        "I": 0.0,
                        "K": 0.0,
                        "L": 0.0,
                        "M": 0.0,
                        "N": 0.0,
                        "P": 0.0,
                        "Q": 0.0,
                        "R": 0.0,
                        "S": 1.0,
                        "T": 0.0,
                        "V": 0.0,
                        "W": 0.0,
                        "Y": 0.0
                    },
                    "+1": {
                        "A": 0.05490534202621828,
                        "C": 0.007468918040456186,
                        "D": 0.06766361037597543,
                        "E": 0.0628375542058676,
                        "F": 0.033640957015188974,
                        "G": 0.061012483555777985,
                        "H": 0.015058419487003738,
                        "I": 0.0340534791939226,
                        "K": 0.03329371307133189,
                        "L": 0.08112724631925952,
                        "M": 0.015056606202701613,
                        "N": 0.03198905501595237,
                        "P": 0.17596836181549652,
                        "Q": 0.03636994988988831,
                        "R": 0.04214888696076325,
                        "S": 0.13044948597923245,
                        "T": 0.048158111138008164,
                        "V": 0.04633576041437173,
                        "W": 0.005535050332239016,
                        "Y": 0.015360331323307684
                    },
                    "+2": {
                        "A": 0.0634096454031883,
                        "C": 0.008140739874393796,
                        "D": 0.07143614836654817,
                        "E": 0.08419532335845639,
                        "F": 0.02093527391019347,
                        "G": 0.06940345666386515,
                        "H": 0.018296945250600424,
                        "I": 0.03424478068779687,
                        "K": 0.0488217731925862,
                        "L": 0.06897733485286558,
                        "M": 0.012977675750314378,
                        "N": 0.03836909583298201,
                        "P": 0.08564051094725066,
                        "Q": 0.03496374791358975,
                        "R": 0.05228514620964649,
                        "S": 0.1537900815161958,
                        "T": 0.06087104738021217,
                        "V": 0.04918443005301137,
                        "W": 0.003611155687683538,
                        "Y": 0.015325878921567294
                    },
                    "+3": {
                        "A": 0.06517850423991202,
                        "C": 0.007871467155528115,
                        "D": 0.06987309729811572,
                        "E": 0.09477311733490726,
                        "F": 0.023396807350329247,
                        "G": 0.07053675935269377,
                        "H": 0.020493739182625835,
                        "I": 0.02938336547379759,
                        "K": 0.05711482894835857,
                        "L": 0.06599448217586863,
                        "M": 0.013650404226403052,
                        "N": 0.04357956827514051,
                        "P": 0.07645078610407707,
                        "Q": 0.038047237869354676,
                        "R": 0.05992813954310675,
                        "S": 0.13845241624666468,
                        "T": 0.05231234547417838,
                        "V": 0.04398211739021243,
                        "W": 0.004844189013129085,
                        "Y": 0.01673117425571479
                    },
                    "+4": {
                        "A": 0.06684763244001882,
                        "C": 0.0078107221314069,
                        "D": 0.062273622787906484,
                        "E": 0.0776475537434801,
                        "F": 0.02402239043456265,
                        "G": 0.06404701483538552,
                        "H": 0.019353183356588706,
                        "I": 0.03690486875901542,
                        "K": 0.05810306889301713,
                        "L": 0.08147811683172088,
                        "M": 0.015873490780809286,
                        "N": 0.03940085460089159,
                        "P": 0.07271723372600004,
                        "Q": 0.03810979617777802,
                        "R": 0.057757638233462166,
                        "S": 0.13849412178561357,
                        "T": 0.058000618329947025,
                        "V": 0.049061126720466815,
                        "W": 0.005087169109613943,
                        "Y": 0.016912502685927373
                    },
                    "+5": {
                        "A": 0.06909247840605057,
                        "C": 0.008539662420861474,
                        "D": 0.06308053430235247,
                        "E": 0.07784157516380757,
                        "F": 0.023870981195335143,
                        "G": 0.06467259791961892,
                        "H": 0.021081243296514597,
                        "I": 0.03361285110850602,
                        "K": 0.06112672046681191,
                        "L": 0.07073984719453186,
                        "M": 0.015500860856722434,
                        "N": 0.04107179608530052,
                        "P": 0.08279274795076208,
                        "Q": 0.040810683145794405,
                        "R": 0.06342505831975637,
                        "S": 0.12201499404789427,
                        "T": 0.056001472386853324,
                        "V": 0.04863772483592044,
                        "W": 0.0053972407252774555,
                        "Y": 0.017940634885232704
                    },
                    "+6": {
                        "A": 0.07049505381374488,
                        "C": 0.008905945849890885,
                        "D": 0.05860806857115917,
                        "E": 0.0757463251527012,
                        "F": 0.024692398984198134,
                        "G": 0.06500170902045475,
                        "H": 0.0204701664866982,
                        "I": 0.0342221146340203,
                        "K": 0.06500533558905901,
                        "L": 0.07093477525701039,
                        "M": 0.015467315097133108,
                        "N": 0.039933053543565515,
                        "P": 0.07486144241326381,
                        "Q": 0.0406765001074371,
                        "R": 0.06412861262898117,
                        "S": 0.1234610882788396,
                        "T": 0.057890914629668416,
                        "V": 0.05067222982290559,
                        "W": 0.005540490185145393,
                        "Y": 0.017869916797449797
                    },
                    "+7": {
                        "A": 0.07010157112018357,
                        "C": 0.009086367637952402,
                        "D": 0.05911125496499908,
                        "E": 0.07611895507678805,
                        "F": 0.024230918129307118,
                        "G": 0.06463542559142534,
                        "H": 0.021037724473263575,
                        "I": 0.03371983488233145,
                        "K": 0.06668171692637431,
                        "L": 0.0711151970450719,
                        "M": 0.01556795237590109,
                        "N": 0.04083697576817523,
                        "P": 0.0747834711882724,
                        "Q": 0.04070732594057323,
                        "R": 0.0660271212933069,
                        "S": 0.1198417728117965,
                        "T": 0.05502501879015858,
                        "V": 0.04887889164810317,
                        "W": 0.005742671384832421,
                        "Y": 0.018506379587495955
                    },
                    "+8": {
                        "A": 0.06963918362314149,
                        "C": 0.009273135921071362,
                        "D": 0.05708309647307137,
                        "E": 0.07435462945081965,
                        "F": 0.024506537343230238,
                        "G": 0.06495728355505268,
                        "H": 0.020883595307582884,
                        "I": 0.03453218624968381,
                        "K": 0.06744873618617353,
                        "L": 0.07112426346658253,
                        "M": 0.015429236126788466,
                        "N": 0.0404099473150246,
                        "P": 0.07332196404075901,
                        "Q": 0.04113526103587492,
                        "R": 0.06514133191171843,
                        "S": 0.11952263477462235,
                        "T": 0.056122962435095756,
                        "V": 0.049968675513680776,
                        "W": 0.005957545574634329,
                        "Y": 0.01797146071836884
                    },
                    "+9": {
                        "A": 0.07011245082599633,
                        "C": 0.009456277635586067,
                        "D": 0.05532058413140509,
                        "E": 0.07392669435551796,
                        "F": 0.02466247979321306,
                        "G": 0.0640742140999174,
                        "H": 0.021025031483148694,
                        "I": 0.033952841915154616,
                        "K": 0.06951769357489906,
                        "L": 0.07035633756463225,
                        "M": 0.015455528749169289,
                        "N": 0.0404661591283905,
                        "P": 0.07382333715029679,
                        "Q": 0.041214138903017394,
                        "R": 0.06754030704343088,
                        "S": 0.11660868690110619,
                        "T": 0.05527162545524769,
                        "V": 0.048586952875460915,
                        "W": 0.0061334341519405314,
                        "Y": 0.018229853731421768
                    },
                    "+10": {
                        "A": 0.06999730727281134,
                        "C": 0.009783575452119775,
                        "D": 0.055673267928168554,
                        "E": 0.07366104820525653,
                        "F": 0.02486556763505115,
                        "G": 0.06447132336208296,
                        "H": 0.020946153616006224,
                        "I": 0.03400089394916095,
                        "K": 0.06946692161443954,
                        "L": 0.06969358215220527,
                        "M": 0.015604218061943604,
                        "N": 0.04037005506037784,
                        "P": 0.07229292519930261,
                        "Q": 0.04129120348585774,
                        "R": 0.06610781244475149,
                        "S": 0.11597494403751323,
                        "T": 0.05529157158257107,
                        "V": 0.04924154850852833,
                        "W": 0.005951199079576888,
                        "Y": 0.018191774761077126
                    }
                }
            }
        },
    }
})
async def get_positional_frequency_matrix(
    ptm: str = Query('', description='The dbPTM-annotated Post-Translational Modification.', example='Phosphorylation'),
    residue: str = Query('', description='The amino acid for which the table is required.', example='S'),
    table: str = Query('log-e', description='The type of matrix required. Accepted values are \'freq\' and \'log-e\'.', example='freq')
):
    """
    Get the positional frequency matrix of a Post-Translational Modification (PTM),
    given the PTM, amino acid, and the matrix table type.

    If nothing is provided, all available natural log matrices for all PTMs on all residues will be supplied.

    If only the PTM is provided, all available natural log matrices for that PTM on all residues will be supplied.

    If the table is not provided or is any value other than 'freq' or 'log-e', it will default to 'log-e' and subsequently return the natural log matrix for the specified PTM on the specified residue.

    **Returns:**
    - The Positional Frequency Matrix of the Post-Translational Modification for the specified amino acid. (type: *JSON*)
    """
    
    if not ptm:
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
    elif not residue:
        response = {ptm: []}
        AAs = [i.split("\\")[-1].split('.')[0] for i in glob.glob(f'data/tables/{ptm}/log-e/*.json')]
        for aa in AAs:
            with open(f"data/tables/{ptm}/log-e/{aa}.json", 'r', encoding='utf-8') as f:
                response[ptm].append(
                    {
                        aa: json.load(f)
                    }
                )
    elif table not in ['log-e', 'log2', 'freq']:
        if not os.path.exists(f'./data/tables/{ptm}/log-e/{residue}.json'):
            return {'message': f"Could not find matrix of positional frequency of {ptm} for {residue}."}
        return FileResponse(
            './data/tables/{selection}/log-e/{residue}.json'.format(
                selection=ptm, residue=residue
            )
        )
    else:
        if not os.path.exists(f'./data/tables/{ptm}/{table}/{residue}.json'):
            return {'message': f"Could not find the {table}-based matrix of positional frequency of {ptm} for {residue}."}
        return FileResponse(
            './data/tables/{selection}/{table}/{residue}.json'.format(
                selection=ptm, residue=residue, table=table
            )
        )

@app.get('/ptmkb/api/calculate-propensity', responses={
    200: {
        "description": "Success",
        "content": {
            "application/json": {
                "example": {
                    "logSum": -60.2164362825967,
                    "logLogProduct": -21.3580873581939
                }
            }
        },
    }
})
async def calculate_propensity(
    ptm: str = Query('', description='The dbPTM-annotated Post-Translational Modification.', example='Phosphorylation'),
    subsequence: str = Query('', description='The subsequence to use for calculation. The PTM site will be automatically derived from the sequence.', example='WKLLPENNVLSPLPSQAMDDW')
) -> dict:
    """
    Calculate the Propensity of a residue for a Post-Translational Modification.

    **Returns:**
    - The Log Sum and Log Log Product scores. (type: *JSON*)
    """
    if ptm is None or subsequence is None:
        return {
            'message': "Please provide both the subsequence and the PTM to use for Propensity calculation."
        }
    if not isinstance(ptm, str):
        return {
            'message': "Please ensure that the Post-Translational Modification input is a string."
        }
    if not isinstance(subsequence, str):
        return {
            'message': "Please ensure that the Subsequence input is a string."
        }
    if len(subsequence) < 13 or len(subsequence) > 21:
        return {
            'message': f"Please ensure that the length of the subsequence is at leats 13 residues long."
        }
    if len(subsequence) % 2 != 1:
        return {
            'message': f"Please ensure that the window size of the subsequence is either 13, 15, 17, 19, or 21 (current length is {len(subsequence)})."
        }
    char = subsequence[len(subsequence) // 2]
    if not os.path.exists(f'./data/tables/{ptm}'):
        return {
            'message': f"No such Post-Translational Modification by the name of {ptm} exists."
        }
    if not os.path.exists(f'./data/tables/{ptm}/log-e/{char}.json'):
        return {
            'message': f"No such propensity calculator exists for {ptm} of residue {char}."
        }
    
    # With all input validation done, proceed with the calculation.
    with open(f'./data/tables/{ptm}/log-e/{char}.json', 'r') as f:
        table: dict[str, dict[str, int|str]] = json.load(f)

    KEYS = []

    for i in range(-(len(subsequence) // 2), (len(subsequence) // 2) + 1):
        key = f"+{i}" if i > 0 else str(i)
        KEYS.append(key)

    vector = []
    for index, key in enumerate(KEYS):
        vector.append(
            table.get(key, {})
            .get(subsequence[index], '-inf')
        )
    response = {
        'logSum': additive_calculator(vector)
    }
    mult_score = multiplicative_calculator(vector)[1]
    response.update({
        'logLogProduct': mult_score.get('logLogProduct', 'NIL')
    })
    # A minor change here to account for non-showing of raw multiplicative scores
    # because the value is too large to be used for anything substantial
    return response