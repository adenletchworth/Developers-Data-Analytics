document.addEventListener('DOMContentLoaded', function () {
    fetch('/api/repositories_by_license')
        .then(response => response.json())
        .then(data => {
            const transformedData = data.map(d => ({ license: d._id, count: d.count }));
            createDonutChart(transformedData);
        })
        .catch(error => console.error('Error fetching repository data:', error));
});

function createDonutChart(data) {
    const width = 400;
    const height = 400;
    const radius = Math.min(width, height) / 2;

    const svg = d3.select("#circular-chart-container")
        .append("svg")
        .attr("width", width)
        .attr("height", height)
        .append("g")
        .attr("transform", `translate(${width / 2}, ${height / 2})`);
    
    const color = d3.scaleOrdinal(d3.schemeCategory10);
    
    const pie = d3.pie().value(d => d.count);
    const path = d3.arc()
        .outerRadius(radius - 10)
        .innerRadius(radius - 70);

    // Tooltip
    const tooltip = d3.select("body").append("div")
        .attr("class", "tooltip")
        .style("position", "absolute")
        .style("visibility", "hidden")
        .style("background", "#fff")
        .style("border", "1px solid #ddd")
        .style("padding", "10px")
        .style("border-radius", "4px")
        .style("box-shadow", "0 2px 4px rgba(0, 0, 0, 0.1)");

    const arc = svg.selectAll(".arc")
        .data(pie(data))
        .enter().append("g")
        .attr("class", "arc")
        .on("mouseover", function(event, d) {
            tooltip.html(`${d.data.license}: ${d.data.count}`)
                .style("visibility", "visible");
        })
        .on("mousemove", function(event) {
            tooltip.style("top", (event.pageY - 10) + "px").style("left", (event.pageX + 10) + "px");
        })
        .on("mouseout", function() {
            tooltip.style("visibility", "hidden");
        });
    
    arc.append("path")
        .attr("d", path)
        .attr("fill", d => color(d.data.license));
    
    // Adding legend
    const legend = svg.append("g")
        .attr("transform", `translate(${radius + 20}, ${-radius})`);
    
    data.forEach((d, i) => {
        const legendRow = legend.append("g")
            .attr("transform", `translate(0, ${i * 20})`);
        
        legendRow.append("rect")
            .attr("width", 10)
            .attr("height", 10)
            .attr("fill", color(d.license));
        
        legendRow.append("text")
            .attr("x", 20)
            .attr("y", 10)
            .text(d.license);
    });
}
