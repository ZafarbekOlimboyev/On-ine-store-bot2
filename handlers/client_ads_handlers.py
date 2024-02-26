from time import time

from aiogram import Router, F
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, InputMediaPhoto
from aiogram.filters import CommandStart, Command

from config import DB_NAME, admins
from keyboards.client_inline_keyboards import get_category_list, get_product_list, left_right_k, make_ad_kb, \
    make_ad_kb_with_left_right
from states.client_states import ClientAdsStates
from utils.database import Database

ads_router = Router()
db = Database(DB_NAME)


@ads_router.message(Command('new_ad'))
async def new_ad_handler(message: Message, state: FSMContext):
    await state.set_state(ClientAdsStates.selectAdCategory)
    await message.answer(
        "Please, choose a category for your ad: ",
        reply_markup=get_category_list()
    )


@ads_router.callback_query(ClientAdsStates.selectAdCategory)
async def select_ad_category(callback: CallbackQuery, state: FSMContext):
    await state.set_state(ClientAdsStates.selectAdProduct)
    await callback.message.edit_text(
        "Please, choose a product type for your ad: ",
        reply_markup=get_product_list(int(callback.data))
    )


@ads_router.callback_query(ClientAdsStates.selectAdProduct)
async def select_ad_product(callback: CallbackQuery, state: FSMContext):
    await state.set_state(ClientAdsStates.insertTitle)
    await state.update_data(ad_product=callback.data)
    await callback.message.answer(
        f"Please, send title for your ad!\n\n"
        f"For example:"
        f"\n\t- iPhone 15 Pro Max 8/256 is on sale"
        f"\n\t- Macbook Pro 13\" M1 8/256 is on sale"
    )
    await callback.message.delete()


@ads_router.message(ClientAdsStates.insertTitle)
async def ad_title_handler(message: Message, state: FSMContext):
    await state.update_data(ad_title=message.text)
    await state.set_state(ClientAdsStates.insertText)
    await message.answer("OK, please, send text(full description) for your ad.")


@ads_router.message(ClientAdsStates.insertText)
async def ad_text_handler(message: Message, state: FSMContext):
    await state.update_data(ad_text=message.text)
    await state.set_state(ClientAdsStates.insertPrice)
    await message.answer("OK, please, send price for your ad (only digits).")


@ads_router.message(ClientAdsStates.insertPrice)
async def ad_price_handler(message: Message, state: FSMContext):
    if message.text.isdigit():
        await state.update_data(ad_price=int(message.text))
        await state.set_state(ClientAdsStates.insertImages)
        await message.answer("OK, please, send image(s) for your ad.")
    else:
        await message.answer("Please, send only number...")


@ads_router.message(ClientAdsStates.insertImages)
async def ad_photo_handler(message: Message, state: FSMContext):
    if message.photo:
        await state.update_data(ad_photo=message.photo[-1].file_id)
        await state.set_state(ClientAdsStates.insertPhone)
        await message.answer("OK, please, send phone number for contact with your.")
    else:
        await message.answer("Please, send image(s)...")


@ads_router.message(ClientAdsStates.insertPhone)
async def ad_phone_handler(message: Message, state: FSMContext):
    await state.update_data(ad_phone=message.text)
    all_data = await state.get_data()
    try:
        x = db.insert_ad(
            title=all_data.get('ad_title'),
            text=all_data.get('ad_text'),
            price=all_data.get('ad_price'),
            image=all_data.get('ad_photo'),
            phone=all_data.get('ad_phone'),
            u_id=message.from_user.id,
            prod_id=all_data.get('ad_product'),
            date=time()
        )
        if x:
            await state.clear()
            await message.answer("Your ad successfully added!")
        else:
            await message.answer("Something error, please, try again later...")
    except:
        await message.answer("Resend phone please...")

@ads_router.message(Command('all_ads')) #Bu komanda aslida "ads" edi ammo men uni "all_ads"ga o'zgartirdim
async def all_ads_handler(message: Message, state: FSMContext):
    all_ads = db.get_my_ads(message.from_user.id)
    if all_ads is None:
        await message.answer("You've no any ads")
    elif len(all_ads) == 1:
        await message.answer_photo(
            photo=all_ads[0][4],
            caption=f"<b>{all_ads[0][1]}</b>\n\n{all_ads[0][2]}\n\nPrice: ${all_ads[0][3]}",
            parse_mode=ParseMode.HTML
        )
    else:
        await state.set_state(ClientAdsStates.showAllAds)
        await state.update_data(all_ads=all_ads)
        await state.update_data(index=0)
        await message.answer_photo(
            photo=all_ads[0][4],
            caption=f"<b>{all_ads[0][1]}</b>\n\n{all_ads[0][2]}\n\nPrice: ${all_ads[0][3]}\n\n Ad 1 from {len(all_ads)}.",
            parse_mode=ParseMode.HTML,
            reply_markup=left_right_k
        )


