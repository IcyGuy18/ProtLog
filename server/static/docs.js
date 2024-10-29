document.addEventListener("DOMContentLoaded", () => {
    fetch('/md')
        .then(response => {
            if (!response.ok) throw new Error('Network response was not ok');
            return response.text();
        })
        .then(data => {
            data = data.replaceAll("\\n", "")
            data = data.replace(/^"(.*)"$/, '$1')
            data = data.replace(/^"(.*)"$/, '$1') // I need to do some freaky formatting here...
            document.getElementById('markdown').innerHTML = data;
        })
        .catch(error => {
            console.error('Error fetching file:', error);
        });
});