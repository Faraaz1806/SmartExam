document.addEventListener("visibilitychange", function() {
    if (document.hidden) {
        alert("You Can Not Switch Tab!");
    } else {
        console.log("User returned to the tab.");
    }
});
