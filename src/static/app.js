let network;
let nodes = new vis.DataSet([]);
let edges = new vis.DataSet([]);
let currentNode = null;

const colorMap = {
    'SalesOrder': '#4e79a7',
    'Delivery': '#f28e2b',
    'Billing': '#e15759',
    'JournalEntry': '#76b7b2',
    'BusinessPartner': '#59a14f',
    'Product': '#edc948'
};

document.addEventListener("DOMContentLoaded", () => {
    initGraph();
    loadInitialGraph();

    document.getElementById("send-btn").addEventListener("click", sendMessage);
    document.getElementById("chat-input").addEventListener("keypress", (e) => {
        if (e.key === "Enter") sendMessage();
    });
    
    document.getElementById("expand-btn").addEventListener("click", () => {
        if(currentNode) {
            expandNode(currentNode.type, currentNode.id);
        }
    });
});

function initGraph() {
    const container = document.getElementById("network-graph");
    const data = { nodes: nodes, edges: edges };
    const options = {
        nodes: {
            shape: 'dot',
            size: 15,
            font: { size: 12 }
        },
        edges: {
            arrows: 'to',
            color: { inherit: 'to', opacity: 0.6 },
            font: { size: 10, align: 'middle' }
        },
        physics: {
            forceAtlas2Based: { gravitationalConstant: -50, centralGravity: 0.01, springLength: 100 },
            minVelocity: 0.75
        }
    };
    
    network = new vis.Network(container, data, options);
    
    network.on("click", function (params) {
        if (params.nodes.length > 0) {
            const nodeId = params.nodes[0];
            const node = nodes.get(nodeId);
            showNodeDetails(node.type, node.data.id);
        } else {
            closePopup();
        }
    });
}

function processGraphData(data) {
    const newNodes = [];
    data.nodes.forEach(n => {
        if (!nodes.get(n.id)) {
            newNodes.push({
                ...n,
                color: colorMap[n.type] || '#999'
            });
        }
    });
    nodes.add(newNodes);
    
    const newEdges = [];
    data.edges.forEach(e => {
        const edgeId = `${e.source}_${e.target}`;
        if (!edges.get(edgeId)) {
            newEdges.push({
                id: edgeId,
                ...e
            });
        }
    });
    edges.add(newEdges);
}

async function loadInitialGraph() {
    try {
        const res = await fetch("/api/graph/initial");
        const data = await res.json();
        processGraphData(data);
    } catch (e) {
        console.error("Error loading initial graph", e);
    }
}

async function showNodeDetails(type, id) {
    currentNode = { type, id };
    try {
        const res = await fetch(`/api/graph/node/${type}/${id}`);
        const data = await res.json();
        
        document.getElementById("popup-title").innerText = `${type} Details`;
        const content = document.getElementById("popup-content");
        content.innerHTML = "";
        
        for (const [key, value] of Object.entries(data)) {
            if(value !== null && value !== "") {
                content.innerHTML += `<div class="data-row"><span class="data-key">${key}:</span> ${value}</div>`;
            }
        }
        
        document.getElementById("node-popup").classList.remove("hidden");
    } catch (e) {
        console.error("Error fetching node info", e);
    }
}

async function expandNode(type, id) {
    try {
        const res = await fetch(`/api/graph/expand/${type}/${id}`);
        const data = await res.json();
        processGraphData(data);
    } catch (e) {
        console.error("Error expanding graph", e);
    }
}

function closePopup() {
    document.getElementById("node-popup").classList.add("hidden");
    currentNode = null;
}

async function sendMessage() {
    const input = document.getElementById("chat-input");
    const msg = input.value.trim();
    if (!msg) return;
    
    appendMessage(msg, "user-msg", "U");
    input.value = "";
    
    // Show typing...
    const msgDiv = document.createElement("div");
    msgDiv.className = `message system-msg loading`;
    msgDiv.innerHTML = `<div class="avatar">D</div><div class="text">Analyzing...</div>`;
    document.getElementById("chat-history").appendChild(msgDiv);
    msgDiv.scrollIntoView();

    try {
        const res = await fetch("/api/chat", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({message: msg})
        });
        const data = await res.json();
        
        msgDiv.remove();
        appendMessage(data.reply, "system-msg", "D");
    } catch (e) {
        msgDiv.remove();
        appendMessage("Sorry, an error occurred while connecting to the system.", "system-msg", "D");
    }
}

function appendMessage(text, className, avatarLetter) {
    const history = document.getElementById("chat-history");
    const msgDiv = document.createElement("div");
    msgDiv.className = `message ${className}`;
    msgDiv.innerHTML = `<div class="avatar">${avatarLetter}</div><div class="text"></div>`;
    // Prevent XSS
    msgDiv.querySelector('.text').innerText = text;
    history.appendChild(msgDiv);
    history.scrollTop = history.scrollHeight;
}