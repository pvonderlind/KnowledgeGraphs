from typing import List
import networkx as nx
import numpy as np
import pandas as pd
from pathlib import Path
from backend.helpers import path_util
import math
from tqdm import tqdm
import matplotlib.pyplot as plt
import os
from pykeen import pipeline, triples, predict, nn
from sklearn.cluster import KMeans
import torch
from backend.helpers import neo4j_driver

# Initialise NEO4J database driver
driver = neo4j_driver.WillhabenDriver()

N_DATA = 100
SEED = 12334 
willhaben_data = pd.read_csv(Path(path_util.DATA_DIR, 'willhaben_scrape.csv'), header=0).reset_index().sample(n=N_DATA, random_state=SEED, replace=False)
willhaben_data = willhaben_data.rename(columns = {'index':'id'})
willhaben_data = willhaben_data.drop_duplicates()
willhaben_data = willhaben_data.fillna("")
wiener_linien_stops = pd.read_csv(Path(path_util.DATA_DIR, 'wiener_linien_gtfs/stops.txt'), sep=',', header=0)

GRAPH_SAVE_PATH = Path(path_util.DATA_DIR, 'kg_edgelist.csv')
PYKEEN_DIR = Path(path_util.DATA_DIR, 'pykeen/')
CLUSTER_PATH = Path(path_util.DATA_DIR, 'clusters.npy')
N_EPOCHS = 20
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

def re_populate_database():
    # Clear database
    driver.delete_db()

    # Apartments from willhaben
    listings = willhaben_data.to_dict('records')
    driver.add_listings(listings)

    # Stops from Wiener Linien GTFS
    stops = wiener_linien_stops.to_dict('records')
    driver.add_stops(stops)

    # Add edges between houses, stops, etc. via logical rules
    _add_logical_edges()


def _add_logical_edges() -> pd.DataFrame:
    """
    Note that we do this in python, as Neo4J can not handle the complexity of O(Apartments * Stops) 
    and python handles it with ease.
    """
    sources = []
    targets = []
    edges = []
    for idx_i, flat in tqdm(willhaben_data.iterrows()):
        # Create edges to wiener linien stops
        for _, stop in wiener_linien_stops.iterrows():
            d = haversine_distance(flat.LONGITUDE, flat.LATITUDE, stop.stop_lon, stop.stop_lat)
            if d <= walking_distance_km:
                driver.add_walkingDistance_edge(flat.id, stop.stop_id)

        #Create edges to other willhaben flats based on similar price, living area
        #For price, we use a 15% deviation of the comparing flat.
        for idx_j, flat_compare in willhaben_data.iterrows():
            if idx_i == idx_j:
                continue
            
            # PRICE
            flat_lower = flat.PRICE * 0.85
            flat_upper = flat.PRICE * 1.15
            if flat_compare.PRICE >= flat_lower and flat_compare.PRICE <= flat_upper:
                driver.add_apt_to_apt_edge(flat.id, flat_compare.id, 'hasSimilarPrice')
            
            # LIVING AREA
            # Again, we use a 15% deviation of the comparing flat. 
            area_lower = flat.ESTATE_SIZE * 0.85
            area_upper = flat.ESTATE_SIZE * 1.15
            if flat_compare.ESTATE_SIZE >= area_lower and flat_compare.ESTATE_SIZE <= area_upper:
                driver.add_apt_to_apt_edge(flat.id, flat_compare.id, 'hasSimilarArea')
            
    # We drop duplicates as stations have multiple stops and we don't care which of them is accessible if one is!
    return pd.DataFrame({'source':sources, 'target':targets, 'edge':edges}).drop_duplicates()

def _load_edgelist_df() -> pd.DataFrame:
    # if os.path.exists(GRAPH_SAVE_PATH):
    #     print(f"Loading saved edgelist from {GRAPH_SAVE_PATH}")
    #     kg_df = pd.read_csv(GRAPH_SAVE_PATH, header=0)
    # else:
    #     print(f"Generating edgelist and saving to {GRAPH_SAVE_PATH}")
    #     kg_df = _regenerate_edgelist()
    #     kg_df.to_csv(GRAPH_SAVE_PATH, header=True, index=False)
    # return kg_df
    pass

def _get_splits_pykeen(df: pd.DataFrame) -> tuple:
    np_triples = df.to_numpy(dtype=str)
    tf = triples.TriplesFactory.from_labeled_triples(np_triples)
    training, testing, validation = tf.split([.8, .1, .1])
    return training, testing, validation, tf

def train_pykeen_model(training, testing, validation):
    if not os.path.exists(PYKEEN_DIR):
        print("Training new pykeen model ...")
        result = pipeline.pipeline(
            training=training,
            testing=testing,
            validation=validation,
            model=PYKEEN_MODEL,
            stopper='early',
            epochs=N_EPOCHS
        )
        result.save_to_directory(PYKEEN_DIR)
        return result.model
    else:
        print('Loading saved pykeen model ...')
        return torch.load(Path(PYKEEN_DIR,'trained_model.pkl'))

def k_mean_cluster_embeddings(model, k: int = 8) -> np.ndarray:
    entity_embeddings = model.entity_representations[0](indices=None).detach().numpy()
    cluster_assignments = KMeans(n_clusters=k, random_state=0, n_init='auto').fit_predict(entity_embeddings)
    return cluster_assignments



if __name__ == "__main__":
    # kg_df = _load_edgelist_df()
    # train, test, val, full = _get_splits_pykeen(kg_df)
    # model = train_pykeen_model(train, test, val)
    # clusters = k_mean_cluster_embeddings(model)
    # print(clusters.shape)
    # print(clusters)
    # with open(CLUSTER_PATH, 'wb') as f:
    #     np.save(f, clusters)
    pass