# KG Project

Hi and welcome to my KG project!

This application is designed to allow users to see similar flats in Willhaben using
both data from their website, linked with public transportation stops from the Wiener Linien GTFS data.

User can see small number of flats on a map and can click on the to get similar flats, predicted via clustering on KG embeddings. Users can also choose to show public transportation stops in Vienna.

## Installation

The ```data``` folder should contain all data necessary to run the project as is.
This includes an exported edge-list from Neo4J, the pykeen model, the k-means clusters and the Willhaben scrape + Wiener Linien data.

### Backend
For the backend, you will need to install a number of Python dependencies. I recommend doing this via Conda, using the provided environment file ```environment.yml```.

In order for the project to work, devs will need to install ```Neo4J``` locally.
The setups requires the following credentials to work:
```
URI = 'bolt://localhost:7687'
AUTH = ('neo4j', 'kg2023summer')
DB = 'neo4j'
```
If you want to change the connection parameters, please navigate to ```helpers/neo4j_driver``` and adapt them!

### Frontend

For the frontend, you will need to install ```Vue 3 in Vite```. I recommend doing this via the Node package manager ```npm```. In theory nodejs should be included in the Conda environment, but it may be weird, so check if node is installed and then install Vue 3 in Vite.