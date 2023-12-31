// Set up the SVG and the force simulation
const width = window.innerWidth;
const height = window.innerHeight;
const svg = d3.select('#visualization').append('svg')
    .attr('width', 10000)
    .attr('height', 10000);
const legend_svg = d3.select('#visualization').append('svg')
    .attr('id', 'legend_svg')
    .attr('width', width)
    .attr('height', height);

console.log(width);
console.log(height)

window.onload = function() {
    let url_elements = window.location.href.split("/");
    let username = url_elements[url_elements.length - 1];
    document.getElementById("b-color-pink").style.setProperty("z-index", "-10");
    document.getElementById("b-color-pink").style.setProperty("opacity", "0");
    document.getElementById("background-title").style.setProperty("opacity", "0.1");
    document.getElementById("background-title").style.setProperty("transform", "none");
    document.getElementById("navigation_select").value = "similar_user";
    document.getElementById("background-title").innerHTML = "SIMILAR<br />USER";
    document.getElementById("b-color").style.setProperty("opacity", "1");
    document.getElementById("instruction").style.setProperty("z-index", "11");
    document.getElementById("instruction").style.setProperty("opacity", "0.8");
    document.getElementById("totop").style.setProperty("opacity", "0.8");
    document.getElementById("totop").style.setProperty("z-index", "11");
    var types = [
        {type: 'user', color: 'url(#pinkGradient)'},
    ];
    fetch(`/clear_explored_users/${username}`, {
        method: 'POST',
    })
    .then(response => response.json())
    .then(data => console.log(data))
    .catch((error) => {
        console.error('Error:', error);
    });

    var legend = legend_svg.selectAll('.legend')
    .data(types)
    .enter().append('g')
    .attr('class', 'legend')
    .attr('transform', function(d, i) { return 'translate(-30,' + (i * 40 + 30) + ')'; })
    .style('opacity', 0); // initially set the opacity to 0

    // Transition the opacity to 1 over 1 second
    legend.transition()
        .duration(3000)
        .style('opacity', 1);

    // Append a circle to each g
    legend.append('circle')
        .attr('cx', width - 18)
        .attr('r', 12)
        .style('fill', 'none') // make the circle hollow
        .style('stroke', d => d.color) // color the circle's outline
        .style('stroke-width', 5);

    // Apply the filter to your text
    legend.append('text')
        .attr('x', width - 37)
        .attr('y', 4)
        .attr('dy', '.35em')
        .style('text-anchor', 'end')
        .style('fill', 'white')
        .style('font-size', '15px')
        .style('font-weight', 'bold')
        .text(d => d.type);

};

// let nodes = [
//     { id: 'miranta8', size: 50, fx: width / 2, fy: height / 2, imageURL: 'https://lastfm.freetls.fastly.net/i/u/64s/da96584a76354358c3bc7b3fccaefb40.png'} // Start user
// ];

let nodes = [];

function navigateTo(page) {
    document.getElementById("instruction").style.setProperty("opacity", "0");
    document.getElementById("totop").style.setProperty("opacity", "0");
    document.getElementById("b-color").style.setProperty("opacity", "0");
    document.getElementById("b-color-pink").style.setProperty("z-index", "10");
    document.body.style.setProperty("background", "rgb(225, 211, 230)");
    document.getElementById("b-color-pink").style.setProperty("opacity", "1");
    let warning_text = document.getElementById("warning-text");
    if (warning_text != null) {
        warning_text.style.setProperty("transition-duration", "3s");
        setTimeout(function() {
            warning_text.style.setProperty("opacity", "0");
        }, 100);
    }
    setTimeout(function()
        {
            if (page) {
                url_elements = window.location.href.split("/");
                let username = url_elements[url_elements.length - 1];
                window.location.href = window.location.origin + '/' + page + '/' + username;
            }
        }, 3000);
}

