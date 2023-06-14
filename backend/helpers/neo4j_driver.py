from neo4j import GraphDatabase

URI = 'bolt://localhost:7687'
AUTH = ('neo4j', 'kg2023summer')
DB = 'neo4j'

class WillhabenDriver:

    def __init__(self, uri: str, auth: tuple):
        self.driver = GraphDatabase.driver(uri=uri, auth=auth)
    
    def close(self):
        self.driver.close()

    def add_listings(self, listings: list[dict]):
        with self.driver.session() as session:
            for listing in listings:
                session.execute_write(self._create_listing, listing)
    
    @staticmethod
    def _create_listing(tx, listing: dict):
        attribute_str = '{' + ','.join([f'{k}: $l.{k}' for k in listing.keys()]) + '}'
        query = f'CREATE (a:Apartment {attribute_str})'
        tx.run(query,l=listing)

if __name__ == "__main__":
    test = WillhabenDriver(URI, AUTH)
    test.add_listings([{'a':'test','best':'b','chest':3}])
    test.close()