# -*- coding: utf-8 -*-
'''
@author: Alex von Brandenfels

'''

import datetime
import sqlite3

# Number of seconds in 365.25 years (1 Julian year):
SECS_IN_YEAR = 31557600

LIGHT_YEARS_IN_1_PARSEC = 3.26163344

# Standard constellation abbreviations, as dict:
CONST_ABBREV = {"And": "Andromeda","Ant": "Antlia","Aps": "Apus","Aqr": "Aquarius","Aql": "Aquila","Ara": "Ara","Ari": "Aries","Aur": "Auriga","Boo": "Boötes","Cae": "Caelum","Cam": "Camelopardalis","Cnc": "Cancer","CVn": "Canes Venatici","CMa": "Canis Major","CMi": "Canis Minor","Cap": "Capricornus","Car": "Carina","Cas": "Cassiopeia","Cen": "Centaurus","Cep": "Cepheus","Cet": "Cetus","Cha": "Chamaeleon","Cir": "Circinus","Col": "Columba", "Com": "Coma Berenices","CrA": "Corona Australis","CrB": "Corona Borealis","Crv": "Corvus","Crt": "Crater","Cru": "Crux","Cyg": "Cygnus","Del": "Delphinus","Dor": "Dorado","Dra": "Draco","Equ": "Equuleus","Eri": "Eridanus","For": "Fornax","Gem": "Gemini","Gru": "Grus","Her": "Hercules","Hor": "Horologium","Hya": "Hydra","Hyi": "Hydrus","Ind": "Indus","Lac": "Lacerta","Leo": "Leo","LMi": "Leo Minor","Lep": "Lepus","Lib": "Libra","Lup": "Lupus","Lyn": "Lynx","Lyr": "Lyra","Men": "Mensa","Mic": "Microscopium","Mon": "Monoceros","Mus": "Musca","Nor": "Norma","Oct": "Octans","Oph": "Ophiuchus","Ori": "Orion","Pav": "Pavo","Peg": "Pegasus","Per": "Perseus","Phe": "Phoenix","Pic": "Pictor","Psc": "Pisces","PsA": "Piscis Austrinus","Pup": "Puppis","Pyx": "Pyxis","Ret": "Reticulum","Sge": "Sagitta (not to be confused with Sagittarius)","Sgr": "Sagittarius","Sco": "Scorpius","Scl": "Sculptor","Sct": "Scutum","Ser": "Serpens","Sex": "Sextans","Tau": "Taurus","Tel": "Telescopium","Tri": "Triangulum","TrA": "Triangulum Australe","Tuc": "Tucana","UMa": "Ursa Major","UMi": "Ursa Minor","Vel": "Vela","Vir": "Virgo","Vol": "Volans","Vul": "Vulpecula"}

