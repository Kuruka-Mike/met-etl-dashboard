if (window.dash_clientside === undefined) { window.dash_clientside = {}; }
window.dash_clientside.clients_notification = {
    show: function (notification) {
        if (notification) {
            // Return the notification in the format expected by NotificationContainer
            return [{
                "action": "show",
                "id": notification.id || "notification-" + Date.now(),
                "title": notification.title,
                "message": notification.message,
                "color": notification.color,
                "icon": notification.icon
            }];
        }
        return window.dash_clientside.no_update;
    }
}
