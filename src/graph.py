import sqlite3

def get_db():
    conn = sqlite3.connect("o2c.db")
    conn.row_factory = sqlite3.Row
    return conn

def query_db(query, args=(), one=False):
    conn = get_db()
    cur = conn.execute(query, args)
    rv = cur.fetchall()
    conn.close()
    return (rv[0] if rv else None) if one else rv

def get_node_details(node_type: str, node_id: str):
    if node_type == 'SalesOrder':
        return query_db('SELECT * FROM sales_order_headers WHERE salesOrder = ?', (node_id,), one=True)
    if node_type == 'Delivery':
        return query_db('SELECT * FROM outbound_delivery_headers WHERE deliveryDocument = ?', (node_id,), one=True)
    if node_type == 'Billing':
        return query_db('SELECT * FROM billing_document_headers WHERE billingDocument = ?', (node_id,), one=True)
    if node_type == 'JournalEntry':
        return query_db('SELECT * FROM journal_entry_items_accounts_receivable WHERE accountingDocument = ?', (node_id,), one=True)
    if node_type == 'BusinessPartner':
        return query_db('SELECT * FROM business_partners WHERE businessPartner = ?', (node_id,), one=True)
    if node_type == 'Product':
        return query_db('SELECT * FROM products WHERE product = ?', (node_id,), one=True)
    return None

def expand_node(node_type: str, node_id: str):
    nodes = []
    edges = []
    
    def add_node(ntype, nid, label):
        nodes.append({"id": f"{ntype}_{nid}", "type": ntype, "label": f"{ntype}: {label}", "data": {"id": nid}})
        
    def add_edge(src, tgt, label):
        edges.append({"source": src, "target": tgt, "label": label})

    # Base expansion logic (simplified for O2C flow)
    if node_type == 'SalesOrder':
        # Find Delivery
        deliveries = query_db('SELECT DISTINCT deliveryDocument FROM outbound_delivery_items WHERE referenceSDDocument = ?', (node_id,))
        for d in deliveries:
            add_node('Delivery', d['deliveryDocument'], d['deliveryDocument'])
            add_edge(f"SalesOrder_{node_id}", f"Delivery_{d['deliveryDocument']}", "has_delivery")
            
        # Find billing if directly associated
        billings = query_db('SELECT DISTINCT billingDocument FROM billing_document_items WHERE referenceSDDocument = ?', (node_id,))
        for b in billings:
            add_node('Billing', b['billingDocument'], b['billingDocument'])
            add_edge(f"SalesOrder_{node_id}", f"Billing_{b['billingDocument']}", "has_billing")

        # Find Business Partner
        bp = query_db('SELECT soldToParty FROM sales_order_headers WHERE salesOrder = ?', (node_id,), one=True)
        if bp and bp['soldToParty']:
            add_node('BusinessPartner', bp['soldToParty'], bp['soldToParty'])
            add_edge(f"SalesOrder_{node_id}", f"BusinessPartner_{bp['soldToParty']}", "ordered_by")
            
        # Find items & products
        items = query_db('SELECT material FROM sales_order_items WHERE salesOrder = ?', (node_id,))
        for i in items:
            add_node('Product', i['material'], i['material'])
            add_edge(f"SalesOrder_{node_id}", f"Product_{i['material']}", "contains_product")

    elif node_type == 'Delivery':
        # Find Billing
        billings = query_db('SELECT DISTINCT billingDocument FROM billing_document_items WHERE referenceSDDocument = ?', (node_id,))
        for b in billings:
            add_node('Billing', b['billingDocument'], b['billingDocument'])
            add_edge(f"Delivery_{node_id}", f"Billing_{b['billingDocument']}", "has_billing")
            
    elif node_type == 'Billing':
        # Find Journal Entry
        jes = query_db('SELECT DISTINCT accountingDocument, companyCode FROM journal_entry_items_accounts_receivable WHERE referenceDocument = ?', (node_id,))
        for je in jes:
            add_node('JournalEntry', je['accountingDocument'], je['accountingDocument'])
            add_edge(f"Billing_{node_id}", f"JournalEntry_{je['accountingDocument']}", "has_journal")

    return {"nodes": nodes, "edges": edges}

def get_initial_graph():
    # Return a handful of initial sales orders to start exploring
    nodes = []
    edges = []
    orders = query_db('SELECT salesOrder FROM sales_order_headers LIMIT 5')
    for o in orders:
        nodes.append({"id": f"SalesOrder_{o['salesOrder']}", "type": "SalesOrder", "label": f"SO {o['salesOrder']}"})
        expanded = expand_node("SalesOrder", o['salesOrder'])
        nodes.extend(expanded['nodes'])
        edges.extend(expanded['edges'])
        
    # Deduplicate nodes and edges
    unique_nodes = list({n['id']: n for n in nodes}.values())
    unique_edges = [dict(t) for t in {tuple(d.items()) for d in edges}]
    
    return {"nodes": unique_nodes, "edges": unique_edges}
