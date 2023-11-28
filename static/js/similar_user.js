// Set up the SVG and the force simulation
const width = window.innerWidth;
const height = window.innerHeight;
const svg = d3.select('#visualization').append('svg')
    .attr('width', width)
    .attr('height', height);


window.onload = function() {
    fetch('/clear_explored_users', {
        method: 'POST',
    })
    .then(response => response.json())
    .then(data => console.log(data))
    .catch((error) => {
        console.error('Error:', error);
    });
};

// let nodes = [
//     { id: 'miranta8', size: 50, fx: width / 2, fy: height / 2, imageURL: 'https://lastfm.freetls.fastly.net/i/u/64s/da96584a76354358c3bc7b3fccaefb40.png'} // Start user
// ];

let nodes = [];

function getFirstNode(username) {
    console.log(username);
    fetch(`/get_user_image/${username}`)
        .then(response => response.json())
        .then(data => {
            nodes.push({ id: username, size: 50, fx: width / 2, fy: height / 2, imageURL: data })

            let linkSelection = svg.selectAll('.link');
            let nodeGroups = svg.selectAll('.node-group');

            let links = [];

            let isFetching = false;

            console.log(nodes)

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

                nodeGroups.selectAll('image')
                    .data(d => [d]) // Pass the parent node data down to the children
                    .join('image')
                    .attr('class', 'node')
                    .attr('xlink:href', d => d.imageURL) // Set the image URL
                    .attr('x', d => -d.size) // Center the image horizontally
                    .attr('y', d => -d.size) // Center the image vertically
                    .attr('height', d => d.size * 2) // Set the image height
                    .attr('width', d => d.size * 2); // Set the image width

                nodeGroups.selectAll('text')
                    .data(d => [d])
                    .join('text')
                    .attr('class', 'node-text')
                    .text(d => d.id)
                    .attr('x', d => -d.size / 2)
                    .attr('y', d => 4 * d.size)
                    .attr('text-anchor', 'middle')
                    .attr('transform', 'translate(0, 10)')
                    .style('font-family', "'Outfit', sans-serif")
                    .style('font-size', '1rem')
                    .style('font-weight', 'bold')
                    .style('pointer-events', 'all') // Make sure the text element is clickable
                    .on('click', (event, d) => {
                        // Using a direct call to window.open to avoid any delays
                        window.open(`https://www.last.fm/user/${d.id}`, '_blank');
                    });

                nodeGroups.style('cursor', 'pointer');

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



                const size = d.size + 5; // The size of the square
                const squarePath = `M ${-size} ${-size} H ${size} V ${size} H ${-size} Z`; // The path for the square
                
                const progressBar = d3.select(this).append('path')
                    .attr('class', 'progress-bar')
                    .attr('d', squarePath) // Set the path
                    .attr('transform', `translate(${d.x}, ${d.y})`) // Position the square
                    .attr('stroke-width', 5)
                    .attr('fill', 'none')
                    .attr('stroke', '#335778');

                const progressBarDuration = 30000; // Initial duration for the progress bar


                const circumference = 2 * Math.PI * progressBar.attr('r');
                progressBar.attr('stroke-dasharray', `${circumference} ${circumference}`)
                    .attr('stroke-dashoffset', circumference);

                const pathLength = progressBar.node().getTotalLength();
                progressBar.attr('stroke-dasharray', `${pathLength} ${pathLength}`)
                    .attr('stroke-dashoffset', pathLength);
                
                // Animate the progress bar
                progressBar.transition()
                    .duration(progressBarDuration)  // Duration of the fetch operation
                    .ease(d3.easeCubicOut)  // Apply an easing function to slow down progress over time
                    .attr('stroke-dashoffset', 0)
                    .on('end', () => {
                        progressBar.remove();  // Remove the progress bar when the fetch operation is done
                    });

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
                        for (let i = 0; i < 7; i++) {
                            console.log(data[i]);
                            let angle = angleIncrement * i; // angle for this node
                            let newNode = {
                                id: `${data[i].username}`,
                                size: data[i].similarity_score,
                                // Calculate the x, y position based on angle and a fixed radius
                                x: d.x + Math.cos(angle) * 100,
                                y: d.y + Math.sin(angle) * 100,
                                imageURL: data[i].imageURL
                            };
                            nodes.push(newNode);
                            links.push({ source: d.id, target: newNode.id });
                        }

                        // After the fetch operation is complete, hide the progress bar and clear the flag
                        document.getElementById('progress-bar').style.display = 'none';

                        //After the fetch operation is complete, clear the circle progress bar
                        progressBar.remove();

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
                nodeSelection = nodeGroups.select('image')
                    .attr('x', d => d.x - d.size)
                    .attr('y', d => d.y - d.size);

                nodeGroups.select('text')
                    .attr('x', d => d.x)
                    .attr('y', d => d.y + d.size + 15);


                nodeGroups.select('.progress-bar')
                .attr('transform', d => `translate(${d.x}, ${d.y})`);

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
        });
}

url_elements = window.location.href.split("/");
getFirstNode(url_elements[url_elements.length - 1]);

