import networkx as nx
import pandas as pd
from pathlib import Path
from helpers import path_util
import math
from tqdm import tqdm
import matplotlib.pyplot as plt
import os
from pykeen import pipeline, triples

willhaben_data = pd.read_csv(Path(path_util.DATA_DIR, 'willhaben_scrape.csv'), header=0, index_col=0).reset_index()
willhaben_data = willhaben_data.rename(columns = {'index':'id'})
wiener_linien_stops = pd.read_csv(Path(path_util.DATA_DIR, 'wiener_linien_gtfs/stops.txt'), sep=',', header=0, index_col=0)

GRAPH_SAVE_DIR = Path(path_util.DATA_DIR, 'kg_edgelist.csv')
PYKEEN_DIR = Path(path_util.DATA_DIR, 'pykeen/')
N_EPOCHS = 100
PYKEEN_MODEL = 'TransE'

# Greenwhich coordinate origin
origin = [51.4825766, -0.0076589]

# Standard definition of walking distance is 800m (~10 min walk)
walking_distance_km = 0.8

def haversine_distance(lat: float, lng: float, lat0: float, lng0: float) -> float:
    deglen = 110.25
    x = lat - lat0
    y = (lng - lng0)*math.cos(lat0)
    return deglen*math.sqrt(x*x + y*y)

def _regenerate_edgelist() -> pd.DataFrame:
    sources = []
    targets = []
    edges = []
    for idx_i, flat in tqdm(willhaben_data.iterrows()):
        # Create edges to wiener linien stops
        for _, stop in wiener_linien_stops.iterrows():
            d = haversine_distance(flat.LONGITUDE, flat.LATITUDE, stop.stop_lon, stop.stop_lat)
            if d <= walking_distance_km:
                sources.append(flat.id)
                targets.append(stop.stop_name)
                edges.append('inWalkingDistanceOf')
        # Create edges to other willhaben flats based on similar price, living area
        # For price, we use a 15% deviation of the comparing flat.
        for idx_j, flat_compare in willhaben_data.iterrows():
            if idx_i == idx_j:
                continue
            
            # PRICE
            flat_lower = flat.PRICE * 0.85
            flat_upper = flat.PRICE * 1.15
            if flat_compare.PRICE >= flat_lower and flat_compare.PRICE <= flat_upper:
                sources.append(flat.id)
                targets.append(flat_compare.id)
                edges.append('hasSimilarPrice')
            
            # LIVING AREA
            # Again, we use a 15% deviation of the comparing flat. 
            area_lower = flat.ESTATE_SIZE * 0.85
            area_upper = flat.ESTATE_SIZE * 1.15
            if flat_compare.ESTATE_SIZE >= area_lower and flat_compare.ESTATE_SIZE <= area_upper:
                sources.append(flat.id)
                targets.append(flat_compare.id)
                edges.append('hasSimilarArea')
            
    # We drop duplicates as stations have multiple stops and we don't care which of them is accessible if one is!
    return pd.DataFrame({'source':sources, 'target':targets, 'edge':edges}).drop_duplicates()

def _load_edgelist_df() -> pd.DataFrame:
    if os.path.exists(GRAPH_SAVE_DIR):
        print(f"Loading saved edgelist from {GRAPH_SAVE_DIR}")
        kg_df = pd.read_csv(GRAPH_SAVE_DIR, header=0)
    else:
        print(f"Generating edgelist and saving to {GRAPH_SAVE_DIR}")
        kg_df = _regenerate_edgelist()
        kg_df.to_csv(GRAPH_SAVE_DIR, header=True, index=False)
    return kg_df

def _get_splits_pykeen(df: pd.DataFrame) -> tuple:
    np_triples = df.to_numpy(dtype=str)
    tf = triples.TriplesFactory.from_labeled_triples(np_triples)
    training, testing, validation = tf.split([.8, .1, .1])
    return training, testing, validation

def train_pykeen_model(training, testing, validation):
    result = pipeline.pipeline(
        training=training,
        testing=testing,
        validation=validation,
        model=PYKEEN_MODEL,
        stopper='early',
        epochs=N_EPOCHS
    )
    result.save_to_directory(PYKEEN_DIR)
    return result

if __name__ == "__main__":
    kg_df = _load_edgelist_df()
    train, test, val = _get_splits_pykeen(kg_df)
    result = train_pykeen_model(train, test, val)



