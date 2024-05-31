// script.js

// URL of the API endpoint
const endpoint = 'http://localhost:5000/api/top_keywords_from_readmes';

// Fetch data from the endpoint
fetch(endpoint)
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        createWordCloud(data);
    })
    .catch(error => console.error('Error fetching data:', error));

// Function to create the word cloud
function createWordCloud(data) {
    const words = data.map(d => ({ text: d._id, size: d.count * 10 }));
    const width = document.getElementById('chart').clientWidth;
    const height = document.getElementById('chart').clientHeight;
    const chart = d3.select("#chart");

    const color = d3.scaleOrdinal(d3.schemeCategory10);

    const positions = calculateWordPositions(words, width, height);

    positions.forEach(word => {
        chart.append("div")
            .attr("class", "word")
            .style("font-size", `${word.size}px`)
            .style("color", color(word.text))
            .style("left", `${word.x}px`)
            .style("top", `${word.y}px`)
            .text(word.text);
    });
}

// Simple manual positioning function (this can be improved for better aesthetics)
function calculateWordPositions(words, width, height) {
    const positions = [];
    let x = width / 2;
    let y = height / 2;
    const radius = 50;
    const angleIncrement = 0.1;

    words.forEach((word, i) => {
        const angle = i * angleIncrement;
        const xOffset = radius * Math.cos(angle) * (i + 1);
        const yOffset = radius * Math.sin(angle) * (i + 1);
        positions.push({
            ...word,
            x: x + xOffset,
            y: y + yOffset
        });
    });

    return positions;
}
