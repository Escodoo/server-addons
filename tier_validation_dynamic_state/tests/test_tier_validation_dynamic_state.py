# Copyright 2026 - TODAY, Wesley Oliveira <wesley.oliveira@escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import tagged

from odoo.addons.base_tier_validation.tests.common import CommonTierValidation


@tagged("post_install", "-at_install")
class TestTierValidationDynamicState(CommonTierValidation):
    def setUp(self):
        super().setUp()

        def get_selection_id(model_name, value):
            return (
                self.env["ir.model.fields.selection"]
                .search(
                    [
                        ("field_id.model_id", "=", model_name),
                        ("field_id.name", "=", "state"),
                        ("value", "=", value),
                    ],
                    limit=1,
                )
                .id
            )

        self.draft_state = get_selection_id("tier.validation.tester", "draft")
        self.confirmed_state = get_selection_id("tier.validation.tester", "confirmed")
        self.cancel_state = get_selection_id("tier.validation.tester", "cancel")

        self.tier_def_1 = self.tier_def_obj.create(
            {
                "name": "Tier 1",
                "model_id": self.tester_model.id,
                "review_type": "individual",
                "reviewer_id": self.test_user_1.id,
                "state_from": self.draft_state,
                "state_to": self.confirmed_state,
            }
        )
        self.tier_def_2 = self.tier_def_obj.create(
            {
                "name": "Tier 2",
                "model_id": self.tester_model.id,
                "review_type": "individual",
                "reviewer_id": self.test_user_2.id,
                "state_from": self.confirmed_state,
                "state_to": self.cancel_state,
            }
        )

    def test_compute_need_validation(self):
        record = self.test_record
        self.assertTrue(record.need_validation)

        record.request_validation(target_state="confirmed")

        record.flush_recordset()
        record.invalidate_recordset()
        self.env.registry.clear_cache()
        self.assertFalse(record.need_validation)

    def test_create_review_on_write(self):
        record = self.test_record
        self.assertEqual(record.state, "draft")
        self.assertFalse(record.review_ids)

        res = record.write({"state": "confirmed"})

        self.assertTrue(res)
        self.assertEqual(record.state, "draft")
        self.assertTrue(record.review_ids)

        review = record.review_ids[0]
        self.assertEqual(review.state_from, "draft")
        self.assertEqual(review.state_to, "confirmed")

    def test_compute_validation_status(self):
        record = self.test_record

        record.request_validation(target_state="confirmed")
        record.review_ids.write({"status": "approved"})
        self.assertEqual(record.validation_status, "validated")

        record.write({"state": "confirmed"})

        record._compute_validation_status()
        self.assertEqual(record.validation_status, "no")

        record.request_validation(target_state="cancel")
        record.review_ids.filtered(lambda r: r.state_from == "confirmed").write(
            {"status": "rejected"}
        )
        record._compute_validation_status()
        self.assertEqual(record.validation_status, "rejected")

    def test_request_validation_with_target_state(self):
        record = self.test_record

        self.tier_def_obj.create(
            {
                "name": "Draft to Cancel",
                "model_id": self.tester_model.id,
                "review_type": "individual",
                "reviewer_id": self.test_user_1.id,
                "state_from": self.draft_state,
                "state_to": self.cancel_state,
            }
        )

        record.request_validation(target_state="cancel")
        self.assertEqual(len(record.review_ids), 1)
        self.assertEqual(record.review_ids.state_to, "cancel")

    def test_check_state_conditions(self):
        record = self.test_record

        self.assertTrue(record._check_state_conditions({"state": "confirmed"}))
        self.assertFalse(record._check_state_conditions({"state": "unknown"}))

    def test_prepare_tier_review_vals(self):
        vals = self.test_record._prepare_tier_review_vals(self.tier_def_1, 1)
        self.assertEqual(vals["state_from"], "draft")
        self.assertEqual(vals["state_to"], "confirmed")

    def test_check_and_request_tier_no_definition(self):
        record = self.test_record

        res = record._check_and_request_tier("cancel")
        self.assertFalse(res)

        record.write({"state": "cancel"})
        self.assertEqual(record.state, "cancel")
