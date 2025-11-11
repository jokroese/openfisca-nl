from numpy import maximum as max_

from openfisca_core.periods import MONTH, YEAR
from openfisca_core.variables import Variable

from openfisca_nl.entities import Person


class urencriterium_voldaan(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    label = "Whether the hours criterion (urencriterium) for self-employment is met"
    reference = "https://www.belastingdienst.nl/wps/wcm/connect/nl/zelfstandigen/content/hulpmiddel-urencriterium"
    documentation = """
    The hours criterion requires at least 1225 hours per year spent on self-employment
    to qualify for the zelfstandigenaftrek (self-employed deduction).
    """


class zelfstandigenaftrek(Variable):
    value_type = float
    entity = Person
    definition_period = MONTH
    label = "Self-employed deduction (zelfstandigenaftrek)"
    reference = "https://www.belastingdienst.nl/wps/wcm/connect/nl/zelfstandigen/content/hulpmiddel-zelfstandigenaftrek"

    def formula(person, period, parameters):
        """Self-employed deduction.

        Only applies if the hours criterion (urencriterium) is met.
        """
        # Check if hours criterion is met for the year
        year = period.this_year
        hours_criterion_met = person("urencriterium_voldaan", year)

        # Get annual deduction and convert to monthly
        annual_deduction = parameters(period).self_employment.zelfstandigenaftrek
        monthly_deduction = annual_deduction / 12

        # Only apply if hours criterion is met
        return hours_criterion_met * monthly_deduction


class mkb_winstvrijstelling(Variable):
    value_type = float
    entity = Person
    definition_period = MONTH
    label = "SME profit exemption (mkb-winstvrijstelling)"
    reference = "https://www.belastingdienst.nl/wps/wcm/connect/nl/zelfstandigen/content/hulpmiddel-mkb-winstvrijstelling"

    def formula(person, period, parameters):
        """SME profit exemption.

        Applied to profit after subtracting the zelfstandigenaftrek.
        Only positive profit bases are considered.
        """
        profit_before = person("winst_voor_aftrek", period)
        aftrek = person("zelfstandigenaftrek", period)

        # Clamp to zero - negative bases don't get exemption
        profit_after_deductions = max_(profit_before - aftrek, 0)

        rate = parameters(period).self_employment.mkb_winstvrijstelling_rate
        return profit_after_deductions * rate


class self_employment_taxable_income(Variable):
    value_type = float
    entity = Person
    definition_period = MONTH
    label = "Taxable income from self-employment (Box 1)"
    reference = "https://www.belastingdienst.nl/wps/wcm/connect/nl/zelfstandigen/content/winst-uit-onderneming"

    def formula(person, period, _parameters):
        """Taxable self-employment income.

        Calculated as: profit - zelfstandigenaftrek - mkb_winstvrijstelling.
        Result is clamped to zero (no negative taxable income).
        """
        winst = person("winst_voor_aftrek", period)
        zelfstandigenaftrek = person("zelfstandigenaftrek", period)
        mkb = person("mkb_winstvrijstelling", period)

        taxable = winst - zelfstandigenaftrek - mkb
        return max_(taxable, 0)
