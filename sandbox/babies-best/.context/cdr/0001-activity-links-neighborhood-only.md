# Activity links neighborhood only

Activities sit in NYC’s borough → neighborhood hierarchy. We store only an optional Neighborhood on Activity (`null` = citywide) and derive borough from `neighborhood.borough`, instead of duplicating both levels on the activity. PlaceFilter may still step borough then neighborhood for browse; that filter state is not copied onto Activity.
