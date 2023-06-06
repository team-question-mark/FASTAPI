from fastapi import FastAPI

from models.gptRequest import extract_meaningful_words
from models.signLanguage import signLangs
from config.db import conn
from schemas.signLang import signLang
from sqlalchemy import text
from config.configkey import API_KEY_OPENAI## 주호꺼
from config.configkey import API_KEY_OPENAI_JAC ## 내꺼
import openai
import uuid
from fastapi.middleware.cors import CORSMiddleware

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

@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}


@app.get("/find/{word}")
def fetch_all(word):
    # data = conn.execute(signLangs.select().where(signLangs.c.word.like('%' + word + '%'))).fetchall()
    print("단어" + word)
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
    openai.api_key = API_KEY_OPENAI
    ans = ""
    ans = fetch_all(word)
    if ans == "nodata":
        prompt = word + "와 뜻이 똑같은 표준어로 이루어진 5개를 유사도 높은순으로 한줄로 나열해주는데 '단어/단어/단어/단어/단어' 형식으로 출력해줘"
        completion = openai.ChatCompletion.create(
            model='gpt-3.5-turbo',
            messages=[
                {'role': 'user', 'content': prompt}
            ],
            temperature=0.5
        )
        gpt = completion['choices'][0]['message']['content']
        print(gpt)
        print(type(gpt))

        result = gpt.split('/')

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


@app.get("/combineWord/{words}")
def combine_word(words: str):
    openai.api_key = API_KEY_OPENAI
    prompt = words+"위 단어들만 가지고 문법에 맞게 조사를 넣어서 자연스럽게 문장을 끝내줘"
    completion = openai.ChatCompletion.create(
        model='gpt-3.5-turbo',
        messages=[
            {'role': 'user', 'content': prompt}
        ],
        temperature=0.5
    )
    gpt = completion['choices'][0]['message']['content']
    print(gpt)

    return gpt


@app.get("/sentenceAnalysis/{sentence}")
def sentence_analysis(sentence: str):
    # 예시 문장
    sentence = "한문장에서 유의미한 표준어의 단어 혹은 숙어를 추출하고자 합니다. "+sentence

    # 유의미한 단어와 숙어 추출
    words = extract_meaningful_words(sentence)
    print(type(words))
    for word in words:
        print(find_same(word))
    return words ## 미완성
