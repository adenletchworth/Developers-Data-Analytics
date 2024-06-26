document.addEventListener('DOMContentLoaded', function () {
    fetch('/api/repositories_by_license')
        .then(response => response.json())
        .then(data => {
            const transformedData = data
                .filter(d => d._id !== 'None')
                .map(d => ({ license: d._id, count: d.count }));
            const total = transformedData.reduce((acc, d) => acc + d.count, 0);
            createDonutChart(transformedData, total);
        })
        .catch(error => console.error('Error fetching repository data:', error));
});

function createDonutChart(data, total) {
    const container = document.getElementById('circular-chart-container');

    const width = container.offsetWidth;
    const height = container.offsetHeight - 75;
    const radius = Math.min(width, height) / 2;
    
    d3.select("#circular-chart-container").select("svg").remove();

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

    svg.append("text")
        .attr("text-anchor", "middle")
        .attr("dy", "-0.5em")
        .attr("class", "total-count")
        .style("font-size", "24px")
        .text(total);

    svg.append("text")
        .attr("text-anchor", "middle")
        .attr("dy", "1em")
        .attr("class", "total-text")
        .style("font-size", "14px")
        .text("Total Repositories");
}
