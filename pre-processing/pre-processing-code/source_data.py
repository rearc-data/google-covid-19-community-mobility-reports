from urllib.request import urlopen
import boto3
from urllib.error import URLError, HTTPError
from html.parser import HTMLParser
from s3_md5_compare import md5_compare
from io import BytesIO
import os

class MyHTMLParser(HTMLParser):

	def __init__(self):
		HTMLParser.__init__(self)
		self.data = None

	def handle_starttag(self, tag, attr):
		if tag.lower() == 'a' and self.data == None:
			for item in attr:
				if item[0].lower() == 'href' and '.csv' in item[1]:
					self.data = item[1].split('?', 1)[0]

def source_dataset():

	source_url = 'https://www.google.com/covid19/mobility/'

	dataset_name = os.getenv('DATASET_NAME')
	asset_bucket = os.getenv('ASSET_BUCKET')

	data_dir = '/tmp'
	if not os.path.exists(data_dir):
		os.mkdir(data_dir)

	file_location = os.path.join(data_dir, dataset_name + '.csv')

	# throws error occured if there was a problem accessing data
	# otherwise downloads and uploads to s3

	try:
		source_response = urlopen(source_url)

	except HTTPError as e:
		raise Exception('HTTPError: ', e.code, dataset_name)

	except URLError as e:
		raise Exception('URLError: ', e.reason, dataset_name)

	else:

		html = source_response.read().decode()

		parser = MyHTMLParser()
		parser.feed(html)
		
		try:
			data_response = urlopen(parser.data)

		except HTTPError as e:
			raise Exception('HTTPError: ', e.code, dataset_name)

		except URLError as e:
			raise Exception('URLError: ', e.reason, dataset_name)

		else:

			filedata = data_response.read()

			s3_uploads = []
			s3_resource = boto3.resource('s3')
			s3 = boto3.client('s3')

			obj_name = file_location.split('/', 3).pop().replace(' ', '_').lower()
			new_s3_key = dataset_name + '/dataset/' + obj_name

			has_changes = md5_compare(s3, asset_bucket, new_s3_key, BytesIO(filedata))
			if has_changes:
				s3_resource.Object(asset_bucket, new_s3_key).put(Body=filedata)
				# s3.upload_file(file_location, asset_bucket, new_s3_key)
				print('Uploaded: ' + new_s3_key)
			else:
				print('No changes in: ' + new_s3_key)

			asset_source = {'Bucket': asset_bucket, 'Key': new_s3_key + new_s3_key}
			s3_uploads.append({'has_changes': has_changes, 'asset_source': asset_source})

			count_updated_data = sum(upload['has_changes'] == True for upload in s3_uploads)

			asset_list = []
			if count_updated_data > 0:
				asset_list = list(map(lambda upload: upload['asset_source'], s3_uploads))
				if len(asset_list) == 0:
					raise Exception('Something went wrong when uploading files to s3')

			return asset_list

if __name__ == '__main__':
    source_dataset()