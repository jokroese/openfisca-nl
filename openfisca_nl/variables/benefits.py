"""This file defines variables for the modelled legislation.

A variable is a property of an Entity such as a Person, a Household…

See https://openfisca.org/doc/key-concepts/variables.html
"""

# Import from openfisca-core the objects used to code the legislation in OpenFisca
from openfisca_core.periods import MONTH
from openfisca_core.variables import Variable

# Import the Entities specifically defined for this tax and benefit system
from openfisca_nl.entities import Household, Person


class pension(Variable):
    value_type = float
    entity = Person
    definition_period = MONTH
    label = "Pension income"
    reference = "https://www.belastingdienst.nl/wps/wcm/connect/nl/pensioen/pensioen"

    def formula(person, period, _parameters):
        """Pension income.

        This is a user input representing pension income received.
        """
        # This is an input variable - the default formula just returns 0
        return 0


class household_income(Variable):
    value_type = float
    entity = Household
    definition_period = MONTH
    label = "The sum of the salaries of those living in a household"

    def formula(household, period, _parameters):
        """A household's income."""
        salaries = household.members("salary", period)
        return household.sum(salaries)
