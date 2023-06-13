from fastapi import FastAPI

from models.gptRequest import extract_meaningful_words
from models.signLanguage import signLangs
from config.db import conn
from schemas.signLang import signLang
from sqlalchemy import text
from config.configkey import API_KEY_OPENAI  ## 주호꺼
from config.configkey import API_KEY_OPENAI_JAC  ## 내꺼
import openai
import uuid
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

## CORS 에러 해결하기
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class KSL_translater_to_req(BaseModel):
    sentence: str

class KSL_translater_from_req(BaseModel):
    word_arr: list
@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/find/{word}")
def fetch_all(word):
    print("단어:" + word)
    query = text("SELECT aniadress FROM sign_lang WHERE word LIKE :pattern")
    query = query.bindparams(pattern='%' + word + '%')
    data2 = conn.execute(query)
    print(data2)
    type(data2)
    for row in data2:
        print(row)

    if data2.rowcount > 0:
        for row in data2:
            print(row)
            break
        link = row[0]
    else:
        print("no data")
        link = "nodata"
    return link


@app.get("/wFind/{word}")
def find_same(word):
    openai.api_key = API_KEY_OPENAI_JAC
    ans = ""
    ans = fetch_all(word)
    if ans == "nodata":
        prompt = word + "와 뜻이 똑같은 표준어로 이루어진 5개를 유사도 높은순으로 한줄로 나열해주는데 '단어/단어/단어/단어/단어' 형식으로 출력해줘"
        completion = openai.ChatCompletion.create(
            model='gpt-3.5-turbo',
            messages=[
                {'role': 'user', 'content': prompt}
            ],
            temperature=0
        )

        # 응답 필터링
        response_messages = completion['choices'][0]['message']['content'].split('/')
        filtered_messages = filter_responses(response_messages)

        # 결과 출력
        output = '/'.join(filtered_messages)
        print(output)
        print(type(output))

        result = output.split('/')

        for row in result:
            ans = fetch_all(row)
            if ans != "nodata":
                break
    return ans


@app.post("/roomCreate")
def room_create():
    generated_uuid = uuid.uuid1()
    print(generated_uuid)
    room_id = str(generated_uuid)
    query = text(f"INSERT INTO room VALUES ('{room_id}')")
    result = conn.execute(query)
    conn.commit()
    return room_id


@app.get("/roomCheck/{room_id}")
def room_check(room_id: str):
    print("123123")
    query = text(f"SELECT COUNT(*) FROM room WHERE roomId = '{room_id}'")
    result = conn.execute(query)
    count = result.scalar()
    print(result)
    print(count)

    reply = False
    if count > 0:
        print("success")
        reply = True
    else:
        print("failed")
    return reply


@app.delete("/deleteRoom/{room_id}")
def delete_room(room_id: str):
    # SQL query to delete the room
    query = text("DELETE FROM room WHERE roomId = :room_id")

    # Execute the DELETE query
    result = conn.execute(query, {"room_id": room_id})
    conn.commit()
    # Check the number of affected rows
    if result.rowcount > 0:
        return {"message": "Room deleted successfully",
                "status": "success"
                }
    else:
        return {"message": "Room not found",
                "status": "failed"
                }


@app.post("/combineWord")
def combine_word(req: KSL_translater_from_req):
    openai.api_key = API_KEY_OPENAI
    a=req.word_arr
    result = ', '.join(a)
    print(result)
    prompt = "단어가 담긴 배열을 너한태 넘겨 줄건데 그 단어들만 사용해서 최대한 문맥에 맞게 한문장만 만들어줘" + result
    completion = openai.ChatCompletion.create(
        model='gpt-3.5-turbo',
        messages=[
            {'role': 'user', 'content': prompt}
        ],
        temperature=0
    )
    gpt = completion['choices'][0]['message']['content']
    print(gpt)
    abc={"translated_sentence": gpt}

    return abc


@app.post("/sentenceAnalysis")
def sentence_analysis(req: KSL_translater_to_req):
    # 문장 문법검사후 단어들을 배열에 넣음
    print(req.sentence)
    words_array = extract_meaningful_words(req.sentence)
    print(type(words_array))
    link = []
    for word in words_array:
        print(find_same(word))
        link.append(find_same(word))
    return link


def filter_responses(responses):
    filtered_responses = []
    for response in responses:
        if "세요" not in response:
            filtered_responses.append(response)
    return filtered_responses
