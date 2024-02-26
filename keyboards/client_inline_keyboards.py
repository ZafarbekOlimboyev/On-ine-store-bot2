from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from config import DB_NAME
from utils.database import Database


db = Database(DB_NAME)


# Function for make inline keyboards from category names
def get_category_list() -> InlineKeyboardMarkup:
    categories = db.get_categories()
    rows = []
    for category in categories:
        rows.append([
            InlineKeyboardButton(
                text=category[1],
                callback_data=str(category[0])
            )
        ])
    kb_categories = InlineKeyboardMarkup(inline_keyboard=rows)
    return kb_categories


# Function for make inline keyboards from product names
def get_product_list(cat_id: int) -> InlineKeyboardMarkup:
    products = db.get_products(cat_id)
    rows = []
    for product in products:
        rows.append([
            InlineKeyboardButton(
                text=product[1],
                callback_data=str(product[0])
            )
        ])
    kb_products = InlineKeyboardMarkup(inline_keyboard=rows)
    return kb_products


left_right_k = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="⬅️",callback_data="left"),
     InlineKeyboardButton(text="➡️",callback_data="right")]
])

def make_ad_kb_with_left_right(start,stop) -> InlineKeyboardMarkup:
    row1 = []
    row2 = []
    s = 1
    for i in range(start,stop):
        if s <= 5:
            row1.append(
                InlineKeyboardButton(text=str(s), callback_data=str(i))
            )
        else:
            row2.append(
                InlineKeyboardButton(text=str(s), callback_data=str(i))
            )
        s +=1
    ad_list_kb = InlineKeyboardMarkup(inline_keyboard=[
        row1,
        row2,
        [InlineKeyboardButton(text="⬅️", callback_data="left"),
         InlineKeyboardButton(text="➡️", callback_data="right")]
    ])
    return ad_list_kb
def make_ad_kb(id) -> InlineKeyboardMarkup:
    row1 = []
    row2 = []
    s = 1
    for i in id:
        if s <= 5:
            row1.append(
                InlineKeyboardButton(text=str(s), callback_data=str(i))
            )
        else:
            row2.append(
                InlineKeyboardButton(text=str(s), callback_data=str(i))
            )
        s +=1
    ad_list_kb = InlineKeyboardMarkup(inline_keyboard=[
        row1,
        row2
    ])
    return ad_list_kb