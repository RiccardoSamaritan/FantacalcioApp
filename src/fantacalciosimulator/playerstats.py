from dataclasses import dataclass

@dataclass
class PlayerStats:
    """
    This class represents the statistics of a player for a specific matchday in Fantacalcio.
    """
    rating: float = 0.0
    gf: int = 0      # Goals scored
    gs: int = 0      # Goals conceded
    rp: int = 0      # Penalty saved
    rs: int = 0      # Penalty scored
    rf: int = 0      # Penalty failed
    au: int = 0      # Own goals
    amm: int = 0     # Yellow card
    esp: int = 0     # Red card
    ass: int = 0     # Assists

    
    def __post_init__(self):
        """
        Convert the rating instance to a float. If there's an "*" in the rating, the rating is put to 0.
        """
        if isinstance(self.rating, str) and "*" in self.rating:
            self.rating = 0.0
        else:
            self.rating = float(self.rating)