@ads_router.callback_query(ClientAdsStates.showAllAds)
async def show_all_ads_handler(callback: CallbackQuery, state: FSMContext):
    all_data = await state.get_data()
    index = all_data.get('index')
    all_ads = all_data.get('all_ads')

    if callback.data == 'right':
        if index == len(all_ads)-1:
            index = 0
        else:
            index = index + 1
        await state.update_data(index=index)

        await callback.message.edit_media(
            media=InputMediaPhoto(
                media=all_ads[index][4],
                caption=f"<b>{all_ads[index][1]}</b>\n\n{all_ads[index][2]}\n\nPrice: ${all_ads[index][3]}\n\n Ad {index+1} from {len(all_ads)}.",
                parse_mode=ParseMode.HTML
            ),
            reply_markup=left_right_k
        )
    else:
        if index == 0:
            index = len(all_ads) - 1
        else:
            index = index - 1

        await state.update_data(index=index)

        await callback.message.edit_media(
            media=InputMediaPhoto(
                media=all_ads[index][4],
                caption=f"<b>{all_ads[index][1]}</b>\n\n{all_ads[index][2]}\n\nPrice: ${all_ads[index][3]}\n\n Ad {index+1} from {len(all_ads)}.",
                parse_mode=ParseMode.HTML
            ),
            reply_markup=left_right_k
        )


#----------------------------HOME WORK-------------------------------------------------#

#-------------------------COMMAND 'ads' -----------------------------------------------#

#___________________________START______________________________________________________#

@ads_router.message(Command("ads"))
async def ads(msg: Message,  state: FSMContext):
    await msg.answer("Please send your ad name..")
    await state.set_state(ClientAdsStates.ad_state)

#-------------------------------------------------------------------------------------#

@ads_router.message(ClientAdsStates.ad_state)
async def find_ad(msg: Message, state: FSMContext):
    all_ads = db.find_my_ads(u_id=msg.from_user.id,ads_name=msg.text)
    if not all_ads:
        await msg.answer(text="You have no any ads")
        await state.clear()
    elif len(all_ads) == 1:
        ids = [i for i in range(len(all_ads))]
        await state.update_data(all_ads=all_ads)
        await msg.answer(text="Results 1 of 1\n\n1. "+all_ads[0][1],reply_markup=make_ad_kb(id=ids))
    elif len(all_ads) <= 10:
        ids = [i for i in range(len(all_ads))]
        await state.update_data(all_ads=all_ads,ids=ids)
        text = f'Results 1-{len(all_ads)}  of {len(all_ads)}\n\n'
        titles = [i[1] for i in all_ads]
        s = 1
        for i in titles:
            text += f"\t{s}. {i}\n"
            s += 1
        await msg.answer(text=text,reply_markup=make_ad_kb(id=ids))
    else:
        await state.update_data(all_ads=all_ads,interval_start=0,interval_stop=10)
        text = f'Results 1-10  of {len(all_ads)}\n\n'
        titles = [i[1] for i in all_ads]
        s = 1
        for i in range(10):
            text += f"\t{s}. {titles[i]}\n"
            s += 1
        await msg.answer(text=text, reply_markup=make_ad_kb_with_left_right(start=0,stop=10))


#------------------------------------------------------------------------------------------------#


@ads_router.callback_query(ClientAdsStates.ad_state)
async def ads_handler(query: CallbackQuery, state: FSMContext):
    all_ads = (await state.get_data()).get('all_ads')
    data = await state.get_data()
    start = data.get("interval_start")
    stop = data.get("interval_stop")
    if query.data == "left":
        if start == 0:
            start = len(all_ads)-(len(all_ads)%10)
            stop = len(all_ads)
        elif len(all_ads) == stop:
            start = 0
            stop = 10
        else:
            start -= 10
            stop -= 10
        await state.update_data(interval_start=start, interval_stop=stop)
        text = f'Results {start+1}-{stop}  of {len(all_ads)}\n\n'
        titles = [i[1] for i in all_ads]
        s = 1
        for i in range(start,stop):
            text += f"\t{s}. {titles[i]}\n"
            s += 1
        await query.message.edit_text(text=text, reply_markup=make_ad_kb_with_left_right(start=start, stop=stop))
    elif query.data == "right":
        if len(all_ads) == stop:
            start = 0
            stop = 10
        elif len(all_ads)-len(all_ads)%10 == stop:
            start = stop
            stop = len(all_ads)
        else:
            start += 10
            stop += 10
        await state.update_data(all_ads=all_ads, interval_start=start, interval_stop=stop)
        text = f'Results {start+1}-{stop}  of {len(all_ads)}\n\n'
        titles = [i[1] for i in all_ads]
        s = 1
        print(start,stop)
        for i in range(start, stop):
            text += f"\t{s}. {titles[i]}\n"
            s += 1
        await query.message.edit_text(text=text, reply_markup=make_ad_kb_with_left_right(start=start, stop=stop))
    else:
        ads = all_ads[int(query.data)]
        await query.message.answer_photo(
            photo=ads[4],
            caption=f"<b>{ads[1]}</b>\n\n{ads[2]}\n\nPrice: ${ads[3]}",
            parse_mode=ParseMode.HTML
        )
