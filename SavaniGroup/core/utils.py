from datetime import datetime , date  , timedelta

def validate_date_formate(date):
  format = "%d-%m-%Y"
  res = True
  try:
    res = bool(datetime.strptime(date , format))
  except ValueError:
    print('value error :',ValueError)
    res = False
  return res

def is_date_less_than_or_equal_today(input_date):
  try:
    input_date = datetime.strptime(input_date, "%d-%m-%Y").date()
    today = date.today()
    if input_date <= today:
      return True
    else:
      return False
  except ValueError:
    return False

def is_date_grater_than_or_equal_today(input_date):
  try:
    input_date = datetime.strptime(input_date, "%d-%m-%Y").date()
    today = date.today()
    if input_date >= today:
      return False
    else:
      return True
  except ValueError:
    return False

def is_date_less_than_today(input_date):
  try:
    input_date = datetime.strptime(input_date, "%d-%m-%Y").date()
    today = date.today()
    if input_date < today:
      return True
    else:
      return False
  except ValueError:
    return False
  
def is_date_grater_than(start_date , end_date):
  try:
    date_1 = datetime.strptime(start_date , "%d-%m-%Y")
    date_2 = datetime.strptime(end_date , "%d-%m-%Y")
    if date_2 > date_1:
      return True
    else:
      return False
  except ValueError:
    return False
  
def is_date_less_than(start_date , end_date):
  try:
    date_1 = datetime.strptime(start_date , "%d-%m-%Y")
    date_2 = datetime.strptime(end_date , "%d-%m-%Y")
    if date_2 < date_1:
      return True
    else:
      return False
  except ValueError:
    return False
  
def get_start_and_end_date(year, month):
    start_date = datetime(year, month, 1)
    if month == 12:
        end_date = datetime(year + 1, 1, 1) - timedelta(days=1)
    else:
        end_date = datetime(year, month + 1, 1) - timedelta(days=1)

    return start_date, end_date