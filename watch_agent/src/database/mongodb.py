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
        self.collection = self.db[os.getenv('WATCH_COLLECTION_NAME')]

    def initialize_data(self):
        # Check if collection is empty
        if self.collection.count_documents({}) == 0:
            # Get the current file's directory
            current_dir = pathlib.Path(__file__).parent.parent.parent
            # Construct the path to watch_sample_data.json
            json_path = current_dir / 'watch_sample_data.json'
            
            # Load sample data
            with open(json_path, 'r') as file:
                watches = json.load(file)
                self.collection.insert_many(watches)

    def get_all_watches(self):
        watches = list(self.collection.find({}, {'_id': 0}))
        products = []
        
        for watch in watches:
            # Convert reviews
            reviews = [
                Review(
                    id=review["id"],
                    userId=review["userId"],
                    rating=review["rating"],
                    comment=review["comment"],
                    date=review["date"]
                ) for review in watch["reviews"]
            ]
            
            # Convert attributes
            attributes = ProductAttributes(
            attributes={
                "size": watch.get("attributes", {}).get("size", "N/A"),
                "color": watch.get("attributes", {}).get("color", "N/A"),
                "material": watch.get("attributes", {}).get("material", "N/A"),
                "style": watch.get("attributes", {}).get("style", "N/A")
            }
        )
            
            # Create product
            product = Product(
                id=watch["id"],
                name=watch["name"],
                price=watch["price"],
                description=watch["description"],
                images=watch["images"],
                reviews=reviews,
                attributes=attributes
            )
            products.append(product)
            
        return products

    def get_watch_by_id(self, watch_id: str):
        watch = self.collection.find_one({'id': watch_id}, {'_id': 0})
        if not watch:
            return None
            
        # Convert to Dress format
        reviews = [
            Review(
                id=review["id"],
                userId=review["userId"],
                rating=review["rating"],
                comment=review["comment"],
                date=review["date"]
            ) for review in watch["reviews"]
        ]
        
        attributes = ProductAttributes(
            attributes={
                "size": watch["attributes"]["size"],
                "color": watch["attributes"]["color"],
                "material": watch["attributes"]["material"],
                "style": watch["attributes"]["style"]
            }
        )
        
        return Product(
            id=watch["id"],
            name=watch["name"],
            price=watch["price"],
            description=watch["description"],
            images=watch["images"],
            reviews=reviews,
            attributes=attributes
        )

    def update_watch_interaction(self, watch_id: str, interaction_type: str):
        update_field = f"{interaction_type}s"
        self.collection.update_one(
            {'id': watch_id},
            {'$inc': {update_field: 1}}
        ) 