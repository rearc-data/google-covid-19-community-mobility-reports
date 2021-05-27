from urllib.request import urlopen
import boto3
from urllib.error import URLError, HTTPError
from html.parser import HTMLParser
from s3_md5_compare import md5_compare
from io import BytesIO

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

			s3_uploads = []
			s3 = boto3.resource('s3')

			has_changes = md5_compare(s3_bucket, new_s3_key + new_filename, BytesIO(data))
			if has_changes:
				s3.Object(s3_bucket, new_s3_key + new_filename).put(Body=data)
				print('Uploaded: ' + new_filename)
			else:
				print('No changes in: ' + new_filename)
			asset_source = {'Bucket': s3_bucket, 'Key': new_s3_key + new_filename}
			s3_uploads.append({'has_changes': has_changes, 'asset_source': asset_source})

			count_updated_data = sum(upload['has_changes'] == True for upload in s3_uploads)

			asset_list = []
			if count_updated_data > 0:
				asset_list = list(map(lambda upload: upload['asset_source'], s3_uploads))
				if len(asset_list) == 0:
					raise Exception('Something went wrong when uploading files to s3')

			return asset_list