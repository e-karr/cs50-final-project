// Run script once DOM is loaded
document.addEventListener('DOMContentLoaded', function() {

    let db = new sqlite3.Database("/kvkl_registration.db", sqlite3.OPEN_READWRITE, (err) => {
        if (err) {
            console.error(err.message);
        }

        console.log("Connected to the kvkl database.");
    });

});