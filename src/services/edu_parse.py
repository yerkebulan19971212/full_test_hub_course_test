import requests
import base64
import boto3


class S3Service:
    def __init__(self):
        self._bucket_name = 'chi-sextans'
        self.s3 = boto3.client(
            's3',
            endpoint_url='https://object.pscloud.io',
            aws_access_key_id='2Q9W2HT8H61JCYV79ZGG',
            aws_secret_access_key='gFXHzS9xvzhBN9TGJeoPAELXtOzZ3iObCNDkYvCd'
        )

    def upload_base64_data(self, key, base64_data):
        base64_data_list = base64_data.split(",")
        if len(base64_data_list) > 1:
            base64_data = base64_data_list[1]
        binary_data = base64.b64decode(base64_data + '==')
        self.s3.put_object(Bucket=self._bucket_name, Key=key, Body=binary_data, ContentType='image/png')

    def get_url(self, file_name: str = None):
        if file_name is None:
            return None
        return self.s3.generate_presigned_url(
            "get_object",
            Params={"Bucket": self._bucket_name, "Key": file_name},
            ExpiresIn=3600,
        ).split("?A")[0]


s3_service = S3Service()


def get_token():
    login_url = "https://edutest-iam-service.azurewebsites.net/api/auth/login"
    res_login = requests.post(url=login_url, json={
        "username": "87778244593",
        "password": "XGpMyyRF_32yZ8"
    })
    return res_login.json()["data"]["token"]


id = input("Id:")
authorization = "Bearer " + get_token()
print("authorization")
test_url = f"https://edutest-test-results-service.azurewebsites.net/api/student-exam/question-result/{id}"

res_test = requests.get(url=test_url, headers={
    "Authorization": authorization
})
data = res_test.json()["data"]["student_report_subject_responses"]

from bs4 import BeautifulSoup


def get_correct_answer_number(answers, answer_ids):
    correct_answer = []
    for i, answer in enumerate(answers, 1):
        if answer["answer_id"] in answer_ids:
            correct_answer.append(str(i))
    return correct_answer


def parse_images_to_files(html_content, id: str):
    soup = BeautifulSoup(html_content, 'html.parser')
    img_tags = soup.find_all('img')
    for img_tag in img_tags:
        src_data = img_tag['src']
        img_data = src_data.split(',')[-1]
        filename = f"image_{id}.png"
        s3_service.upload_base64_data(filename, img_data)
        path = s3_service.get_url(filename)
        img_tag['src'] = path
    return str(soup)


def download_image_as_base64(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    img_tags = soup.find_all('img')
    for img_tag in img_tags:
        try:
            src_data = img_tag['src']
            response = requests.get(src_data)
            if response.status_code == 200:
                base64_data = base64.b64encode(response.content).decode('utf-8')
                filename = f"image_{src_data.split('/')[-1]}"
                s3_service.upload_base64_data(filename, base64_data)
                path = s3_service.get_url(filename)
                img_tag['src'] = path
            else:
                print(f"Failed to download image. Status code: {response.status_code}")
                return None
        except Exception as e:
            print(f"An error occurred: {e}")
            return str(soup)
    return str(soup)


for d in data:
    questions = d["student_report_question_status_responses"]
    file_name = d["name"].strip() + f'_{id}' + ".txt"
    print(file_name)
    with open(file_name, "w", encoding='utf-8') as f:
        for q in questions:
            question_url = f"https://edutest-test-results-service.azurewebsites.net/api/student-exam/get-question-with-correct?setQuestionId={q['set_question_id']}&studentResultId={id}"
            res_question = requests.get(url=question_url, headers={
                "Authorization": authorization
            })
            question_data = res_question.json()['data']
            question_content = question_data["question_content"]
            question_content = question_content.replace("\n", "<br />") if question_content else question_content
            if "<img" in question_content:
                if "base64" in question_content:
                    question_content = parse_images_to_files(question_content, q['set_question_id'])
                question_content = download_image_as_base64(question_content)
            question_context = question_data["question_context"]
            question_context = question_context.replace("\n", "<br />") if question_context else question_context
            if question_context:
                if "<img" in question_context:
                    if "base64" in question_context:
                        question_context = parse_images_to_files(question_context, q['set_question_id'])
                    question_context = download_image_as_base64(question_context)
            answers = question_data["answers"]
            choice = "CHOICE"
            point = 1
            if len(answers) > 4:
                choice = "MULTICHOICE"
                point = 2
            if question_context:
                f.write("*" + str(question_context))
                f.write("\n")
            f.write("#" + str(question_content))
            f.write("\n")
            f.write("point " + str(point))
            f.write("\n")
            f.write("ch " + choice)
            f.write("\n")
            ans_o = []
            count = 1
            compliance_items = question_data.get("compliance_items", None)
            if compliance_items:
                ans_o_2 = []
                for i, ci in enumerate(compliance_items):
                    content = ci.get('content')
                    if "<img" in content:
                        if "base64" in content:
                            content = parse_images_to_files(content, q['set_question_id'])
                        content = download_image_as_base64(content)
                    if i == 0:
                        f.write(f"$SUB_QUESTION{content}")
                    else:
                        f.write(f"$$SUB_QUESTION{content}")
                    f.write('\n')
                    ans_o_2 += get_correct_answer_number(answers, ci.get("correct_answers"))
                c_ans_new = ",".join(ans_o_2)
            for ans in answers:
                answer_content = ans['answer_content']
                answer_content = answer_content.replace("\n", "<br />")
                if "<img" in answer_content:
                    if "base64" in answer_content:
                        answer_content = parse_images_to_files(answer_content, q['set_question_id'])
                    answer_content = download_image_as_base64(answer_content)
                correct = ans['correct']
                if correct:
                    ans_o.append(str(count))
                f.write(str(answer_content))
                f.write("\n")
                count += 1
            if ans_o:
                if choice == 'MULTICHOICE':
                    c_ans_new = ','.join(ans_o)
                else:
                    c_ans_new = ans_o[0]

            f.write(c_ans_new)
            f.write("\n")
            f.write("\n")
        f.write("End")
