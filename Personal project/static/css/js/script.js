document.addEventListener('DOMContentLoaded', function() {
    // Function to fetch the user name
    function fetchUserName() {
        fetch('/test_token')
            .then(response => response.json())
            .then(data => {
                // Display the user name
                document.getElementById('user_name').textContent = data.user_name;
            })
            .catch(error => {
                console.error('Error fetching user name:', error);
                document.getElementById('user_name').textContent = 'Error fetching user name';
            });
    }

    // Fetch the user name when the page loads
    fetchUserName();
});