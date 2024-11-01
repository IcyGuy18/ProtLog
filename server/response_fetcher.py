import requests
import traceback

def fetch_response(prot_id):
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