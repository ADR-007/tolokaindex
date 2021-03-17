import pycld2


ukr = set(s.lower() for s in 'АБВГҐДЕЄЖЗИІЇЙКЛМНОПРСТУФХЦЧШЩЬЮЯʼ')
rus = set(s.lower() for s in 'АаБбВвГгДдЕеЁёЖжЗзИиЙйКкЛлМмНнОоПпСсТтУуФфХхЦцЧчШшЩщЪъЫыЬьЭэЮюЯя')
eng = set(s.lower() for s in 'AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz')
rus_specific = rus - ukr - eng
cyrillic = ukr | rus


class Language:
    UKR = 'UKRAINIAN'.capitalize()
    ENG = 'ENGLISH'.capitalize()
    RUS = 'RUSSIAN'.capitalize()

    UNKNOWN = 'Unknown'


def detect_language(text: str) -> str:
    text_chars = set(text.lower())

    if text_chars & rus_specific:
        return Language.RUS

    if text_chars & cyrillic:
        return Language.UKR

    is_reliable, _, details = pycld2.detect(text, hintLanguage='en')

    if not is_reliable and text_chars & eng:
        return Language.ENG

    return details[0][0].capitalize()
