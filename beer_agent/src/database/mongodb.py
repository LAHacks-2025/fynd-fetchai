from pymongo import MongoClient
from dotenv import load_dotenv
import os
import json
import pathlib
from src.agent.models import Product, Review, ProductAttributes

load_dotenv()

class MongoDB:
    def __init__(self):
        self.client = MongoClient(os.getenv('MONGODB_URI'))
        self.db = self.client[os.getenv('DATABASE_NAME')]
        self.collection = self.db[os.getenv('COLLECTION_NAME')]

    def initialize_data(self):
        # Check if collection is empty
        if self.collection.count_documents({}) == 0:
            # Get the current file's directory
            current_dir = pathlib.Path(__file__).parent.parent.parent
            # Construct the path to beer_sample_data.json
            json_path = current_dir / 'beer_sample_data.json'
            
            # Load sample data
            with open(json_path, 'r') as file:
                beers = json.load(file)
                self.collection.insert_many(beers)

    def get_all_beers(self):
        beers = list(self.collection.find({}, {'_id': 0}))
        products = []
        
        for beer in beers:
            # Convert reviews
            reviews = [
                Review(
                    id=review["id"],
                    userId=review["userId"],
                    rating=review["rating"],
                    comment=review["comment"],
                    date=review["date"]
                ) for review in beer["reviews"]
            ]
            
            # Convert attributes
            attributes = ProductAttributes(
                attributes={
                    "alcohol_by_volume": beer["attributes"]["alcohol_by_volume"],
                    "ingredients": beer["attributes"]["ingredients"]
                }
            )
            
            # Create product
            product = Product(
                id=beer["id"],
                name=beer["name"],
                price=beer["price"],
                description=beer["description"],
                images=beer["images"],
                reviews=reviews,
                attributes=attributes
            )
            products.append(product)
            
        return products

    def get_beer_by_id(self, beer_id: str):
        beer = self.collection.find_one({'id': beer_id}, {'_id': 0})
        if not beer:
            return None
            
        # Convert to Product format
        reviews = [
            Review(
                id=review["id"],
                userId=review["userId"],
                rating=review["rating"],
                comment=review["comment"],
                date=review["date"]
            ) for review in beer["reviews"]
        ]
        
        attributes = ProductAttributes(
            attributes={
                "alcohol_by_volume": beer["attributes"]["alcohol_by_volume"],
                "ingredients": beer["attributes"]["ingredients"]
            }
        )
        
        return Product(
            id=beer["id"],
            name=beer["name"],
            price=beer["price"],
            description=beer["description"],
            images=beer["images"],
            reviews=reviews,
            attributes=attributes
        )

    def update_beer_interaction(self, beer_id: str, interaction_type: str):
        update_field = f"{interaction_type}s"
        self.collection.update_one(
            {'id': beer_id},
            {'$inc': {update_field: 1}}
        )