document.addEventListener('DOMContentLoaded', function () {
    fetch('/api/stars_over_time')
        .then(response => response.json())
        .then(data => {
            const transformedData = data.map(d => ({
                date: new Date(d._id),
                total_stars: d.total_stars
            }));
            createLineChart(transformedData);
        })
        .catch(error => console.error('Error fetching stars over time:', error));
});

function createLineChart(data) {
    const margin = { top: 20, right: 20, bottom: 30, left: 50 };
    const width = 600 - margin.left - margin.right;
    const height = 400 - margin.top - margin.bottom;

    const svg = d3.select("#line-chart-container").append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .append("g")
        .attr("transform", `translate(${margin.left},${margin.top})`);

    const x = d3.scaleTime().range([0, width]);
    const y = d3.scaleLinear().range([height, 0]);

    const line = d3.line()
        .x(d => x(d.date))
        .y(d => y(d.total_stars));

    x.domain(d3.extent(data, d => d.date));
    y.domain([0, d3.max(data, d => d.total_stars)]);

    svg.append("g")
        .attr("transform", `translate(0,${height})`)
        .call(d3.axisBottom(x).tickFormat(d3.timeFormat("%Y-%m-%d")));

    svg.append("g")
        .call(d3.axisLeft(y));

    svg.append("path")
        .data([data])
        .attr("class", "line")
        .attr("d", line)
        .style("fill", "none")
        .style("stroke", "steelblue")
        .style("stroke-width", "2px");

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

    svg.selectAll("dot")
        .data(data)
        .enter().append("circle")
        .attr("r", 5)
        .attr("cx", d => x(d.date))
        .attr("cy", d => y(d.total_stars))
        .on("mouseover", function(event, d) {
            tooltip.html(`Date: ${d.date.toISOString().split('T')[0]}<br>Total Stars: ${d.total_stars}`)
                .style("visibility", "visible");
        })
        .on("mousemove", function(event) {
            tooltip.style("top", (event.pageY - 10) + "px").style("left", (event.pageX + 10) + "px");
        })
        .on("mouseout", function() {
            tooltip.style("visibility", "hidden");
        });
}