class Star(object):
    """
    A class representing a star in the galaxy. Designed for data from
    the HYG Star Database: github.com/astronexus/HYG-Database
    """
    def __init__(self, database_id, hip_id, gl_id, proper_name, distance,
                 magnitude, color, constellation):
        """
        Most of these args are equivalents of fields in the HYG database.
        Args preceded by * in the list below are considered optional, and
        should be given as an empty string if not known.
        Args:
            database_id: The star's ID in HYG-Database
            *hip_id: The star's ID in the Hipparcos catalog.
            gl_id: The star's ID in the third edition of the Gliese Catalog of Nearby Stars
            dist: The star's distance from Earth in parsecs
            *proper_name: The star's proper name (e.g. Betelgeuse).
            magnitude: The star's "apparent magnitude" (see Wikipedia).
            *color: The star's "color index", where known (see Wikipedia).
            *constellation: The standard 3-letter abbreviation of the
                constellation that the star belongs to. (Abbreviations and
                their corresponding constellations are recorded in the
                dictionary CONST_ABBREV, declared at the beginning of this file)
            
        """
        self._database_id = database_id
        self._gl_id = gl_id
        self._distance = distance
        self._proper_name = proper_name
        self._magnitude = magnitude
        self._color = color
        self._constellation = constellation

        if hip_id != "":
            self._hip_id = "HIP " + str(hip_id)
            # The HIP ID is simply recorded as a number in the HYG database.
            # This is too ambiguous to serve as a unique identifier in most
            # other contexts, so we prefix it with "HIP ".
        else:
            self._hip_id = ""

    def get_color(self):
        """
        Turns a star's B-V color index into either "blue", "yellow", or
        "red". Obviously this is an oversimplification.
        If there's no record of a star's color, we just choose red.
        """
        if self._color != '':
            if self._color < 0.35:
                return 'blue'
            if self._color < 0.8:
                return 'yellow'
        return 'red'
    
    def has_proper_name(self):
        """
        Returns True if there's a record of the star's proper name.
        """
        return self._proper_name != ''
    
    def has_constellation(self):
        """
        Returns True if there's a record of which constellation the star is in.
        """
        return self._constellation != ''

    def get_constellation(self):
        """
        Returns the constellation in which the star is located, if there is
        record of it. Otherwise, returns an empty string.
        """
        return CONST_ABBREV[self._constellation]

    def is_visible(self):
        """
        Returns True if a star is probably visible to the naked eye.
        
        More specifically, returns true if a star's apparent magnutude is
        less than 6.5, which is the criteria for visibility used by the
        "apparent magnitude" page on Wikipedia.
        """
        return self._magnitude < 6.5

    def get_identifier(self):
        """
        Returns the HIP ID if it is known, otherwise returns the GL ID.
        
        Preference is given to the HIP ID, because that is the default
        designation used by another tool that I might use at some point. But
        most astronomical tools these days will accept either kind of ID
        interchangeably, so it shouldn't really matter which kind we get here.
        """
        if self._hip_id != "":
            return self._hip_id
        return self._gl_id

    def get_distance_in_lightyears(self):
        """
        Returns the star's distance from Earth in light years.
        """
        return self._distance * LIGHT_YEARS_IN_1_PARSEC
        
    def when_will_light_hit(self, emit_date):
        """
        The light emitted by the star on emit_date will reach (or did reach)
        Earth on the date returned by this method.
        
        If you give this method your birth date, and it returns today's date,
        it means that the light that left the star when you were born will
        hit Earth today.
        """
        light_years_traveled = years_since_date(emit_date)
        timedelta = datetime.timedelta(days = (self.get_distance_in_lightyears() - light_years_traveled) * 365.25)
        return (datetime.datetime.now() + timedelta).date()
        

def years_since_date(date):
    """
    date: A date, as a datetime.date object
    Returns: The amount of time that has passed since that date, in years
    """
    return (datetime.datetime.now().date() - date).total_seconds() / SECS_IN_YEAR

def get_star_from_years(light_years, db_cursor):
    """
    Returns the star closest to light_years light years away.
    TODO: Check exactly what the max searchable value is
    Args:
        years: a number of years (max value: at least 100)
        db_cursor: The SQLite cursor connected to the stars database
    """
    db_cursor.execute("SELECT * FROM stars ORDER BY ABS(? - distance) LIMIT 1", (light_years/LIGHT_YEARS_IN_1_PARSEC,))
    return Star(*db_cursor.fetchone())

def main():
    with sqlite3.connect('stars.db') as conn:
        c = conn.cursor()
        date_str = input("Enter your birthday (mm/dd/yyyy): ")
        date_object = datetime.datetime.strptime(date_str, "%m/%d/%Y").date()
        star = get_star_from_years(years_since_date(date_object), c)
        print("Your current birth star is " + star.get_identifier() + ".")
        future_tense_modifier = ""
        if years_since_date(star.when_will_light_hit(date_object)) < 0:
            # Date is in the future
            future_tense_modifier = "will "
        print("The light that left this star when you were born " +
              future_tense_modifier + "hit the earth on " + str(star.when_will_light_hit(date_object)))

if __name__ == "__main__":
    main()
