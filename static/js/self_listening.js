// Set up the SVG and the force simulation
const width = window.innerWidth;
const height = window.innerHeight;
const svg = d3.select('#visualization').append('svg')
    .attr('width', 20000)
    .attr('height', 30000);


let nodes = [];

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
            nodes.push({ type: 'user', id: username, size: 30, fx: width / 2, fy: height / 2, imageURL: data })

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
                    .attr('width', d => d.size * 2) // Set the image width
                    .style('clip-path', 'circle(50%)'); // Make the image circular


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

            function expandNode(event, d) {
                // Prevent the simulation from moving nodes around when adding new ones
                simulation.stop();

                if (isFetching) return;  // If a fetch operation is in progress, ignore the event

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
            
                // Define the color stops of the gradient
                gradient.append('stop')
                .attr('offset', '0%')
                .attr('stop-color', '#A9A9A9');
            
                gradient.append('stop')
                    .attr('offset', '100%')
                    .attr('stop-color', '#C0C0C0');

                const progressBar = d3.select(this).append('path')
                    .attr('class', 'progress-bar')
                    .attr('d', circlePath) // Set the path
                    .attr('transform', `translate(${d.x}, ${d.y})`) // Position the circle
                    .attr('stroke-width', 5)
                    .attr('fill', 'none')
                    .attr('stroke', 'url(#gradient)');
                
                    let progressBarDuration;

                    if (d.type == 'user') {
                        progressBarDuration = 20000; // Duration for the progress bar
                    }
                    else if (d.type == 'tag') {    
                        progressBarDuration = 4000; // Duration for the progress bar
                    }
                    else if (d.type == 'artist') {
                        progressBarDuration = 8000; // Duration for the progress bar
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
                                            imageURL: "https://drive.google.com/uc?id=16NKs6mWVua2sPqaDsaj7qo-oNyw36Yjs" //need to change
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
                                    imageURL: "https://drive.google.com/uc?id=1HZ0V0q1x3iVlYMeF3M_245CEu6LZAg2G" //need to change
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
                                let parentAngle = Math.atan2(d.y - height / 2 , d.x - width / 2);
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
                                            imageURL: data
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
                                let parentAngle = Math.atan2(d.y - height / 2 , d.x - width / 2);
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
                                            imageURL: data
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

                            // make artist unique
                            artist = [...new Set(artist)]
                            
                            // add artists into node
                            let angleIncrement = (Math.PI) / (artist.length + tag.length); // Distribute nodes evenly in a circle
                            let parentAngle = Math.atan2(d.y - height / 2 , d.x - width / 2);
                            for (let i = 0; i < artist.length; i++) {
                                console.log(artist[i]);
                                let angle = angleIncrement * i + parentAngle - Math.PI / 2; // angle for this node
                                let newNode = {
                                    type: 'artist',
                                    id: `${artist[i]}`,
                                    size: 30,
                                    // Calculate the x, y position based on angle and a fixed radius
                                    x: d.x + Math.cos(angle) * 100,
                                    y: d.y + Math.sin(angle) * 100,
                                    imageURL: "https://drive.google.com/uc?id=16NKs6mWVua2sPqaDsaj7qo-oNyw36Yjs" //need to change
                                };
                                nodes.push(newNode);
                                links.push({ source: d.id, target: newNode.id });
                            }
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
                                    imageURL: "https://drive.google.com/uc?id=1HZ0V0q1x3iVlYMeF3M_245CEu6LZAg2G" //need to change
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
// showTargets(url_elements[url_elements.length - 1]);
getFirstNode(url_elements[url_elements.length - 1]);
