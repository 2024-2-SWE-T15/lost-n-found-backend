import math
import base64

from fastapi import HTTPException

from geoalchemy2 import WKTElement, WKBElement
from geoalchemy2.shape import to_shape
from shapely.geometry import Point

from haversine import haversine, inverse_haversine, Unit, Direction

from db.mysql.model import *

def distance(a: tuple[float, float], b: tuple[float, float]):
  return math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)


def haversineDistance(a: tuple[float, float], b: tuple[float, float]):
  return haversine(a, b, unit=Unit.METERS)


def haversineSquare(a: tuple[float, float], distance: float):
  boundary = {}
  boundary['NORTH'] = inverse_haversine(a, distance, direction=Direction.NORTH, unit=Unit.METERS)
  boundary['SOUTH'] = inverse_haversine(a, distance, direction=Direction.SOUTH, unit=Unit.METERS)
  boundary['EAST'] = inverse_haversine(a, distance, direction=Direction.EAST, unit=Unit.METERS)
  boundary['WEST'] = inverse_haversine(a, distance, direction=Direction.WEST, unit=Unit.METERS)
  return boundary


def tuple2PointString(coordinates: tuple[float, float]):
  return f"POINT({coordinates[0]} {coordinates[1]})"


def parsePointString(point_str: str):
  if "POINT" in point_str:
    point_coords = point_str.split('POINT(')[1].strip(')')
    longitude, latitude = map(float, point_coords.split())
    return Point(longitude, latitude)
  return None


def tuple2Point(coordinates: tuple[float, float]):
  return Point(coordinates[0], coordinates[1])


def point2Tuple(point: Point):
  if point is not None:
    shape = to_shape(point)
    return (shape.x, shape.y)
  return None

def point2TupleStructure(obj: object):
  for key, value in obj.__dict__.items():
    if isinstance(value, Point) or isinstance(value, WKTElement) or isinstance(value, WKBElement):
      obj.__dict__[key] = point2Tuple(value)
  return obj

def convertTuple2Zone(coordinates: tuple[float, float], gap: float):
  def binarySearch(start, end, gap, target):
    constant = 1 // gap + 1
    start = int(start) * constant
    end = int(end) * constant
    tmp = target * constant
    
    while start < end:
      mid = (start + end) // 2
      if tmp < mid:
        end = mid - 1
      else:
        start = mid + 1
    
    result = start / constant
    if target < result:
      result -= gap
    elif target > result + gap:
      result += gap
    
    return result
  
  return (binarySearch(-90, 90, gap, coordinates[0]), binarySearch(-180, 180, gap, coordinates[1]))


def postImgName(post_id: str, img_id: str, ext: str):
  return f"{post_id}_{img_id}.ext"


def dataURL2Img(data_url: str):
  header, base64_data = data_url.split(',', 1)
  ext = header.split('/')[1].split(';')[0]
  
  binary_data = base64.b64decode(base64_data)
  return ext, binary_data


def tokenReform(token: dict, provider: str):
  try:
    return {'access_token': f"{provider} {token['access_token']}",
            'refresh_token': f"{provider} {token['refresh_token']}",
            'token_type': 'Bearer'}
  except KeyError:
    pass
  
  try:
    return {'access_token': f"{provider} {token['access_token']}",
            'token_type': 'Bearer'}
  except KeyError:
    raise HTTPException(status_code=403, detail='forbidden')



# model structure
modelDict = {
  User: ['id', 'nickname', 'profile_image_url', 'create_time', 'update_time'],
  Post: ['id', 'title', 'user_id', 'coordinates', 'description', 'create_time', 'update_time', 'valid', 'is_lost'],
  Hashtag: ['name', 'last_access'],
  Stronghold: ['id', 'name', 'coordinates', 'description'],
  Photo: ['id', 'post_id', 'extension', 'data'],
  Identity: ['post_id', 'name', 'value'],
  TagMatch: ['post_id', 'tag_name'],
}

def model2Array(model):
  return [(model.__dict__[attr] if not isinstance(model.__dict__[attr], (WKTElement, WKBElement)) 
           else point2Tuple(model.__dict__[attr]))
           for attr in modelDict[type(model)]]
            

def models2Array(models):
  return [model2Array(model) for model in models]
