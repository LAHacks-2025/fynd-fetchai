from uagents import Agent, Context, Model
import google.generativeai as genai
import os
from dotenv import load_dotenv
from typing import List, Dict, Optional
import uvicorn
import threading
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import asyncio
import time
import aiohttp

# Load environment variables
load_dotenv()

# Configure Gemini
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if not GEMINI_API_KEY:
    raise ValueError("Please set GEMINI_API_KEY in your .env file")

genai.configure(api_key=GEMINI_API_KEY)
print(f"List of models: {genai.list_models()}")
model = genai.GenerativeModel('gemini-1.5-flash')

# FastAPI Models
class QueryRequest(BaseModel):
    query: str

class Product(BaseModel):
    name: str
    price: float
    description: str
    attributes: Dict
    images: List[str]
    reviews: List[Dict]

class QueryResponse(BaseModel):
    status: str
    data: List[Product]

# Agent Models
class ProductRequest(Model):
    type: str = "get_all_products"

class ProductResponse(Model):
    type: str
    data: List[Dict]
    status: str
    timestamp: int

# Known agents mapping
AGENT_ADDRESSES = {
    "beer": "agent1qfnz78k70mv2z5607m78g0z9arnqkkkcpazm4qh90uhyyskguxssuggcd7m",
    "dress": "YOUR_DRESS_AGENT_ADDRESS",
    "watch": "YOUR_WATCH_AGENT_ADDRESS"
}

# Agent endpoints
AGENT_ENDPOINTS = {
    "beer": "http://localhost:8009/products",
    "dress": "http://localhost:8010/products",
    "watch": "http://localhost:8011/products",
    "shoe": "http://localhost:8012/products"
}

def analyze_query(query: str) -> str:
    """Use Gemini to determine the product type from the query"""
    try:
        prompt = f"""
        From the user query, determine one of the product type from the below list.
        Return just the word, nothing else and in singular form
        List of product types:
        - beer
        - dress
        - watch
        - shoe

        Query: {query}
        """
        
        response = model.generate_content(prompt)
        return response.text.strip().lower()
    except Exception as e:
        print(f"Error in Gemini API: {e}")
        return ""  # Default fallback

# Create the combined agent
query_search_agent = Agent(
    name="query_search_agent",
    seed="query_search_agent_seed_phrase_lahacks",
    port=8002,
    endpoint=["http://localhost:8002/submit"],
    mailbox=True,
)

# Create FastAPI app
app = FastAPI()

# Global variables
agent_ready = False
agent_context = None

@query_search_agent.on_event("startup")
async def startup(ctx: Context):
    global agent_ready, agent_context
    ctx.logger.info("Query Search Agent Started")
    agent_context = ctx
    agent_ready = True
    print("Agent is ready!")

# FastAPI Routes
@app.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    global agent_ready, agent_context
    
    # Check if agent is ready
    if not agent_ready or agent_context is None:
        raise HTTPException(status_code=503, detail="Agent is not ready yet. Please try again in a few seconds.")
    
    try:
        # Analyze query to get product type
        print(f"Query: {request.query}")
        product_type = analyze_query(request.query)
        print(f"Product type: {product_type}")

        if not product_type:
            raise HTTPException(status_code=400, detail="Could not determine product type")
        
        # Get agent endpoint for this product type
        agent_endpoint = AGENT_ENDPOINTS.get(product_type)
        print(f"Agent endpoint: {agent_endpoint}")
        if not agent_endpoint:
            raise HTTPException(status_code=404, detail=f"No agent found for product type: {product_type}")
        
        # Make HTTP request to the agent endpoint
        async with aiohttp.ClientSession() as session:
            async with session.post(
                agent_endpoint,
                json={"type": "get_all_products"}
            ) as response:
                if response.status != 200:
                    raise HTTPException(status_code=response.status, detail="Error from product agent")
                
                data = await response.json()
                if data["status"] == "success":
                    return QueryResponse(
                        status="success",
                        data=data["data"]
                    )
                else:
                    raise HTTPException(status_code=400, detail=data["status"])
            
    except Exception as e:
        print(f"Error processing query: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    global agent_ready
    return {
        "status": "healthy" if agent_ready else "starting",
        "agent_ready": agent_ready
    }

def run_agent():
    query_search_agent.run()

def run_api():
    # Wait for agent to be ready
    while not agent_ready:
        print("Waiting for agent to be ready...")
        time.sleep(1)
    
    print("Starting FastAPI server...")
    uvicorn.run(app, host="0.0.0.0", port=8001)

if __name__ == "__main__":
    # Start the agent in a separate thread
    agent_thread = threading.Thread(target=run_agent)
    agent_thread.start()
    
    # Run the FastAPI server
    run_api()