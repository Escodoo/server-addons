Go to **Settings > Technical > Parameters > System Parameters** and change the
value of the parameter created by the module:

.. list-table::
   :header-rows: 1

   * - Parameter
     - Default
     - What it sets
   * - ``web_theme_color.primary``
     - ``#71639e``
     - Brand color of the backend

The value is an hexadecimal color such as ``#D01000``. Both the three digit
(``#D10``) and the six digit form are accepted. Any other value is rejected
when you save the parameter, so a typo cannot break the assets. Clearing the
value deletes the parameter, which puts the backend back on the standard Odoo
color.

After saving, reload the backend with a hard refresh (Ctrl+F5) so the browser
drops the cached assets. The default value is the standard Odoo color, so
installing the module alone changes nothing.
