import {Plugin} from "@html_editor/plugin";
import {registry} from "@web/core/registry";
import {_t} from "@web/core/l10n/translation";
import {BaseOptionComponent} from "@html_builder/core/utils";

export class MembershipOption extends BaseOptionComponent {
    static template = "website_membership.membershipOption";
    static selector = "main:has(#oe_structure_website_membership_index_1)";
    static title = _t("Membership Snippet Options");
    static groups = ["website.group_website_designer"];
    static editableOnly = false;
}

class MembershipOptionPlugin extends Plugin {
    static id = "membershipOption";
    resources = {builder_options: [MembershipOption]};
}

registry
    .category("website-plugins")
    .add(MembershipOptionPlugin.id, MembershipOptionPlugin);
