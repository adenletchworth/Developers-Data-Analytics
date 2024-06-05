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

    aggregatedData.sort((a, b) => a.date - b.date);
    return aggregatedData;
}

function createLineChart(data) {
    const margin = { top: 20, right: 20, bottom: 50, left: 50 };
    
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
            .ticks(d3.timeMonth.every(6))
        )
        .selectAll("text")
        .attr("transform", "rotate(-45)")
        .style("text-anchor", "end")
        .style("font-size", "12px");

    svg.append("g")
        .call(d3.axisLeft(y)
            .ticks(10)
            .tickSize(-width)
            .tickFormat(d => d3.format(",")(d))
        )
        .selectAll("text")
        .style("font-size", "12px");

    svg.append("g")
        .attr("class", "grid")
        .call(d3.axisLeft(y)
            .ticks(10)
            .tickSize(-width)
            .tickFormat("")
        )
        .style("stroke-dasharray", "3 3");

    svg.append("path")
        .data([data])
        .attr("class", "line")
        .attr("d", line)
        .style("fill", "none")
        .style("stroke", "steelblue")
        .style("stroke-width", "2px")
        .style("clip-path", "url(#clip)")
        .transition()
        .duration(2000)
        .attrTween("d", function(d) {
            const interpolate = d3.scaleQuantile()
                .domain([0, 1])
                .range(d3.range(1, data.length + 1));
            return function(t) {
                return line(d.slice(0, interpolate(t)));
            };
        });

    const tooltip = d3.select("body").append("div")
        .attr("class", "tooltip")
        .style("position", "absolute")
        .style("visibility", "hidden")
        .style("background", "#fff")
        .style("border", "1px solid #ddd")
        .style("padding", "10px")
        .style("border-radius", "4px")
        .style("box-shadow", "0 2px 4px rgba(0, 0, 0, 0.1)")
        .style("font-size", "12px");

    svg.selectAll("circle")
        .data(data)
        .enter().append("circle")
        .attr("r", 2)  
        .attr("cx", d => x(d.date))
        .attr("cy", d => y(d.total_stars))
        .style("fill", "steelblue")
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

    svg.selectAll("rect")
        .data(data)
        .enter().append("rect")
        .attr("x", d => x(d.date) - 5)
        .attr("y", d => y(d.total_stars) - 5)
        .attr("width", 10)
        .attr("height", 10)
        .style("fill", "none")
        .style("pointer-events", "all")
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
