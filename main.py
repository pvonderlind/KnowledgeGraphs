from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
from helpers import path_util
from pathlib import Path

app = FastAPI()
willhaben_data = pd.read_csv(Path(path_util.DATA_DIR, 'willhaben_scrape.csv'))
wiener_linien_stops = pd.read_csv(Path(path_util.DATA_DIR, 'wiener_linien_gtfs/stops.txt'), sep=',', header=0)

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
    return willhaben_data.to_json(orient='records')


@app.get('/api/stops/all')
def get_all_stops():
    return wiener_linien_stops.to_json(orient='records')
