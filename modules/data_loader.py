import pandas as pd
from modules.matches import HARDCODED_MATCHES

def get_matches():
    # Maak DataFrame van je 72 wedstrijden
    df = pd.DataFrame(HARDCODED_MATCHES)
    
    # Zorg dat getallen ook echt als getallen worden gezien voor de sortering
    df['match_id'] = pd.to_numeric(df['match_id'])
    df['speeldag'] = pd.to_numeric(df['speeldag'])
    
    return df.sort_values('match_id')
