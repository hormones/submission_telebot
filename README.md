# a simple telegram bot for channel submission

**English | [简体中文](./README_ZH.md) | [日本語](./README_JP.md)**<br>

## Features
- [x] Anonymous submission, support text, image, video and so on
- [x] Reply to user with reason when submission is approved or rejected
- [x] Multi-language, support Chinese, English and Japanese
- [x] Admin can view/ban/unban user
- [x] Admin can view/modify some config in bot
- [x] Anonymous not allowed for forwarded message
- [x] User can feedback with `/feedback` command

## TODO
- [ ] Submission statistics
- [ ] Submission limit, like word limit, image limit and so on
- [ ] Comments in the submission through BOT (very useful when anonymous)
- [ ] Docker support


## Q&A
1. What are the roles?

    Admin: BOT administrator, can view/modify some config, view/ban/unban user

    Approver: approve submission

    User: submission with BOT

2. How to add admin?
    Before server start, configure in `config.yml` by property `super_admins`, multiple admins are separated by commas `,`
3. How to add approver?
    Invite approver to join approval channel, all users who subscribe to the approval channel can approve submission
4. How to set default language?
    Configure in `i18n.yml` by property `langs`, put the default language in the first place

## Prepare
1. Apply api_id and api_hash from https://my.telegram.org/apps
2. Apply a bot token from [@botfather](https://t.me/botfather)
3. Prepare a channel for approval, must be private channel, add bot to channel and grant admin permission
4. Prepare a group for approval, must be private group, link to approval channel, add bot to group and grant admin permission
5. Prepare a channel for show, add bot to channel and grant admin permission, submission will be forwarded to this channel when approved
6. Get channel and group id from [@userinfobot](https://t.me/userinfobot)

## Deploy

The first time you run this BOT service, you need to perform steps 1, 2, and 3. After that, you can run directly step 3

1. Run the following command on server (install git first, only support python3 and python3 version >= 3.10.6)
```bash
git clone https://github.com/hormones/submission_telebot
cd submission_telebot
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
2. Modify file `config.py` or set environment variable, see `config.py` for more detail
3. Run `source ./venv/bin/activate && nohup python main.py >/dev/null 2>&1 &` to start bot

## Commands

Users can use `/help`、`/lang`、`/feedback` by default, you can add or delete user commands in `user_command` in file `config.py`

BOT administrators can use all commands by default, can not be modified

| Command   | Parameter                            | Default permission            | Use range                                 | Description                                                  |
| --------- | ------------------------------------ | ----------------------------- | ----------------------------------------- | ------------------------------------------------------------ |
| /help     | Optional, command name               | All                    | in BOT                            | View help, you can enter command parameters to view the corresponding command detailed usage method |
| /setting  | -                                    | BOT admin              |  in BOT                            | View/modify some settings                                    |
| /ban      | Optional, user ID/username/@username | BOT admin              |  in BOT                            | View/ban/unban user                                          |
| /lang     | -                                    | All                    |  in BOT                            | Multi-language                                               |
| /feedback | Required, feedback content           | User                   |  in BOT                            | Feedback                                                     |
| /reply    | Required, reply content              | approval channel members  |  in approval channel message comments | Reply to user with reason when submission is approved or rejected  |

## License
MIT

## Example
[@submission_telebot](https://t.me/submission_telebot)

## Current problems/optimization points
- [ ] When the desktop version submits multiple pictures in one message, if you choose not to compress the picture, it will be sent by Telegram in turn, resulting in the submission being split into multiple messages (there is no problem with compressed pictures, and there is no good solution for the time being)

## FAQ
1. If server start failed, please check log file `submission_telebot.log` first, if you have any question, please submit issue
1. all config in `config.yml` can be set as environment variable, when there is a corresponding environment variable, it will overwrite the configuration in the configuration file
1. The English and Japanese translations in this project are translated by [Github Copilot](https://github.com/features/copilot) plugin, if there is any objection, please submit issue
1. If you need to customize the information display, you can study and edit the multi-language configuration in the `i18n.yml` file to better fit the project theme
1. If you have any other questions or suggestions, please submit issue