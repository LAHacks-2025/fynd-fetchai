from uagents import Agent, Context, Protocol, Model
from .models import (
    Product, Review, ProductAttributes
)
import json
import uvicorn
import threading
import asyncio
import time
from src.database.mongodb import MongoDB
from pydantic import BaseModel

# Initialize MongoDB
db = MongoDB()

# Create shoe agent
shoe_agent = Agent(
    name="shoe_agent",
    port=8012,
    seed="shoe_agent_seed_phrase_fynd_project",
    endpoint=["http://localhost:8012/products"]
)

# Initialize data
db.initialize_data()

# Define request and response models
class ProductRequest(Model):
    type: str = "get_all_products"

class ProductResponse(Model):
    type: str
    data: list[dict]
    status: str
    timestamp: int

@shoe_agent.on_event("startup")
async def startup(ctx: Context):
    ctx.logger.info("Shoes Agent Started")
    ctx.logger.info(f"Agent Address: {ctx.agent.address}")

@shoe_agent.on_rest_post("/products", ProductRequest, ProductResponse)
async def handle_product_request(ctx: Context, req: ProductRequest) -> ProductResponse:
    ctx.logger.info("Received product request")
    
    try:
        # Get all dresses from database
        shoees = db.get_all_shoees()
        ctx.logger.info(f"Found {len(shoees)} shoees in database")
        
        # Send response
        return ProductResponse(
            type="products",
            data=shoees,
            status="success",
            timestamp=int(time.time())
        )
    except Exception as e:
        ctx.logger.error(f"Error handling request: {e}")
        return ProductResponse(
            type="error",
            data=[],
            status=f"Error: {str(e)}",
            timestamp=int(time.time())
        )

if __name__ == "__main__":
    shoe_agent.run() 