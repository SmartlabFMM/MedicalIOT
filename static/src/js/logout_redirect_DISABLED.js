/** @odoo-module **/

import { registry } from "@web/core/registry";
import { patch } from "@web/core/utils/patch";
import { LogoutButton } from "@web/webclient/user_menu/user_menu";

// Override the logout action to redirect to custom login page
patch(LogoutButton.prototype, {
    async onClick() {
        // Perform the logout action on the server first
        try {
            await this.orm.call('res.users', 'action_logout');
        } catch (e) {
            console.warn('Logout call failed:', e);
        }

        // Redirect to custom login page instead of default
        window.location.href = '/mediot/logout';
    }
});
