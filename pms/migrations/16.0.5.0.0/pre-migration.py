# Copyright 2026 Commit [Sun]
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
"""Keep the commercial inventory of the availability plan rules alive.

Odoo drops the column of a field that disappeared from the code when it
garbage-collects its ``ir.model.data`` entry, and that happens AFTER the
post-migration runs. Renaming the three columns here is what lets the
post-migration read them, and it leaves the data in the database as the
material to roll back with and to verify against.

The rules are also copied night by night to ``pms_inventory_migration_plan_rule``,
which is what the post-migration reads. Odoo runs the pre-migrations of every
version before the post-migration of any, so a database upgraded straight past
16.0.6.0.0 has its rules collapsed into date ranges, and their ``date`` column
set aside, by the time this version's post-migration runs.
"""
import logging

from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)

_INVENTORY_COLUMNS = ("quota", "max_avail", "plan_avail")

# What the post-migration reads: the rules as they were, one row per night.
SNAPSHOT_TABLE = "pms_inventory_migration_plan_rule"
_SNAPSHOT = """
    CREATE TABLE {table} AS
    SELECT
        id,
        availability_plan_id,
        pms_property_id,
        room_type_id,
        date,
        {columns}
    FROM pms_availability_plan_rule
"""

# A view that still shows the removed fields breaks the validation of the
# combined arch while any sibling view is written, which aborts the upgrade.
# The ones owned by a module are replaced by their own update, so only the
# orphans are dealt with here.
_DISABLE_ORPHAN_VIEWS = """
    UPDATE ir_ui_view view
    SET active = FALSE
    WHERE view.active
      AND view.arch_db::text ~ %(fields)s
      AND 'pms.availability.plan.rule' IN (
          view.model,
          (SELECT root.model FROM ir_ui_view root WHERE root.id = view.inherit_id)
      )
      AND NOT EXISTS (
          SELECT 1
          FROM ir_model_data data
          WHERE data.model = 'ir.ui.view'
            AND data.res_id = view.id
      )
    RETURNING view.id, view.name
"""


@openupgrade.migrate()
def migrate(env, version):
    for column in _INVENTORY_COLUMNS:
        if openupgrade.column_exists(env.cr, "pms_availability_plan_rule", column):
            openupgrade.rename_columns(
                env.cr, {"pms_availability_plan_rule": [(column, None)]}
            )
    env.cr.execute(
        _DISABLE_ORPHAN_VIEWS,
        {"fields": "|".join('name="%s"' % column for column in _INVENTORY_COLUMNS)},
    )
    disabled = env.cr.fetchall()
    if disabled:
        _logger.warning(
            "%s view(s) showing the inventory of the availability plan rules "
            "were archived, they belong to no module and need a manual "
            "review: %s",
            len(disabled),
            disabled,
        )
    _snapshot_rules(env)


def _snapshot_rules(env):
    cr = env.cr
    if openupgrade.table_exists(cr, SNAPSHOT_TABLE):
        return
    columns = []
    for column in _INVENTORY_COLUMNS:
        legacy = openupgrade.get_legacy_name(column)
        if openupgrade.column_exists(cr, "pms_availability_plan_rule", legacy):
            columns.append(legacy)
        else:
            columns.append(f"NULL::integer AS {legacy}")
    if openupgrade.column_exists(cr, "pms_availability_plan_rule", "real_avail"):
        columns.append("real_avail")
    else:
        columns.append("NULL::integer AS real_avail")
    openupgrade.logged_query(
        cr, _SNAPSHOT.format(table=SNAPSHOT_TABLE, columns=", ".join(columns))
    )
