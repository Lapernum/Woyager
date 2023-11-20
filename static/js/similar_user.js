// Set up the SVG and the force simulation
const width = window.innerWidth;
const height = window.innerHeight;
const svg = d3.select('#visualization').append('svg')
    .attr('width', width)
    .attr('height', height);



let nodes = [
    { id: 'miranta8', size: 30, fx: width / 2, fy: height / 2  } // Start user
];

let linkSelection = svg.selectAll('.link');
let nodeGroups = svg.selectAll('.node-group');

let links = [];

let isFetching = false;


const simulation = d3.forceSimulation(nodes)
    .force('link', d3.forceLink(links).id(d => d.id).distance(300)) // Increase the distance as needed
    .force('charge', d3.forceManyBody().strength(-100))
    .force('center', d3.forceCenter(width / 2, height / 2));

// Function to update the visualization
function update() {
    // Join the updated nodes data to the groups
    nodeGroups = svg.selectAll('.node-group')
        .data(nodes, d => d.id)
        .join('g')
        .attr('class', 'node-group')
        .call(drag);

    // Append circles to each group if they don't already exist
    nodeGroups.selectAll('circle')
        .data(d => [d]) // Pass the parent node data down to the children
        .join('circle')
        .attr('class', 'node')
        .attr('r', d => d.size);

    // Append text to each group if it doesn't already exist
    nodeGroups.selectAll('text')
        .data(d => [d]) // Pass the parent node data down to the children
        .join('text')
        .attr('class', 'node-text')
        .text(d => d.id)
        .attr('x', 0)  // Center the text horizontally
        .attr('y', 3)  // Center the text vertically
        .attr('text-anchor', 'middle');  // Center the text around (x, y)

    // Add click event to nodeGroups
    nodeGroups.on('click', expandNode);

    // Update the link selection
    linkSelection = svg.selectAll('.link')
        .data(links)
        .join('line')
        .attr('class', 'link');

    // Update and restart the simulation
    simulation.nodes(nodes);
    simulation.force('link').links(links);
    simulation.alpha(1).restart();
}


// Function to expand nodes
function expandNode(event, d) {
    // Prevent the simulation from moving nodes around when adding new ones
    simulation.stop();

    if (isFetching) return;  // If a fetch operation is in progress, ignore the event

    isFetching = true;
    document.getElementById('progress-bar').style.display = 'block';  // Show the progress bar

    // Fetch data from the server
    fetch(`/get_data/${d.id}`)
        .then(response => response.json())
        .then(data => {
            if (typeof data === 'string') {
                try {
                    data = JSON.parse(data);
                } catch (error) {
                    console.error('Failed to parse data as JSON:', error);
                    return;
                }
            }
            // Logic to add new nodes connected to the clicked node
            let angleIncrement = (2 * Math.PI) / 10; // Distribute nodes evenly in a circle
            for (let i = 0; i < 10; i++) {
                console.log(data[i]);
                let angle = angleIncrement * i; // angle for this node
                let newNode = {
                    id: `${data[i].username}`,
                    size: data[i].similarity_score,
                    // Calculate the x, y position based on angle and a fixed radius
                    x: d.x + Math.cos(angle) * 100,
                    y: d.y + Math.sin(angle) * 100,
                };
                nodes.push(newNode);
                links.push({ source: d.id, target: newNode.id });
            }

            // After the fetch operation is complete, hide the progress bar and clear the flag
            document.getElementById('progress-bar').style.display = 'none';
            isFetching = false;

            // Update the simulation with the new nodes and links
            
            update();
        })

}

// Drag functionality
const drag = d3.drag()
    .on('start', (event, d) => {
        if (!event.active) simulation.alphaTarget(0.3).restart();
        d.fx = event.x;
        d.fy = event.y;
    })
    .on('drag', (event, d) => {
        d.fx = event.x;
        d.fy = event.y;
    })
    .on('end', (event, d) => {
        if (!event.active) simulation.alphaTarget(0);
        d.fx = null;
        d.fy = null;
    });

// Handle the simulation "tick" event
simulation.on('tick', () => {
    nodeSelection = nodeGroups.select('circle')
        .attr('cx', d => d.x)
        .attr('cy', d => d.y);

    nodeGroups.select('text')
        .attr('x', d => d.x)
        .attr('y', d => d.y + 3); // Adjust the y-offset as needed

    linkSelection.attr('x1', d => {
                     let dx = d.target.x - d.source.x;
                     let dy = d.target.y - d.source.y;
                     let angle = Math.atan2(dy, dx);
                     return d.source.x + Math.cos(angle) * d.source.size;
                 })
                 .attr('y1', d => {
                     let dx = d.target.x - d.source.x;
                     let dy = d.target.y - d.source.y;
                     let angle = Math.atan2(dy, dx);
                     return d.source.y + Math.sin(angle) * d.source.size;
                 })
                 .attr('x2', d => {
                     let dx = d.target.x - d.source.x;
                     let dy = d.target.y - d.source.y;
                     let angle = Math.atan2(dy, dx);
                     return d.target.x - Math.cos(angle) * d.target.size;
                 })
                 .attr('y2', d => {
                     let dx = d.target.x - d.source.x;
                     let dy = d.target.y - d.source.y;
                     let angle = Math.atan2(dy, dx);
                     return d.target.y - Math.sin(angle) * d.target.size;
                 });
});
// Initial update call
update();