import os
import requests
from dotenv import load_dotenv
import datetime
import base64
import mimetypes
import openai

load_dotenv()
STABILITY_KEY = os.getenv('STABILITYAI_API_KEY')
OPENAI_KEY = os.getenv("OPENAI_API_KEY")


if not OPENAI_KEY:
    raise RuntimeError("OPENAI_API_KEY 환경 변수가 설정되지 않았습니다.")

openai.api_key = OPENAI_KEY

# Stability AI를 사용하여 새로운 이미지 생성
def generate_image_from_prompt(image_path, output_path):
    # Stability AI API
    response = requests.post(
        "https://api.stability.ai/v2beta/stable-image/control/style",
        headers={
            "authorization": STABILITY_KEY,
            "accept": "image/*"
        },
        files={
            "image": open(image_path, "rb"),
        },
        data={
            "prompt": f'''
            Combine these two image into one thing that one can sit on.
            All materials should be wood or 90% wood (0.9). 
            Details should be minimalistic and bold(0.8), with a clean, modern(0.9) aesthetic.
            Take the key design concepts from the given image.
            Keep it rectangular and simple.
            Maintain the top surface's original shape.
            The final image should be on against a clean white studio background with soft, even lighting.
            ''',
           'negative_prompt': '''
           ''',
           'fidelity': 1.0,
            "output_format": "png"
        },
    )
    if response.status_code == 200: # successes -> file save 
        with open(output_path, 'wb') as file:
            file.write(response.content)
        print(f"Image saved successfully: {output_path}")
    else: # error -> print error message
        raise Exception(str(response.json()))




# image to url
def image_to_base64(image_path):
    # MIME 타입 추론
    mime_type, _ = mimetypes.guess_type(image_path)
    
    # 이미지 파일을 읽고 Base64로 인코딩
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
    
    # 데이터 URL 형식으로 반환
    return f"data:{mime_type};base64,{encoded_string}"
    

# OpenAI를 사용하여 이미지 설명 생성
def describe_furniture(image_url):
    """
    OpenAI API를 사용하여 이미지에 대한 설명을 생성하는 함수
    """
    try:
        prompt = '''
        이미지 속 가구에 대한 자세한 설명을 제공해 주세요. ~처럼, ~같다의 표현이 아니라, ~입니다. 같은 확실한 표현을 사용해 주세요. 먼저, 첫번째 부분은 가구에 대해 흥미롭게 설명할 수 있도록 가구의 스타일은 어떤 것에 가까우며, 언제 사용하면 좋을지 창의적으로 재치있게 알려주세요.
        먼저, 첫번째 부분은 가구에 대해 흥미롭게 설명할 수 있도록 가구의 스타일은 어떤 것에 가까우며, 언제 사용하면 좋을지 창의적으로 재치있게 알려주세요.
        두번째는 도면 제작을 위해서 각 부분의 재료, 색상, 크기, 두께를 포함해야 하며, 모든 치수는 밀리미터(mm) 단위로 작성해 주세요. 먼저 가구의 상단 표면을 우선적으로 묘사해 주세요. 상단 표면의 모양을 가능한 한 정확하게 설명하고, 모든 치수와 세부 사항을 포함해 주세요.

        다음 각 부분에 대해 구체적인 정보를 제공해 주세요:

        1. 상단 표면: 재료, 색상, 모양, 치수, 두께.
        2. 다리: 재료, 색상, 높이, 폭, 두께.
        3. 프레임: 재료, 색상, 치수, 두께.
        4. 추가 요소: 선반이나 서랍 같은 기타 부품이 있다면, 해당 부품의 재료, 색상, 치수, 두께.

        묘사가 정확하고 상세하며 포괄적이어야, 도면이 가구의 모든 필수 특성을 반영할 수 있습니다.

        '''

        response = openai.chat.completions.create(
            model="gpt-4o-mini",  
            messages=[
                {"role": "system", "content": "You are a furniture designer."},
                {
                    "role": "user",
                    "content":[
                        {"type": "text", "text" : prompt},
                        {
                            "type": "image_url",
                            "image_url":{
                                "url": image_url,
                            },
                        },
                    ],
                }
            ],
            max_tokens=500,
        )
        # ```html과 ```제거
        content = response.choices[0].message.content.replace("```html", "").replace("```", "")
        print(content)
        return content

    except Exception as e:
        raise Exception(f"설명 생성 실패: {e}")


# Vision API만 TEST
if __name__ == "__main__":
    image_path = "app/static/images/output/0e083918d5a64687e1d1deffb182b78f_output.png"
    image_data = image_to_base64(image_path)
    description = describe_furniture(image_data)
    print(description)