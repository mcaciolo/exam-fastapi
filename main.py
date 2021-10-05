from fastapi import FastAPI, HTTPException
from fastapi.params import Header
from pydantic import BaseModel
from typing import Literal, Optional

import pandas as pd
import csv

api = FastAPI(title='QCM_Generator',
              description='Generator of sample QCM about Data Engineer',
              version='0.0.1 (beta)',
              openapi_tags=[
                    {
                        'name': 'Basic APIs',
                        'description': 'Endpoints accessible to all users'
                    },
                    {
                        'name': 'Admin APIs',
                        'description': 'Endpoints accessible to admin users only'
                    }
               ])

#List of users (hard coded)
user_list = {
    'alice': {'password': 'wonderland', 'auth' : ['basic']},
    'bob': {'password': 'builder', 'auth' : ['basic']},
    'clementine': {'password': 'mandarine', 'auth' : ['basic']},
    'admin': {'password': '4dm1N', 'auth' : ['basic', 'admin']}
}

#List of questions (from file)
df_questions = pd.read_csv('questions.csv')
df_questions = df_questions.fillna('')

#Verify authorization
def verify_authorization(auth_header, auth_level):
    if auth_header is None:
        raise HTTPException(status_code=401, detail="No Authorization header")
    
    username_password = auth_header.split(':')
    if len(username_password) != 2:
        raise HTTPException(status_code=401, detail="Authorization header should be in the form username:password")
    if username_password[0] not in user_list:
        raise HTTPException(status_code=401, detail=f"Specified username {username_password[0]} does not exist")
    if username_password[1] != user_list[username_password[0]]['password']:
        raise HTTPException(status_code=401, detail=f"Mismatch password")
    if auth_level not in user_list[username_password[0]]['auth']:
        raise HTTPException(status_code=403, detail=f"Unauthorized action for user {username_password[0]}")

#Status Responses
status_responses = {
    200: {"description": "OK"},
    401: {"description": "Authentification error"},
    403: {"description": "Not enough priviledges"}
}

@api.get('/status', tags=['Basic APIs'], name='Check status', responses=status_responses)
def check_status(Auth_header:str = Header(None, description='username:password')):
    """
    Check the API status. Should always return 1 \n
    Minimum authorization : basic \n
    """
    verify_authorization(Auth_header, 'basic')
    return {'status' : 1}


#QCM Responses
qcm_responses = {
    200: {"description": "OK"},
    401: {"description": "Authentification error"},
    403: {"description": "Not enough priviledges"},
    404: {"description": "No questions corresponding to specified use and/or subjects"}
}

@api.get('/QCM', responses=qcm_responses, tags=['Basic APIs'], name='Generate QCM')
def get_QCM(n_questions:Optional[Literal['5','10','20']] = '10', 
            use:Optional[str] = None, 
            subjects:Optional[str] = None,
            auth_header:str = Header(None, description='username:password')):
    """
    Generate a random QCM composed by n_questions, filtered basing on the use and a list of subjects. \n
    Minimum authorization : basic \n 
    Subjects should be separated by commas \n
    -> If the use is not specified, questions are not filtered by use \n
    -> If no list of subjects is specified, questions are not filtered by subject \n
    -> If the number of questions are not specified, a QCM of 10 questions is provided \n
    """

    verify_authorization(auth_header, 'basic')
    
    #Filter on subject and use, if any
    if subjects is None:
        subjects = df_questions.subject.unique() # No filter on subjects
    else:
        subjects = [s.strip() for s in subjects.split(',')]
    if use is None:
        df_filtered = df_questions[df_questions.subject.isin(subjects)]
    else:
        df_filtered = df_questions[((df_questions.use==use)) & (df_questions.subject.isin(subjects))]
    
    #Check the number of filtered questions and compare it to the number of requested questions
    if len(df_filtered)==0:
        raise HTTPException(status_code=404, detail="No questions corresponding to specified use and/or subjects")
    n_questions = int(n_questions)
    incomplete_answer = (len(df_filtered) < n_questions)
    n_questions = min(n_questions, len(df_filtered))

    return {
        'QCM': df_filtered.sample(n_questions).to_dict(orient='records'),
        'imcomplete_answer_flag': incomplete_answer
    }


#Question body
class NewQuestion(BaseModel):
    question : str
    subject : str
    use : str
    correct: Literal['A', 'B', 'C', 'D']
    responseA: str
    responseB : str
    responseC : str
    responseD : Optional[str] = ''
    remark : Optional[str] = ''

#Questions Responses
questions_responses = {
    200: {"description": "OK"},
    401: {"description": "Authentification error"},
    403: {"description": "Not enough priviledges"},
    404: {"description": "No questions corresponding to specified use and/or subjects"}
}
@api.post('/Questions', responses=questions_responses, tags=['Admin APIs'], name='Add question')
def add_question(new_question:NewQuestion, Auth_header:str= Header(None, description='username:password')):
    """
    Add a new question to the question pool \n
    Minimum authorization : admin \n
    """

    verify_authorization(Auth_header, 'admin')

    #Update the file
    with open(file='questions.csv',mode='a', newline='') as file:
        wr = csv.writer(file, dialect='excel')
        wr.writerow(new_question.__dict__.values())

    #Read the updated file
    global df_questions
    df_questions = pd.read_csv('questions.csv')
    df_questions = df_questions.fillna('')

    return new_question.__dict__




