document.addEventListener("DOMContentLoaded", function() {
    var s = io.connect('http://' + document.domain + ':' + location.port);
    
    s.on('screen_switch', function(data) {
        document.getElementById('window-name').innerText = data.window;
    });
});
