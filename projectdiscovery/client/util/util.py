#Embedded file name: e:\jenkins\workspace\client_SERENITY\branches\release\SERENITY\packages\projectdiscovery\client\util\util.py


def calculate_score_bar_length(experience, total_xp_needed_for_current_rank, total_xp_needed_for_next_rank, max_score_bar_length):
    xp_available_for_next_rank = float(experience - total_xp_needed_for_current_rank)
    xp_needed_for_next_rank = float(total_xp_needed_for_next_rank - total_xp_needed_for_current_rank)
    tol = 0.001
    if xp_needed_for_next_rank < tol:
        ratio = 1
    else:
        ratio = xp_available_for_next_rank / xp_needed_for_next_rank
    length = ratio * max_score_bar_length
    if length > max_score_bar_length:
        length = max_score_bar_length
    return length


def calculate_rank_band(rank):
    if rank < 10:
        rank_band = 1
    elif rank >= 100:
        rank_band = rank / 100 + 10
        if rank_band > 20:
            rank_band = 20
    else:
        rank_band = rank / 10 + 1
    return rank_band
