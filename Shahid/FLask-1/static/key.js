var s = io();

// Log connection status
s.on('connect', function() {
    console.log("Connected to Flask-SocketIO server");
});

s.on('server_message', function(data) {
    console.log("Message from server:", data.message);
});

s.on('screen_switch', function(data) {
    console.log("Switched to:", data.window);
    alert("Switched to: " + data.window); 
});


document.addEventListener("keydown", function(event) {
    let key = event.key.toLowerCase();
    if (key === "c" || key === "v") {
        if (event.ctrlKey || event.metaKey) {
            alert("Copying and Pasting are restricted on this page!");
            event.preventDefault();
        }else {
                alert("The '" + event.key.toUpperCase() + "' key is restricted on this page!");
                event.preventDefault();
            }
        }
    
});

