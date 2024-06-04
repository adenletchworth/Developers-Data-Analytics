// Function to fetch data from a given endpoint and update the word cloud
function fetchData(endpoint) {
    fetch(endpoint)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            // Map the API data to the format required by the word cloud
            const processedData = data.map(item => ({
                text: item._id,
                size: item.count * 10 
            }));
            createWordCloud(processedData);
        })
        .catch(error => console.error('Error fetching data:', error));
}

function createWordCloud(data) {
    // Clear the existing word cloud
    d3.select("#word-cloud-container").selectAll("*").remove();

    // Get the dimensions of the container
    const container = d3.select("#word-cloud-container");
    const width = container.node().getBoundingClientRect().width;
    const height = container.node().getBoundingClientRect().height;

    var layout = d3.layout.cloud()
        .size([width, height])
        .words(data)
        .padding(1) // Decrease the padding value to bring words closer
        .rotate(function() { return ~~(Math.random() * 2) * 90; })
        .font("Impact")
        .fontSize(function(d) { return d.size; })
        .on("end", draw);

    layout.start();

    function draw(words) {
        var color = d3.scaleOrdinal(d3.schemeCategory10); // Use D3's categorical color scale

        d3.select("#word-cloud-container").append("svg")
            .attr("width", layout.size()[0])
            .attr("height", layout.size()[1])
            .append("g")
            .attr("transform", "translate(" + layout.size()[0] / 2 + "," + layout.size()[1] / 2 + ")")
            .selectAll("text")
            .data(words)
            .enter().append("text")
            .style("font-size", function(d) { return d.size + "px"; })
            .style("font-family", "Impact")
            .style("fill", function(d, i) { return color(i); }) // Assign a color based on index
            .attr("text-anchor", "middle")
            .attr("transform", function(d) {
                return "translate(" + [d.x, d.y] + ")rotate(" + d.rotate + ")";
            })
            .text(function(d) { return d.text; });
    }
}

fetchData('/api/top_keywords_from_readmes');
