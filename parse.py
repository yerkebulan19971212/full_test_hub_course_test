import requests

url = 'https://probtest.testcenter.kz/tester/core/api/v1/subject/items/4/question/items/2'

a = [20, 10, 10, 40, 40]
answersign = ["A", "B", "C", "D", "E", "F", "G", "H", ]
for k in range(5):
    text = ""
    for i in range(a[k]):
        url = f"https://probtest.testcenter.kz/tester/core/api/v1/subject/items/{k + 1}/question/items/{i + 1}"
        r = requests.get(
            url=url,
            headers={
                "Authorization": "Bearer eyJhbGciOiJIUzUxMiJ9.eyJtb2R1bGVzIjoyLCJzdHVkZW50VGVzdElkIjoxODg4ODUsInRlc3RUeXBlR3JvdXAiOjJ9.EJswbxhsMBrKpEhTPMCeyDnOtBSkl0xkvB0SrOTEwlQ1Xh7ISWfyupY5T73CHDHsmD0x9zVvIG-88gNz_Am72A"
            }
        )
        data = r.json().get("data")
        answers = data.get("answers")
        text += f"{i + 1}" + data.get("content").replace("\n", "")
        text += "\n"
        for n, ans in enumerate(answers):
            text += answersign[n] + "." + ans.get("content").replace("\n", "")
        text += "\n"
        text += "\n"
        text += "\n"
    with open(f'example-{k + 1}.txt', 'w', encoding='utf-8') as file:
        file.write(text)
