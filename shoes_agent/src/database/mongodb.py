from pymongo import MongoClient
from dotenv import load_dotenv
import os
import json
import pathlib
from ..agent.models import Product, Review, ProductAttributes

load_dotenv()

class MongoDB:
    def __init__(self):
        self.client = MongoClient(os.getenv('MONGODB_URI'))
        self.db = self.client[os.getenv('DATABASE_NAME')]
        self.collection = self.db[os.getenv('SHOE_COLLECTION_NAME')]

    def initialize_data(self):
        # Check if collection is empty
        if self.collection.count_documents({}) == 0:
            # Get the current file's directory
            current_dir = pathlib.Path(__file__).parent.parent.parent
            # Construct the path to shoe_sample_data.json
            json_path = current_dir / 'shoe_sample_data.json'
            print(f"Loading sample data from {json_path}")
            # Load sample data
            with open(json_path, 'r') as file:
                shoees = json.load(file)
                print(f"Inserting {len(shoees)} shoees into the database")
                self.collection.insert_many(shoees)

    def get_all_shoees(self):
        shoees = list(self.collection.find({}, {'_id': 0}))
        products = []
        
        for shoe in shoees:
            # Convert reviews
            reviews = [
                Review(
                    id=review["id"],
                    userId=review["userId"],
                    rating=review["rating"],
                    comment=review["comment"],
                    date=review["date"]
                ) for review in shoe["reviews"]
            ]
            
            # Convert attributes
            attributes = ProductAttributes(
                attributes={
                    "size": shoe.get("attributes", {}).get("size", "N/A"),
                    "color": shoe.get("attributes", {}).get("color", "N/A"),
                    "material": shoe.get("attributes", {}).get("material", "N/A"),
                    "style": shoe.get("attributes", {}).get("style", "N/A")
                }
            )
            
            # Create product
            product = Product(
                id=shoe["id"],
                name=shoe["name"],
                price=shoe["price"],
                description=shoe["description"],
                images=shoe["images"],
                reviews=reviews,
                attributes=attributes
            )
            products.append(product)
            
        return products

    def get_shoe_by_id(self, shoe_id: str):
        shoe = self.collection.find_one({'id': shoe_id}, {'_id': 0})
        if not shoe:
            return None
            
        # Convert to shoe format
        reviews = [
            Review(
                id=review["id"],
                userId=review["userId"],
                rating=review["rating"],
                comment=review["comment"],
                date=review["date"]
            ) for review in shoe["reviews"]
        ]
        
        attributes = ProductAttributes(
            attributes={
                "size": shoe["attributes"]["size"],
                "color": shoe["attributes"]["color"],
                "material": shoe["attributes"]["material"],
                "style": shoe["attributes"]["style"]
            }
        )
        
        return Product(
            id=shoe["id"],
            name=shoe["name"],
            price=shoe["price"],
            description=shoe["description"],
            images=shoe["images"],
            reviews=reviews,
            attributes=attributes
        )

    def update_shoe_interaction(self, shoe_id: str, interaction_type: str):
        update_field = f"{interaction_type}s"
        self.collection.update_one(
            {'id': shoe_id},
            {'$inc': {update_field: 1}}
        ) 