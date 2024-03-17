import requests

url = 'https://probtest.testcenter.kz/tester/core/api/v1/subject/items/4/question/items/2'

arr = [20, 10, 10, 40, 40]
answersign = ["A", "B", "C", "D", "E", "F", "G", "H", ]
for k in range(5):
    text = ""
    print(k)
    print("k")
    for i in range(arr[k]):
        url = f"https://probtest.testcenter.kz/tester/core/api/v1/subject/items/{k + 1}/question/items/{i + 1}"
        r = requests.get(
            url=url,
            headers={
                "Authorization": "Bearer eyJhbGciOiJIUzUxMiJ9.eyJtb2R1bGVzIjoyLCJzdHVkZW50VGVzdElkIjoxODg4ODUsInRlc3RUeXBlR3JvdXAiOjJ9.EJswbxhsMBrKpEhTPMCeyDnOtBSkl0xkvB0SrOTEwlQ1Xh7ISWfyupY5T73CHDHsmD0x9zVvIG-88gNz_Am72A"
            }
        )
        point = 1
        choice = "CHOICE"
        data = r.json().get("data")
        additionalContent = data.get("additionalContent")
        if additionalContent:
            text += "*" + additionalContent['content'].strip() + "\n"
        answers = data.get("answers")
        text += f"#" + data.get("content").strip() + "\n"
        if len(answers) == 6:
            point = 2
            choice = "MULTICHOICE"
        text += f"point {str(point)} \n"
        text += f"ch {str(choice)} \n"
        if len(answers) == 2:
            a = answers[0]["answerVariants"]
            sub_1 = "$SUB_QUESTION" + answers[0]['content'].strip() + "\n"
            sub_2 = "$$SUB_QUESTION" + answers[1]['content'].strip() + "\n"
            answers = answers[0]["answerVariants"]
            text += sub_1
            text += sub_2
            print(answers)
            print("answers")
            for n, ans in enumerate(answers):
                text += ans.get("content").strip() + "\n"
        else:
            for n, ans in enumerate(answers):
                text += ans.get("content").strip() + "\n"

        text += "\n"
        text += "\n"
        text += "\n"
    with open(f'example-{k + 1}.txt', 'w', encoding='utf-8') as file:
        file.write(text)
