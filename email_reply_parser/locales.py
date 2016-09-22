class Locales(object):
    @classmethod
    def get_locale(cls, locale='en'):
        return getattr(cls, locale)

    en = dict(
        sig='(--|__|-\w)|(^Sent from my (\w+\s*){1,3})',
        quote_hdr='^:etorw.*nO',
        multi_quote_hdr='(?!On.*On\s.+?wrote:)(On\s(.+?)wrote:)',
        quoted='(>+)',
        header='^(From|Sent|To|Subject): .+',
    )
    it = dict(
        sig='(--|__|-\w)|(^Inviato da (\w+\s*){1,3})',
        quote_hdr='^:ottircs\sah.*lI',
        multi_quote_hdr='(?!Il.*Il\s.+?ha\sscritto:)(Il\s(.+?)ha\sscritto:)',
        quoted='(>+)',
        header='^(Da|Data|A|Ogg): .+',
    )
