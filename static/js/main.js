document.addEventListener('DOMContentLoaded', function() {
    // Check if first visit
    if (!localStorage.getItem('helpBubbleDismissed')) {
        document.getElementById('helpBubble').classList.remove('hidden');
    } else {
        document.getElementById('helpBubble').classList.add('hidden');
    }

    // Set today's date by default
    document.getElementById('date').valueAsDate = new Date();

    // Initialize the delay chart
    let delayChart = new Chart(document.getElementById('delayChart'), {
        type: 'bar',
        data: {
            labels: [],
            datasets: [{
                label: 'Total Delay Time (hours)',
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
    loadDelays();

    // Form submission handler
    document.getElementById('delayForm').addEventListener('submit', function(e) {
        e.preventDefault();

        const formData = new FormData(this);
        const otherCheckbox = document.getElementById('dept_Other');

        if (otherCheckbox && otherCheckbox.checked && otherCheckbox.value) {
            formData.append('dept_Other_value', otherCheckbox.value);
        }

        fetch('/submit_delay', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                this.reset();
                document.getElementById('date').valueAsDate = new Date();
                loadDelays();
            } else {
                alert('Error submitting delay: ' + data.message);
            }
        });
    });

    // Handle Other department input
    const otherCheckbox = document.getElementById('dept_Other');
    if (otherCheckbox) {
        otherCheckbox.addEventListener('change', function() {
            if (this.checked) {
                const otherDept = prompt('Please enter the department name:');
                if (otherDept) {
                    this.value = otherDept;
                } else {
                    this.checked = false;
                }
            }
        });
    }

    // Ensure only one department checkbox can be selected at a time
    const deptCheckboxes = document.querySelectorAll('.dept-checkbox');
    deptCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            if (this.checked) {
                deptCheckboxes.forEach(cb => {
                    if (cb !== this) cb.checked = false;
                });
            }
        });
    });
});

function loadDelays() {
    fetch('/get_delays')
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
        const delays = info.delays;
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
                            <th>Delay Time</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${delays.map(delay => `
                            <tr>
                                <td>${delay.date}</td>
                                <td>${delay.discovery_department}</td>
                                <td>${delay.job_number}</td>
                                <td>${delay.part_number || '-'}</td>
                                <td>${delay.description}</td>
                                <td>${delay.delay_time.toFixed(1)}</td>
                                <td>
                                    <button class="btn btn-sm btn-outline-warning" 
                                            onclick="openContestModal(${delay.id})">
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

    const chart = Chart.getChart('delayChart');
    chart.data.labels = labels;
    chart.data.datasets[0].data = values;
    chart.update();
}

function openContestModal(delayId) {
    document.getElementById('contest_delay_id').value = delayId;
    new bootstrap.Modal(document.getElementById('contestModal')).show();
}

function submitContest() {
    const delayId = document.getElementById('contest_delay_id').value;
    const newDepartment = document.getElementById('new_department').value;
    const reason = document.getElementById('contest_reason').value;

    fetch('/contest_delay', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            delay_id: delayId,
            new_department: newDepartment,
            reason: reason
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            bootstrap.Modal.getInstance(document.getElementById('contestModal')).hide();
            loadDelays();
        } else {
            alert('Error contesting delay: ' + data.message);
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

function clearAllData() {
    if (confirm('Are you sure you want to clear all delay data? This cannot be undone.')) {
        fetch('/clear_data', {
            method: 'POST'
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                loadDelays();  // Refresh the display
            } else {
                alert('Error clearing data: ' + data.message);
            }
        });
    }
}