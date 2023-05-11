from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext

from tgbot.keyboards.user.inlinekeyboard.order_ikb.order_cake_ikb import choice_subcategory_cake_ikb, \
    choice_filling_cake_biscuit_ikb, choice_value_cake_bis_mus_ikb, \
    choice_filling_bento_cake_ikb, choice_subctg_cb, choice_filling_cake_cb, choice_filling_cake_mousse_ikb, \
    choice_value_bento_cake_ikb, choice_value_cake_cb
from tgbot.keyboards.user.inlinekeyboard.order_ikb.order_main_ikb import accept_ikb, choice_category_cb, stop_ikb
from tgbot.misc.info_item import cake_info, \
    bento_cake_filling_info, cake_biscuit_filling_info, cake_mousse_filling_info
from tgbot.models.state import OrderStateGroup


async def choice_subcategory_cake_order(callback: types.CallbackQuery, state: FSMContext, callback_data: dict):
    await callback.message.edit_text(text=cake_info,
                                     reply_markup=choice_subcategory_cake_ikb)
    category = callback_data.get('category')
    async with state.proxy() as data:
        data['category'] = category
    await OrderStateGroup.subcategory.set()


async def choice_filling_cake_order(callback: types.CallbackQuery, state: FSMContext, callback_data: dict):
    subcategory = callback_data.get('subcategory')
    async with state.proxy() as data:
        data['subcategory'] = subcategory

    if subcategory == 'Бисквитный торт':
        filling_info = cake_biscuit_filling_info
        filling_ikb = choice_filling_cake_biscuit_ikb
    elif subcategory == 'Бенто-торт':
        filling_info = bento_cake_filling_info
        filling_ikb = choice_filling_bento_cake_ikb
    elif subcategory == 'Муссовый торт':
        filling_info = cake_mousse_filling_info
        filling_ikb = choice_filling_cake_mousse_ikb
    else:
        return

    await callback.message.edit_text(text=filling_info, reply_markup=filling_ikb)
    await OrderStateGroup.filling.set()


async def choice_value_cake_order(callback: types.CallbackQuery, state: FSMContext, callback_data: dict):
    filling = callback_data.get('filling')
    async with state.proxy() as data:
        data['filling'] = filling
        subcategory = data['subcategory']
    if subcategory in ['Бисквитный торт', 'Муссовый торт']:
        await callback.message.edit_text(text='Выберете размер торта',
                                         reply_markup=choice_value_cake_bis_mus_ikb)

    elif subcategory == 'Бенто-торт':
        await callback.message.edit_text(text='Выберете размер торта',
                                         reply_markup=choice_value_bento_cake_ikb)
    else:
        return
    await OrderStateGroup.value.set()


async def send_photo_cake_order(callback: types.CallbackQuery, state: FSMContext, callback_data: dict):
    value = callback_data.get('value')
    async with state.proxy() as data:
        data['value'] = value
    await callback.message.edit_text(text='Пришлите фотографию вашего дизайна',
                                     reply_markup=stop_ikb)
    await OrderStateGroup.photo.set()


async def enter_photo_order(message: types.Message, state: FSMContext):
    await message.delete()
    async with state.proxy() as data:
        data['photo'] = message.photo[0].file_id
    await message.answer_photo(photo=data['photo'],
                               caption=f"Категория: {data['category']}\n"
                                       f"Подкатегория: {data['subcategory']}\n"
                                       f"Начинка: {data['filling']}\n"
                                       f"Размер: {data['value']}\n",
                               reply_markup=accept_ikb)

    await OrderStateGroup.await_accept.set()


def register_make_cake_order_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(choice_subcategory_cake_order, choice_category_cb.filter(category='Торт'),
                                       state=OrderStateGroup.category)

    dp.register_callback_query_handler(choice_filling_cake_order, choice_subctg_cb.filter(),
                                       state=OrderStateGroup.subcategory)

    dp.register_callback_query_handler(choice_value_cake_order, choice_filling_cake_cb.filter(),
                                       state=OrderStateGroup.filling)

    dp.register_callback_query_handler(send_photo_cake_order, choice_value_cake_cb.filter(),
                                       state=OrderStateGroup.value)

    dp.register_message_handler(enter_photo_order, content_types=types.ContentType.PHOTO,
                                state=OrderStateGroup.photo)