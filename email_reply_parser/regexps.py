from yaml import load

def regexps(locale):
    with open('email_reply_parser/locales.yaml', 'r') as stream:
        return load(stream)['regexps'][locale]

