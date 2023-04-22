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

- [ ] Submission limit, like word limit, image limit and so on
- [ ] Submission statistics

## Q&A
1. What are the roles?
    Admin: BOT administrator, can view/modify some config, view/ban/unban user
    Approver: approve submission
    User: submission with BOT
1. How to add admin?
    Before server start, configure in `config.yml` in `super_admin` property, multiple administrators are separated by commas `,`
1. How to add approver?
    Invite approver to join approval channel, all users who subscribe to the approval channel can approve submission

## Prepare
1. Apply api_id and api_hash from https://my.telegram.org/apps
1. Apply a bot token from [@botfather](https://t.me/botfather)
1. Prepare a channel for approval, must be private channel, add bot to channel and grant admin permission
1. Prepare a group for approval, must be private group, link to approval channel, add bot to group and grant admin permission
1. Prepare a channel for show, add bot to channel and grant admin permission, submission will be forwarded to this channel when approved
1. Get channel and group id from [@userinfobot](https://t.me/userinfobot)

## Deploy
1. Run the following command on server (install git first)
```bash
git clone xxxx/submission_telebot.git
cd submission_telebot
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
1. Modify file `config.py` or set environment variable, see `config.py` for more detail
1. Run `nohup python main.py >/dev/null 2>&1 &` to start bot
1. Use bot to check if it is running normally

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
- [ ] After the approval is completed, the approved log is sent as reply to the approval channel instead of being placed in the comments

## FAQ
1. If server start failed, please check log file `submission_telebot.log` first, if you have any question, please submit issue
1. all config in `config.yml` can be set as environment variable, when there is a corresponding environment variable, it will overwrite the configuration in the configuration file
1. The English and Japanese translations in this project are translated by [Github Copilot](https://github.com/features/copilot) plugin, if there is any objection, please submit issue
1. If you need to customize the information display, you can study and edit the multi-language configuration in the `i18n.yml` file to better fit the project theme
1. If you have any other questions or suggestions, please submit issue