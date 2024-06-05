console.log('force.js loaded');

function fetchData(endpoint) {
    fetch(endpoint)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            console.log('Fetched data:', data); // Debugging line
            const processedData = processData(data);
            createForceGraph(processedData);
        })
        .catch(error => console.error('Error fetching data:', error));
}

function processData(data) {
    const nodes = [];
    const links = [];
    const wordTopics = {};

    data.topics_words.forEach((words, i) => {
        nodes.push({ id: `Topic ${i}`, group: `topic${i}`, topicIndex: i });
        words.forEach(word => {
            if (!wordTopics[word]) wordTopics[word] = [];
            wordTopics[word].push(i);
            links.push({ source: `Topic ${i}`, target: word });
        });
    });

    Object.keys(wordTopics).forEach(word => {
        nodes.push({ id: word, group: 'word', topicIndices: wordTopics[word] });
    });

    return { nodes, links };
}

function drag(simulation) {
    function dragstarted(event, d) {
        if (!event.active) simulation.alphaTarget(0.3).restart();
        d.fx = d.x;
        d.fy = d.y;
    }

    function dragged(event, d) {
        d.fx = event.x;
        d.fy = event.y;
    }

    function dragended(event, d) {
        if (!event.active) simulation.alphaTarget(0);
        d.fx = null;
        d.fy = null;
    }

    return d3.drag()
        .on("start", dragstarted)
        .on("drag", dragged)
        .on("end", dragended);
}

function createForceGraph(data) {
    const { nodes, links } = data;

    const container = document.getElementById('graph');
    const width = container.clientWidth;
    const height = Math.max(container.clientHeight, 900);

    const color = d3.scaleOrdinal(d3.schemeCategory10);

    const svg = d3.select(container).append("svg")
        .attr("width", width)
        .attr("height", height)
        .call(d3.zoom().on("zoom", function (event) {
            svg.attr("transform", event.transform)
        }))
        .append("g");

    const simulation = d3.forceSimulation(nodes)
        .force("link", d3.forceLink(links).id(d => d.id).distance(d => d.source.group.startsWith('topic') ? 200 : 50))
        .force("charge", d3.forceManyBody().strength(-200))
        .force("center", d3.forceCenter(width / 2, height / 2));

    const link = svg.append("g")
        .attr("class", "links")
        .selectAll("line")
        .data(links)
        .enter().append("line")
        .attr("stroke-width", 2)
        .attr("stroke", "#999")
        .style('height', '100%');

    const node = svg.append("g")
        .attr("class", "nodes")
        .selectAll("g")
        .data(nodes)
        .enter().append("g")
        .call(drag(simulation));

    node.append("circle")
        .attr("r", 10)
        .attr("fill", d => {
            if (d.group.startsWith('topic')) {
                return color(d.topicIndex);
            } else {
                const colors = d.topicIndices.map(i => d3.rgb(color(i)));
                const blendedColor = colors.reduce((acc, c) => {
                    acc.r += c.r / colors.length;
                    acc.g += c.g / colors.length;
                    acc.b += c.b / colors.length;
                    return acc;
                }, { r: 0, g: 0, b: 0 });
                return d3.rgb(blendedColor.r, blendedColor.g, blendedColor.b);
            }
        });

    node.append("text")
        .attr("x", 15)
        .attr("y", 3)
        .text(d => d.id);

    simulation.on("tick", () => {
        link
            .attr("x1", d => d.source.x)
            .attr("y1", d => d.source.y)
            .attr("x2", d => d.target.x)
            .attr("y2", d => d.target.y);

        node
            .attr("transform", d => `translate(${d.x},${d.y})`);
    });
}

function initializeGraph() {
    fetchData('/api/lda');

    window.addEventListener('resize', () => {
        d3.select("#graph").selectAll("*").remove();
        fetchData('/api/lda');
    });
}

document.addEventListener('DOMContentLoaded', initializeGraph);
