from urllib.request import urlopen
import boto3
from urllib.error import URLError, HTTPError
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

	# throws error occured if there was a problem accessing data
	# otherwise downloads and uploads to s3

	try:
		source_response = urlopen(source_url)

	except HTTPError as e:
		raise Exception('HTTPError: ', e.code, new_filename)

	except URLError as e:
		raise Exception('URLError: ', e.reason, new_filename)

	else:

		html = source_response.read().decode()

		parser = MyHTMLParser()
		parser.feed(html)
		
		try:
			data_response = urlopen(parser.data)

		except HTTPError as e:
			raise Exception('HTTPError: ', e.code, new_filename)

		except URLError as e:
			raise Exception('URLError: ', e.reason, new_filename)

		else:

			data = data_response.read()
			file_location = '/tmp/' + new_filename

			with open(file_location, 'wb') as f:
				f.write(data)

			# uploading new s3 dataset

			s3 = boto3.client('s3')
			s3.upload_file(file_location, s3_bucket, new_s3_key)

			return [{'Bucket': s3_bucket, 'Key': new_s3_key}]