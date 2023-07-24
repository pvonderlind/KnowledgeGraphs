from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
from backend.helpers import path_util, neo4j_driver
from backend import create_graph
from pathlib import Path
import numpy as np
import json

RE_INIT_DB = True

if RE_INIT_DB:
    print("Repopulating database, this may take a while ...")
    create_graph.re_populate_database()

# Init db driver
db = neo4j_driver.WillhabenDriver()

app = FastAPI()
willhaben_data = pd.read_csv(Path(path_util.DATA_DIR, 'willhaben_scrape.csv'), header=0).reset_index()
willhaben_data = willhaben_data.rename(columns = {'index':'id'})
willhaben_data = willhaben_data.drop_duplicates()
wiener_linien_stops = pd.read_csv(Path(path_util.DATA_DIR, 'wiener_linien_gtfs/stops.txt'), sep=',', header=0, index_col=0)


origins = [
    'http://localhost:8000',
    'http://localhost:5173'
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get('/api/listings/all')
def get_all_listings():
    return db.get_all_apartments()

@app.get('/api/stops/all')
def get_all_stops():
    return wiener_linien_stops.to_json(orient='records')

@app.get('/api/clusters/all')
def get_all_clusters():
    return json.dumps(np.load(Path(path_util.DATA_DIR, 'clusters.npy')).tolist())