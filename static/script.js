function readDocuments() {
    fetch('http://127.0.0.1:5000/read')
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success' && data.data.length > 0) {
            const formattedData = data.data.map(doc => JSON.stringify(doc, null, 2)).join('\n');
            document.getElementById('responseArea').innerText = formattedData;
        } else {
            document.getElementById('responseArea').innerText = 'No documents found';
        }
    })
    .catch(error => console.error('Error:', error));
}
