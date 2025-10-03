// static/script.js

document.addEventListener('DOMContentLoaded', () => {
    const analyzeBtn = document.getElementById('analyzeBtn');
    const fileInput = document.getElementById('csvFileInput');
    const loader = document.getElementById('loader');
    const resultsDiv = document.getElementById('results');

    analyzeBtn.addEventListener('click', async () => {
        if (fileInput.files.length === 0) {
            alert('Please select a CSV file first.');
            return;
        }

        // Show loader and hide old results
        loader.style.display = 'block';
        resultsDiv.style.display = 'none';

        const formData = new FormData();
        formData.append('file', fileInput.files[0]);

        try {
            const response = await fetch('/analyze', {
                method: 'POST',
                body: formData,
            });

            if (!response.ok) {
                throw new Error('Analysis failed. The server returned an error.');
            }

            const data = await response.json();

            // Populate the result divs with data from the backend
            document.getElementById('clusterResults').innerHTML = data.cluster_analysis_html;
            document.getElementById('aprioriResults').innerHTML = data.association_rules_html;
            document.getElementById('harmfulItemsResults').innerHTML = data.harmful_items_html;
            
            // Display the plot image
            const plotContainer = document.getElementById('plotResult');
            plotContainer.innerHTML = `<img src="${data.cluster_plot_url}" class="img-fluid" alt="Cluster Plot">`;

            // Hide loader and show results
            loader.style.display = 'none';
            resultsDiv.style.display = 'block';

        } catch (error) {
            loader.style.display = 'none';
            alert('An error occurred: ' + error.message);
            console.error('Error:', error);
        }
    });
});