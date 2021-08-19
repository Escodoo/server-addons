To configure this module, you will need to set up products for vehicle Model and for inspection item.


* Activate Developer Mode
* Open menu ``[[ Settings ]] >> Technical >> Automation >> Automated Actions``
* Create new record and set field **Action To Do** to *Execute Python Code*.
  For example:

  * **Action Name**: *Test*
  * **Model**: *Contact*
  * **Trigger Condition**: *On Creation*
  * **Before Update Domain**: Optional. You can specify a condition that must be
    satisfied before record is updated. The field may not be available
    depending on **Trigger Condition** value.
  * **Server actions to run**:

    * **Action Name**: *Test Action*
    * **Action To Do**: *Execute Python Code*
    * **Condition**: Optional. You can specify a condition that must be satisfied before executing the Action.
    * **Python Code**:
      ::

          WEBHOOK="https://PASTE-YOUR-WEBHOOK-URL"
          data = {
              "partner_id": record.id,
              "partner_name": record.name,
          }
          make_request("POST", WEBHOOK, data=data)

  * Save everything
