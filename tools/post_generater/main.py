import os, sys
import random
from dotenv import load_dotenv
from geopy.distance import distance

import torch
from transformers import BitsAndBytesConfig
from langchain_huggingface import ChatHuggingFace, HuggingFacePipeline

from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(os.path.dirname(__file__)))))

from db.mysql import database as mysql_db
from db.mysql import model as mysql_model
from db.mysql import crud as mysql_crud
from db.mysql import schema as mysql_schema

from modules.utils import tuple2PointString

load_dotenv()

class generator:
  quantization_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype="float16",
    bnb_4bit_use_double_quant=True,
    llm_int8_enable_fp32_cpu_offload=True,
  )

  chat_model = HuggingFacePipeline.from_model_id(
    model_id="LGAI-EXAONE/EXAONE-3.0-7.8B-Instruct",
    task="text-generation",
    # device_map="auto",
    pipeline_kwargs=dict(
      max_new_tokens=512,
      do_sample=False,
      repetition_penalty=1.03,
    ),
    model_kwargs={
      'torch_dtype': torch.float16,
      'device_map': 'auto',
      'quantization_config': quantization_config,
      'trust_remote_code':True
      }
  )
  
  llm = ChatHuggingFace(llm=chat_model)

  with open("word.txt") as f:
    words = f.read().split('\n')
    
  @classmethod
  def generate(cls):
    post = {}
    word = random.choice(cls.words)

    ai_message = cls.llm.invoke(f"잃어버린 물건을 찾기 위해 작성하는 포스트를 만들어줘. 관련된 물건은 {word}야. 해시태그를 붙일 경우에만 #을 사용해. 그 외 필요 없는 말은 하지마.")
    ai_message = ai_message.content.split('[|assistant|]')[1].split('\n')
    
    try:
      ai_message.remove('')
    except ValueError:
      pass
    post['description'] = ' '.join(ai_message)
    
    hashtags = [tag[1:] for tag in post['description'][post['description'].find('#'):].split()]
    
    ai_message = cls.llm.invoke(f"description은 잃어버린 물건을 찾기 위해 작성하는 포스트글이야. 해당 글의 적절한 제목을 지어줘. 오직 제목만 보여주고 제목을 선정한 이유는 전부 출력하지 마. description: {post['description']}")
    ai_message = ai_message.content.split('[|assistant|]')[1].split('"')[1]
    
    post['title'] = ai_message
    post['hashtags'] = hashtags
    return post


def randomCoordinate(coordinate, radius):
  radius_km = radius / 1000
  
  random_angle = random.uniform(0, 360)
  random_distance = random.uniform(0, radius_km)
  
  random_location = distance(kilometers=random_distance).destination(coordinate, random_angle)
  
  return (random_location.latitude, random_location.longitude)

def pushPost(postSchemaAdd: mysql_schema.PostSchemaAddLost,
             hashtags: list[str],
             db: Session):
  
  
  if not (post := mysql_crud.post.register(db, mysql_model.Post(title=postSchemaAdd.title, 
                                                              user_id="110467447451800603165", 
                                                              coordinates=tuple2PointString(postSchemaAdd.coordinates), 
                                                              description=postSchemaAdd.description,
                                                              is_lost=True))):
    pass

  # hash tags
  for hashtag in hashtags:
    if not (tag := mysql_crud.hashtag.get(db, hashtag)):
      tag = mysql_crud.hashtag.register(db, hashtag)
    
    if not hashtag in mysql_crud.tag_match.getAll(db, post.id) and (tag_match := mysql_crud.tag_match.register(db, mysql_model.TagMatch(post_id=post.id, tag_name=tag.name))):
      tag = mysql_crud.hashtag.update(db, tag.name)

if __name__ == "__main__":
  SessionLocal = mysql_db.initDB()
  db: Session = SessionLocal()
  try:
    for i in range(70):
      post = generator.generate()
      pushPost(mysql_model.Post(title=post['title'],
                                user_id="110467447451800603165",
                                coordinates=randomCoordinate((37.295346404935195, 126.97159007969412), 500),
                                description=post['description'],
                                ), post['hashtags'], db)
  finally:
    db.close()