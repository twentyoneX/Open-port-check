// vercel-port-checker/public/script.js
document.addEventListener('DOMContentLoaded', () => {
    const scanButton = document.getElementById('scanButton');
    const resultsArea = document.getElementById('resultsArea');
    const yourIpInfo = document.getElementById('yourIpInfo');
    const loadingIndicator = document.getElementById('loadingIndicator');
    const testedPortsList = document.getElementById('testedPortsList');

    // These should match the PORTS_TO_CHECK in your Python script
    const portsToCheck = [
        21, 22, 23, 25, 53, 80, 110, 143, 443, 445, 465, 587, 993, 995,
        1194, 1701, 1723, 3306, 3389, 5060, 5061, 5222, 5555, 8080
    ];

    // Populate the list of tested ports
    portsToCheck.forEach(port => {
        const li = document.createElement('li');
        li.textContent = port;
        testedPortsList.appendChild(li);
    });


    scanButton.addEventListener('click', async () => {
        resultsArea.innerHTML = '';
        yourIpInfo.innerHTML = '';
        scanButton.disabled = true;
        loadingIndicator.style.display = 'block';

        try {
            // The path to your serverless function.
            // Vercel automatically routes /api/filename to the function.
            const response = await fetch('/api/port_check'); 
            
            if (!response.ok) {
                let errorMsg = `Error: ${response.status} ${response.statusText}`;
                try {
                    const errData = await response.json();
                    errorMsg = `Error: ${errData.error || response.statusText}`;
                } catch (e) { /* ignore if error response is not json */ }
                throw new Error(errorMsg);
            }

            const data = await response.json();

            if (data.error) {
                resultsArea.innerHTML = `<p class="error">${data.error}</p>`;
                return;
            }

            yourIpInfo.innerHTML = `<p>Scanning ports for IP: <strong>${data.client_ip}</strong></p>`;
            
            let output = '<table><thead><tr><th>Port</th><th>Status</th></tr></thead><tbody>';
            for (const port in data.ports) {
                const status = data.ports[port];
                output += `<tr><td>${port}</td><td class="${status.toLowerCase()}">${status}</td></tr>`;
            }
            output += '</tbody></table>';
            resultsArea.innerHTML = output;

        } catch (error) {
            resultsArea.innerHTML = `<p class="error">Failed to perform scan: ${error.message}</p>`;
            console.error('Scan failed:', error);
        } finally {
            scanButton.disabled = false;
            loadingIndicator.style.display = 'none';
        }
    });
});
