// static/script.js - Global Microplastic Research Analyzer

document.addEventListener('DOMContentLoaded', () => {
    const analyzeBtn = document.getElementById('analyzeBtn');
    const fileInput = document.getElementById('csvFileInput');
    const loader = document.getElementById('loader');
    const resultsDiv = document.getElementById('results');

    analyzeBtn.addEventListener('click', async () => {
        if (fileInput.files.length === 0) {
            showAlert('Please select a CSV file first.', 'warning');
            return;
        }

        // Show loader and hide old results
        loader.style.display = 'block';
        resultsDiv.style.display = 'none';
        document.querySelector('.upload-section').style.display = 'none';

        const formData = new FormData();
        formData.append('file', fileInput.files[0]);

        try {
            const response = await fetch('/analyze', {
                method: 'POST',
                body: formData,
            });

            if (!response.ok) {
                throw new Error('Analysis failed. Please check your file format and try again.');
            }

            const data = await response.json();

            // Display all results
            displayGlobalOverview(data.global_insights, data.research_summary);
            displayCountryAnalysis(data.country_analyses);
            displayPopulationClusters(data.population_clusters);
            displayFoodSourceAnalysis(data.food_source_analysis);
            displayConsumptionPatterns(data.consumption_patterns);
            displayResearchSummary(data.research_summary);
            displayVisualization(data.visualization_url);

            // Hide loader and show results
            loader.style.display = 'none';
            resultsDiv.style.display = 'block';

            // Scroll to results
            resultsDiv.scrollIntoView({ behavior: 'smooth' });

        } catch (error) {
            loader.style.display = 'none';
            document.querySelector('.upload-section').style.display = 'block';
            showAlert('An error occurred: ' + error.message, 'danger');
            console.error('Error:', error);
        }
    });

    function showAlert(message, type) {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        document.querySelector('.container').insertBefore(alertDiv, document.querySelector('.upload-section'));
        
        setTimeout(() => {
            alertDiv.remove();
        }, 5000);
    }

    function displayGlobalOverview(insights, summary) {
        const container = document.getElementById('globalOverview');
        const riskDist = summary.risk_distribution;
        
        container.innerHTML = `
            <div class="row">
                <div class="col-md-3">
                    <div class="stats-card">
                        <h3>${insights.total_countries}</h3>
                        <p class="mb-0">Countries/Regions Analyzed</p>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="stats-card">
                        <h3>${insights.global_avg_intake}</h3>
                        <p class="mb-0">Global Average Intake<br><small>(particles/gram)</small></p>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="stats-card">
                        <h3 class="text-danger">${insights.highest_risk_country}</h3>
                        <p class="mb-0">Highest Risk Region</p>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="stats-card">
                        <h3 class="text-success">${insights.lowest_risk_country}</h3>
                        <p class="mb-0">Lowest Risk Region</p>
                    </div>
                </div>
            </div>
            <div class="row mt-3">
                <div class="col-md-4">
                    <div class="card border-danger">
                        <div class="card-body text-center">
                            <h2 class="text-danger">${riskDist.high_risk}</h2>
                            <p class="mb-0">High Risk Regions</p>
                        </div>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="card border-warning">
                        <div class="card-body text-center">
                            <h2 class="text-warning">${riskDist.moderate_risk}</h2>
                            <p class="mb-0">Moderate Risk Regions</p>
                        </div>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="card border-success">
                        <div class="card-body text-center">
                            <h2 class="text-success">${riskDist.low_risk}</h2>
                            <p class="mb-0">Low Risk Regions</p>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    function displayCountryAnalysis(countries) {
        const container = document.getElementById('countryAnalysis');
        let html = '';

        countries.forEach(country => {
            html += `
                <div class="card country-card risk-${country.risk_level.toLowerCase().replace(' ', '-')} mb-3">
                    <div class="card-body">
                        <div class="row align-items-center">
                            <div class="col-md-3">
                                <h5 class="mb-1">${country.country}</h5>
                                <span class="badge" style="background-color: ${country.color}">
                                    ${country.risk_level} Risk
                                </span>
                            </div>
                            <div class="col-md-2">
                                <strong>Total Intake:</strong><br>
                                ${country.total_intake} particles/gram
                            </div>
                            <div class="col-md-3">
                                <strong>Policy Recommendation:</strong><br>
                                <small class="text-muted">${country.recommendations.policy}</small>
                            </div>
                            <div class="col-md-4">
                                <strong>Top Risk Foods:</strong><br>
                                <small class="text-muted">
                                    ${country.food_breakdown.slice(0, 2).map(food => 
                                        `${food.food_source}: ${food.intake_level}`
                                    ).join(', ')}
                                </small>
                            </div>
                        </div>
                        <div class="mt-2">
                            <button class="btn btn-sm btn-outline-primary" type="button" data-bs-toggle="collapse" 
                                    data-bs-target="#country-${country.sample_id}" aria-expanded="false">
                                View Detailed Breakdown
                            </button>
                        </div>
                        <div class="collapse mt-3" id="country-${country.sample_id}">
                            <div class="row">
                                <div class="col-md-6">
                                    <h6>Food Source Breakdown:</h6>
                                    ${country.food_breakdown.map(food => `
                                        <div class="d-flex justify-content-between">
                                            <span>${food.food_source}:</span>
                                            <span class="text-${food.color === 'green' ? 'success' : food.color === 'orange' ? 'warning' : 'danger'}">
                                                ${food.intake_level} (${food.risk_level})
                                            </span>
                                        </div>
                                    `).join('')}
                                </div>
                                <div class="col-md-6">
                                    <h6>Public Health Actions:</h6>
                                    <p><small>${country.recommendations.public_health}</small></p>
                                    <h6>Individual Actions:</h6>
                                    <p><small>${country.recommendations.individual}</small></p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            `;
        });

        container.innerHTML = html;
    }

    function displayPopulationClusters(clusters) {
        const container = document.getElementById('populationClusters');
        let html = '';

        clusters.forEach(cluster => {
            let cardClass = 'cluster-low';
            if (cluster.risk_category.includes('Moderate')) cardClass = 'cluster-moderate';
            if (cluster.risk_category.includes('High')) cardClass = 'cluster-high';

            html += `
                <div class="card cluster-card ${cardClass} mb-3">
                    <div class="card-body">
                        <h5 class="card-title">
                            <i class="fas fa-users me-2"></i>${cluster.risk_category}
                        </h5>
                        <p class="card-text">${cluster.description}</p>
                        <div class="row">
                            <div class="col-md-6">
                                <strong>Countries/Regions:</strong> ${cluster.countries.join(', ') || 'Various samples'}
                            </div>
                            <div class="col-md-6">
                                <strong>Avg. Intake:</strong> ${cluster.average_intake} particles/gram
                            </div>
                        </div>
                        <div class="mt-3">
                            <strong><i class="fas fa-heartbeat me-2"></i>Health Impact:</strong>
                            <p class="mb-2">${cluster.health_impact}</p>
                            <strong><i class="fas fa-balance-scale me-2"></i>Policy Recommendation:</strong>
                            <p class="mb-0">${cluster.policy_recommendation}</p>
                        </div>
                    </div>
                </div>
            `;
        });

        container.innerHTML = html;
    }

    function displayFoodSourceAnalysis(foodSources) {
        const container = document.getElementById('foodSourceAnalysis');
        let html = '';

        foodSources.forEach(food => {
            html += `
                <div class="card food-source-card mb-3" style="border-left-color: ${food.color}">
                    <div class="row align-items-center">
                        <div class="col-md-2">
                            <h6 class="mb-1">${food.food_source}</h6>
                            <span class="badge" style="background-color: ${food.color}">
                                ${food.risk_level}
                            </span>
                        </div>
                        <div class="col-md-2">
                            <strong>Global Avg:</strong><br>
                            ${food.global_average} particles/gram
                        </div>
                        <div class="col-md-2">
                            <strong>Range:</strong><br>
                            ${food.lowest_exposure} - ${food.highest_exposure}
                        </div>
                        <div class="col-md-2">
                            <strong>At-Risk Countries:</strong><br>
                            ${food.countries_at_risk}
                        </div>
                        <div class="col-md-4">
                            <strong>Global Solution:</strong><br>
                            <small class="text-muted">${food.global_solution}</small>
                        </div>
                    </div>
                    <div class="mt-2">
                        <button class="btn btn-sm btn-outline-info" type="button" data-bs-toggle="collapse" 
                                data-bs-target="#food-${food.food_source.replace(' ', '')}" aria-expanded="false">
                            View Country Actions
                        </button>
                    </div>
                    <div class="collapse mt-2" id="food-${food.food_source.replace(' ', '')}">
                        <div class="alert alert-info">
                            <strong>Recommended Country Actions:</strong> ${food.country_action}
                        </div>
                    </div>
                </div>
            `;
        });

        container.innerHTML = html || '<p class="text-muted">No specific food source analysis available.</p>';
    }

    function displayConsumptionPatterns(patterns) {
        const container = document.getElementById('consumptionPatterns');
        let html = '';

        if (patterns.length > 0) {
            patterns.forEach(pattern => {
                html += `
                    <div class="card mb-2">
                        <div class="card-body py-3">
                            <div class="row align-items-center">
                                <div class="col-md-4">
                                    <strong>High consumption in:</strong><br>
                                    ${pattern.high_consumption_in}
                                </div>
                                <div class="col-md-1 text-center">
                                    <i class="fas fa-arrow-right text-primary"></i>
                                </div>
                                <div class="col-md-4">
                                    <strong>Often leads to high:</strong><br>
                                    ${pattern.often_leads_to_high}
                                </div>
                                <div class="col-md-3">
                                    <strong>Confidence:</strong> ${pattern.confidence}<br>
                                    <small class="text-muted">${pattern.implication}</small>
                                </div>
                            </div>
                        </div>
                    </div>
                `;
            });
        } else {
            html = '<p class="text-muted">No significant consumption patterns identified in the dataset.</p>';
        }

        container.innerHTML = html;
    }

    function displayResearchSummary(summary) {
        const container = document.getElementById('researchSummary');
        const riskDist = summary.risk_distribution;
        const total = summary.total_samples;
        
        container.innerHTML = `
            <div class="row">
                <div class="col-md-6">
                    <div class="card">
                        <div class="card-header">
                            <h5 class="mb-0">Risk Distribution Analysis</h5>
                        </div>
                        <div class="card-body">
                            <canvas id="riskChart" width="300" height="300"></canvas>
                        </div>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="card">
                        <div class="card-header">
                            <h5 class="mb-0">Key Research Findings</h5>
                        </div>
                        <div class="card-body">
                            <ul class="list-unstyled">
                                <li class="mb-2">
                                    <i class="fas fa-chart-pie text-primary me-2"></i>
                                    <strong>${((riskDist.high_risk / total) * 100).toFixed(1)}%</strong> of regions show high risk levels
                                </li>
                                <li class="mb-2">
                                    <i class="fas fa-exclamation-triangle text-warning me-2"></i>
                                    <strong>${((riskDist.moderate_risk / total) * 100).toFixed(1)}%</strong> require moderate intervention
                                </li>
                                <li class="mb-2">
                                    <i class="fas fa-check-circle text-success me-2"></i>
                                    <strong>${((riskDist.low_risk / total) * 100).toFixed(1)}%</strong> maintain acceptable levels
                                </li>
                                <li class="mb-2">
                                    <i class="fas fa-users text-info me-2"></i>
                                    Total <strong>${total}</strong> regions analyzed
                                </li>
                            </ul>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        // Simple text-based chart since we don't have Chart.js
        const chartContainer = document.getElementById('riskChart');
        if (chartContainer) {
            chartContainer.innerHTML = `
                <div class="text-center">
                    <div class="mb-3">
                        <div style="display: inline-block; width: 60px; height: 60px; background: #dc3545; border-radius: 50%; line-height: 60px; color: white; font-weight: bold;">
                            ${riskDist.high_risk}
                        </div>
                        <div class="small">High Risk</div>
                    </div>
                    <div class="mb-3">
                        <div style="display: inline-block; width: 50px; height: 50px; background: #ffc107; border-radius: 50%; line-height: 50px; color: white; font-weight: bold;">
                            ${riskDist.moderate_risk}
                        </div>
                        <div class="small">Moderate Risk</div>
                    </div>
                    <div class="mb-3">
                        <div style="display: inline-block; width: 40px; height: 40px; background: #28a745; border-radius: 50%; line-height: 40px; color: white; font-weight: bold;">
                            ${riskDist.low_risk}
                        </div>
                        <div class="small">Low Risk</div>
                    </div>
                </div>
            `;
        }
    }

    function displayVisualization(plotUrl) {
        const container = document.getElementById('clusterVisualization');
        container.innerHTML = `<img src="${plotUrl}" class="img-fluid rounded" alt="Global Risk Distribution Visualization">`;
    }
});