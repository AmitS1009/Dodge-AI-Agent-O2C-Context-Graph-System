import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import sqlite3
import pandas as pd
import json

from llm import chat_with_data
from graph import get_node_details, expand_node, get_initial_graph

app = FastAPI(title="Order-to-Cash AI Graph API")

class ChatRequest(BaseModel):
    message: str
    
@app.get("/api/graph/initial")
def initial_graph():
    return get_initial_graph()

@app.get("/api/graph/node/{node_type}/{node_id}")
def node_details(node_type: str, node_id: str):
    data = get_node_details(node_type, node_id)
    if not data:
        raise HTTPException(status_code=404, detail="Node not found")
    return data

@app.get("/api/graph/expand/{node_type}/{node_id}")
def expand_graph_node(node_type: str, node_id: str):
    return expand_node(node_type, node_id)

@app.post("/api/chat")
def chat_endpoint(req: ChatRequest):
    return {"reply": chat_with_data(req.message)}

# Mount static files for UI
static_dir = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(static_dir, exist_ok=True)
app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)
