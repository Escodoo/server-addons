# Copyright 2026 - TODAY, Wesley Oliveira <wesley.oliveira@escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from lxml import etree

from odoo import api, models


class TierValidation(models.AbstractModel):
    _inherit = "tier.validation"

    @api.depends("review_ids", "review_ids.status", "review_ids.state_from")
    def _compute_validation_status(self):
        for item in self:
            current_state = item._tier_validation_get_current_state_value()
            reviews = item.review_ids.filtered(
                lambda r, cs=current_state: r.state_from == cs
            )

            if not reviews:
                item.validation_status = "no"
                continue

            validated_states = item._validated_states()
            rejected_states = item._rejected_states()

            if any(reviews.filtered(lambda x, rs=rejected_states: x.status in rs)):
                item.validation_status = "rejected"
            elif all(x.status in validated_states for x in reviews):
                item.validation_status = "validated"
            elif any(reviews.filtered(lambda x: x.status == "pending")):
                item.validation_status = "pending"
            else:
                item.validation_status = "waiting"

    def _compute_need_validation(self):
        for rec in self:
            if not rec.id:
                rec.need_validation = False
                continue

            current_state = rec._tier_validation_get_current_state_value()
            tier_definitions = (
                self.env["tier.definition"]
                .sudo()
                .search(
                    [
                        ("model", "=", self._name),
                        ("company_id", "in", [False] + rec._get_company().ids),
                        ("state_from.value", "=", current_state),
                    ]
                )
            )

            valid_tiers = any([rec.evaluate_tier(tier) for tier in tier_definitions])
            current_reviews = rec.review_ids.filtered(
                lambda r, cs=current_state: r.state_from == cs
            )

            rec.need_validation = not current_reviews and valid_tiers

    def _prepare_tier_review_vals(self, definition, sequence):
        vals = super()._prepare_tier_review_vals(definition, sequence)
        vals.update(
            {
                "state_from": definition.state_from.value,
                "state_to": definition.state_to.value,
            }
        )
        return vals

    def _check_state_conditions(self, vals):
        self.ensure_one()
        state_field = self._state_field
        if state_field not in vals:
            return False

        current_state = self._tier_validation_get_current_state_value()
        target_state = vals[state_field]

        matching_tiers = (
            self.env["tier.definition"]
            .sudo()
            .search(
                [
                    ("model", "=", self._name),
                    ("company_id", "in", [False] + self._get_company().ids),
                    ("state_from.value", "=", current_state),
                    ("state_to.value", "=", target_state),
                ]
            )
        )
        return any(self.evaluate_tier(tier) for tier in matching_tiers)

    def request_validation(self, target_state=None):
        if not target_state:
            return super().request_validation()

        td_obj = self.env["tier.definition"]
        tr_obj = self.env["tier.review"]
        vals_list = []
        for rec in self:
            current_state = rec._tier_validation_get_current_state_value()
            domain = [
                ("model", "=", self._name),
                ("company_id", "in", [False] + rec._get_company().ids),
                ("state_from.value", "=", current_state),
            ]
            if target_state:
                domain.append(("state_to.value", "=", target_state))

            tier_definitions = td_obj.sudo().search(domain, order="sequence desc")

            sequence = len(rec.review_ids)
            for td in tier_definitions:
                if rec.evaluate_tier(td):
                    sequence += 1
                    vals_list.append(rec._prepare_tier_review_vals(td, sequence))

        created_trs = tr_obj.create(vals_list)
        self._notify_review_requested(created_trs)
        return created_trs

    def _check_and_request_tier(self, target_state):
        self.ensure_one()
        tier_definitions = (
            self.env["tier.definition"]
            .sudo()
            .search(
                [
                    ("model", "=", self._name),
                    ("state_from.value", "=", self.state),
                    ("state_to.value", "=", target_state),
                ],
            )
        )
        valid_tiers = any([self.evaluate_tier(tier) for tier in tier_definitions])

        if not valid_tiers:
            return False

        current_reviews = self.review_ids.filtered(
            lambda r: r.state_from == self.state and r.state_to == target_state
        )

        if not current_reviews:
            self.request_validation(target_state=target_state)
            return True

        if any(review.status != "approved" for review in current_reviews):
            return True

        return False

    def write(self, vals):
        if self._state_field in vals:
            target_state = vals[self._state_field]
            needs_validation = False
            for rec in self:
                if rec._check_and_request_tier(target_state):
                    needs_validation = True

            if needs_validation:
                return True
        return super().write(vals)

    def _add_tier_validation_buttons(self, node, params):
        str_element = self.env["ir.qweb"]._render(
            "tier_validation_dynamic_state.tier_validation_buttons_hide_request", params
        )
        new_node = etree.fromstring(str_element)
        return new_node

    def _compute_hide_reviews(self):
        for rec in self:
            hide_reviews = True
            tier_definitions = (
                rec.env["tier.definition"]
                .sudo()
                .search(
                    [
                        ("model", "=", rec._name),
                        ("state_from.value", "=", rec.state),
                    ],
                )
            )
            if tier_definitions:
                hide_reviews = False
            rec.hide_reviews = hide_reviews
