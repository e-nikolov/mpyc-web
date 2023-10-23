var count = 0;
var tabIDs = [];

localStorage.tabCount = 0;

onconnect = function (event) {
    const port = event.ports[0];
    localStorage.tabCount = parseInt(localStorage.tabCount) + 1;

    port.onmessage = function (e) {
        data = e.data;

        switch (data.command) {
            case "closing":
                localStorage.tabCount = parseInt(localStorage.tabCount) - 1;
                break;
        }
    };
};
