// Set up the SVG and the force simulation
const width = window.innerWidth;
const height = window.innerHeight;
const svg = d3.select('#visualization').append('svg')
    .attr('width', 20000)
    .attr('height', 30000);

window.scrollTo(0, 0);

let nodes = [];

window.onload = function() {
    document.getElementById("b-color-pink").style.setProperty("z-index", "-10");
    document.getElementById("b-color-pink").style.setProperty("opacity", "0");
    document.getElementById("background-title").style.setProperty("opacity", "0.1");
    document.getElementById("background-title").style.setProperty("transform", "none");
    document.getElementById("navigation_select").value = "self_listening";
    document.getElementById("background-title").innerHTML = "SELF<br />LISTENING";
    document.getElementById("b-color").style.setProperty("opacity", "1");
    document.getElementById("instruction").style.setProperty("opacity", "0.8");
    document.getElementById("instruction").style.setProperty("z-index", "11");
    document.getElementById("totop").style.setProperty("opacity", "0.8");
    document.getElementById("totop").style.setProperty("z-index", "11");
    var types = [
        {type: 'tag', color: 'url(#lightBlueGradient)'},
        {type: 'artist', color: 'url(#pinkGradient)'},
        {type: 'user', color: 'url(#lightPurpleGradient)'},
        {type: 'track', color: 'url(#blueGradient)'},
    ];
    
    var legend = svg.selectAll('.legend')
    .data(types)
    .enter().append('g')
    .attr('class', 'legend')
    .attr('transform', function(d, i) { return 'translate(-20,' + (i * 30 + 20) + ')'; })
    .style('opacity', 0); // initially set the opacity to 0

    // Transition the opacity to 1 over 1 second
    legend.transition()
        .duration(1000)
        .style('opacity', 1);

    // Append a circle to each g
    legend.append('circle')
        .attr('cx', width - 18)
        .attr('r', 12)
        .style('fill', 'none') // make the circle hollow
        .style('stroke', d => d.color) // color the circle's outline
        .style('stroke-width', 3);

    // Apply the filter to your text
    legend.append('text')
        .attr('x', width - 35)
        .attr('y', 4)
        .attr('dy', '.35em')
        .style('text-anchor', 'end')
        .style('fill', 'white')
        .style('font-size', '15px')
        .text(d => d.type);
}

