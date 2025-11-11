"""This file defines variables for the modelled legislation.

A variable is a property of an Entity such as a Person, a Household…

See https://openfisca.org/doc/key-concepts/variables.html
"""

# Import from openfisca-core the objects used to code the legislation in OpenFisca
from openfisca_core.periods import MONTH
from openfisca_core.variables import Variable

# Import the Entities specifically defined for this tax and benefit system
from openfisca_nl.entities import Household


class total_taxes(Variable):
    value_type = float
    entity = Household
    definition_period = MONTH
    label = "Sum of the taxes paid by a household"
    reference = "https://www.cbs.nl/nl-nl/cijfers/detail/80068NED"

    def formula(household, period, _parameters):
        """Total taxes."""
        income_tax_i = household.members("income_tax", period)
        social_security_contribution_i = household.members(
            "social_security_contribution", period
        )

        return (
            +household.sum(income_tax_i)
            + household.sum(social_security_contribution_i)
            + household("housing_tax", period.this_year) / 12
        )
