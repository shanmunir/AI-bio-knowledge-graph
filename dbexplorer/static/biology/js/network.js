let cy;

// Function to fetch data from the server
async function fetchData(url) {
    try {
        const response = await fetch(url);
        if (!response.ok) throw new Error(`Error ${response.status}: ${response.statusText}`);
        return await response.json();
    } catch (error) {
        console.error(`Failed to fetch ${url}:`, error);
        return null;
    }
}

// Function to initialize the Cytoscape network
function initializeNetwork() {
    // Initialize the Cytoscape graph container
    cy = cytoscape({
        container: document.getElementById('network'),
        elements: [ // Initial root node "species"
            { data: { id: 'species', label: 'Species' } } // Root node
        ],
        style: [ // Define node and edge styles
            { selector: 'node', style: { label: 'data(label)', 'background-color': '#61bffc' } },
            { selector: 'edge', style: { width: 2, 'line-color': '#ccc' } }
        ],
        layout: { name: 'breadthfirst' } // Arrange nodes in a tree-like structure
    });

    // Fetch species data dynamically from the backend
    fetchData('/network/get_species/').then(data => {
        if (data && data.nodes) {
            // Map the species data to create child nodes for the "Species" node
            const speciesNodes = data.nodes.map(name => ({ data: { id: name, label: name, parent: 'species' } }));

            // Add the species nodes to the graph
            cy.add(speciesNodes);
            cy.layout({ name: 'breadthfirst' }).run(); // Re-layout the nodes
        } else {
            console.error('No species data received.');
        }
    });
}

// Event listener to run once the DOM is fully loaded
document.addEventListener('DOMContentLoaded', initializeNetwork);
