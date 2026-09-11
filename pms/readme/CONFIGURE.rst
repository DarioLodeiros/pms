You will find the hotel settings in PMS Management > Configuration > Properties > Your Property.

This module required additional configuration for company, accounting, invoicing and user privileges.

Derived room type prices
~~~~~~~~~~~~~~~~~~~~~~~~

A room type can take its price from another one, e.g. a Superior room costing
10 more than the Double one, so that the pricelists only need the prices of
the latter. Set it in the *Derived Price* section of the room type:

* *Price Derived From*: the room type the price is taken from. It must be
  available in all the properties of the room type, and it can take its price
  from a third one in turn (e.g. Family = Superior + 20), up to ten levels.
* *Price Variation Type* and *Price Variation*: a fixed amount, in the currency
  of the pricelist, or a percentage of the base price. Negative values lower
  it, and the price never goes below zero.
* *Price Rounding*: the multiple the prices derived by a percentage are rounded
  to, e.g. 1 for whole amounts. Zero rounds them to the currency.
* *Derive in Pricelists*: the pricelists the price is derived in. Leave it
  empty to derive it in all of them.

Mind that a derived room type with no rule of its own in a pricelist it does
not derive in gets its sales price there.

Children and room capacity
~~~~~~~~~~~~~~~~~~~~~~~~~~

By default children take no place in the room, so only the adults are checked
against its capacity. Properties that want to count them can set the system
parameter ``pms.children_occupy_capacity`` to ``True``, in Settings > Technical
> System Parameters.

Once it is on, children take the regular places of the room first and only
overflow into its children places, the ones where only a child can sleep, such
as child bunk beds. Adults never occupy those, so a room with free children
places can still be full.

Mind that turning it on refuses reservations that the property may have been
taking until then.

Commercial inventory
~~~~~~~~~~~~~~~~~~~~

How many rooms of a type the property puts on sale is configured in
PMS Management > Revenue Management > Inventory, and does not depend on the rate.
Each rule covers a date range and applies to every night in it, either in general,
through a sale channel or through an agency:

* ``Quota`` is an allowance: what is left to sell is the quota minus what the scope
  already sold. Cancelling a reservation does **not** give it back, since the quota
  was spent when it was sold.
* ``Max. Availability`` is an exposure cap and is never consumed.
* Use ``-1`` for no limit and ``0`` to close the scope.

The effective limit is the **lowest** one across the scopes that apply, so a rule for
a sale channel can only restrict further what the general rule allows. With no general
rule for a night, the ``Default Quota`` and ``Default Max. Availability`` of the room
type are used instead; the absence of a channel or agency rule adds no limit of its own.

Rules of the same scope may overlap on purpose, which is how a season is overridden for
a shorter period: on the overlap, the rule modified last wins.

Several properties, room types or days of the week can be configured at once from
PMS Management > Revenue Management > Massive Inventory Changes. Repeating a massive
change over the same period and scope rewrites the rule already there instead of adding
another one on top of it.
