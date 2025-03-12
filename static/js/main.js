document.addEventListener('DOMContentLoaded', function() {
    // Check if first visit
    if (!localStorage.getItem('helpBubbleDismissed')) {
        document.getElementById('helpBubble').classList.remove('hidden');
    } else {
        document.getElementById('helpBubble').classList.add('hidden');
    }

    // Set today's date by default
    document.getElementById('date').valueAsDate = new Date();

    // Initialize the impact chart
    let issueChart = new Chart(document.getElementById('issueChart'), {
        type: 'bar',
        data: {
            labels: [],
            datasets: [{
                label: 'Total Impact Time (hours)',
                data: [],
                backgroundColor: 'rgba(54, 162, 235, 0.5)',
                borderColor: 'rgba(54, 162, 235, 1)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Hours'
                    }
                }
            }
        }
    });

    // Load initial data
    loadIssues();

    // Form submission handler
    document.getElementById('issueForm').addEventListener('submit', submitForm);
});

function submitForm(e) {
    e.preventDefault();
    const formData = new FormData(this);

    fetch('/submit_issue', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            this.reset();
            document.getElementById('date').valueAsDate = new Date();
            loadIssues();
        } else {
            alert('Error submitting issue: ' + data.message);
        }
    });
}

function loadIssues() {
    fetch('/get_issues')
        .then(response => response.json())
        .then(data => {
            updateDepartmentTables(data);
            updateChart(data);
        });
}

function updateDepartmentTables(data) {
    const container = document.getElementById('departmentTables');
    container.innerHTML = '';

    for (const [dept, info] of Object.entries(data)) {
        const issues = info.issues;
        const totalTime = info.total_time;

        const section = document.createElement('div');
        section.className = 'department-table';

        section.innerHTML = `
            <div class="department-header">
                <h4>${dept} <span class="badge bg-primary">${totalTime.toFixed(1)} hours</span></h4>
            </div>
            <div class="table-responsive">
                <table class="table table-striped">
                    <thead>
                        <tr>
                            <th>Date</th>
                            <th>Discovered in</th>
                            <th>Job Number</th>
                            <th>Part Number</th>
                            <th>Description</th>
                            <th>Issue Time</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${issues.map(issue => `
                            <tr>
                                <td>${issue.date}</td>
                                <td>${issue.discovery_department}</td>
                                <td>${issue.job_number}</td>
                                <td>${issue.part_number || '-'}</td>
                                <td>${issue.description}</td>
                                <td>${issue.issue_time.toFixed(1)}</td>
                                <td>
                                    <button class="btn btn-sm btn-outline-warning" 
                                            onclick="openContestModal(${issue.id})">
                                        Contest
                                    </button>
                                </td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        `;

        container.appendChild(section);
    }
}

function updateChart(data) {
    const labels = Object.keys(data);
    const values = labels.map(dept => data[dept].total_time);

    const chart = Chart.getChart('issueChart');
    chart.data.labels = labels;
    chart.data.datasets[0].data = values;
    chart.update();
}

function openContestModal(issueId) {
    document.getElementById('contest_issue_id').value = issueId;
    new bootstrap.Modal(document.getElementById('contestModal')).show();
}

function submitContest() {
    const issueId = document.getElementById('contest_issue_id').value;
    const newDepartment = document.getElementById('new_department').value;
    const reason = document.getElementById('contest_reason').value;

    fetch('/contest_issue', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            issue_id: issueId,
            new_department: newDepartment,
            reason: reason
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            bootstrap.Modal.getInstance(document.getElementById('contestModal')).hide();
            loadIssues();
        } else {
            alert('Error contesting issue: ' + data.message);
        }
    });
}

function exportCSV() {
    window.location.href = '/export_csv';
}

function closeHelpBubble() {
    document.getElementById('helpBubble').classList.add('hidden');
    localStorage.setItem('helpBubbleDismissed', 'true');
}

function clearData() {
    if (confirm('Are you sure you want to clear all data? This cannot be undone.')) {
        fetch('/clear_data', {
            method: 'POST'
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                loadIssues();
            } else {
                alert('Error clearing data: ' + data.message);
            }
        });
    }
}