class Airport(object):
    """An Airport class holds valuable information to interact with
    the 3-letter code cities defined by iata."""

    def __init__(self, iata, name, short_name, country_code, country_name,
                 tz_region, viat_payscale):
        """
        Provide all required fields to create an airport.
        """
        self.iata = iata
        self.name = name
        self.shortName = short_name
        self.countryCode = country_code
        self.countryName = country_name
        self.tzRegionName = tz_region
        self.viatPayScale = viat_payscale

    def __str__(self):
        """
        Only print as the iata 3-letter code
        """
        return self.iata
