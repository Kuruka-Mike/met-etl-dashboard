if (window.dash_clientside === undefined) { window.dash_clientside = {}; }
window.dash_clientside.clients_notification = {
    show: function (notification) {
        if (notification && window.dash_mantine_components && window.dash_mantine_components.showNotification) {
            window.dash_mantine_components.showNotification(notification);
        }
        return window.dash_clientside.no_update;
    }
}
