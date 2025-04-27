from pymongo import MongoClient
from dotenv import load_dotenv
import os
import json
import pathlib
from ..agent.models import Dress, Review, DressAttributes

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
            # Construct the path to dress_sample_data.json
            json_path = current_dir / 'dress_sample_data.json'
            
            # Load sample data
            with open(json_path, 'r') as file:
                dresses = json.load(file)
                self.collection.insert_many(dresses)

    def get_all_dresses(self):
        dresses = list(self.collection.find({}, {'_id': 0}))
        products = []
        
        for dress in dresses:
            # Convert reviews
            reviews = [
                Review(
                    id=review["id"],
                    userId=review["userId"],
                    rating=review["rating"],
                    comment=review["comment"],
                    date=review["date"]
                ) for review in dress["reviews"]
            ]
            
            # Convert attributes
            attributes = ProductAttributes(
                attributes={
                    "size": dress["attributes"]["size"],
                    "color": dress["attributes"]["color"],
                    "material": dress["attributes"]["material"],
                    "style": dress["attributes"]["style"]
                }
            )
            
            # Create product
            product = Product(
                id=dress["id"],
                name=dress["name"],
                price=dress["price"],
                description=dress["description"],
                images=dress["images"],
                reviews=reviews,
                attributes=attributes
            )
            products.append(product)
            
        return products

    def get_dress_by_id(self, dress_id: str):
        dress = self.collection.find_one({'id': dress_id}, {'_id': 0})
        if not dress:
            return None
            
        # Convert to Dress format
        reviews = [
            Review(
                id=review["id"],
                userId=review["userId"],
                rating=review["rating"],
                comment=review["comment"],
                date=review["date"]
            ) for review in dress["reviews"]
        ]
        
        attributes = ProductAttributes(
            attributes={
                "size": dress["attributes"]["size"],
                "color": dress["attributes"]["color"],
                "material": dress["attributes"]["material"],
                "style": dress["attributes"]["style"]
            }
        )
        
        return Product(
            id=dress["id"],
            name=dress["name"],
            price=dress["price"],
            description=dress["description"],
            images=dress["images"],
            reviews=reviews,
            attributes=attributes
        )

    def update_dress_interaction(self, dress_id: str, interaction_type: str):
        update_field = f"{interaction_type}s"
        self.collection.update_one(
            {'id': dress_id},
            {'$inc': {update_field: 1}}
        ) 