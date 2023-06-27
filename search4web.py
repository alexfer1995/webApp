def search4vowels(word: str)-> set:
    """ Return any vowels found in word"""
    vowels = set('aeiou')
    return vowels.intersection(set(word))

def search4letters(phrase: str, letters: str = 'aeiou')->set:
    """ Return any letters found in phrase"""
    return set(letters).intersection(set(phrase))

def log_request(req: 'flask_request', res: str, timestamp: float)-> None:
    """logger for web operations"""
    with open('search.log', 'a') as log:
        print(req.form, file=log)
        print(req.remote_addr, file=log)
        print(req.user_agent, file=log)
        print(res, file=log)
        print("timestamp: ", timestamp, file=log)