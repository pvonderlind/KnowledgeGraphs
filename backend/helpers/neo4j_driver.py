import json
from neo4j import GraphDatabase

URI = 'bolt://localhost:7687'
AUTH = ('neo4j', 'kg2023summer')
DB = 'neo4j'

# Use bin\neo4j-admin server console
# inside of the downloaded server applicaiton folder to launch server first !

class WillhabenDriver:

    def __init__(self, uri: str = URI, auth: tuple = AUTH):
        self.driver = GraphDatabase.driver(uri=uri, auth=auth)
    
    def close(self):
        self.driver.close()

    def get_all_apartments(self) -> list[dict]:
        return [r.data()['a'] for r in self.driver.execute_query("MATCH (a: Apartment) RETURN a").records]

    def add_apt_to_apt_edge(self, apartment_id_a: int, apartment_id_b: int, edge_type: str):
        with self.driver.session() as session:
            session.execute_write(self._create_apt_edge, apartment_id_a, apartment_id_b, edge_type)
    
    @staticmethod
    def _create_apt_edge(tx, apartment_id_a: int, apartment_id_b: int, edge_type: str):
        query = f'MATCH (a:Apartment {{id:$ap_a}}),(b:Apartment {{id:$ap_b}}) CREATE (a)-[r:{edge_type}]->(b)'
        tx.run(query, ap_a=apartment_id_a, ap_b=apartment_id_b)

    def add_walkingDistance_edge(self, apartment_id: int, stop_id:str):
        with self.driver.session() as session:
            session.execute_write(self._create_walkingDistance_edge, apartment_id, stop_id)

    @staticmethod
    def _create_walkingDistance_edge(tx, apartment_id: int, stop_id:str):
        query = 'MATCH (a:Apartment {id:$ap}),(s:Stop {stop_id:$stop_id}) CREATE (a)-[r:inWalkingDistanceOf]->(s)'
        tx.run(query, ap=apartment_id, stop_id=stop_id)

    def add_listings(self, listings: list[dict]):
        with self.driver.session() as session:
            for listing in listings:
                session.execute_write(self._create_listing, listing)
    
    @staticmethod
    def _create_listing(tx, listing: dict):
        attribute_str = '{' + ','.join([f'{k.replace("/","_")}: $l.{k.replace("/","_")}' for k in listing.keys()]) + '}'
        query = f'CREATE (a:Apartment {attribute_str})'
        tx.run(query,l=listing)

    def add_stops(self, stops: list[dict]):
        with self.driver.session() as session:
            for stop in stops:
                session.execute_write(self._add_stop, stop)
    
    @staticmethod
    def _add_stop(tx, stop: dict):
        attribute_str = '{' + ','.join([f'{k}: $l.{k}' for k in stop.keys()]) + '}'
        query = f'CREATE (a:Stop {attribute_str})'
        tx.run(query,l=stop)
    
    def delete_db(self):
        with self.driver.session() as session:
            session.execute_write(self._delete_everything)

    @staticmethod
    def _delete_everything(tx):
        query = 'MATCH (n) DETACH DELETE n'
        tx.run(query)

if __name__ == "__main__":
    test = WillhabenDriver(URI, AUTH)
    test.add_listings([{'a':'test','best':'b','chest':3}])
    test.close()