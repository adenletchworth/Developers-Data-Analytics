document.addEventListener('DOMContentLoaded', function () {
    fetch('/api/language_pairs')
        .then(response => response.json())
        .then(data => {
            createChordDiagram(data);
        })
        .catch(error => console.error('Error fetching chord diagram data:', error));
});

function createChordDiagram(data) {
    const container = document.getElementById('chord-diagram-container');
    const width = container.offsetWidth;
    const height = container.offsetHeight;
    const outerRadius = Math.min(width, height) * 0.5 - 90;
    const innerRadius = outerRadius - 30;

    d3.select("#chord-diagram-container").select("svg").remove();

    const svg = d3.select("#chord-diagram-container")
        .append("svg")
        .attr("width", width)
        .attr("height", height)
        .attr('font-size', '16px')
        .style('overflow', 'visible')
        .append("g")
        .attr("transform", `translate(${width / 2},${height / 2})`);

    const chord = d3.chord()
        .padAngle(0.05)
        .sortSubgroups(d3.descending);

    const arc = d3.arc()
        .innerRadius(innerRadius)
        .outerRadius(outerRadius);

    const ribbon = d3.ribbon()
        .radius(innerRadius);

    const color = d3.scaleOrdinal(d3.schemeCategory10);

    const languages = Array.from(new Set(data.flatMap(d => [d._id.source, d._id.target])));
    const matrix = Array.from({ length: languages.length }, () => Array(languages.length).fill(0));

    data.forEach(d => {
        const i = languages.indexOf(d._id.source);
        const j = languages.indexOf(d._id.target);
        matrix[i][j] = d.count;
        matrix[j][i] = d.count;
    });

    const chords = chord(matrix);

    const group = svg.append("g")
        .selectAll("g")
        .data(chords.groups)
        .enter().append("g");

    group.append("path")
        .style("fill", d => color(languages[d.index]))
        .style("stroke", d => d3.rgb(color(languages[d.index])).darker())
        .attr("d", arc);

    group.append("text")
        .each(d => d.angle = (d.startAngle + d.endAngle) / 2)
        .attr("dy", ".35em")
        .attr("transform", d => `
            rotate(${d.angle * 180 / Math.PI - 90})
            translate(${outerRadius + 20})
            ${d.angle > Math.PI ? "rotate(180)" : ""}
        `)
        .attr("text-anchor", d => d.angle > Math.PI ? "end" : null)
        .text(d => languages[d.index]);

    const ribbons = svg.append("g")
        .selectAll("path")
        .data(chords)
        .enter().append("path")
        .attr("d", ribbon)
        .style("fill", d => color(languages[d.source.index]))
        .style("stroke", d => d3.rgb(color(languages[d.source.index])).darker())
        .on("mouseover", function(event, d) {
            svg.selectAll("path")
                .style("opacity", 0.1);
            d3.select(this)
                .style("opacity", 1);
            svg.selectAll("path")
                .filter(p => p.source.index === d.source.index || p.target.index === d.source.index || p.source.index === d.target.index || p.target.index === d.target.index)
                .style("opacity", 1);
        })
        .on("mouseout", function() {
            svg.selectAll("path")
                .style("opacity", 1);
        });
}
