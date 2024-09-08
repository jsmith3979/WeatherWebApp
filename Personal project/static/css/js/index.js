// You can access user_name via JavaScript, though it's already embedded in the HTML
document.addEventListener('DOMContentLoaded', function() {
    const userName = document.getElementById('user_name').textContent;
    console.log('Current user:', userName);
});