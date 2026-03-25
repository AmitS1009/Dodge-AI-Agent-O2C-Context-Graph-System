import os
import sqlite3
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

client = None
if GROQ_API_KEY and GROQ_API_KEY != "your_groq_api_key_here":
    # Groq provides an OpenAI-compatible API endpoint
    client = OpenAI(
        base_url="https://api.groq.com/openai/v1",
        api_key=GROQ_API_KEY
    )

SCHEMA_INSTRUCTIONS = """
Database Schema for SAP Order-to-Cash:
- `sales_order_headers`: salesOrder (PK), salesOrderType, salesOrganization, soldToParty, totalNetAmount, transactionCurrency
- `sales_order_items`: salesOrder, salesOrderItem, material, requestedQuantity, netAmount
- `outbound_delivery_headers`: deliveryDocument (PK), creationDate, overallGoodsMovementStatus
- `outbound_delivery_items`: deliveryDocument, deliveryDocumentItem, referenceSDDocument (Join to salesOrder), material, actualDeliveryQuantity
- `billing_document_headers`: billingDocument (PK), billingDocumentType, totalNetAmount, soldToParty, accountingDocument, billingDocumentIsCancelled
- `billing_document_items`: billingDocument, billingDocumentItem, referenceSDDocument (Join to deliveryDocument or salesOrder), material, billingQuantity
- `journal_entry_items_accounts_receivable`: accountingDocument (PK), referenceDocument (Join to billingDocument), companyCode, amountInCompanyCodeCurrency
- `business_partners`: businessPartner (PK), businessPartnerName
- `products`: product (PK), productType

GUARDRAILS: 
You are an AI assistant exclusively designed for Order-to-Cash data analysis. 
If the user asks a question not related to SAP, Orders, Deliveries, Billing, Customers, or Payments, reply EXACTLY with:
"REJECT"
"""

def generate_sql(user_query: str) -> str:
    prompt = f"""
{SCHEMA_INSTRUCTIONS}

Based on the prompt, generate a valid SQLite SQL statement to answer the question. 
Output ONLY the raw SQL query, without markdown blocks, without backticks snippet formatting, and without explanation.
If the query is out of scope and violates the guardrails, just return: REJECT

User Query: {user_query}
"""
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",  # Fast, highly capable Groq model
        messages=[
            {"role": "system", "content": "You are a strict SQL query generator. Output only raw SQL. No markdown, no explanations."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.0
    )
    result = response.choices[0].message.content.strip(' `\n')
    if result.lower().startswith('sql'):
        result = result[3:].strip()
    return result

def format_answer(user_query: str, sql: str, results: list) -> str:
    prompt = f"""
{SCHEMA_INSTRUCTIONS}

User asked: "{user_query}"
SQL executed: {sql}
Results from DB: {results}

Provide a natural language answer based ONLY on the data from the results. Be concise, clear, and accurate. Do not mention the SQL query itself in the final reply.
"""
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "You are a helpful data analyst translating SQL query results into natural language."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3
    )
    return response.choices[0].message.content.strip()

def chat_with_data(user_query: str) -> str:
    if not client:
        return "System error: Groq API Key not configured."
        
    try:
        sql = generate_sql(user_query)
        if "REJECT" in sql.upper():
            return "This system is designed to answer questions related to the provided dataset only."
            
        # Execute SQL securely logic
        conn = sqlite3.connect("o2c.db")
        conn.row_factory = sqlite3.Row
        cur = conn.execute(sql)
        rows = cur.fetchall()
        results = [dict(row) for row in rows]
        conn.close()
        
        # Limit rows for the prompt to avoid token overflow
        if len(results) > 20:
            results_str = str(results[:20]) + f"... (and {len(results)-20} more rows)"
        else:
            results_str = str(results)
            
        return format_answer(user_query, sql, results_str)
        
    except sqlite3.Error as e:
        return f"Database query error: {str(e)}\n\nAttempted SQL: {sql}"
    except Exception as e:
        return f"An error occurred while processing the request: {str(e)}"
