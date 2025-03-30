// Budget Simulation Game JavaScript

document.addEventListener('DOMContentLoaded', function() {
    const availableContainer = document.getElementById('available-expenses');
    const selectedContainer = document.getElementById('selected-expenses');
    const totalExpensesElement = document.getElementById('total-expenses');
    const remainingBudgetElement = document.getElementById('remaining-budget');
    const submitButton = document.getElementById('submit-budget');
    const simulationForm = document.getElementById('simulation-form');
    const selectedExpensesInput = document.getElementById('selected-expenses-input');
    const feedbackContainer = document.getElementById('feedback-container');
    const feedbackContent = document.getElementById('feedback-content');
    const feedbackHeader = document.getElementById('feedback-header');
    const feedbackTitle = document.getElementById('feedback-title');
    
    // Initialize chart
    const ctx = document.getElementById('budget-chart').getContext('2d');
    let budgetChart = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: ['Remaining', 'Expenses'],
            datasets: [{
                label: 'Budget',
                data: [initialMonthlyIncome, 0],
                backgroundColor: [
                    'rgba(54, 162, 235, 0.5)',
                    'rgba(255, 99, 132, 0.5)'
                ],
                borderColor: [
                    'rgba(54, 162, 235, 1)',
                    'rgba(255, 99, 132, 1)'
                ],
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false
        }
    });
    
    // Setup SortableJS for drag and drop
    const availableSortable = new Sortable(availableContainer, {
        group: 'expenses',
        animation: 150,
        ghostClass: 'ghost',
        onEnd: updateTotals
    });
    
    const selectedSortable = new Sortable(selectedContainer, {
        group: 'expenses',
        animation: 150,
        ghostClass: 'ghost',
        onEnd: updateTotals
    });
    
    // Add event listeners for the add/remove buttons
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('add-expense-btn') || 
            e.target.parentElement.classList.contains('add-expense-btn')) {
            const button = e.target.classList.contains('add-expense-btn') ? 
                e.target : e.target.parentElement;
            const expenseItem = button.closest('.expense-item');
            
            if (expenseItem.parentElement === availableContainer) {
                // Move from available to selected
                selectedContainer.appendChild(expenseItem);
                button.innerHTML = '<i class="fas fa-arrow-left"></i>';
                button.classList.remove('btn-outline-primary');
                button.classList.add('btn-outline-danger');
                button.setAttribute('aria-label', 'Remove from budget');
            } else {
                // Move from selected to available
                availableContainer.appendChild(expenseItem);
                button.innerHTML = '<i class="fas fa-arrow-right"></i>';
                button.classList.remove('btn-outline-danger');
                button.classList.add('btn-outline-primary');
                button.setAttribute('aria-label', 'Add to budget');
            }
            
            updateTotals();
        }
    });
    
    // Update totals and chart whenever expenses are moved
    function updateTotals() {
        let totalExpenses = 0;
        const selectedExpenses = [];
        const monthlyIncome = initialMonthlyIncome;
        const expenseBreakdown = {};
        
        // Loop through all selected expenses
        selectedContainer.querySelectorAll('.expense-item').forEach(function(item) {
            const amount = parseFloat(item.dataset.amount);
            const name = item.dataset.name;
            totalExpenses += amount;
            selectedExpenses.push(parseInt(item.dataset.id));
            
            // Add to expense breakdown for chart
            expenseBreakdown[name] = amount;
        });
        
        // Update display
        totalExpensesElement.textContent = '$' + totalExpenses.toFixed(2);
        const remainingBudget = monthlyIncome - totalExpenses;
        remainingBudgetElement.textContent = '$' + remainingBudget.toFixed(2);
        
        // Update remaining budget color based on balance
        if (remainingBudget < 0) {
            remainingBudgetElement.className = 'text-danger';
        } else {
            remainingBudgetElement.className = 'text-primary';
        }
        
        // Update form input
        selectedExpensesInput.value = JSON.stringify(selectedExpenses);
        
        // Update chart
        updateChart(expenseBreakdown, remainingBudget);
    }
    
    function updateChart(expenseBreakdown, remainingBudget) {
        // Create labels and data for chart
        const labels = Object.keys(expenseBreakdown);
        const data = Object.values(expenseBreakdown);
        
        // Only show remaining budget if positive
        if (remainingBudget > 0) {
            labels.push('Remaining');
            data.push(remainingBudget);
        }
        
        // Generate colors for each expense
        const colors = generateColors(labels.length);
        
        // Update chart
        budgetChart.data.labels = labels;
        budgetChart.data.datasets[0].data = data;
        budgetChart.data.datasets[0].backgroundColor = colors.map(c => c + '0.5)');
        budgetChart.data.datasets[0].borderColor = colors.map(c => c + '1)');
        budgetChart.update();
    }
    
    // Generate colors for chart
    function generateColors(count) {
        const colors = [];
        for (let i = 0; i < count; i++) {
            // Use a predefined color for "Remaining"
            if (i === count - 1) {
                colors.push('rgba(54, 162, 235, ');
            } else {
                // Generate a color based on position in the spectrum
                const hue = (i * 137.5) % 360; // Use golden angle approximation for distribution
                colors.push(`rgba(${hslToRgb(hue / 360, 0.7, 0.5)}, `);
            }
        }
        return colors;
    }
    
    // Convert HSL to RGB for chart colors
    function hslToRgb(h, s, l) {
        let r, g, b;
        
        if (s === 0) {
            r = g = b = l;
        } else {
            const hue2rgb = (p, q, t) => {
                if (t < 0) t += 1;
                if (t > 1) t -= 1;
                if (t < 1/6) return p + (q - p) * 6 * t;
                if (t < 1/2) return q;
                if (t < 2/3) return p + (q - p) * (2/3 - t) * 6;
                return p;
            };
            
            const q = l < 0.5 ? l * (1 + s) : l + s - l * s;
            const p = 2 * l - q;
            r = hue2rgb(p, q, h + 1/3);
            g = hue2rgb(p, q, h);
            b = hue2rgb(p, q, h - 1/3);
        }
        
        return [Math.round(r * 255), Math.round(g * 255), Math.round(b * 255)];
    }
    
    // Handle form submission
    submitButton.addEventListener('click', function(e) {
        e.preventDefault();
        
        // Get the form data
        const formData = new FormData(simulationForm);
        
        // Submit using fetch API
        fetch(simulationForm.action, {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            },
            credentials: 'same-origin'
        })
        .then(response => response.json())
        .then(data => {
            // Display feedback
            feedbackContainer.style.display = 'block';
            
            // Update feedback header based on success
            if (data.is_successful) {
                // If successful, show success message and redirect to result page
                window.location.href = resultUrl + '?simulation_id=' + data.simulation_id + 
                                      '&selected=' + encodeURIComponent(JSON.stringify(data.selected_expenses)) + 
                                      '&totalSelected=' + data.total_selected + 
                                      '&monthlyIncome=' + data.monthly_income;
                return; // Exit early as we're redirecting
            } else {
                feedbackHeader.className = 'card-header bg-warning';
                feedbackTitle.textContent = 'Budget Needs Adjustment';
            }
            
            // Add random feedback content only
            feedbackContent.innerHTML = '';
            if (data.random_feedback) {
                const randomFeedback = document.createElement('div');
                randomFeedback.className = 'alert alert-info';
                randomFeedback.textContent = data.random_feedback;
                feedbackContent.appendChild(randomFeedback);
            }
            
            // Add budget summary
            const summary = document.createElement('div');
            summary.className = 'mt-4';
            summary.innerHTML = `
                <h5>Budget Summary:</h5>
                <p>Total Selected: $${data.total_selected.toFixed(2)}</p>
                <p>Monthly Income: $${data.monthly_income.toFixed(2)}</p>
                <p>
                    Difference: 
                    <span class="${data.budget_difference >= 0 ? 'text-success' : 'text-danger'}">
                        $${data.budget_difference.toFixed(2)}
                    </span>
                </p>
            `;
            feedbackContent.appendChild(summary);
            
            // Add Show Solution button
            const showSolutionBtn = document.createElement('button');
            showSolutionBtn.className = 'btn btn-info mb-3';
            showSolutionBtn.textContent = 'Show Solution';
            showSolutionBtn.id = 'show-solution-btn';
            feedbackContent.appendChild(showSolutionBtn);
            
            // Add event listener for Show Solution button
            showSolutionBtn.addEventListener('click', function() {
                this.style.display = 'none';
                
                // Create a container for detailed solution
                const detailedSolution = document.createElement('div');
                detailedSolution.className = 'mt-4';
                feedbackContent.appendChild(detailedSolution);
                
                // If there are missing essential expenses, display them
                if (data.missing_essential && data.missing_essential.length > 0) {
                    const missingList = document.createElement('div');
                    missingList.className = 'alert alert-danger mt-3';
                    missingList.innerHTML = '<h5>Missing Essential Expenses:</h5><ul></ul>';
                    const missingUl = missingList.querySelector('ul');
                    
                    data.missing_essential.forEach(expense => {
                        const li = document.createElement('li');
                        li.innerHTML = `<strong>${expense.name}</strong> - $${expense.amount.toFixed(2)}`;
                        missingUl.appendChild(li);
                        
                        // Highlight this expense in the available list
                        const availableItems = availableContainer.querySelectorAll('.expense-item');
                        availableItems.forEach(item => {
                            if (parseInt(item.dataset.id) === expense.id) {
                                item.style.backgroundColor = '#f8d7da';
                                item.style.borderColor = '#dc3545';
                                item.style.borderLeft = '4px solid #dc3545';
                            }
                        });
                    });
                    
                    detailedSolution.appendChild(missingList);
                }
                
                // Show selected expenses with their status
                if (data.selected_expenses && data.selected_expenses.length > 0) {
                    const expensesList = document.createElement('div');
                    expensesList.className = 'mt-4';
                    expensesList.innerHTML = '<h5>Your Selected Expenses:</h5>';
                    
                    const table = document.createElement('table');
                    table.className = 'table table-sm';
                    table.innerHTML = `
                        <thead>
                            <tr>
                                <th>Expense</th>
                                <th>Amount</th>
                                <th>Status</th>
                            </tr>
                        </thead>
                        <tbody></tbody>
                    `;
                    
                    const tbody = table.querySelector('tbody');
                    
                    data.selected_expenses.forEach(expense => {
                        const tr = document.createElement('tr');
                        tr.innerHTML = `
                            <td>${expense.name}</td>
                            <td>$${expense.amount.toFixed(2)}</td>
                            <td>${expense.essential ? 
                                '<span class="badge bg-danger">Essential</span>' : 
                                '<span class="badge bg-secondary">Optional</span>'}</td>
                        `;
                        tbody.appendChild(tr);
                    });
                    
                    expensesList.appendChild(table);
                    detailedSolution.appendChild(expensesList);
                }
            });
            
            submitButton.style.display = 'none';
            
            // Scroll to feedback
            feedbackContainer.scrollIntoView({ behavior: 'smooth' });
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred while submitting your budget. Please try again.');
        });
    });
});