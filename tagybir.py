from bs4 import BeautifulSoup
import base64
import re
import regex
import json
import boto3
import time
from typing import IO, List, Union


S3_ACCESS_KEY='2Q9W2HT8H61JCYV79ZGG'
S3_SECRET_ACCESS_KEY='gFXHzS9xvzhBN9TGJeoPAELXtOzZ3iObCNDkYvCd'
S3_URL='https://object.pscloud.io'
S3_BUCKET_NAME='chi-sextans'

class S3Service:
    def __init__(
            self,
            endpoint_url: str,
            aws_access_key_id: str,
            aws_secret_access_key: str,
            bucket_name: str
    ):
        self._bucket_name = bucket_name
        self.s3 = boto3.client(
                's3',
                endpoint_url=endpoint_url
                ,aws_access_key_id=aws_access_key_id,
                aws_secret_access_key=aws_secret_access_key
        )

    def upload_file(self, key, file_data: Union[bytes, IO]):
        self.s3.put_object(Bucket=self._bucket_name, Key=key, Body=file_data)

    def upload_files(self, key: str, files: List[Union[bytes, IO]]):
        for f in files:
            self.upload_file(key, f)

    def upload_base64_data(self, key, base64_data):
        base64_data_list = base64_data.split(",")
        if len(base64_data_list) > 1:
            base64_data = base64_data_list[1]
        binary_data = base64.b64decode(base64_data + '==')
        self.s3.put_object(Bucket=self._bucket_name, Key=key, Body=binary_data, ContentType='image/svg')

    def get_url(self, file_name: str = None):
        if file_name is None:
            return None
        return self.s3.generate_presigned_url(
                "get_object",
                Params={"Bucket": self._bucket_name, "Key": file_name},
                ExpiresIn=3600,
        )

    def get_inline_url(self, file_name: str = None):
        if file_name is None:
            return None
        return self.s3.generate_presigned_url(
                "get_object",
                Params={
                    "Bucket": self._bucket_name,
                    "Key": file_name,
                    'ResponseContentDisposition': 'inline'
                },
                ExpiresIn=3600,
        )

    def get_object(self, file_name: str) -> bytes:
        res = self.s3.get_object(Bucket=self._bucket_name, Key=file_name)
        return res['Body'].read()

    def get_file_base_64(self, file_name):
        file_data = self.get_object(file_name=file_name)
        return base64.b64encode(file_data).decode('utf-8')

s3_service = S3Service(
        endpoint_url=S3_URL,
        aws_access_key_id=S3_ACCESS_KEY,
        aws_secret_access_key=S3_SECRET_ACCESS_KEY,
        bucket_name=S3_BUCKET_NAME
)

def get_max_img_cnt():
    response = s3_service.s3.list_objects_v2(Bucket=S3_BUCKET_NAME, Prefix='media_dev/parse-images/')
    img_indices = [int(re.search(r'img_(\d+)\.svg', obj['Key']).group(1)) for obj in response.get('Contents', []) if re.search(r'img_(\d+)\.svg', obj['Key'])]
    return max(img_indices, default=0)


def img_save_replace(content):
    global img_cnt
    img_pattern = r'<img[^>]+src="([^"]+)"'
    image_urls = re.findall(img_pattern, content)

    for url in image_urls:
        filename = f'img_{img_cnt}.svg'
        full_path = f'media_dev/parse-images/{filename}'
        print(url)
        s3_service.upload_file(full_path, url)
        # s3_service.upload_base64_data(full_path, base64_code)
        time.sleep(2)
        img_url_with_key = s3_service.get_url(full_path)
        img_url = img_url_with_key.split('?')[0]
        print(img_url)
        img_tag = f'<img src="{img_url}"'
        content = re.sub(img_pattern, img_tag, content)
        img_cnt+=1
    return content



def main():
    # main_dir = "C:/Users/Admin/Desktop/ЕНТ/ent/"
    main_dir = "C:/Users/Admin/Documents/Documents/Itest/"
    #   main_dir = "C:/Users/aitua/Desktop/tagybir/"
    xxx = "№720029120.html"
    downloaded_html = open(main_dir + xxx, "r", encoding='utf-8')
    index = downloaded_html.read()
    soup = BeautifulSoup(index, 'html.parser')

    script = str(soup.find_all('script'))
    pattern = regex.compile(r'ExamTest\((\{.*?\})\);')
    data = pattern.findall(script)[0]
    data_dic = json.loads(data)
    data_dic = data_dic['data']

    for s_index, subject in enumerate(data_dic['tests']):
        s_name = data_dic['tests'][s_index]['subject']['title']
        print(s_name)
        texts = {}
        try:
            for key, value in data_dic['tests'][s_index]['texts'].items():
                texts[key] = (
                    value['text']
                    .replace("/uploads/images", "https://itest.kz/uploads/images")
                    .strip().replace("\r","").replace("\n", "").replace('<meta charset="utf-8" />', ''))
        except: pass
        with open(f'{main_dir + s_name + " " + xxx[4:15]}.txt', 'w', encoding="utf-8") as the_file:
            for q_index, question in enumerate(data_dic['tests'][s_index]['questions']):
                print(q_index)
                sub_questions = data_dic['tests'][s_index]['questions'][q_index].get('children')
                try:
                    text_id = data_dic['tests'][s_index]['questions'][q_index].get('text_id')
                    if text_id:
                        text = texts[str(text_id)]
                        text = img_save_replace(text)
                        the_file.write("*" + text + "\n")
                finally:
                    quest = data_dic['tests'][s_index]['questions'][q_index]['question'].strip()\
                        .replace("\r","").replace("\n", "").replace('<meta charset="utf-8" />', '')
                    quest = img_save_replace(quest)
                    the_file.write("#" + quest + '\n')
                    corrects = []
                    ans = []
                    for a_index, answer in enumerate(data_dic['tests'][s_index]['questions'][q_index]['answer']):
                        try:
                            if data_dic['tests'][s_index]['questions'][q_index]['answer'][a_index].get('correct') == 1:
                                corrects.append(str(a_index + 1))
                        finally:
                            ans.append(data_dic['tests'][s_index]['questions'][q_index]['answer'][a_index][
                                           'answer'].strip().replace("\r", "").replace("\n", "").replace(
                                    '<meta charset="utf-8" />', '') + '\n')
                if len(ans) == 4:
                    if len(sub_questions) > 0:
                        the_file.write("ch MATCHING\n")
                        for idx, sq in enumerate(sub_questions):
                            the_file.write(f'{"$" * (idx + 1)}SUB_QUESTION {sq["question"]}\n')
                    else:
                        the_file.write("point 1\n")
                        the_file.write("ch CHOICE\n")
                else:
                    the_file.write("point 2\n")
                    the_file.write("ch MULTICHOICE\n")

                for a in ans:
                    the_file.write(a)
                the_file.write(",".join(corrects) + '\n')
                the_file.write('\n')

            pos = the_file.tell()
            pos = pos - 1
            the_file.seek(pos)
            the_file.write('End')
            the_file.close()

    #     the_file.write('Hello\n')

if __name__ == '__main__':
    img_cnt = get_max_img_cnt() + 1
    main()