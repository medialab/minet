import random as rd

import minet.user_agents.data as data

def get_random_useragent():
    return rd.choices(data.USER_AGENTS, cum_weights=data.USER_AGENTS_SHARE_CDF, k=1)[0]

