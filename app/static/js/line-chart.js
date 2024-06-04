document.addEventListener('DOMContentLoaded', function () {
    fetch('/api/stars_over_time')
        .then(response => response.json())
        .then(data => {
            const transformedData = data.map(d => ({
                date: new Date(d._id),
                total_stars: d.total_stars
            }));
            const aggregatedData = aggregateData(transformedData);
            createLineChart(aggregatedData);
        })
        .catch(error => console.error('Error fetching stars over time:', error));
});

function aggregateData(data) {
    const aggregatedData = [];
    const dateMap = new Map();

    // Aggregate data by month
    data.forEach(d => {
        const month = d.date.getFullYear() + '-' + (d.date.getMonth() + 1);
        if (!dateMap.has(month)) {
            dateMap.set(month, { date: new Date(d.date.getFullYear(), d.date.getMonth()), total_stars: 0 });
        }
        dateMap.get(month).total_stars += d.total_stars;
    });

    dateMap.forEach(value => {
        aggregatedData.push(value);
    });

    // Sort the aggregated data by date
    aggregatedData.sort((a, b) => a.date - b.date);
    return aggregatedData;
}

function createLineChart(data) {
    const margin = { top: 20, right: 20, bottom: 50, left: 50 };
    
    // Select the parent container and get its dimensions
    const container = d3.select("#line-chart-container");
    const containerWidth = container.node().getBoundingClientRect().width;
    const containerHeight = container.node().getBoundingClientRect().height;

    const width = containerWidth - margin.left - margin.right;
    const height = containerHeight - margin.top - margin.bottom;

    const svg = container.append("svg")
        .attr("width", containerWidth)
        .attr("height", containerHeight)
        .append("g")
        .attr("transform", `translate(${margin.left},${margin.top})`);

    const x = d3.scaleTime().range([0, width]);
    const y = d3.scaleLinear().range([height, 0]);

    const line = d3.line()
        .x(d => x(d.date))
        .y(d => y(d.total_stars))
        .curve(d3.curveMonotoneX); // Apply smoothing

    x.domain(d3.extent(data, d => d.date));
    y.domain([0, d3.max(data, d => d.total_stars)]);

    svg.append("g")
        .attr("transform", `translate(0,${height})`)
        .call(d3.axisBottom(x)
            .tickFormat(d3.timeFormat("%b %Y"))
            .ticks(d3.timeMonth.every(6)) // Reduce the number of ticks
        )
        .selectAll("text")
        .attr("transform", "rotate(-45)")
        .style("text-anchor", "end");

    svg.append("g")
        .call(d3.axisLeft(y));

    svg.append("path")
        .data([data])
        .attr("class", "line")
        .attr("d", line);

    const tooltip = d3.select("body").append("div")
        .attr("class", "tooltip")
        .style("position", "absolute")
        .style("visibility", "hidden")
        .style("background", "#fff")
        .style("border", "1px solid #ddd")
        .style("padding", "10px")
        .style("border-radius", "4px")
        .style("box-shadow", "0 2px 4px rgba(0, 0, 0, 0.1)");

    svg.selectAll("path")
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
