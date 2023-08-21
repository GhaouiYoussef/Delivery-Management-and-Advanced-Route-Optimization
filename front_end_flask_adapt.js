function optimizeDelivery() {
    const firm = document.getElementById("firm").value;
    const locations = document.getElementById("locations").value.split("/");
    const num_vehicles = parseInt(document.getElementById("num_vehicles").value);
    const max_duration= document.getElementById("max_duration").value;


    const data = { firm, locations, num_vehicles , max_duration };
    //the data is collected successfully
    console.log(data);
    fetch('http://localhost:5000/optimize', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        
        body: JSON.stringify(data),
    })
    .then(response => response.json())
    .then(result => {
        console.log(result); // Add this line to check the received data in the console
        // Split the result by "\n" and create separate <p> elements for each line
    const resultLines = result.split('\n');
    const resultHTML = resultLines.map(line => `<p>${line}</p>`).join('');

    document.getElementById("result").innerHTML = resultHTML;
})

    .catch(error => {
        console.error('Error fetching optimized routes:(najem yetaada lel flask', error);
    });
}
//   