function getFirstNode(username) {
    console.log(username);
    fetch(`/get_user_image/${username}`)
        .then(response => response.json())
        .then(data => {
            nodes.push({ id: username, size: 30, fx: width / 2, fy: height / 2, imageURL: data, transformed: false, clickable: true, first: true })

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
                
                var gradient = svg.append("defs")
                    .append("linearGradient")
                    .attr("id", "pinkGradient")
                    .attr("x1", "0%")
                    .attr("y1", "0%")
                    .attr("x2", "100%")
                    .attr("y2", "100%");

                    gradient.append("stop")
                    .attr("offset", "0%")
                    .attr("stop-color", "LightPink");

                    gradient.append("stop")
                    .attr("offset", "100%")
                    .attr("stop-color", "DeepPink");

                var circle = nodeGroups.selectAll('circle')
                    .data(d => [d]) // Pass the parent node data down to the children
                    .join('circle')
                    .attr('class', 'node-circle')
                    .attr('cx', d => d.x) // Position the circle at the node's center
                    .attr('cy', d => d.y)
                    .attr("r", function(d) { 
                        if (d.transformed == true) {
                            return d.size  + 5;
                        } else {
                            return d.size/2 + 5;
                        }
                    }) 
                    .style('fill', 'none') // No fill for hollow effect
                    .style('stroke', 'url(#pinkGradient)') // Light purple stroke color                    
                    .style('stroke-width', 2)
                    .style('opacity', d => {
                        if (d.transformed == true){
                            return 1;
                        } else {
                            return 0;
                        }
                    });

                circle.transition()
                    .duration(1000)
                    .style('opacity', 1)
                    .attr("r", function(d) { return d.size + 5; });  // Set the circle radius


                
                nodeGroups.selectAll('image')
                    .data(d => [d]) // Pass the parent node data down to the children
                    .join('image')
                    .attr('id', d => d.id)
                    .attr('class', 'node')
                    .attr('xlink:href', d => d.imageURL) // Set the image URL
                    .attr('x', d => -d.size) // Center the image horizontally
                    .attr('y', d => -d.size) // Center the image vertically
                    .attr('height', d => {
                        if (d.transformed == true) {
                            return d.size * 2;
                        } else {
                            return d.size;
                        }
                    }) // Set the image height
                    .attr('width', d => {
                        if (d.transformed == true) {
                            return d.size * 2;
                        } else {
                            return d.size;
                        }
                    }) // Set the image width
                    .style('pointer-events', 'none')
                    .style('clip-path', 'circle(50%)') // Make the image circular
                    .style('opacity', d => {
                        if (d.transformed == true){
                            return 1;
                        } else {
                            return 0;
                        }
                    });
                
                nodeGroups.selectAll('image')
                    .data(d => [d])
                    .transition()
                    .duration(1000)
                    .style('opacity', 1)
                    .style('pointer-events', 'all')
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
                    .style('opacity', d => {
                        if (d.transformed == true) {
                            return 1;
                        } else {
                            return 0;
                        }
                    })
                    .on('click', (event, d) => {
                        // Using a direct call to window.open to avoid any delays
                        window.open(`https://www.last.fm/user/${d.id}`, '_blank');
                        event.stopPropagation(); // Stop the click event from bubbling up to the parent node group
                    });
                
                    nodeGroups.selectAll('text')
                        .data(d => [d])
                        .transition()
                        .duration(1000)
                        .delay(500)
                        .style('opacity', 1);

                    for (let i = 0; i < nodes.length; i++) {
                        nodes[i].transformed = true;
                    }

                nodeGroups.style('cursor', 'pointer');

                // Add click event to nodeGroups
                nodeGroups.on('click', expandNode);

                // Update the link selection
                linkSelection = svg.selectAll('.link')
                    .data(links)
                    .join('line')
                    .attr('class', 'link')
                    .style('opacity', 0.5)
                    .style('stroke-width', 1)
                    .style('stroke', '#335778');

                // Update and restart the simulation
                simulation.nodes(nodes);
                simulation.force('link').links(links);
                simulation.alpha(1).restart();
            }


            // Function to expand nodes
            function expandNode(event, d) {
                // Prevent the simulation from moving nodes around when adding new ones
                simulation.stop();
                if (!d.clickable) return;
                // each node only clickable once
                d.clickable = false;
                if (isFetching) return;  // If a fetch operation is in progress, ignore the event

                isFetching = true;
                document.getElementById('progress-bar').style.display = 'block';  // Show the progress bar

                d3.select(this).select('.error-text').remove();


                const radius = d.size + 5; // The radius of the circle
                const circlePath = `
                    M ${-radius}, 0
                    a ${radius},${radius} 0 1,0 ${2*radius},0
                    a ${radius},${radius} 0 1,0 ${-2*radius},0
                `;
            
                const gradient = d3.select('svg').append('defs')
                .append('linearGradient')
                .attr('id', 'gradient')
                .attr('x1', '0%')
                .attr('y1', '0%')
                .attr('x2', '100%')
                .attr('y2', '0%');
            
                // Define the color stops of the gradient
                gradient.append('stop')
                .attr("offset", "0%")
                .attr("stop-color", "DeepPink");

            
                gradient.append('stop')
                .attr("offset", "100%")
                .attr("stop-color", "MediumVioletRed");


                const progressBar = d3.select(this).append('path')
                    .attr('class', 'progress-bar')
                    .attr('d', circlePath) // Set the path
                    .attr('transform', `translate(${d.x}, ${d.y})`) // Position the circle
                    .attr('stroke-width', 5)
                    .attr('fill', 'none')
                    .attr('stroke', 'url(#gradient)');

                const progressBarDuration = 32000; // Initial duration for the progress bar


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
                        // Check if data is empty
                        if (data === null || data.length === 0) {
                            console.log('No data returned from server');
                            // eliminate the progress bar
                            progressBar.remove();
                            isFetching = false;
                            document.getElementById('progress-bar').style.display = 'none';
                            // Display a message to the user
                            let bodyGroup = document.body;
                            const warning = document.createElement('text');
                            warning.style.setProperty("font-family", "'Outfit', sans-serif");
                            warning.style.setProperty("font-size", "1.5rem");
                            warning.style.setProperty("color", "#fc46aa");
                            warning.style.setProperty("position", "fixed");
                            warning.style.setProperty("text-anchor", "middle");
                            warning.style.setProperty("top", "90vh");
                            warning.style.setProperty("left", "calc(50vw - 18rem)");
                            warning.style.setProperty("z-index", "8");
                            warning.style.setProperty("font-weight", "bold");
                            warning.style.setProperty("opacity", "0");
                            warning.style.setProperty("pointer-events", "none");
                            warning.style.setProperty("transition-duration", "1s");
                            warning.id = "warning-text";
                            warning.innerHTML = 'Expansion progress failed due to insufficient data.';
                            bodyGroup.appendChild(warning);
                            setTimeout(function()
                            {
                                document.getElementById("warning-text").style.setProperty("opacity", "0.5");
                            }, 100);
                            return;
                        }        

                        if(d.first == true){   
                            // Logic to add new nodes connected to the clicked node
                            let angleIncrement = (2 * Math.PI) / 7; // Distribute nodes evenly in a circle
                            for (let i = 0; i < 7; i++) {
                                console.log(data[i]);
                                let angle = angleIncrement * i; // angle for this node
                                let newNode = {
                                    id: `${data[i].username}`,
                                    size: data[i].similarity_score,
                                    // Calculate the x, y position based on angle and a fixed radius
                                    x: d.x + Math.cos(angle) * 100,
                                    y: d.y + Math.sin(angle) * 100,
                                    imageURL: data[i].imageURL,
                                    transformed: false,
                                    first: false,
                                    clickable: true,
                                    parentnode: d
                                };
                                nodes.push(newNode);
                                links.push({ source: d.id, target: newNode.id });
                            }
                        } else {
                            // Logic to add new nodes connected to the clicked node
                            let angleIncrement =  Math.PI / 5; // Distribute nodes evenly in a half circle
                            let parentAngle = Math.atan2(d.y - d.parentnode.y , d.x - d.parentnode.x);
                            for (let i = 0; i < 5; i++) {
                                console.log(data[i]);
                                let angle = parentAngle + angleIncrement * i -  Math.PI / 2; // angle for this node
                                let newNode = {
                                    id: `${data[i].username}`,
                                    size: data[i].similarity_score,
                                    // Calculate the x, y position based on angle and a fixed radius
                                    x: d.x + Math.cos(angle) * 100,
                                    y: d.y + Math.sin(angle) * 100,
                                    imageURL: data[i].imageURL,
                                    transformed: false,
                                    first: false,
                                    clickable: true,
                                    parentnode: d
                                };
                                nodes.push(newNode);
                                links.push({ source: d.id, target: newNode.id });
                            }


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
                
                nodeGroups.select('circle')
                    .attr('cx', d => d.x)
                    .attr('cy', d => d.y);



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

function instructionSwitch() {
    let instruction_but = document.getElementById("instruction");
    if (instruction_but.innerHTML == "<b>How to use?</b>") {
        instruction_but.innerHTML = "Welcome to <b>Similar User</b> mode!<br /><b>Click on Avatars</b> to expand the tree to find users similar to you<br /><b>Click on the names</b> to jump to last.fm if you're interested!<br />Enjoy!!";
    } else {
        instruction_but.innerHTML = "<b>How to use?</b>";
    }
}

function scroll_Top() {
    window.scrollTo({top: 0, left: 0, behavior: 'smooth'});
}

url_elements = window.location.href.split("/");
getFirstNode(url_elements[url_elements.length - 1]);