document.addEventListener('DOMContentLoaded', function () {
    fetch('/api/avg_statistics')
        .then(response => response.json())
        .then(data => {
            // Check if the data array is not empty
            if (data.length > 0) {
                const stats = data[0];
                document.getElementById('total-repos').textContent = stats.total_repos || 0;
                document.getElementById('avg-forks').textContent = stats.avg_forks.toFixed(2) || 0;
                document.getElementById('avg-stars').textContent = stats.avg_stargazers.toFixed(2) || 0;
                document.getElementById('avg-watchers').textContent = stats.avg_watchers.toFixed(2) || 0;
                document.getElementById('avg-issues').textContent = stats.avg_issues.toFixed(2) || 0;
            } else {
                console.error('No data available');
            }
        })
        .catch(error => console.error('Error fetching statistics:', error));
});