function navigateTo(page) {
    document.getElementById("instruction").style.setProperty("opacity", "0");
    document.getElementById("totop").style.setProperty("opacity", "0");
    document.getElementById("b-color").style.setProperty("opacity", "0");
    document.getElementById("b-color-pink").style.setProperty("z-index", "10");
    document.body.style.setProperty("background", "rgb(225, 211, 230)");
    document.getElementById("b-color-pink").style.setProperty("opacity", "1");
    fetch('/clear_explored_users', {
        method: 'POST',
    })
    .then(response => response.json())
    .then(data => console.log(data))
    .catch((error) => {
        console.error('Error:', error);
    });

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
    // fetch(`/targets/${username}`)
    //     .then(response => response.json())
    //     .then(data => {
    //         // Handle the data
    //         console.log('Artists:', data.artist);
    //         console.log('Tags:', data.tag)
    //     })
    //     .catch(error => {
    //         console.error('There was a problem with the fetch operation:', error);
    //     });
    fetch(`/get_user_image/${username}`)
        .then(response => response.json())
        .then(data => {
            nodes.push({ type: 'user', id: username, size: 30, fx: width / 2, fy: height / 2, imageURL: data, transformed: false, clickable: true })

            let linkSelection = svg.selectAll('.link');
            let nodeGroups = svg.selectAll('.node-group');

            let links = [];

            let isFetching = false;

            let newAddedNode = [];

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

                // Light blue gradient
                var lightBlueGradient = svg.append("defs")
                .append("linearGradient")
                .attr("id", "lightBlueGradient")
                .attr("x1", "0%")
                .attr("y1", "0%")
                .attr("x2", "100%")
                .attr("y2", "100%");

                lightBlueGradient.append("stop")
                .attr("offset", "0%")
                .attr("stop-color", "SkyBlue");
              
                lightBlueGradient.append("stop")
                .attr("offset", "100%")
                .attr("stop-color", "DeepSkyBlue");
                
                // Blue gradient
                var blueGradient = svg.append("defs")
                .append("linearGradient")
                .attr("id", "blueGradient")
                .attr("x1", "0%")
                .attr("y1", "0%")
                .attr("x2", "100%")
                .attr("y2", "100%");
                
                blueGradient.append("stop")
                .attr("offset", "0%")
                .attr("stop-color", "RoyalBlue");
              
                blueGradient.append("stop")
                .attr("offset", "100%")
                .attr("stop-color", "MidnightBlue");

                // Pink gradient
                var pinkGradient = svg.append("defs")
                .append("linearGradient")
                .attr("id", "pinkGradient")
                .attr("x1", "0%")
                .attr("y1", "0%")
                .attr("x2", "100%")
                .attr("y2", "100%");

                pinkGradient.append("stop")
                .attr("offset", "0%")
                .attr("stop-color", "LightPink");

                pinkGradient.append("stop")
                .attr("offset", "100%")
                .attr("stop-color", "DeepPink");

                // Light purple gradient
                var lightPurpleGradient = svg.append("defs")
                .append("linearGradient")
                .attr("id", "lightPurpleGradient")
                .attr("x1", "0%")
                .attr("y1", "0%")
                .attr("x2", "100%")
                .attr("y2", "100%");

                lightPurpleGradient.append("stop")
                .attr("offset", "0%")
                .attr("stop-color", "Thistle");

                lightPurpleGradient.append("stop")
                .attr("offset", "100%")
                .attr("stop-color", "MediumPurple");
                                
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
                    .style('stroke', d => {
                        switch(d.type) {
                            case 'tag':
                                return 'url(#lightBlueGradient)';
                            case 'artist':
                                return 'url(#pinkGradient)';
                            case 'user':
                                return 'url(#lightPurpleGradient)';
                            case 'track':
                                return 'url(#blueGradient)';
                            default:
                                return 'black';
                        }
                    })                    
                    .style('stroke-width', 3)
                    .style('opacity', d => {
                        if (d.transformed == true){
                            return 1;
                        } else {
                            return 0;
                        }
                    })

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
                        console.log(d)
                        if (d.type == 'tag') {
                            window.open(`https://www.last.fm/tag/${d.id}`, '_blank');
                        }
                        else if (d.type == 'artist') {
                            window.open(`https://www.last.fm/artist/${d.id}`, '_blank');
                        }
                        else if (d.type == 'user') {
                            window.open(`https://www.last.fm/user/${d.id}`, '_blank');
                        }
                        else {
                            window.open(`https://www.last.fm/music/${d.artist}/_/${d.track}`, '_blank')
                        }
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
                // nodeGroups.on('click', function(e, d) { expandNode(e, d) });

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

            function expandNode(event, d) {
                // Prevent the simulation from moving nodes around when adding new ones
                simulation.stop();
                if (!d.clickable) return;
                if (isFetching) return;  // If a fetch operation is in progress, ignore the event
                // only clickable once
                d.clickable = false;
                isFetching = true;
                document.getElementById('progress-bar').style.display = 'block';  // Show the progress bar


                // Define the circle path generator
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
            
                // Define the color stops of the progress bar gradient
                gradient.append('stop')
                .attr('offset', '0%')
                .attr('stop-color', 'MediumPurple');  // Lighter purple
            
                gradient.append('stop')
                .attr('offset', '100%')
                .attr('stop-color', 'Indigo');

                var deepLightPurpleGradient = svg.append("defs")
                .append("linearGradient")
                .attr("id", "deepLightPurpleGradient")
                .attr("x1", "0%")
                .attr("y1", "0%")
                .attr("x2", "100%")
                .attr("y2", "100%");

                deepLightPurpleGradient.append("stop")
                .attr("offset", "0%")
                .attr("stop-color", "MediumPurple");

                deepLightPurpleGradient.append("stop")
                .attr("offset", "100%")
                .attr("stop-color", "Purple");
                
                var deepLightBlueGradient = svg.append("defs")
                .append("linearGradient")
                .attr("id", "deepLightBlueGradient")
                .attr("x1", "0%")
                .attr("y1", "0%")
                .attr("x2", "100%")
                .attr("y2", "100%");

                deepLightBlueGradient.append("stop")
                .attr("offset", "0%")
                .attr("stop-color", "DodgerBlue");

                deepLightBlueGradient.append("stop")
                .attr("offset", "100%")
                .attr("stop-color", "MidnightBlue");

                // Deeper pink gradient
                var deepPinkGradient = svg.append("defs")
                .append("linearGradient")
                .attr("id", "deepPinkGradient")
                .attr("x1", "0%")
                .attr("y1", "0%")
                .attr("x2", "100%")
                .attr("y2", "100%");

                deepPinkGradient.append("stop")
                .attr("offset", "0%")
                .attr("stop-color", "DeepPink");

                deepPinkGradient.append("stop")
                .attr("offset", "100%")
                .attr("stop-color", "MediumVioletRed");

                var deepBlueGradient = svg.append("defs")
                .append("linearGradient")
                .attr("id", "deepBlueGradient")
                .attr("x1", "0%")
                .attr("y1", "0%")
                .attr("x2", "100%")
                .attr("y2", "100%");

                deepBlueGradient.append("stop")
                .attr("offset", "0%")
                .attr("stop-color", "RoyalBlue");

                deepBlueGradient.append("stop")
                .attr("offset", "100%")
                .attr("stop-color", "Navy");

                const progressBar = d3.select(this).append('path')
                    .attr('class', 'progress-bar')
                    .attr('d', circlePath) // Set the path
                    .attr('transform', `translate(${d.x}, ${d.y})`) // Position the circle
                    .attr('stroke-width', 5)
                    .attr('fill', 'none')
                    .attr('stroke', () => {
                        switch(d.type) {
                            case 'user':
                                return 'url(#deepLightPurpleGradient)';
                            case 'tag':
                                return 'url(#deepLightBlueGradient)';
                            case 'artist':
                                return 'url(#deepPinkGradient)';
                            default:
                                return 'url(#deepBlueGradient)';
                        }
                    });
                                
                    let progressBarDuration;

                    if (d.type == 'user') {
                        progressBarDuration = 13000; // Duration for the progress bar
                    }
                    else if (d.type == 'tag') {    
                        progressBarDuration = 6000; // Duration for the progress bar
                    }
                    else if (d.type == 'artist') {
                        progressBarDuration = 6200; // Duration for the progress bar
                    }

                

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
   
                if (d.type == 'user') {
                    // Fetch targets from server
                    fetch(`/targets/${encodeURIComponent(d.id)}`)
                        .then(response => response.json())
                        .then(data => {
                            artist = data['artist']
                            tag = data['tag']
                            
                            // add artists into node
                            let angleIncrement = (2 * Math.PI) / (artist.length + tag.length); // Distribute nodes evenly in a circle
                
                            let fetchPromises = artist.map((artistName, i) => {
                                console.log(artistName);
                                let angle = angleIncrement * i; // angle for this node
                
                                return fetch(`/get_artist_image/${encodeURIComponent(artistName)}`)
                                    .then(response => response.json())
                                    .then(data => {
                                        console.log(data)
                                        let newNode = {
                                            type: 'artist',
                                            id: `${artistName}`,
                                            size: 30,
                                            // Calculate the x, y position based on angle and a fixed radius
                                            x: d.x + Math.cos(angle) * 100,
                                            y: d.y + Math.sin(angle) * 100,
                                            imageURL: "https://drive.google.com/uc?id=16NKs6mWVua2sPqaDsaj7qo-oNyw36Yjs", //need to change
                                            transformed: false, 
                                            parent: d,
                                            clickable: true
                                        };
                                        nodes.push(newNode);
                                        links.push({ source: d.id, target: newNode.id });
                                    })
                                    .catch(error => {
                                        console.error('There was a problem with the artist image:', error);
                                    });
                            });
                
                            for (let i = 0; i < tag.length; i++) {
                                console.log(tag[i]);
                                let angle = angleIncrement * (i + artist.length); // angle for this node
                                let newNode = {
                                    type: 'tag',
                                    id: `${tag[i]}`,
                                    size: 30,
                                    // Calculate the x, y position based on angle and a fixed radius
                                    x: d.x + Math.cos(angle) * 100,
                                    y: d.y + Math.sin(angle) * 100,
                                    imageURL: "https://drive.google.com/uc?id=1HZ0V0q1x3iVlYMeF3M_245CEu6LZAg2G", //need to change
                                    transformed: false,
                                    parent: d,
                                    clickable: true
                                };
                                nodes.push(newNode);
                                links.push({ source: d.id, target: newNode.id });
                            }
                
                            return Promise.all(fetchPromises);
                        })
                        .then(() => {
                            // After the fetch operation is complete, hide the progress bar and clear the flag
                            document.getElementById('progress-bar').style.display = 'none';
                
                            //After the fetch operation is complete, clear the circle progress bar
                            progressBar.remove();
                
                            isFetching = false;
                
                            // Update the simulation with the new nodes and links
                            update();
                        })
                        .catch(error => {
                            console.error('There was a problem with the fetch operation:', error);
                        });
                }
                else if (d.type == 'tag') {
                    fetch(`/self_listening/targets/${encodeURIComponent(d.id)}`)
                        .then(response => response.json())
                        .then(data => {
                            console.log(data)
                            scores = data.scores
                            ten_songs = data.ten_songs
                
                            let angleIncrement = (2 * Math.PI) / 10; // Distribute nodes evenly in a circle
                
                            let fetchPromises = ten_songs.map((song, i) => {
                                let track = song['track_name'];
                                let artist = song['artist_name'];
                                let parentAngle = Math.atan2(d.y - d.parent.y , d.x - d.parent.x);
                                let angle = angleIncrement * i + parentAngle - Math.PI / 2;
                            
                                return fetch(`/get_track_image/${encodeURIComponent(artist)}/${encodeURIComponent(track)}`)
                                    .then(response => response.json())
                                    .then(data => {
                                        let newNode = {
                                            type: 'track',
                                            id: `${track}, by ${artist}`,
                                            artist: `${artist}`,
                                            track: `${track}`,
                                            size: 30 / scores[0]['score'] * scores[i]['score'],
                                            x: d.x + Math.cos(angle) * 100,
                                            y: d.y + Math.sin(angle) * 100,
                                            imageURL: data,
                                            parent: d,
                                            clickable: true
                                        };
                
                                        nodes.push(newNode);
                                        links.push({ source: d.id, target: newNode.id });
                                    });
                            });
                            
                            Promise.all(fetchPromises)
                                .then(() => {
                                    document.getElementById('progress-bar').style.display = 'none';
                                    progressBar.remove();
                                    isFetching = false;
                                    update();
                                })
                                .catch(error => {
                                    console.error('Problem with tag operation', error);
                                });
                        })
                        .catch(error => {
                            console.error('Problem with tag operation', error);
                        });
                }
                else if (d.type == 'artist') {
                    fetch(`/self_listening/targets/${encodeURIComponent(d.id)}`)
                        .then(response => response.json())
                        .then(data => {
                            console.log(data)
                            scores = data.scores
                            ten_songs = data.ten_songs
                
                            let angleIncrement = (2 * Math.PI) / 10; // Distribute nodes evenly in a circle
                
                            let fetchPromises = ten_songs.map((song, i) => {
                                let track = song['track_name'];
                                let artist = song['artist_name'];
                                console.log(song)
                            
                                // Calculate the angle of the parent node relative to the center of the circle
                                let parentAngle = Math.atan2(d.y - d.parent.y , d.x - d.parent.x);
                                console.log(parentAngle)

                            
                                let angle = angleIncrement * i + parentAngle - Math.PI / 2;
                
                                return fetch(`/get_track_image/${encodeURIComponent(artist)}/${encodeURIComponent(track)}`)
                                    .then(response => response.json())
                                    .then(data => {
                                        let newNode = {
                                            type: 'track',
                                            id: `${track}, by ${artist}`,
                                            artist: `${artist}`,
                                            track: `${track}`,
                                            size: 30 / scores[0]['score'] * scores[i]['score'],
                                            x: d.x + Math.cos(angle) * 100,
                                            y: d.y + Math.sin(angle) * 100,
                                            imageURL: data,
                                            parent: d,
                                            clickable: true
                                        };
                
                                        nodes.push(newNode);
                                        links.push({ source: d.id, target: newNode.id });
                                    });
                            });
                
                            Promise.all(fetchPromises)
                                .then(() => {
                                    document.getElementById('progress-bar').style.display = 'none';
                                    progressBar.remove();
                                    isFetching = false;
                                    update();
                                })
                                .catch(error => {
                                    console.error('Problem with artist operation', error);
                                });
                        })
                        .catch(error => {
                            console.error('Problem with artist operation', error);
                        });
                }
                else {
                    fetch(`/self_listening/add_track/${encodeURIComponent(d.artist)}/${encodeURIComponent(d.track)}`)
                        .then(response => response.json())
                        .then(data => {
                            artist = data['artist']
                            tag = data['tag']
                            console.log(artist)

                            // make artist unique
                            
                            // add artists into node
                            let angleIncrement = (Math.PI) / (artist.length + tag.length); // Distribute nodes evenly in a circle
                            let parentAngle = Math.atan2(d.y - d.parent.y , d.x - d.parent.x);
                            let angle = angleIncrement  + parentAngle - Math.PI / 2; // angle for this node
                            let newNode = {
                                type: 'artist',
                                id: `${artist}`,
                                size: 30,
                                // Calculate the x, y position based on angle and a fixed radius
                                x: d.x + Math.cos(angle) * 100,
                                y: d.y + Math.sin(angle) * 100,
                                imageURL: "https://drive.google.com/uc?id=16NKs6mWVua2sPqaDsaj7qo-oNyw36Yjs", //need to change
                                transformed: false, 
                                parent: d,
                                clickable: true
                            };
                            nodes.push(newNode);
                            links.push({ source: d.id, target: newNode.id });
                        
                            for (let i = 0; i < tag.length; i++) {
                                console.log(tag[i]);
                                let angle = angleIncrement * (i + 1) + parentAngle - Math.PI / 2; // angle for this node
                                let newNode = {
                                    type: 'tag',
                                    id: `${tag[i]}`,
                                    size: 30,
                                    // Calculate the x, y position based on angle and a fixed radius
                                    x: d.x + Math.cos(angle) * 100,
                                    y: d.y + Math.sin(angle) * 100,
                                    imageURL: "https://drive.google.com/uc?id=1HZ0V0q1x3iVlYMeF3M_245CEu6LZAg2G", //need to change
                                    transformed: false, 
                                    parent: d,
                                    clickable: true
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
                        .catch(error => {
                            console.error('Problem with new iteration', error)
                        })
                }
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
    if (instruction_but.innerHTML == "How to use?") {
        instruction_but.innerHTML = "Welcome to <b>Self Listening</b> mode!<br /><b>Click on Avatars</b> to expand the tree to see something you may love<br /><b>Click on the names</b> to jump to last.fm if you're interested!<br />Enjoy!!";
    } else {
        instruction_but.innerHTML = "How to use?";
    }
}

function scroll_Top() {
    window.scrollTo({top: 0, left: 0, behavior: 'smooth'});
}

url_elements = window.location.href.split("/");
// showTargets(url_elements[url_elements.length - 1]);
getFirstNode(url_elements[url_elements.length - 1]);
