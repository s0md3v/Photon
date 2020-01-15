import re
import hashlib

from core.values import result

meta = {
    'author' : 'Somdev Sangwan',
    'description' : 'extracts input forms from webpages',
    'phase' : 'while-parsing'
}

result['modules']['forms'] = {}

def forms(data):
    response = re.sub(r'(?s)<!--.*?-->', '', data['response'].text)
    forms = []
    matches = re.findall(r'(?i)(?s)<form.*?</form.*?>', response)
    if matches:
        for match in matches:
            page = re.search(r'(?i)action=[\'"](.*?)[\'"]', match)
            method = re.search(r'(?i)method=[\'"](.*?)[\'"]', match)
            form = {}
            form['action'] = (page.group(1)) if page else data['response'].url
            form['method'] = (method.group(1)).lower() if method else 'get'
            form['inputs'] = []
            inputs = re.findall(r'(?i)(?s)<input.*?>', response)
            for inp in inputs:
                inpName = re.search(r'(?i)name=[\'"](.*?)[\'"]', inp)
                if inpName:
                    inpType = re.search(r'(?i)type=[\'"](.*?)[\'"]', inp)
                    inpValue = re.search(r'(?i)value=[\'"](.*?)[\'"]', inp)
                    inpName = (inpName.group(1))
                    inpType = (inpType.group(1)) if inpType else ''
                    inpValue = (inpValue.group(1)) if inpValue else ''
                    if inpType.lower() == 'submit' and inpValue == '':
                        inpValue = 'Submit Query'
                    inpDict = {
                    'name' : inpName,
                    'type' : inpType,
                    'value' : inpValue
                    }
                    form['inputs'].append(inpDict)
            forms.append(form)
    for form in forms:
        checksum = hashlib.md5((str(form)).encode('utf-8')).hexdigest()
        result['modules']['forms'][checksum] = form
