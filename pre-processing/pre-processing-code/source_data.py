import boto3
from urllib.request import urlopen, Request
from html.parser import HTMLParser

class MyHTMLParser(HTMLParser):

    def __init__(self):
        HTMLParser.__init__(self)
        self.data = None

    def handle_starttag(self, tag, attr):
        if tag.lower() == 'a' and self.data == None:
            for item in attr:
                if item[0].lower() == 'href' and '.csv' in item[1]:
                    self.data = item[1].split('?', 1)[0]

def source_dataset(new_filename, s3_bucket, new_s3_key):

    source_url = 'https://www.google.com/covid19/mobility/'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'}
    
    request = Request(source_url, None, headers)
    html = urlopen(request)
    str_html = html.read().decode()

    parser = MyHTMLParser()
    parser.feed(str_html)

    csv_request = Request(parser.data, None, headers)

    csv_file = urlopen(csv_request).read()

    with open('/tmp/' + new_filename, 'wb') as f:
        f.write(csv_file)

    s3 = boto3.client('s3')
    s3.upload_file('/tmp/' + new_filename, s3_bucket, new_s3_key)

    return [{'Bucket': s3_bucket, 'Key': new_s3_key}]