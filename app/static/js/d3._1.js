console.log("d3.js loaded!")

// confirm d3 is loaded
//d3.select("h2").style("color", "red").text("Hello World!");

var data = [10, 20, 30, 40, 50];
var width = 500;
var height = 600;

var widthScale = d3.scaleLinear()
                .domain([0, d3.max(data)])
                .range([0, width]);

var colors = d3.scaleLinear()
                .domain([d3.min(data), d3.max(data)])
                .range(["red", "blue"]);

var axis = d3.axisBottom()
            .ticks(3)
            .scale(widthScale);

var canvas = d3.select("body")
            .append("svg")
            .attr("width", width)
            .attr("height", height)
            .append("g")
            .attr("transform", "translate(50, 50)");

var bars = canvas.selectAll("rect")
            .data(data)
            .enter()
                .append("rect")
                .attr("width", function(d) { return widthScale(d); })
                .attr("height", 50)
                .attr("fill", function(d) { return colors(d); })
                .attr("y", function(d, i) { return i * 100; });

canvas.append("g")
    .attr("transform", "translate(0, 500)")
    .call(axis);










