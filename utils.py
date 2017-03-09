import pint

def speed_to_pace(speed):
    """ Convert speed (m/s) to pace (MM:SS/mile)"""
    
    u = pint.UnitRegistry()
    
    pace = 1 / (speed * u.meter / u.second).to(u.mile / u.minute)
    pace = ':'.join([str(int(pace.magnitude)),                 
                     str(int((pace.magnitude * 60) % 60)).zfill(2)])
    return pace

def nanosecond_to_hms(t):
    """ Convert time in nanosecond to HH:MM:SS """
    u = pint.UnitRegistry()
    
    # convert from nanoseconds to hour
    t = (t * 1e-9 * u.second).to(u.hour)
    
    hms = [str(int(t.magnitude)),
           str(int(t.magnitude * 60) % 60).zfill(2),
           str(int((t.magnitude * 3600) % 60)).zfill(2)]
    
    t = ':'.join(hms) if t.magnitude >= 1 else ':'.join(hms[1:])
                    
    return t