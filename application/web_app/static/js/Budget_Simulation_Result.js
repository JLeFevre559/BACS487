// Budget Simulation Result Page JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Get the expenses data from the template
    const selectedExpenses = JSON.parse(document.getElementById('selected-expenses-data').textContent);
    const monthlyIncome = parseFloat(document.getElementById('monthly-income').textContent);
    const totalSelected = parseFloat(document.getElementById('total-selected').textContent);
    const remainingBudget = monthlyIncome - totalSelected;
    
    // Initialize chart
    const ctx = document.getElementById('budget-chart').getContext('2d');
    
    // Create labels and data for chart
    const labels = selectedExpenses.map(exp => exp.name);
    const data = selectedExpenses.map(exp => exp.amount);
    
    // Only show remaining budget if positive
    if (remainingBudget > 0) {
        labels.push('Remaining');
        data.push(remainingBudget);
    }
    
    // Generate colors for the chart
    const colors = generateColors(labels.length);
    
    // Create the chart
    let budgetChart = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: labels,
            datasets: [{
                label: 'Budget',
                data: data,
                backgroundColor: colors.map(c => c + '0.5)'),
                borderColor: colors.map(c => c + '1)'),
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false
        }
    });
    
    // Generate colors for chart
    function generateColors(count) {
        const colors = [];
        for (let i = 0; i < count; i++) {
            // Use a predefined color for "Remaining"
            if (i === count - 1 && labels[i] === 'Remaining') {
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
});