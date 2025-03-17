document.addEventListener("visibilitychange", function() {
    if (document.hidden) {
        console.log("User switched window");
    } else {
        console.log("User returned to the tab, reloading...");
        window.location.reload(); 
    }
});
