- [x] Засетапить простейшую команду start
- [x] Добавить авторизацию
    - [ ] Спрятать разрешенных пользователей
- [x] Добавить функцию /chat
    - See [link](https://pycoders.com/link/11037/urrlnpecgc)
- [ ] Добавить сохраненные prompt-ы /prompt {prompt_name}
- [ ] Добавить функицю /sum статей по ссылке /sum {url}
- [x] Добавить кнопки End chat, New chat
- [ ] Добавить перевод через Deepl


Для удаления клавиатуры
 ```python
from telegram import ReplyKeyboardRemove
await update.message.reply_text(reply_text, reply_markup=ReplyKeyboardRemove())
 ``` 

```bash
sudo systemctl restart nginx && sudo systemctl status nginx
```